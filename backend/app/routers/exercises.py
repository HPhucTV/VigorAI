# [OWNER: M3] 3D Exercises & Alternatives Router (T-M3-08)
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_exercises() -> dict:
    return {"items": []}


@router.get("/{code}/alternatives")
async def get_exercise_alternatives(code: str) -> dict:
    return {"exercise_code": code, "alternatives": []}
