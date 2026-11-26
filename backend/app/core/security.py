# [OWNER: M3] Bao mat JWT & bam mat khau Argon2/bcrypt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {
            "sub": subject,
            "exp": expire,
            "type": "access",
            "jti": str(uuid.uuid4()),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return jwt.encode(
        {
            "sub": subject,
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Giai ma va kiem tra chu ky, han dung va loai JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError("Token không hợp lệ hoặc đã hết hạn.") from exc

    if expected_type is not None and payload.get("type") != expected_type:
        raise ValueError("Loại token không hợp lệ.")

    if not payload.get("sub"):
        raise ValueError("Token thiếu định danh người dùng.")

    return payload
