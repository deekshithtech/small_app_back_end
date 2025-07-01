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

@router.put("/{item_id}", response_model=schemas.Inventory)
async def update_inventory(
    item_id: int, 
    inventory: schemas.InventoryUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(models.Inventory)
        .where(models.Inventory.item_id == item_id)
    )
    db_inventory = result.scalars().first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    db_inventory.quantity = inventory.quantity
    db_inventory.last_restocked = date.today()
    
    await db.commit()
    await db.refresh(db_inventory)
    return db_inventory