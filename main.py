from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import shutil
from pathlib import Path
import pytesseract
from PIL import Image
import cv2
import numpy as np
import PyPDF2
from pdf2image import convert_from_path
import tempfile
import re
from typing import Dict, Any
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Invoice Reader API",
    description="API for uploading and processing invoices and receipts",
    version="1.0.0"
)

# Configuration
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

def extract_text_from_image(image_path: str) -> dict:
    """
    Extract text from image using OCR
    """
    try:
        # Read image with OpenCV
        image = cv2.imread(image_path)
        if image is None:
            return {"success": False, "error": "Could not read image"}
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Preprocess image for better OCR
        # Convert to grayscale
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to get black text on white background
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text with Tesseract
        # Try multiple languages: English and Spanish
        text = pytesseract.image_to_string(thresh, lang='eng+spa')
        
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(thresh, lang='eng+spa', output_type=pytesseract.Output.DICT)
        
        # Calculate confidence
        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "success": True,
            "text": text.strip(),
            "confidence": avg_confidence,
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text from PDF using direct extraction first, then OCR if needed
    """
    try:
        # First attempt: Direct text extraction
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If we got meaningful text, return it
            if text.strip():
                return {
                    "success": True,
                    "text": text.strip(),
                    "method": "direct_extraction",
                    "confidence": 100.0,
                    "word_count": len(text.split()),
                    "char_count": len(text),
                    "pages": len(pdf_reader.pages)
                }
        except Exception as e:
            # If direct extraction fails, continue to OCR
            pass
        
        # Second attempt: Convert PDF to image and use OCR
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            all_text = []
            total_confidence = 0
            total_words = 0
            total_chars = 0
            
            for i, image in enumerate(images):
                # Save temporary image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    image.save(tmp_file.name, 'PNG')
                    tmp_path = tmp_file.name
                
                try:
                    # Extract text from image
                    ocr_result = extract_text_from_image(tmp_path)
                    
                    if ocr_result["success"]:
                        all_text.append(f"--- Page {i+1} ---\n{ocr_result['text']}")
                        total_confidence += ocr_result.get('confidence', 0)
                        total_words += ocr_result.get('word_count', 0)
                        total_chars += ocr_result.get('char_count', 0)
                finally:
                    # Clean up temporary file
                    os.unlink(tmp_path)
            
            if all_text:
                avg_confidence = total_confidence / len(images) if images else 0
                return {
                    "success": True,
                    "text": "\n".join(all_text),
                    "method": "ocr_conversion",
                    "confidence": avg_confidence,
                    "word_count": total_words,
                    "char_count": total_chars,
                    "pages": len(images)
                }
            
        except Exception as e:
            return {"success": False, "error": f"OCR conversion failed: {str(e)}"}
        
        return {"success": False, "error": "No text could be extracted from PDF"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_invoice_fields_ai(text: str) -> Dict[str, Any]:
    """
    Parse invoice text using Mistral 7B Instruct via OpenRouter
    """
    result = {
        "contacto": None,
        "numero_documento": None,
        "fecha_emision": None,
        "divisa": None,
        "precio": None,
        "descuento": None,
        "impuesto": None,
        "total": None,
        "confidence": "high" if text else "low"
    }
    
    if not text:
        return result
    
    try:
        # Use OpenRouter API directly with requests
        api_key = os.getenv('OPENROUTER_API_KEY')
        print(f"API Key found: {api_key[:10]}..." if api_key else "No API key found")
        
        if not api_key:
            raise Exception("OPENROUTER_API_KEY environment variable is required. Get a free API key from https://openrouter.ai/")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://invoice-reader-api.com",
            "X-Title": "Invoice Reader API"
        }
        
        data = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": "Eres un experto en extraer información de facturas y tickets. Responde siempre en formato JSON válido."},
                {"role": "user", "content": f"Extrae la siguiente información de este texto de factura/ticket. Responde SOLO en formato JSON válido con los siguientes campos: contacto, numero_documento, fecha_emision, divisa, precio, descuento, impuesto, total. Si algún campo no se encuentra, usa null. Para valores numéricos, usa solo números. Texto: {text}"}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"].strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting if present
                if ai_response.startswith("```json"):
                    ai_response = ai_response[7:]
                if ai_response.endswith("```"):
                    ai_response = ai_response[:-3]
                
                parsed_data = json.loads(ai_response)
                
                # Update result with AI extracted data
                for key in result.keys():
                    if key in parsed_data and parsed_data[key] is not None:
                        result[key] = parsed_data[key]
                
                result["confidence"] = "high"
                
            except json.JSONDecodeError as e:
                # Fallback to regex if AI parsing fails
                result = parse_invoice_fields_fallback(text)
                result["confidence"] = "medium"
        else:
            raise Exception(f"OpenRouter API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        # Fallback to regex if AI fails
        result = parse_invoice_fields_fallback(text)
        result["confidence"] = "low"
        result["ai_error"] = f"OpenRouter Error: {str(e)}"
        print(f"OpenRouter API Error: {e}")
        print(f"Error type: {type(e)}")
    
    return result

def parse_invoice_fields_fallback(text: str) -> Dict[str, Any]:
    """
    Fallback regex-based parsing when AI fails
    """
    result = {
        "contacto": None,
        "numero_documento": None,
        "fecha_emision": None,
        "divisa": None,
        "precio": None,
        "descuento": None,
        "impuesto": None,
        "total": None,
        "confidence": "low"
    }
    
    if not text:
        return result
    
    text_lower = text.lower()
    
    # Extract document number
    doc_patterns = [
        r'invoice\s*#?\s*:?\s*([a-zA-Z0-9\-_]+)',
        r'ticket\s*#?\s*:?\s*([a-zA-Z0-9\-_]+)',
        r'factura\s*#?\s*:?\s*([a-zA-Z0-9\-_]+)',
        r'#\s*([a-zA-Z0-9\-_]+)'
    ]
    
    for pattern in doc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["numero_documento"] = match.group(1).upper()
            break
    
    # Extract total
    total_patterns = [
        r'total\s*:?\s*\$?\s*([0-9,]+\.?[0-9]*)',
        r'amount\s*:?\s*\$?\s*([0-9,]+\.?[0-9]*)',
        r'\$\s*([0-9,]+\.?[0-9]*)'
    ]
    
    for pattern in total_patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                result["total"] = float(amount_str)
                break
            except ValueError:
                continue
    
    # Extract currency
    if re.search(r'\$', text):
        result["divisa"] = "USD"
    elif re.search(r'eur', text_lower):
        result["divisa"] = "EUR"
    elif re.search(r'mxn', text_lower):
        result["divisa"] = "MXN"
    
    # Extract date
    date_patterns = [
        r'date\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            result["fecha_emision"] = match.group(1)
            break
    
    return result

def validate_file(file: UploadFile) -> bool:
    """Validates the uploaded file"""
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False
    
    return True

@app.post("/upload-invoice")
async def upload_invoice(
    file: UploadFile = File(..., description="Invoice/receipt file to upload"),
    user_id: str = Form(..., description="User ID")
):
    """
    Upload an invoice/receipt image or document
    
    - **file**: File (image or PDF)
    - **user_id**: ID of the user uploading the file
    
    Text extraction:
    - Images: OCR processing
    - PDFs: Direct text extraction first, then OCR if needed
    
    AI-powered field extraction:
    - contacto: Company or person issuing the invoice
    - numero_documento: Invoice/ticket number
    - fecha_emision: Issue date
    - divisa: Currency (USD, EUR, MXN, etc.)
    - precio: Base price or subtotal
    - descuento: Discount amount if applicable
    - impuesto: Tax or VAT amount
    - total: Total amount to pay
    """
    
    if not file:
        raise HTTPException(status_code=400, detail="You must upload a file")
    
    try:
        # Validate file
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file or file too large")
        
        # Generate unique name
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text based on file type
        ocr_result = None
        if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}:
            ocr_result = extract_text_from_image(str(file_path))
        elif file_extension.lower() == '.pdf':
            ocr_result = extract_text_from_pdf(str(file_path))
        
        # Parse extracted text to extract key fields
        parsed_fields = None
        if ocr_result and ocr_result.get("success") and ocr_result.get("text"):
            parsed_fields = parse_invoice_fields_ai(ocr_result["text"])
        
        # Create response
        response_data = {
            "success": True,
            "file_info": {
                "original_name": file.filename,
                "saved_name": unique_filename,
                "file_path": str(file_path),
                "file_size": file.size,
                "content_type": file.content_type,
                "uploaded_at": datetime.now().isoformat()
            },
            "user_id": user_id,
            "ocr_result": ocr_result,
            "parsed_fields": parsed_fields
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Invoice Reader API",
        "version": "1.0.0",
        "endpoints": {
            "upload_invoice": "/upload-invoice",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    return {
        "api_key_exists": bool(api_key),
        "api_key_preview": api_key[:10] + "..." if api_key else None,
        "env_file_exists": os.path.exists(".env"),
        "current_working_dir": os.getcwd()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 