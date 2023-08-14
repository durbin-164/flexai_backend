from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

URL = "postgresql+asyncpg://root:root12345@0.0.0.0:5432/flexai_local"

engine = create_async_engine(
        URL,
        # echo=True,
    )

async_session = async_sessionmaker(engine, expire_on_commit=False)