import json
from functools import lru_cache
import logging
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources.types import NoDecode

class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://mobile_otp:mobile_otp@localhost:5432/mobile_otp",
        alias="DATABASE_URL"
    )
    twilio_account_sid: str = Field(alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(alias="TWILIO_AUTH_TOKEN")
    twilio_service_sid: str = Field(alias="TWILIO_SERVICE_SID")
    twilio_base_url: str = Field(default="https://verify.twilio.com/v2", alias="TWILIO_BASE_URL")
    otp_expiry_seconds: int = Field(default=300, alias="OTP_EXPIRY_SECONDS")
    app_env: str = Field(default="development", alias="APP_ENV")
    cors_allow_private_network: bool = Field(default=False, alias="CORS_ALLOW_PRIVATE_NETWORK")
    cors_allow_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:4000", "http://127.0.0.1:4000"],
        alias="CORS_ALLOW_ORIGINS"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return cls.model_fields["database_url"].default
            if normalized.startswith("sqlite"):
                return cls.model_fields["database_url"].default
            if normalized.startswith("postgres://"):
                return normalized.replace("postgres://", "postgresql+psycopg://", 1)
            if normalized.startswith("postgresql://"):
                return normalized.replace("postgresql://", "postgresql+psycopg://", 1)
            return normalized
        return value

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().upper()
            if not normalized:
                return cls.model_fields["log_level"].default
            return normalized
        return value

    def cors_allow_origins_list(self) -> list[str]:
        return list(self.cors_allow_origins)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    logger = logging.getLogger(__name__)
    logger.debug(
        "settings_loaded",
        extra={
            "app_env": settings.app_env,
            "log_level": settings.log_level,
            "log_json": settings.log_json,
        }
    )
    return settings
