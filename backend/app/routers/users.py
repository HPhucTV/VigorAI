# [OWNER: M3] Users & CH Play Account Deletion / Data Export Router (T-M3-04)
import html
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.core_schemas import MessageResponse, UserProfileResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()
_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Lay thong tin ho so nguoi dung hien tai",
)
async def get_current_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


@router.get(
    "/me/export",
    summary="Xuat toan bo du lieu ca nhan dang JSON (Data Portability)",
)
async def export_user_data(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    return await auth_service.export_user_data(db, current_user)


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Xoa vinh vien tai khoan & toan bo du lieu (Cascade Delete CH Play)",
)
async def delete_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    await auth_service.delete_user_cascade(db, current_user)
    return MessageResponse(
        status="deleted",
        message="Tài khoản và toàn bộ dữ liệu đã được xóa vĩnh viễn.",
    )


@router.post(
    "/delete-via-web",
    response_class=HTMLResponse,
    summary="Xu ly form xoa tai khoan cong khai tu trang /delete-account",
)
async def delete_account_via_web(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> HTMLResponse:
    deleted = await auth_service.delete_user_by_credentials(db, email, password)
    safe_email = html.escape(email.strip())

    if not deleted:
        body = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8" /><title>Xác thực thất bại — VigorAI</title></head>
<body style="font-family:system-ui,sans-serif;max-width:600px;margin:40px auto;padding:0 16px;">
  <div style="border:1px solid #fecaca;background:#fef2f2;padding:24px;border-radius:12px;">
    <h1 style="color:#b91c1c;margin-top:0;">Không thể xóa tài khoản</h1>
    <p>Email (<strong>{safe_email}</strong>) hoặc mật khẩu xác nhận không chính xác.</p>
    <p><a href="/delete-account">Quay lại trang yêu cầu xóa tài khoản</a></p>
  </div>
</body>
</html>"""
        return HTMLResponse(content=body, status_code=status.HTTP_401_UNAUTHORIZED)

    body = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8" /><title>Đã xóa tài khoản — VigorAI</title></head>
<body style="font-family:system-ui,sans-serif;max-width:600px;margin:40px auto;padding:0 16px;">
  <div style="border:1px solid #bbf7d0;background:#f0fdf4;padding:24px;border-radius:12px;">
    <h1 style="color:#15803d;margin-top:0;">Đã xóa tài khoản vĩnh viễn</h1>
    <p>Tài khoản <strong>{safe_email}</strong> và toàn bộ dữ liệu liên quan (hồ sơ sinh trắc học, nhật ký bữa ăn, ảnh món ăn, lịch sử buổi tập và dữ liệu AI) đã được xóa vĩnh viễn khỏi hệ thống VigorAI.</p>
  </div>
</body>
</html>"""
    return HTMLResponse(content=body, status_code=status.HTTP_200_OK)


@router.get(
    "/privacy-policy",
    response_class=HTMLResponse,
    summary="Trang Chinh sach Quyen rieng tu cong khai cho Google Play Console",
)
async def public_privacy_policy_page() -> HTMLResponse:
    content = (_TEMPLATES_DIR / "privacy_policy.html").read_text(encoding="utf-8")
    return HTMLResponse(content=content, status_code=status.HTTP_200_OK)
