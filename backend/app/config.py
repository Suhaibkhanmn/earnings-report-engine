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
    # NOTE:
    # These are optional so the service can boot (e.g. for /health) even when
    # Railway variables aren't configured yet. Endpoints that require these
    # must call require_*() to enforce presence.
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")

    def require_database_url(self) -> str:
        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is not set. Configure it in Railway Variables "
                "to enable database-backed endpoints."
            )
        return self.database_url

    def require_gemini_api_key(self) -> str:
        if not self.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Configure it in Railway Variables "
                "to enable Gemini-powered endpoints."
            )
        return self.gemini_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

