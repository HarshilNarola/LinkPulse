from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.click import Click
from app.models.url import URL


def count_clicks_for_url(db: Session, url_id: int) -> dict:
    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        return {}

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    total_clicks = db.query(func.count(Click.id)).filter(Click.url_id == url_id).scalar() or 0
    clicks_today = (
        db.query(func.count(Click.id)).filter(Click.url_id == url_id, Click.clicked_at >= today_start).scalar() or 0
    )
    clicks_this_week = (
        db.query(func.count(Click.id)).filter(Click.url_id == url_id, Click.clicked_at >= week_start).scalar() or 0
    )
    clicks_this_month = (
        db.query(func.count(Click.id)).filter(Click.url_id == url_id, Click.clicked_at >= month_start).scalar() or 0
    )

    device_rows = db.query(Click.device_type, func.count(Click.id)).filter(Click.url_id == url_id).group_by(Click.device_type).all()
    browser_rows = db.query(Click.browser, func.count(Click.id)).filter(Click.url_id == url_id).group_by(Click.browser).all()
    referrer_rows = db.query(Click.referrer, func.count(Click.id)).filter(Click.url_id == url_id).group_by(Click.referrer).all()

    date_rows = db.query(func.date(Click.clicked_at), func.count(Click.id)).filter(Click.url_id == url_id).group_by(func.date(Click.clicked_at)).all()

    return {
        "total_clicks": total_clicks,
        "clicks_today": clicks_today,
        "clicks_this_week": clicks_this_week,
        "clicks_this_month": clicks_this_month,
        "device_breakdown": {key or "unknown": value for key, value in device_rows},
        "browser_breakdown": {key or "unknown": value for key, value in browser_rows},
        "clicks_by_date": {date.isoformat() if date else "unknown": count for date, count in date_rows},
        "referrers": {referrer or "direct": count for referrer, count in referrer_rows},
    }


def count_global_stats(db: Session) -> dict:
    from app.models.user import User

    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0
    total_urls = db.query(func.count(URL.id)).scalar() or 0
    active_urls = db.query(func.count(URL.id)).filter(URL.is_active.is_(True)).scalar() or 0
    total_clicks = db.query(func.count(Click.id)).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    clicks_today = db.query(func.count(Click.id)).filter(Click.clicked_at >= today_start).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_urls": total_urls,
        "active_urls": active_urls,
        "total_clicks": total_clicks,
        "clicks_today": clicks_today,
    }
