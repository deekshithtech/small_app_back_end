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
    image: Optional[str] = None

class ItemUpdate(BaseModel):
    name: str= Field(None, max_length=100)
    description: str = None
    price: float = Field(None, gt=0)
    category: str = Field(None, max_length=50)
    image: Optional[str] = None

    
    class Config:
        orm_mode = True

class Item(BaseModel):
    item_id: int
    name: str

    class Config:
        orm_mode = True

class Inventory(BaseModel):
    inventory_id: int
    item_id: int
    quantity: int
    last_restocked: Optional[date] = None
    item: Optional[Item] = None

    class Config:
        orm_mode = True

class InventoryUpdate(BaseModel):
    quantity:int
# /==================================================



# /==================================================



class CustomerBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=10)
    address: str = None

class CustomerCreate(CustomerBase):
    customer_id: Optional[int] = None  # ✅ Add this

class Customer(CustomerBase):
    customer_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class PurchaseItemCreate(BaseModel):
    item_id: int
    quantity: int
    
class PurchaseCreate(BaseModel):
    customer: CustomerCreate
    items: List[PurchaseItemCreate]
    total: Optional[float] = None


class PurchaseResponse(BaseModel):
    success: bool
    message: str
    customer: CustomerCreate
    items: List[PurchaseItemCreate]
    total: Optional[float] = None
