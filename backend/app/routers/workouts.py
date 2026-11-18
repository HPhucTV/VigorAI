# [OWNER: M3] Workout Sessions Router (T-M3-09)
from fastapi import APIRouter

router = APIRouter()


@router.get("/sessions")
async def list_workout_sessions() -> dict:
    return {"items": []}
