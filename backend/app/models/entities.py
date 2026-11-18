# [OWNER: M3] Khai bao 11 bang nghiep vu + 1 bang tu dien dinh duong khop ERD Muc 4 system-design-spec.md
import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(150))
    gender: Mapped[str] = mapped_column(String(20), default="MALE")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[float] = mapped_column(Float, default=170.0)
    activity_level: Mapped[str] = mapped_column(String(30), default="MODERATE")
    fitness_goal: Mapped[str] = mapped_column(String(20), default="MAINTAIN")
    avatar_preset: Mapped[str] = mapped_column(String(30), default="MALE_FIT")
    medical_disclaimer_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    disclaimer_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class BiometricLog(Base):
    __tablename__ = "biometric_logs"
    __table_args__ = (Index("ix_biometric_user_date", "user_id", "logged_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    weight_kg: Mapped[float] = mapped_column(Float)
    body_fat_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    muscle_mass_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    bmi: Mapped[float] = mapped_column(Float)
    circumferences_cm: Mapped[dict] = mapped_column(JSONB, default=dict)
    logged_date: Mapped[date] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class DailyHealthLog(Base):
    __tablename__ = "daily_health_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="uq_daily_health_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    log_date: Mapped[date] = mapped_column(Date)
    steps_count: Mapped[int] = mapped_column(Integer, default=0)
    distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    active_calories_kcal: Mapped[int] = mapped_column(Integer, default=0)
    water_ml: Mapped[int] = mapped_column(Integer, default=0)
    target_water_ml: Mapped[int] = mapped_column(Integer, default=2000)
    sleep_hours: Mapped[float] = mapped_column(Float, default=0.0)
    sleep_quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class SupplementSchedule(Base):
    __tablename__ = "supplement_schedules"
    __table_args__ = (Index("ix_supplement_user_active", "user_id", "is_active"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    supplement_name: Mapped[str] = mapped_column(String(120))
    dosage_label: Mapped[str] = mapped_column(String(80))
    reminder_time: Mapped[time] = mapped_column(Time)
    workout_days_only: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class FoodNutritionCatalog(Base):
    __tablename__ = "food_nutrition_catalog"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    class_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name_vi: Mapped[str] = mapped_column(String(150))
    name_en: Mapped[str] = mapped_column(String(150))
    kcal_per_100g: Mapped[float] = mapped_column(Float)
    protein_per_100g: Mapped[float] = mapped_column(Float)
    carbs_per_100g: Mapped[float] = mapped_column(Float)
    fat_per_100g: Mapped[float] = mapped_column(Float)
    default_serving_g: Mapped[float] = mapped_column(Float, default=150.0)
    source_standard: Mapped[str] = mapped_column(String(80), default="NIN_VN_USDA")


class MealLog(Base):
    __tablename__ = "meal_logs"
    __table_args__ = (Index("ix_meal_user_logged", "user_id", "logged_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    catalog_food_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("food_nutrition_catalog.id", ondelete="SET NULL"),
        nullable=True,
    )
    meal_type: Mapped[str] = mapped_column(String(20))
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ai_detected_items: Mapped[list] = mapped_column(JSONB, default=list)
    total_calories: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name_vi: Mapped[str] = mapped_column(String(150))
    name_en: Mapped[str] = mapped_column(String(150))
    equipment_type: Mapped[str] = mapped_column(String(30))
    model_3d_glb_url: Mapped[str] = mapped_column(String(500))
    asset_checksum: Mapped[str] = mapped_column(String(128))
    primary_muscles: Mapped[list] = mapped_column(JSONB, default=list)
    secondary_muscles: Mapped[list] = mapped_column(JSONB, default=list)
    stabilizer_muscles: Mapped[list] = mapped_column(JSONB, default=list)
    phase_keyframes: Mapped[dict] = mapped_column(JSONB, default=dict)
    bad_form_warnings: Mapped[list] = mapped_column(JSONB, default=list)
    setup_guide: Mapped[dict] = mapped_column(JSONB, default=dict)


class WorkoutRoutine(Base):
    __tablename__ = "workout_routines"
    __table_args__ = (Index("ix_routine_user_deleted", "user_id", "deleted_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(150))
    split_type: Mapped[str] = mapped_column(String(40))
    scheduled_weekdays: Mapped[list] = mapped_column(JSONB, default=list)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RoutineExercise(Base):
    __tablename__ = "routine_exercises"
    __table_args__ = (Index("ix_routine_ex_order", "routine_id", "order_index"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    routine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_routines.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="RESTRICT")
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    superset_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_sets: Mapped[int] = mapped_column(Integer, default=3)
    target_rep_min: Mapped[int] = mapped_column(Integer, default=8)
    target_rep_max: Mapped[int] = mapped_column(Integer, default=12)
    default_rest_seconds: Mapped[int] = mapped_column(Integer, default=90)


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    __table_args__ = (Index("ix_session_user_started", "user_id", "started_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    routine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_routines.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_title: Mapped[str] = mapped_column(String(150))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    total_volume_kg: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    __table_args__ = (
        Index("ix_set_session_ex_num", "session_id", "exercise_id", "set_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="RESTRICT")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    set_type: Mapped[str] = mapped_column(String(20), default="NORMAL")
    weight_kg: Mapped[float] = mapped_column(Float)
    reps: Mapped[int] = mapped_column(Integer)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_1rm: Mapped[float] = mapped_column(Float, default=0.0)
    is_pr: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AIReadinessLog(Base):
    __tablename__ = "ai_readiness_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "target_date", name="uq_ai_readiness_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    target_date: Mapped[date] = mapped_column(Date)
    readiness_score: Mapped[float] = mapped_column(Float)
    readiness_level: Mapped[str] = mapped_column(String(20))
    muscle_fatigue_map: Mapped[dict] = mapped_column(JSONB, default=dict)
    weight_recommendations: Mapped[list] = mapped_column(JSONB, default=list)
    feature_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    model_version: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
