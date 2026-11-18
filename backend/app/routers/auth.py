# [OWNER: M3] Auth Router (T-M3-03)
from fastapi import APIRouter, HTTPException, status

from app.schemas.core_schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest) -> TokenResponse:
    if not payload.medical_disclaimer_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ban phai chap nhan Mien tru Trach nhiem Y te de dang ky.",
        )
    return TokenResponse(access_token="stub-access-token", refresh_token="stub-refresh")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    return TokenResponse(access_token="stub-access-token", refresh_token="stub-refresh")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token() -> TokenResponse:
    return TokenResponse(access_token="stub-access-token", refresh_token="stub-refresh")
