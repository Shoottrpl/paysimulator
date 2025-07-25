from contextvars import ContextVar

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from settings import settings

engine = create_async_engine(
    url=settings.db_url,
    echo=True,
)

_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

_base_model_session_ctx = ContextVar("session")
