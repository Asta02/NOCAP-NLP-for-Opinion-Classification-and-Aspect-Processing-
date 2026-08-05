"""
=========================================================
Application Settings
=========================================================
"""

from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(
    BaseSettings,
):

    #
    # Database
    #
    DATABASE_URL: str

    #
    # JWT
    #
    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    JWT_EXPIRE_MINUTES: int = 1440

    #
    # Admin
    #
    ADMIN_USERNAME: str

    ADMIN_PASSWORD: str

    #
    # FastAPI
    #
    DEBUG: bool = True

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        extra="ignore",

    )


settings = Settings()