import os
from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str
    PORT: str
    DB: str
    PASSWORD: str
    USER: str

    SQLALCHEMY_ENGINE_CONFIG: dict = {
        "future": True,
        "echo": False,
        "max_overflow": 3,
    }

    def __init__(self):
        super().__init__()
        self.POSTGRES_HOST = self.HOST
        self.POSTGRES_PORT = self.PORT
        self.POSTGRES_DB = self.DB
        self.POSTGRES_PASSWORD = self.PASSWORD
        self.POSTGRES_USER = self.USER

    @property
    def get_db_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def get_db_uri_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file: str = ".env"
        extra = Extra.allow


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
