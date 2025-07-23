# Invoice Reader API

A modern, fast, and secure API for processing and managing invoices built with FastAPI.

## Features

- 🔐 **Authentication & Authorization** - JWT-based authentication with user management
- 📄 **Invoice Management** - Full CRUD operations for invoices
- 📁 **File Upload** - Support for PDF, JPG, PNG, and TIFF invoice files
- 📊 **Statistics** - Invoice analytics and summary data
- 🗄️ **Database** - SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL)
- 📝 **Auto Documentation** - Interactive API docs with Swagger UI
- 🔒 **Security** - CORS, trusted hosts, and input validation
- ⚡ **Performance** - Async endpoints with request timing

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invoice-reader
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/` - List users (paginated)
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Invoices
- `GET /api/v1/invoices/` - List invoices (with filtering and pagination)
- `POST /api/v1/invoices/` - Create a new invoice
- `GET /api/v1/invoices/{invoice_id}` - Get invoice by ID
- `PUT /api/v1/invoices/{invoice_id}` - Update invoice
- `DELETE /api/v1/invoices/{invoice_id}` - Delete invoice
- `POST /api/v1/invoices/upload` - Upload invoice file
- `GET /api/v1/invoices/stats/summary` - Get invoice statistics

## Example Usage

### Create an Invoice
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-001",
    "vendor_name": "Tech Solutions Inc",
    "client_name": "Acme Corp",
    "invoice_date": "2024-01-15T00:00:00",
    "subtotal": 1000.00,
    "total_amount": 1100.00,
    "currency": "USD"
  }'
```

### Upload Invoice File
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/upload?invoice_id=1" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf"
```

## Project Structure

```
invoice-reader/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── invoices.py
│   │       │   └── users.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── invoice.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── invoice.py
│   │   └── user.py
│   └── main.py
├── requirements.txt
├── run.py
└── README.md
```

## Configuration

Key configuration options in `.env`:

- `SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `MAX_FILE_SIZE`: Maximum file upload size
- `ALLOWED_ORIGINS`: CORS allowed origins

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
The app uses SQLAlchemy with automatic table creation. For production, consider using Alembic for migrations.

### Adding New Endpoints
1. Create endpoint file in `app/api/v1/endpoints/`
2. Add router to `app/api/v1/api.py`
3. Create schemas in `app/schemas/`
4. Add models if needed in `app/models/`

## Production Deployment

1. **Set production environment variables**
2. **Use a production database** (PostgreSQL recommended)
3. **Configure proper CORS settings**
4. **Set up reverse proxy** (nginx recommended)
5. **Use process manager** (systemd, supervisor, etc.)

## License

MIT License
