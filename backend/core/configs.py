import os

from fastapi import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
        case_sensitive=False,
        extra='ignore',
    )

    JWT_SECRET_KEY: str = "C6kHOMvR3kRXNhDAGTT71NQGDhj6Y0920RrLgLIswmd"
    JWT_REFRESH_SECRET_KEY: str = "C6kfsdvR3kRXNhDAeff71NQGDhj6Y0920RrLgLIswmd"
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAIL_USERNAME: str = "dangkhoa11102001@gmail.com"
    MAIL_PASSWORD: str = "zwbs febd zoaz texw"
    MAIL_FROM: str = "dangkhoa11102001@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True




settings = Settings()