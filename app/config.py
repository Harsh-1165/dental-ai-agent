"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "QuensultingAI Dental Clinic API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    clinic_name: str = "QuensultingAI Dental Clinic"
    working_days_start: int = 0  # Monday
    working_days_end: int = 5  # Saturday (0=Mon, 6=Sun)
    working_hour_start: int = 9
    working_hour_end: int = 18

    valid_services: List[str] = Field(
        default=[
            "Dental Cleaning",
            "Root Canal Treatment",
            "Teeth Whitening",
            "Braces Consultation",
            "Tooth Extraction",
            "General Dental Consultation",
        ]
    )

    google_credentials_path: str = Field(
        default="credentials.json",
        description="Path to Google service account credentials JSON file",
    )
    google_sheet_id: str = Field(
        default="",
        description="Google Spreadsheet ID for appointment storage",
    )
    google_sheet_name: str = Field(
        default="Appointments",
        description="Worksheet name within the spreadsheet",
    )

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance for dependency injection."""
    return Settings()
