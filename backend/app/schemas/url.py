from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class URLCreate(BaseModel):
    original_url: str
    expires_at: datetime | None = None

    @field_validator("original_url")
    @classmethod
    def validate_original_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("original_url cannot be empty")
        if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
            raise ValueError("original_url must start with http:// or https://")
        return cleaned


class URLUpdate(BaseModel):
    original_url: str | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None

    @field_validator("original_url")
    @classmethod
    def validate_original_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("original_url cannot be empty")
        if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
            raise ValueError("original_url must start with http:// or https://")
        return cleaned


class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool
    click_count: int = 0
