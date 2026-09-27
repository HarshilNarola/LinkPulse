from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.database import get_db
from app.models.click import Click
from app.models.url import URL
from app.models.user import User
from app.schemas.analytics import AdminStatistics
from app.services.analytics_service import count_global_stats

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", summary="List all users", response_model=list[dict])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]


@router.get("/urls", summary="List all URLs", response_model=list[dict])
def list_all_urls(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    urls = db.query(URL).order_by(URL.created_at.desc()).all()
    return [
        {
            "id": url.id,
            "user_id": url.user_id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "created_at": url.created_at.isoformat() if url.created_at else None,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "is_active": url.is_active,
        }
        for url in urls
    ]


@router.get("/statistics", response_model=AdminStatistics, summary="Get global admin statistics")
def get_admin_statistics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    stats = count_global_stats(db)
    return AdminStatistics(**stats)


@router.patch("/users/{user_id}/status", summary="Activate or deactivate a user")
def toggle_user_status(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if "is_active" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="is_active is required")

    user.is_active = bool(payload["is_active"])
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_active": user.is_active, "email": user.email}
