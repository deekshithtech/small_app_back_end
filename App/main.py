from fastapi import FastAPI
from .models import Base
from .database import sync_engine, async_engine
from .api.items import router as items_router
from .api.inventory import router as inventory_router
from .api.purchases import router as purchases_router

app = FastAPI(title="Store Backend API")

# Include routers
app.include_router(items_router, prefix="/api/items", tags=["Items"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(purchases_router, prefix="/api/purchases", tags=["Purchases"])

# Create tables on startup (for demo only - use migrations in production)
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=sync_engine)

@app.get("/")
async def root():
    return {"message": "Store Backend API"}