from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import app_settings

engine = create_async_engine(app_settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """
    Dependency to get a database session.

    Yields a session object that should be used as a dependency
    in a FastAPI path operation function.
    """
    async with AsyncSessionLocal() as session:
        yield session


Base = declarative_base()
