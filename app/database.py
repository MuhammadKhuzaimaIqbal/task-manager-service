from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 1. Create the async engine
# echo=True prints the SQL queries to the terminal (great for debugging!)
# connect_args={"check_same_thread": False} is required for SQLite in FastAPI
engine = create_async_engine(
    settings.database_url,
    echo=True, 
    connect_args={"check_same_thread": False} 
)

# 2. Create the async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 3. Base class for all SQLAlchemy models
class Base(DeclarativeBase):
    pass

# 4. Dependency function to get the DB session in our route handlers
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()