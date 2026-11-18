# [LOCKED STUB] Khoi tao FastAPI & Mount san toan bo routers cua M3 va M4
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.routers import (
    ai,
    analytics,
    auth,
    exercises,
    health,
    routines,
    sync,
    users,
    workouts,
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="VigorAI: 3D Gym & Health Log RESTful API (CH Play Compliant)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers thuoc quyen so huu M3
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users & Privacy"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Offline-First Sync"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health & Biometrics"])
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["Exercises & 3D"])
app.include_router(routines.router, prefix="/api/v1/routines", tags=["Routines"])
app.include_router(workouts.router, prefix="/api/v1/workouts", tags=["Workouts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Router thuoc quyen so huu M4 (AI Models B & C)
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Engine (Model B & C)"])


@app.get("/healthz", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/delete-account", response_class=HTMLResponse, tags=["CH Play Compliance"])
async def public_delete_account_page(request: Request) -> HTMLResponse:
    """Trang web cong khai bat buoc cho bieu mau Data Safety tren Google Play Console."""
    return templates.TemplateResponse(request=request, name="delete_account.html")
