from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    app_environment: Literal["development", "test", "production"] = "development"

    embedding_provider: Literal["openai"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = Field(default=1536, gt=0)

    ai_answer_provider: Literal["openai"] = "openai"
    ai_answer_model: str = "gpt-5.6-luna"

    ai_reliability_max_evidence_distance: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
    )
    ai_reliability_max_source_age_days: int = Field(default=30, gt=0)

    openai_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        if self.app_environment != "production":
            return self

        if self.openai_api_key is None or not self.openai_api_key.get_secret_value().strip():
            raise ValueError("OPENAI_API_KEY is required in production")

        if "change_me" in self.database_url.lower():
            raise ValueError(
                "DATABASE_URL contains an unsafe placeholder credential"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()