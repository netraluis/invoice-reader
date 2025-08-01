# Invoice Reader API

API for uploading and processing invoices and receipts in image or document format.

## Features

- ✅ Individual file upload (images and PDFs)
- ✅ File type and size validation
- ✅ User ID association
- ✅ Unique names to avoid conflicts
- ✅ Automatic documentation with Swagger
- ✅ OCR text extraction from images
- ✅ AI-powered field extraction using Mistral 7B (free)

## Installation

### OpenRouter Setup

This API uses **Mistral 7B Instruct** via OpenRouter for AI-powered field extraction. You need a free API key:

1. **Get Free API Key**: Visit [https://openrouter.ai/](https://openrouter.ai/) and sign up
2. **Copy API Key**: From your dashboard, copy your API key
3. **Configure**: Add it to your `.env` file

### Local Development

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set up OpenRouter API key (required - get free key from https://openrouter.ai/)
cp env.example .env
# Edit .env and add your OpenRouter API key
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

#### Image response or PDF response:
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
  },
  "parsed_fields": {
    "contacto": "ABC Corp",
    "numero_documento": "INV-001",
    "fecha_emision": "15/01/2024",
    "divisa": "USD",
    "precio": 150.50,
    "descuento": null,
    "impuesto": 15.05,
    "total": 165.55,
    "confidence": "high"
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
- **Pydantic** - Data validation
- **Tesseract OCR** - Text extraction from images
- **Mistral 7B Instruct** - AI-powered field extraction (via OpenRouter)

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
