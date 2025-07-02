from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from .. import models, schemas
from ..database import get_async_db
from sqlalchemy.orm import selectinload

router = APIRouter()
@router.get("/", response_model=list[schemas.Inventory])
async def get_all_inventory(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.Inventory)
        .options(selectinload(models.Inventory.item))
    )
    inventory = result.scalars().all()
    return inventory

@router.patch("/{inventory_id}")
async def update_inventory(
    inventory_id: int,
    inventory: schemas.InventoryUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    # Fetch the inventory record
    result = await db.execute(
        select(models.Inventory).where(models.Inventory.inventory_id == inventory_id)
    )
    db_inventory = result.scalars().first()

    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    # Get only the fields that were actually sent in the request
    update_data = inventory.dict(exclude_unset=True)

    # Update each field on the db model
    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    await db.commit()
    await db.refresh(db_inventory)

    return {
        "success": True,
        "msg": "Inventory updated successfully",
        "data": {
            "inventory_id": db_inventory.inventory_id,
            "item_id": db_inventory.item_id,
            "quantity": db_inventory.quantity,
            "last_restocked": db_inventory.last_restocked.isoformat() if db_inventory.last_restocked else None,
        }
    }
