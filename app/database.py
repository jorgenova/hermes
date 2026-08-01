from sqlalchemy.ext.asyncio import create_async_engine, async_sesionmaker
from sqlalchemy.orm import DeclaratveBase

from config import settings

engine = create_async_engine(settings.database_url, echo=settings.api_debug)
AsyncSession = async_sessionmaker(engine, expire_on_commit=false)

class Base(DeclarativeBase):
	pass
