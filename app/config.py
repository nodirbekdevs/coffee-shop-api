from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent

TRANSLATION_DIRECTORY = f"{APP_DIR}/locales"
I18N_DOMAIN = "messages"
TIME_ZONE = "Asia/Tashkent"
DEFAULT_LOCALE = "uz"


class DatabaseSettings(BaseSettings):
    USER: str
    HOST: str
    PORT: str
    PASSWORD: str
    NAME: str
    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_TIMEOUT: int
    POOL_RECYCLE: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    model_config = SettingsConfigDict(env_prefix="DB__")


class RedisSettings(BaseSettings):
    HOST: str
    PORT: str
    PASSWORD: str | None = None
    DB: int

    @property
    def REDIS_URL(self) -> str:
        if self.PASSWORD:
            return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
        else:
            return f"redis://{self.HOST}:{self.PORT}/{self.DB}"

    @property
    def CELERY_URL(self) -> str:
        if self.PASSWORD:
            return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB + 1}"
        else:
            return f"redis://{self.HOST}:{self.PORT}/{self.DB + 1}"

    model_config = SettingsConfigDict(env_prefix="REDIS__")


class VerificationSettings(BaseSettings):
    COOKIE_NAME: str
    RETRY_LIMIT: int
    MAX_ATTEMPTS: int
    EXPIRE_SECONDS: int
    TIMEOUT_SECONDS: int
    BAN_TIME_SECONDS: int

    model_config = SettingsConfigDict(env_prefix="VERIFICATION__")


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    SIGNING_ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_SECONDS: int
    REFRESH_TOKEN_EXPIRY_SECONDS: int

    model_config = SettingsConfigDict(env_prefix="JWT__")


class AppSettings(BaseSettings):
    APP_NAME: str = "coffee-shop-app"
    DEPLOYMENT_STAGE: str
    CORS_ALLOWED_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
        ]
    )

    DB: DatabaseSettings = Field(default_factory=DatabaseSettings)
    REDIS: RedisSettings = Field(default_factory=RedisSettings)
    VERIFICATION: VerificationSettings = Field(default_factory=VerificationSettings)
    JWT: JWTSettings = Field(default_factory=JWTSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )


settings = AppSettings()
