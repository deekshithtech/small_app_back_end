from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc
from datetime import date, datetime
from .. import models, schemas
from ..database import get_async_db
from sqlalchemy.orm import selectinload
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Purchase)
async def create_purchase(
    purchase: schemas.PurchaseCreate, 
    db: AsyncSession = Depends(get_async_db)
):
    async with db.begin():
        try:
            # Create or find customer
            if hasattr(purchase.customer, 'customer_id'):
                result = await db.execute(
                    select(models.Customer)
                    .where(models.Customer.customer_id == purchase.customer.customer_id)
                )
                customer = result.scalars().first()
                if not customer:
                    raise HTTPException(status_code=404, detail="Customer not found")
            else:
                customer = models.Customer(**purchase.customer.dict())
                db.add(customer)
                await db.flush()
            
            # Calculate total amount and validate items
            total_amount = 0.0
            purchase_items = []
            
            for item in purchase.items:
                # Get item with inventory
                result = await db.execute(
                    select(models.Item)
                    .where(models.Item.item_id == item.item_id)
                    .options(selectinload(models.Item.inventory))
                )
                db_item = result.scalars().first()
                
                if not db_item:
                    raise HTTPException(status_code=404, detail=f"Item with ID {item.item_id} not found")
                
                if not db_item.inventory or db_item.inventory.quantity < item.quantity:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Not enough stock for item {db_item.name}"
                    )
                
                total_amount += db_item.price * item.quantity
                purchase_items.append({
                    "item_id": item.item_id,
                    "quantity": item.quantity,
                    "unit_price": db_item.price
                })
                
                # Reduce inventory
                db_item.inventory.quantity -= item.quantity
            
            # Create purchase
            db_purchase = models.Purchase(
                customer_id=customer.customer_id,
                total_amount=total_amount,
                shipping_address=purchase.shipping_address,
                status="completed"
            )
            db.add(db_purchase)
            await db.flush()
            
            # Add purchase items
            for item in purchase_items:
                db_purchase_item = models.PurchaseItem(
                    purchase_id=db_purchase.purchase_id,
                    **item
                )
                db.add(db_purchase_item)
            
            # Create shipping record
            db_shipping = models.Shipping(
                purchase_id=db_purchase.purchase_id,
                status="preparing"
            )
            db.add(db_shipping)
            
            await db.commit()
            await db.refresh(db_purchase)
            return db_purchase
        except exc.IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[schemas.Purchase])
async def get_all_purchases(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.Purchase)
        .options(
            selectinload(models.Purchase.customer),
            selectinload(models.Purchase.items)
            .selectinload(models.PurchaseItem.item),
            selectinload(models.Purchase.shipping)
        )
        .order_by(models.Purchase.purchase_date.desc())
    )
    purchases = result.scalars().all()
    return purchases

@router.get("/{purchase_id}", response_model=schemas.Purchase)
async def get_purchase(purchase_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.Purchase)
        .where(models.Purchase.purchase_id == purchase_id)
        .options(
            selectinload(models.Purchase.customer),
            selectinload(models.Purchase.items)
            .selectinload(models.PurchaseItem.item),
            selectinload(models.Purchase.shipping)
        )
    )
    purchase = result.scalars().first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase

@router.put("/{purchase_id}/shipping", response_model=schemas.Shipping)
async def update_shipping(
    purchase_id: int, 
    shipping: schemas.ShippingUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(models.Shipping)
        .where(models.Shipping.purchase_id == purchase_id)
    )
    db_shipping = result.scalars().first()
    if not db_shipping:
        raise HTTPException(status_code=404, detail="Shipping record not found")
    
    update_data = shipping.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status" and value == "shipped" and not db_shipping.shipping_date:
            setattr(db_shipping, "shipping_date", date.today())
        setattr(db_shipping, key, value)
    
    # Update purchase status if shipping is delivered
    if shipping.status == "delivered":
        result = await db.execute(
            select(models.Purchase)
            .where(models.Purchase.purchase_id == purchase_id)
        )
        db_purchase = result.scalars().first()
        if db_purchase and db_purchase.status != "cancelled":
            db_purchase.status = "shipped"
    
    await db.commit()
    await db.refresh(db_shipping)
    return db_shipping