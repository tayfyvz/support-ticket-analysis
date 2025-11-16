from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "Support Ticket Analyst API"
    database_url: Annotated[str, PostgresDsn] = "postgresql+asyncpg://postgres:postgres@db:5432/support_tickets"
    openai_api_key: str = ""

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()


BASE_DIR = Path(__file__).resolve().parent.parent

