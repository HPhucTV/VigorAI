# [OWNER: M3] Analytics Summary Router (T-M3-10)
from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
async def get_analytics_summary() -> dict:
    return {"weekly_volume": [], "muscle_radar": {}, "personal_records": []}
