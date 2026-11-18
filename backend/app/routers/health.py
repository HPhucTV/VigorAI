# [OWNER: M3] Health & Biometrics Router (T-M3-07)
from fastapi import APIRouter

router = APIRouter()


@router.get("/biometrics")
async def list_biometrics() -> dict:
    return {"items": []}


@router.get("/daily/{log_date}")
async def get_daily_health(log_date: str) -> dict:
    return {"log_date": log_date, "steps_count": 0, "water_ml": 0}


@router.get("/meals")
async def list_meals() -> dict:
    return {"items": []}


@router.get("/supplements")
async def list_supplements() -> dict:
    return {"items": []}
