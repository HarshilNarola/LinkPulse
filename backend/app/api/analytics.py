from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.click import Click
from app.models.url import URL
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/{url_id}", response_model=AnalyticsResponse, summary="Get analytics for a URL")
def get_analytics(url_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url_record = db.query(URL).filter(URL.id == url_id).first()
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    if url_record.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this analytics")

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    total_clicks = db.query(Click).filter(Click.url_id == url_id).count()
    clicks_today = db.query(Click).filter(Click.url_id == url_id, Click.clicked_at >= today_start).count()
    clicks_this_week = db.query(Click).filter(Click.url_id == url_id, Click.clicked_at >= week_start).count()
    clicks_this_month = db.query(Click).filter(Click.url_id == url_id, Click.clicked_at >= month_start).count()

    device_breakdown = {}
    for device, count in db.query(Click.device_type, Click.id).filter(Click.url_id == url_id).all():
        device_breakdown[device or "unknown"] = device_breakdown.get(device or "unknown", 0) + 1

    browser_breakdown = {}
    for browser, count in db.query(Click.browser, Click.id).filter(Click.url_id == url_id).all():
        browser_breakdown[browser or "unknown"] = browser_breakdown.get(browser or "unknown", 0) + 1

    clicks_by_date = {}
    for row in db.query(Click.clicked_at).filter(Click.url_id == url_id).all():
        date_key = row[0].strftime("%Y-%m-%d")
        clicks_by_date[date_key] = clicks_by_date.get(date_key, 0) + 1

    referrers = {}
    for referrer, count in db.query(Click.referrer, Click.id).filter(Click.url_id == url_id).all():
        referrer_key = referrer or "direct"
        referrers[referrer_key] = referrers.get(referrer_key, 0) + 1

    return {
        "total_clicks": total_clicks,
        "clicks_today": clicks_today,
        "clicks_this_week": clicks_this_week,
        "clicks_this_month": clicks_this_month,
        "device_breakdown": device_breakdown,
        "browser_breakdown": browser_breakdown,
        "clicks_by_date": clicks_by_date,
        "referrers": referrers,
    }
