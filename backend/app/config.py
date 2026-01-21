from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "test", "production"] = Field(
        default="development", validation_alias="ENVIRONMENT"
    )
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

