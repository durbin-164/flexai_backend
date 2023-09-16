from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# URL = "postgresql+asyncpg://root:root12345@0.0.0.0:5432/flexai_local"
URL = settings.db.url
engine = create_async_engine(
    URL,
    # echo=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

# sync_engine = create_engine(URL)
#
# sync_session = sessionmaker(sync_engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass
