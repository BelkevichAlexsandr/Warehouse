from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    id: Any
