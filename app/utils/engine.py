from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.utils.metaclass import Singleton


class Engine(metaclass=Singleton):
    def __init__(self):
        self._engine = create_async_engine(
            settings.get_db_uri,
            **settings.SQLALCHEMY_ENGINE_CONFIG,
        )

    def get_engine(self):
        return self._engine
