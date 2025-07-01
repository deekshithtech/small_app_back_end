from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from urllib.parse import quote_plus

# URL encode the password to handle special characters
password = "Deek@2002"
encoded_password = quote_plus(password)

# Database configurations
SYNC_DB_URL = f"mysql+pymysql://root:{encoded_password}@localhost:3306/deegle"
ASYNC_DB_URL = f"mysql+aiomysql://root:{encoded_password}@localhost:3306/deegle"

# Sync engine and session
sync_engine = create_engine(
    SYNC_DB_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine and session
async_engine = create_async_engine(
    ASYNC_DB_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Dependency for sync sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for async sessions
async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()