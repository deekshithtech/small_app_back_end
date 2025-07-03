import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from a .env file (optional but useful for local development)
load_dotenv()

# Read environment variables with defaults
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")

# Encode the password to safely use special characters
encoded_password = quote_plus(MYSQL_ROOT_PASSWORD)

# Database URLs
SYNC_DB_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
ASYNC_DB_URL = (
    f"mysql+aiomysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

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
