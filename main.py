from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import shutil
from pathlib import Path

app = FastAPI(
    title="Invoice Reader API",
    description="API for uploading and processing invoices and receipts",
    version="1.0.0"
)

# Configuración de directorios
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Crear directorio de uploads si no existe
UPLOAD_DIR.mkdir(exist_ok=True)

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
            "user_id": user_id
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 