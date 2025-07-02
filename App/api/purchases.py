from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from datetime import datetime
from sqlalchemy.orm import selectinload
from .. import models, schemas
from ..database import get_async_db

router = APIRouter()

@router.post("/", response_model=schemas.PurchaseResponse)
async def place_order(
    order: schemas.PurchaseCreate,
    db: AsyncSession = Depends(get_async_db)
):
    async with db.begin():
        try:
            result = await db.execute(
                select(models.Customer).where(
                    or_(
                        models.Customer.email == order.customer.email,
                        models.Customer.phone == order.customer.phone
                    )
                )
            )
            customer = result.scalars().first()

            if not customer:
                customer = models.Customer(
                    name=order.customer.name,
                    email=order.customer.email,
                    phone=order.customer.phone,
                    address=order.customer.address
                )
                db.add(customer)
                await db.flush()

            for item in order.items:
                item_result = await db.execute(
                    select(models.Item)
                    .options(selectinload(models.Item.inventory))
                    .where(models.Item.item_id == item.item_id)
                )
                db_item = item_result.scalars().first()

                if not db_item:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Item {item.item_id} not found"
                    )

                if not db_item.inventory or db_item.inventory.quantity < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for item {db_item.name}"
                    )

                total_price = float(db_item.price) * item.quantity

                order_entry = models.CustomerAdded(
                     customer_id=customer.customer_id,
                     item_id=item.item_id,
                     quantity=item.quantity,
                     total_price=total_price,
                     item_name=db_item.name,  # save current name
                     item_description=db_item.description  # save current description
                )
                db.add(order_entry)

                db_item.inventory.quantity -= item.quantity

            await db.commit()
            return {
                "success": True,
                "message": "Order placed successfully",
                "customer": order.customer,
                "items": order.items,
                "total": order.total
            }

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error processing order: {str(e)}"
            )
@router.get("/api/purchases/{customer_id}")
async def get_customer_orders(customer_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.CustomerAdded).where(models.CustomerAdded.customer_id == customer_id)
    )
    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this customer")

    return [
        {
            "item_name": order.item_name,
            "item_description": order.item_description,
            "quantity": order.quantity,
            "total_price": float(order.total_price),
            "ordered_at": str(order.ordered_at)
        }
        for order in orders
    ]
