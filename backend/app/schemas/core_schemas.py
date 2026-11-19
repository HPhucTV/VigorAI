# [OWNER: M3] Pydantic Schemas cho Auth, Users & CH Play Compliance (T-M3-03, T-M3-04, T-M3-05)
import uuid
from datetime import date, datetime
from typing import Annotated, Any, Literal

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


# =====================================================================
# SPRINT 2 SCHEMAS: SYNC, HEALTH, EXERCISES, ROUTINES, WORKOUTS, ANALYTICS
# =====================================================================


class SyncPushRequest(BaseModel):
    biometric_logs: list[dict[str, Any]] = Field(default_factory=list)
    daily_health_logs: list[dict[str, Any]] = Field(default_factory=list)
    supplement_schedules: list[dict[str, Any]] = Field(default_factory=list)
    meal_logs: list[dict[str, Any]] = Field(default_factory=list)
    workout_routines: list[dict[str, Any]] = Field(default_factory=list)
    workout_sessions: list[dict[str, Any]] = Field(default_factory=list)
    workout_sets: list[dict[str, Any]] = Field(default_factory=list)


class SyncPushResponse(BaseModel):
    status: str = "ok"
    synced_ids: dict[str, list[str]]
    total_applied: int
    server_time_utc: datetime


class BiometricLogCreate(BaseModel):
    id: uuid.UUID | None = None
    weight_kg: float = Field(gt=20.0, lt=350.0)
    height_cm: float | None = Field(default=None, gt=80.0, lt=260.0)
    body_fat_pct: float | None = Field(default=None, ge=1.0, le=75.0)
    muscle_mass_kg: float | None = Field(default=None, ge=5.0, le=200.0)
    bmi: float | None = None
    circumferences_cm: dict[str, float] = Field(default_factory=dict)
    logged_date: date | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class DailyHealthUpsert(BaseModel):
    id: uuid.UUID | None = None
    steps_count: int = Field(default=0, ge=0)
    target_steps: int = Field(default=8000, ge=1000)
    distance_km: float = Field(default=0.0, ge=0.0)
    active_calories_kcal: int = Field(default=0, ge=0)
    water_ml: int = Field(default=0, ge=0)
    target_water_ml: int | None = Field(default=None, ge=500)
    sleep_hours: float = Field(default=0.0, ge=0.0, le=24.0)
    sleep_quality_score: int | None = Field(default=None, ge=1, le=5)
    updated_at: datetime | None = None


class MealLogCreate(BaseModel):
    id: uuid.UUID | None = None
    catalog_food_id: uuid.UUID | None = None
    class_code: str | None = None
    grams: float | None = Field(default=None, gt=0.0)
    meal_type: str = "LUNCH"
    title: str | None = None
    image_url: str | None = None
    ai_detected_items: list[dict[str, Any]] = Field(default_factory=list)
    total_calories: float | None = Field(default=None, ge=0.0)
    protein_g: float | None = Field(default=None, ge=0.0)
    carbs_g: float | None = Field(default=None, ge=0.0)
    fat_g: float | None = Field(default=None, ge=0.0)
    logged_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class SupplementScheduleCreate(BaseModel):
    id: uuid.UUID | None = None
    supplement_name: str = Field(min_length=1, max_length=120)
    dosage_label: str = Field(min_length=1, max_length=80)
    reminder_time: str = Field(default="08:00", description="Dinh dang HH:MM hoac HH:MM:SS")
    workout_days_only: bool = False
    is_active: bool = True
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class RoutineExerciseInput(BaseModel):
    id: uuid.UUID | None = None
    exercise_id: uuid.UUID | None = None
    exercise_code: str | None = None
    order_index: int = 0
    superset_group_id: int | None = None
    target_sets: int = Field(default=3, ge=1, le=20)
    target_rep_min: int = Field(default=8, ge=1, le=100)
    target_rep_max: int = Field(default=12, ge=1, le=100)
    default_rest_seconds: int = Field(default=90, ge=15, le=600)


class WorkoutRoutineUpsert(BaseModel):
    id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=150)
    split_type: str = "CUSTOM"
    scheduled_weekdays: list[int] = Field(default_factory=list)
    is_template: bool = False
    exercises: list[RoutineExerciseInput] = Field(default_factory=list)
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class WorkoutSetInput(BaseModel):
    id: uuid.UUID | None = None
    exercise_id: uuid.UUID | None = None
    exercise_code: str | None = None
    set_number: int = Field(default=1, ge=1)
    set_type: str = "NORMAL"
    weight_kg: float = Field(default=0.0, ge=0.0)
    reps: int = Field(default=0, ge=0)
    rpe: float | None = Field(default=None, ge=1.0, le=10.0)
    completed_at: datetime | None = None
    updated_at: datetime | None = None


class WorkoutSessionCreate(BaseModel):
    id: uuid.UUID | None = None
    routine_id: uuid.UUID | None = None
    session_title: str = Field(min_length=1, max_length=150)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int = Field(default=0, ge=0)
    status: str = "COMPLETED"
    sets: list[WorkoutSetInput] = Field(default_factory=list)
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
