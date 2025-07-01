from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class ItemCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=50)
    quantity: int = Field(0, ge=0)

class ItemUpdate(BaseModel):
    name: str= Field(None, max_length=100)
    description: str = None
    price: float = Field(None, gt=0)
    category: str = Field(None, max_length=50)

    
    class Config:
        orm_mode = True

class InventoryBase(BaseModel):
    quantity: int
    last_restocked: Optional[date] = None

class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)

class Inventory(InventoryBase):
    inventory_id: int
    item_id: int
    
    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    shipped = 'shipped'
    cancelled = 'cancelled'

class PurchaseItemBase(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class PurchaseItemCreate(PurchaseItemBase):
    pass

class PurchaseItem(PurchaseItemBase):
    purchase_item_id: int
    purchase_id: int
    
    class Config:
        orm_mode = True

class PurchaseBase(BaseModel):
    customer_id: int
    total_amount: float = Field(..., gt=0)
    status: PurchaseStatus = PurchaseStatus.pending
    shipping_address: Optional[str] = None

class PurchaseCreate(BaseModel):
    customer: CustomerCreate
    items: List[PurchaseItemCreate]
    shipping_address: Optional[str] = None

class Purchase(PurchaseBase):
    purchase_id: int
    purchase_date: datetime
    customer: Customer
    items: List[PurchaseItem]
    
    class Config:
        orm_mode = True

class ShippingStatus(str, Enum):
    preparing = 'preparing'
    shipped = 'shipped'
    delivered = 'delivered'
    returned = 'returned'

class ShippingBase(BaseModel):
    shipping_date: Optional[date] = None
    tracking_number: Optional[str] = Field(None, max_length=100)
    carrier: Optional[str] = Field(None, max_length=50)
    estimated_delivery: Optional[date] = None
    status: ShippingStatus = ShippingStatus.preparing

class ShippingUpdate(BaseModel):
    shipping_date: Optional[date] = None
    tracking_number: Optional[str] = Field(None, max_length=100)
    carrier: Optional[str] = Field(None, max_length=50)
    estimated_delivery: Optional[date] = None
    status: Optional[ShippingStatus] = None

class Shipping(ShippingBase):
    shipping_id: int
    purchase_id: int
    
    class Config:
        orm_mode = True