from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.urls import router as urls_router
from app.core.config import get_settings
from app.db.database import Base, engine
from app import models  # noqa: F401

settings = get_settings()
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(
    title="LinkPulse",
    description="URL shortener and analytics platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    origin.strip()
    for origin in settings.backend_cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(?:localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):(?:5500|8000)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(urls_router)
app.include_router(analytics_router)
app.include_router(admin_router)

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", tags=["Root"])
def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Welcome to LinkPulse API"}


@app.get("/{path:path}", include_in_schema=False)
def serve_frontend_or_short_code(path: str):
    frontend_root = FRONTEND_DIR.resolve()
    requested_file = (frontend_root / path).resolve()
    if frontend_root in requested_file.parents and requested_file.is_file():
        return FileResponse(requested_file)

    return RedirectResponse(url=f"/api/urls/redirect/{path}", status_code=307)
