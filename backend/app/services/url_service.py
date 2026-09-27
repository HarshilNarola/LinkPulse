from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.url import URL
from app.models.user import User
from app.utils.short_code import generate_short_code


def generate_unique_short_code(db: Session) -> str:
    for _ in range(20):
        short_code = generate_short_code(length=8)
        existing = db.query(URL).filter(URL.short_code == short_code).first()
        if existing is None:
            return short_code
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate unique short code")


def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()


def ensure_url_is_valid(url_record: URL) -> None:
    if not url_record.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This short URL is disabled")
    if url_record.expires_at:
        expires_at = url_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="This short URL has expired")


def get_user_url_count(db: Session, user_id: int) -> int:
    return db.query(URL).filter(URL.user_id == user_id).count()


def get_user_click_count(db: Session, user_id: int) -> int:
    url_ids = db.query(URL.id).filter(URL.user_id == user_id).subquery()
    return db.query(func.count()).select_from(url_ids).count()
