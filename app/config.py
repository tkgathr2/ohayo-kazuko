import os
from typing import Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    line_channel_access_token: SecretStr = Field(..., alias="LINE_CHANNEL_ACCESS_TOKEN")
    line_channel_secret: SecretStr = Field(..., alias="LINE_CHANNEL_SECRET")
    twilio_account_sid: str = Field(..., alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: SecretStr = Field(..., alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., alias="TWILIO_PHONE_NUMBER")
    google_sheets_credentials_json: str = Field(..., alias="GOOGLE_SHEETS_CREDENTIALS_JSON")
    google_sheets_spreadsheet_id: str = Field(..., alias="GOOGLE_SHEETS_SPREADSHEET_ID")
    tz: str = Field("Asia/Tokyo", alias="TZ")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_file: str = Field("./logs/app.log", alias="LOG_FILE")
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")

    control_line_id: Optional[str] = Field(None, alias="CONTROL_LINE_ID")

    @field_validator("twilio_account_sid")
    @classmethod
    def validate_twilio_account_sid(cls, value: str) -> str:
        if not value.startswith("AC") or len(value) != 34:
            raise ValueError("TWILIO_ACCOUNT_SID must match ^AC[a-z0-9]{32}$")
        return value

    @field_validator("twilio_phone_number")
    @classmethod
    def validate_twilio_phone_number(cls, value: str) -> str:
        if not value.startswith("+"):
            raise ValueError("TWILIO_PHONE_NUMBER must be E.164 format")
        return value


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def ensure_required_env() -> None:
    missing = []
    for key in (
        "LINE_CHANNEL_ACCESS_TOKEN",
        "LINE_CHANNEL_SECRET",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "GOOGLE_SHEETS_CREDENTIALS_JSON",
        "GOOGLE_SHEETS_SPREADSHEET_ID",
    ):
        if not os.getenv(key):
            missing.append(key)
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")