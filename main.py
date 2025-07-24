from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime
import shutil
from pathlib import Path

app = FastAPI(
    title="Invoice Reader API",
    description="API para subir y procesar facturas y tickets",
    version="1.0.0"
)

# Configuración de directorios
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Crear directorio de uploads si no existe
UPLOAD_DIR.mkdir(exist_ok=True)

def validate_file(file: UploadFile) -> bool:
    """Valida el archivo subido"""
    # Verificar extensión
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False
    
    # Verificar tamaño
    if file.size and file.size > MAX_FILE_SIZE:
        return False
    
    return True

@app.post("/upload-invoice")
async def upload_invoice(
    files: List[UploadFile] = File(..., description="Archivos de factura/ticket a subir"),
    description: Optional[str] = Form(None, description="Descripción opcional de la factura"),
    amount: Optional[float] = Form(None, description="Monto de la factura"),
    date: Optional[str] = Form(None, description="Fecha de la factura (YYYY-MM-DD)")
):
    """
    Sube una o más imágenes/documentos de factura o ticket
    
    - **files**: Lista de archivos (imágenes o PDFs)
    - **description**: Descripción opcional
    - **amount**: Monto opcional de la factura
    - **date**: Fecha opcional de la factura
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="Debe subir al menos un archivo")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validar archivo
            if not validate_file(file):
                errors.append(f"Archivo '{file.filename}' no válido o demasiado grande")
                continue
            
            # Generar nombre único
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "original_name": file.filename,
                "saved_name": unique_filename,
                "file_path": str(file_path),
                "file_size": file.size,
                "content_type": file.content_type,
                "uploaded_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            errors.append(f"Error al procesar '{file.filename}': {str(e)}")
    
    # Crear respuesta
    response_data = {
        "success": len(uploaded_files) > 0,
        "uploaded_files": uploaded_files,
        "total_files": len(files),
        "successful_uploads": len(uploaded_files),
        "errors": errors,
        "metadata": {
            "description": description,
            "amount": amount,
            "date": date,
            "upload_timestamp": datetime.now().isoformat()
        }
    }
    
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No se pudo procesar ningún archivo")
    
    return JSONResponse(content=response_data, status_code=200)

@app.get("/health")
async def health_check():
    """Endpoint de salud de la API"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
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