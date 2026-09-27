import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, get_current_user, hash_password, verify_password
from app.db.database import get_db
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.auth import PasswordChange, PasswordReset, PasswordResetRequest, TokenResponse, UserLogin
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _send_reset_email(email: str, reset_url: str) -> None:
    if not settings.smtp_username or not settings.smtp_password or not settings.smtp_from_email:
        raise RuntimeError("Gmail SMTP is not configured")

    message = EmailMessage()
    message["Subject"] = "Reset your LinkPulse password"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        "We received a request to reset your LinkPulse password.\n\n"
        f"Open this link within 30 minutes:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_password = hash_password(payload.password)
    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hashed_password,
        role="USER",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse, summary="Login and return JWT tokens")
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

    access_token = create_access_token(user.id, user.role, user_name=user.name, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(user.id, expires_delta=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/change-password", summary="Change the authenticated user's password")
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/forgot-password", summary="Send a password reset email")
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raw_token = secrets.token_urlsafe(48)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=_token_hash(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        db.add(reset_token)
        db.commit()

        reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password.html?token={raw_token}"
        try:
            _send_reset_email(user.email, reset_url)
        except (OSError, smtplib.SMTPException, RuntimeError) as exc:
            db.delete(reset_token)
            db.commit()
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Password reset email is not configured") from exc

    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/reset-password", summary="Reset a password with an emailed token")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == _token_hash(payload.token), PasswordResetToken.used_at.is_(None))
        .first()
    )
    if not reset_token or reset_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid")

    user.password_hash = hash_password(payload.new_password)
    reset_token.used_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Password reset successfully"}
