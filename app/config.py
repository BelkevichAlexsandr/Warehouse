from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MS_WAREHOUSE_HOST: str
    MS_WAREHOUSE_PORT: str
    MS_WAREHOUSE_DB: str
    MS_WAREHOUSE_PASSWORD: str
    MS_WAREHOUSE_USER: str

    MS_WAREHOUSE_USER_NAME: str
    MS_WAREHOUSE_USER_PASSWORD: str

    SQLALCHEMY_ENGINE_CONFIG: dict = {
        "future": True,
        "echo": False,
        "max_overflow": 3,
    }

    def __init__(self):
        super().__init__()
        self.POSTGRES_HOST = self.MS_WAREHOUSE_HOST
        self.POSTGRES_PORT = self.MS_WAREHOUSE_PORT
        self.POSTGRES_DB = self.MS_WAREHOUSE_DB
        self.POSTGRES_PASSWORD = self.MS_WAREHOUSE_PASSWORD
        self.POSTGRES_USER = self.MS_WAREHOUSE_USER

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
