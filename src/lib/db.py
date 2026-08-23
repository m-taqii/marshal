from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings

settings = get_settings()
BaseModel = declarative_base()

# Use the correct async driver prefixes for Postgres and SQLite
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+psycopg://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
pool_kwargs = {}
if "sqlite" in database_url:
    if not database_url.startswith("sqlite+aiosqlite://"):
        database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    connect_args = {"check_same_thread": False}
else:
    # pool_size and max_overflow are only valid for Postgres/MySQL
    pool_kwargs = {"pool_size": 10, "max_overflow": 20}

engine = create_async_engine(
    database_url,
    echo=True,
    connect_args=connect_args,
    **pool_kwargs
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def init_db():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

async def close_db():
    """Dispose of the connection pool."""
    await engine.dispose()

async def get_db():
    async with SessionLocal() as db:
        yield db