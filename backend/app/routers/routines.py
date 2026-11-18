# [OWNER: M3] Workout Routines Router (T-M3-09)
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_routines() -> dict:
    return {"items": []}
