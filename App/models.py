from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    inventory = relationship("Inventory", back_populates="item", uselist=False, passive_deletes=True)
    purchase_items = relationship("PurchaseItem", back_populates="item")


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    last_restocked = Column(Date)

    item = relationship("Item", back_populates="inventory")


class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    purchases = relationship("Purchase", back_populates="customer")

class Purchase(Base):
    __tablename__ = "purchases"
    
    purchase_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    purchase_date = Column(TIMESTAMP, server_default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum('pending', 'completed', 'shipped', 'cancelled', name='purchase_status'), default='pending')
    shipping_address = Column(Text)
    
    customer = relationship("Customer", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")
    shipping = relationship("Shipping", back_populates="purchase", uselist=False)

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    
    purchase_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchases.purchase_id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    
    purchase = relationship("Purchase", back_populates="items")
    item = relationship("Item", back_populates="purchase_items")

class Shipping(Base):
    __tablename__ = "shipping"
    
    shipping_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchases.purchase_id"), nullable=False)
    shipping_date = Column(Date)
    tracking_number = Column(String(100))
    carrier = Column(String(50))
    estimated_delivery = Column(Date)
    status = Column(Enum('preparing', 'shipped', 'delivered', 'returned', name='shipping_status'), default='preparing')
    
    purchase = relationship("Purchase", back_populates="shipping")