from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceList
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    # Check if invoice number already exists
    existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice.invoice_number).first()
    if existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice number already exists"
        )
    
    db_invoice = Invoice(**invoice.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.get("/", response_model=InvoiceList)
async def get_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    vendor_name: Optional[str] = Query(None, description="Filter by vendor name"),
    db: Session = Depends(get_db)
):
    """Get list of invoices with pagination and filtering"""
    query = db.query(Invoice)
    
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    if vendor_name:
        query = query.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))
    
    total = query.count()
    invoices = query.offset(skip).limit(limit).all()
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return InvoiceList(
        invoices=invoices,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing invoice"""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    update_data = invoice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)
    
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Delete an invoice"""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Delete associated file if exists
    if db_invoice.file_path and os.path.exists(db_invoice.file_path):
        os.remove(db_invoice.file_path)
    
    db.delete(db_invoice)
    db.commit()
    return None


@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice_file(
    invoice_id: int = Query(..., description="Invoice ID to attach file to"),
    file: UploadFile = File(..., description="Invoice file to upload"),
    db: Session = Depends(get_db)
):
    """Upload a file for an invoice"""
    # Validate file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Get invoice
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"invoice_{invoice_id}_{timestamp}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update invoice with file path
    db_invoice.file_path = file_path
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice


@router.get("/stats/summary")
async def get_invoice_stats(db: Session = Depends(get_db)):
    """Get invoice statistics summary"""
    total_invoices = db.query(Invoice).count()
    pending_invoices = db.query(Invoice).filter(Invoice.status == "pending").count()
    paid_invoices = db.query(Invoice).filter(Invoice.status == "paid").count()
    overdue_invoices = db.query(Invoice).filter(Invoice.status == "overdue").count()
    
    total_amount = db.query(Invoice).filter(Invoice.status == "pending").with_entities(
        db.func.sum(Invoice.total_amount)
    ).scalar() or 0.0
    
    return {
        "total_invoices": total_invoices,
        "pending_invoices": pending_invoices,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "total_pending_amount": round(total_amount, 2)
    } 