# Invoice Reader API

API for uploading and processing invoices and receipts in image or document format.

## Features

- ✅ Individual file upload (images and PDFs)
- ✅ File type and size validation
- ✅ User ID association
- ✅ Unique names to avoid conflicts
- ✅ Automatic documentation with Swagger
- ✅ OCR text extraction from images

## Installation

### Local Development

```bash
# Install dependencies
pip3 install -r requirements.txt
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t invoice-reader .

# Run the container
docker run -p 8000:8000 invoice-reader
```

## Usage

### Run the server

```bash
# Option 1: Direct
python main.py

# Option 2: With uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Docker
docker run -p 8000:8000 invoice-reader
```

### Endpoints

- **POST** `/upload-invoice` - Upload invoices/receipts
- **GET** `/health` - Check API status
- **GET** `/` - API information
- **GET** `/docs` - Interactive documentation (Swagger)

### Example usage with curl

```bash
# Upload an image with user_id
curl -X POST "http://localhost:8000/upload-invoice" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@factura.jpg" \
  -F "user_id=user123"

# Upload a PDF with user_id
curl -X POST "http://localhost:8000/upload-invoice" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ticket.pdf" \
  -F "user_id=user456"
```

### Supported file types

- **Images**: JPG, JPEG, PNG, TIFF, BMP
- **Documents**: PDF
- **Maximum size**: 10MB per file

### Example responses

#### Image response:
```json
{
  "success": true,
  "file_info": {
    "original_name": "factura.jpg",
    "saved_name": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
    "file_path": "uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
    "file_size": 245760,
    "content_type": "image/jpeg",
    "uploaded_at": "2024-01-15T10:30:00.123456"
  },
  "user_id": "user123",
  "ocr_result": {
    "success": true,
    "text": "INVOICE\nCompany: ABC Corp\nAmount: $150.50\nDate: 2024-01-15",
    "confidence": 85.5,
    "word_count": 8,
    "char_count": 45
  }
}
```

#### PDF response (direct extraction):
```json
{
  "success": true,
  "file_info": {
    "original_name": "invoice.pdf",
    "saved_name": "b2c3d4e5-f6g7-8901-bcde-f23456789012.pdf",
    "file_path": "uploads/b2c3d4e5-f6g7-8901-bcde-f23456789012.pdf",
    "file_size": 512000,
    "content_type": "application/pdf",
    "uploaded_at": "2024-01-15T10:30:00.123456"
  },
  "user_id": "user123",
  "ocr_result": {
    "success": true,
    "text": "INVOICE\nCompany: ABC Corp\nAmount: $150.50\nDate: 2024-01-15",
    "method": "direct_extraction",
    "confidence": 100.0,
    "word_count": 8,
    "char_count": 45,
    "pages": 1
  }
}
```

#### PDF response (OCR conversion):
```json
{
  "success": true,
  "file_info": {
    "original_name": "scanned_invoice.pdf",
    "saved_name": "c3d4e5f6-g7h8-9012-cdef-g34567890123.pdf",
    "file_path": "uploads/c3d4e5f6-g7h8-9012-cdef-g34567890123.pdf",
    "file_size": 1024000,
    "content_type": "application/pdf",
    "uploaded_at": "2024-01-15T10:30:00.123456"
  },
  "user_id": "user123",
  "ocr_result": {
    "success": true,
    "text": "--- Page 1 ---\nINVOICE\nCompany: ABC Corp\nAmount: $150.50\nDate: 2024-01-15",
    "method": "ocr_conversion",
    "confidence": 82.3,
    "word_count": 8,
    "char_count": 45,
    "pages": 1
  }
}
```

## Project structure

```
invoice-reader/
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── Dockerfile          # Docker configuration
├── uploads/            # Uploaded files directory
├── .gitignore          # Git ignored files
└── README.md           # This file
```

## Development

The API is built with:
- **FastAPI** - Modern and fast web framework
- **Uvicorn** - ASGI server
- **Pillow** - Image processing
- **Pydantic** - Data validation
- **Tesseract OCR** - Text extraction from images

## Deployment

### Docker (Recommended)

The included Dockerfile automatically installs Tesseract OCR and all dependencies:

```bash
# Build and run
docker build -t invoice-reader .
docker run -p 8000:8000 invoice-reader

# With volume for persistent uploads
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads invoice-reader
```

### Cloud Deployment

The Docker image can be deployed to:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku** (with Docker support)
- **DigitalOcean App Platform**
