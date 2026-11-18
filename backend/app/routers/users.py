# [OWNER: M3] Users & CH Play Account Deletion / Data Export Router (T-M3-04)
from fastapi import APIRouter

router = APIRouter()


@router.get("/me/export")
async def export_user_data() -> dict:
    return {"status": "stub", "message": "Data export endpoint (T-M3-04)"}


@router.delete("/me")
async def delete_current_user() -> dict[str, str]:
    return {
        "status": "deleted_stub",
        "message": "Tai khoan va toan bo du lieu da duoc xoa vinh vien.",
    }
