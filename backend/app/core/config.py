from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LinkPulse"
    database_url: str = Field(default="sqlite:///./linkpulse.db")
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    backend_cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000"
    frontend_url: str = "http://localhost:5500"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    def model_post_init(self, __context):
        placeholder_values = {
            "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/linkpulse",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/linkpulse",
        }
        if self.database_url in placeholder_values or self.database_url.startswith("postgresql") and "YOUR_PASSWORD" in self.database_url:
            self.database_url = "sqlite:///./linkpulse.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
