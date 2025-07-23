from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InvoiceBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=100)
    vendor_name: str = Field(..., min_length=1, max_length=200)
    vendor_address: Optional[str] = None
    client_name: str = Field(..., min_length=1, max_length=200)
    client_address: Optional[str] = None
    invoice_date: datetime
    due_date: Optional[datetime] = None
    subtotal: float = Field(..., gt=0)
    tax_amount: float = Field(default=0.0, ge=0)
    total_amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    status: str = Field(default="pending", regex="^(pending|paid|overdue|cancelled)$")
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    vendor_address: Optional[str] = None
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_address: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    subtotal: Optional[float] = Field(None, gt=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    status: Optional[str] = Field(None, regex="^(pending|paid|overdue|cancelled)$")
    notes: Optional[str] = None
    is_processed: Optional[bool] = None


class InvoiceResponse(InvoiceBase):
    id: int
    file_path: Optional[str] = None
    is_processed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InvoiceList(BaseModel):
    invoices: list[InvoiceResponse]
    total: int
    page: int
    size: int
    pages: int 