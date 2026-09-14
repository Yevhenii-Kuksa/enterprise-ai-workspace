from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    embedding_provider: Literal["openai"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    ai_answer_provider: Literal["openai"] = "openai"
    ai_answer_model: str = "gpt-5.6-luna"

    openai_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()