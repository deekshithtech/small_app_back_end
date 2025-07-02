from sqlalchemy import Column,Numeric, Integer, String, Text, DECIMAL, Date, Enum, ForeignKey, TIMESTAMP ,DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
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
    orders = relationship("CustomerAdded", back_populates="item")

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    last_restocked = Column(Date)

    item = relationship("Item", back_populates="inventory")
    
    
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    address = Column(String(255))
    created_at = Column(Date, server_default=func.now())

    orders = relationship("CustomerAdded", back_populates="customer")

class CustomerAdded(Base):
    __tablename__ = "customer_added"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    item_id = Column(Integer, ForeignKey("items.item_id"))
    quantity = Column(Integer)
    total_price = Column(Numeric(10, 2))
    ordered_at = Column(Date, server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    item = relationship("Item", back_populates="orders")





