# [OWNER: M3] Pydantic Schemas cho Auth, Users & CH Play Compliance (T-M3-03, T-M3-04, T-M3-05)
import uuid
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Kiem tra dinh dang email bang Pydantic v2 StringConstraints (khong phu thuoc goi email-validator ngoai requirements.txt)
EmailAddress = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]


class RegisterRequest(BaseModel):
    email: EmailAddress = Field(examples=["user@vigorai.app"])
    password: str = Field(min_length=8, max_length=128, examples=["VigorAI@2026"])
    full_name: str = Field(min_length=1, max_length=150, examples=["Nguyen Van An"])
    gender: Literal["MALE", "FEMALE", "OTHER"] = "MALE"
    birth_date: date | None = None
    height_cm: float = Field(default=170.0, ge=80.0, le=250.0)
    activity_level: Literal[
        "SEDENTARY", "LIGHT", "MODERATE", "ACTIVE", "VERY_ACTIVE"
    ] = "MODERATE"
    fitness_goal: Literal["BULK", "CUT", "MAINTAIN"] = "MAINTAIN"
    avatar_preset: Literal["MALE_FIT", "FEMALE_FIT", "MALE_BULK"] = "MALE_FIT"
    medical_disclaimer_accepted: bool = Field(
        description="Bat buoc true theo quy dinh Mien tru Y te CH Play (F26)."
    )


class LoginRequest(BaseModel):
    email: EmailAddress = Field(examples=["demo@vigorai.app"])
    password: str = Field(min_length=1, examples=["VigorAI@2026"])


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailAddress
    full_name: str
    gender: str
    birth_date: date | None = None
    height_cm: float
    activity_level: str
    fitness_goal: str
    avatar_preset: str
    medical_disclaimer_accepted: bool
    disclaimer_accepted_at: datetime | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserProfileResponse


class MessageResponse(BaseModel):
    status: str
    message: str
