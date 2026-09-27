from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.click import Click
from app.models.url import URL
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse, URLUpdate
from app.services.url_service import ensure_url_is_valid, generate_unique_short_code, get_url_by_short_code
from app.utils.user_agent import detect_browser, detect_device
from app.core.security import get_current_user

router = APIRouter(prefix="/api/urls", tags=["URLs"])


@router.post("", response_model=URLResponse, status_code=status.HTTP_201_CREATED, summary="Create a shortened URL")
def create_url(
    payload: URLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    short_code = generate_unique_short_code(db)
    url_record = URL(
        user_id=current_user.id,
        original_url=str(payload.original_url),
        short_code=short_code,
        expires_at=payload.expires_at,
        is_active=True,
    )
    db.add(url_record)
    db.commit()
    db.refresh(url_record)

    return URLResponse(
        id=url_record.id,
        user_id=url_record.user_id,
        original_url=url_record.original_url,
        short_code=url_record.short_code,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active,
        click_count=0,
    )


@router.get("", response_model=list[URLResponse], summary="List current user's URLs")
def list_urls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    urls = db.query(URL).filter(URL.user_id == current_user.id).order_by(URL.created_at.desc()).all()
    response = []
    for url_record in urls:
        response.append(
            URLResponse(
                id=url_record.id,
                user_id=url_record.user_id,
                original_url=url_record.original_url,
                short_code=url_record.short_code,
                created_at=url_record.created_at,
                expires_at=url_record.expires_at,
                is_active=url_record.is_active,
                click_count=db.query(func.count(Click.id)).filter(Click.url_id == url_record.id).scalar() or 0,
            )
        )
    return response


@router.get("/redirect/{short_code}")
def redirect_to_original(short_code: str, request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import RedirectResponse

    url_record = get_url_by_short_code(db, short_code)
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    ensure_url_is_valid(url_record)

    user_agent = request.headers.get("user-agent", "")
    click = Click(
        url_id=url_record.id,
        clicked_at=datetime.now(timezone.utc),
        ip_address=request.client.host if request.client else "",
        user_agent=user_agent,
        referrer=request.headers.get("referer", ""),
        device_type=detect_device(user_agent),
        browser=detect_browser(user_agent),
    )
    db.add(click)
    db.commit()

    return RedirectResponse(url=url_record.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/{url_id}", response_model=URLResponse, summary="Get one of the current user's URLs")
def get_url(url_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url_record = db.query(URL).filter(URL.id == url_id, URL.user_id == current_user.id).first()
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    return URLResponse(
        id=url_record.id,
        user_id=url_record.user_id,
        original_url=url_record.original_url,
        short_code=url_record.short_code,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active,
        click_count=db.query(func.count(Click.id)).filter(Click.url_id == url_record.id).scalar() or 0,
    )


@router.put("/{url_id}", response_model=URLResponse, summary="Update a URL")
def update_url(
    url_id: int,
    payload: URLUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    url_record = db.query(URL).filter(URL.id == url_id, URL.user_id == current_user.id).first()
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if payload.original_url is not None:
        url_record.original_url = str(payload.original_url)
    if payload.expires_at is not None:
        url_record.expires_at = payload.expires_at
    if payload.is_active is not None:
        url_record.is_active = payload.is_active

    db.commit()
    db.refresh(url_record)

    return URLResponse(
        id=url_record.id,
        user_id=url_record.user_id,
        original_url=url_record.original_url,
        short_code=url_record.short_code,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active,
        click_count=db.query(func.count(Click.id)).filter(Click.url_id == url_record.id).scalar() or 0,
    )


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a URL")
def delete_url(url_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url_record = db.query(URL).filter(URL.id == url_id, URL.user_id == current_user.id).first()
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    db.delete(url_record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{url_id}/status", response_model=URLResponse, summary="Enable or disable a URL")
def toggle_url_status(
    url_id: int,
    payload: URLUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    url_record = db.query(URL).filter(URL.id == url_id, URL.user_id == current_user.id).first()
    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if payload.is_active is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="is_active flag is required")

    url_record.is_active = payload.is_active
    db.commit()
    db.refresh(url_record)

    return URLResponse(
        id=url_record.id,
        user_id=url_record.user_id,
        original_url=url_record.original_url,
        short_code=url_record.short_code,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active,
        click_count=db.query(func.count(Click.id)).filter(Click.url_id == url_record.id).scalar() or 0,
    )


@router.get("/debug")
def quick_debug(db: Session = Depends(get_db)):
    return {"message": "URL module ready"}
