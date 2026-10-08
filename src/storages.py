from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import app_settings, postgres_settings

engine = create_async_engine(
    postgres_settings.dsn,
    echo=app_settings.debug,
    future=True,
)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
