from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from app.core.config import settings

# Create engine with proper connection pool settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,  # Enable connection health checks before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Maintain 5 connections in the pool
    max_overflow=10,     # Allow up to 10 additional connections
    connect_args={
        "server_settings": {
            "application_name": "cauchy_mentor",
            "jit": "off"
        },
        "command_timeout": 60,
        "timeout": 30
    }
)

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    session = async_session_maker()
    try:
        # Test the connection before yielding
        await session.execute(text("SELECT 1"))
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
    finally:
        await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()
