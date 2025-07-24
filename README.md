# Invoice Reader API

API para subir y procesar facturas y tickets en formato de imagen o documento.

## Características

- ✅ Subida de múltiples archivos (imágenes y PDFs)
- ✅ Validación de tipos de archivo y tamaño
- ✅ Metadatos opcionales (descripción, monto, fecha)
- ✅ Nombres únicos para evitar conflictos
- ✅ Documentación automática con Swagger

## Instalación

```bash
# Instalar dependencias
pip3 install -r requirements.txt
```

## Uso

### Ejecutar el servidor

```bash
# Opción 1: Directo
python main.py

# Opción 2: Con uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints

- **POST** `/upload-invoice` - Subir facturas/tickets
- **GET** `/health` - Verificar estado de la API
- **GET** `/` - Información de la API
- **GET** `/docs` - Documentación interactiva (Swagger)

### Ejemplo de uso con curl

```bash
# Subir una imagen
curl -X POST "http://localhost:8000/upload-invoice" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@factura.jpg" \
  -F "description=Factura de electricidad" \
  -F "amount=150.50" \
  -F "date=2024-01-15"

# Subir múltiples archivos
curl -X POST "http://localhost:8000/upload-invoice" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@factura1.jpg" \
  -F "files=@factura2.pdf" \
  -F "description=Facturas del mes"
```

### Tipos de archivo soportados

- **Imágenes**: JPG, JPEG, PNG, TIFF, BMP
- **Documentos**: PDF
- **Tamaño máximo**: 10MB por archivo

### Respuesta de ejemplo

```json
{
  "success": true,
  "uploaded_files": [
    {
      "original_name": "factura.jpg",
      "saved_name": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
      "file_path": "uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
      "file_size": 245760,
      "content_type": "image/jpeg",
      "uploaded_at": "2024-01-15T10:30:00.123456"
    }
  ],
  "total_files": 1,
  "successful_uploads": 1,
  "errors": [],
  "metadata": {
    "description": "Factura de electricidad",
    "amount": 150.5,
    "date": "2024-01-15",
    "upload_timestamp": "2024-01-15T10:30:00.123456"
  }
}
```

## Estructura del proyecto

```
invoice-reader/
├── main.py              # Aplicación FastAPI
├── requirements.txt     # Dependencias
├── uploads/            # Directorio de archivos subidos
├── .gitignore          # Archivos ignorados por git
└── README.md           # Este archivo
```

## Desarrollo

La API está construida con:
- **FastAPI** - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI
- **Pillow** - Procesamiento de imágenes
- **Pydantic** - Validación de datos
