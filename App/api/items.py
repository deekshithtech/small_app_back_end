from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc
from .. import models, schemas
from ..database import get_async_db
from sqlalchemy.orm import selectinload
from datetime import date


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_async_db)):
    try:
        db_item = models.Item(
            name=item.name,
            description=item.description,
            price=item.price,
            category=item.category
        )
        db.add(db_item)
        await db.flush()

        db_inventory = models.Inventory(
            item_id=db_item.item_id,
            quantity=item.quantity,
            last_restocked=date.today()
        )
        db.add(db_inventory)

        await db.commit()
        await db.refresh(db_item)
        return {
            "success":"true",
            "msg":"item added success from merchant",
            "data":item
        } 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Item creation failed: {str(e)}")

@router.patch("/{item_id}")
async def update_item(
    item_id: int, 
    item: schemas.ItemUpdate, 
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(models.Item)
        .where(models.Item.item_id == item_id)
    )
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    await db.commit()
    await db.refresh(db_item)
    return  {
            "success":"true",
            "msg":"item updated success from merchant",
            "data":db_item
        } 




@router.get("/")
async def get_all_items(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(models.Item).options(
        selectinload(models.Item.inventory)
    ))
    items = result.scalars().all()
    return  {
            "success":"true",
            "data":items
        } 


@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.Item)
        .where(models.Item.item_id == item_id)
        .options(selectinload(models.Item.inventory))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "success":"true",
        "data":item
        }


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(models.Item)
        .where(models.Item.item_id == item_id)
    )
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(db_item)
    await db.commit()
    return {
         {
        "success":"true",
        "data":"data deleted success"
        }
    }