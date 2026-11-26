# [OWNER: M3] Auth & Account Deletion / Data Export Service (T-M3-03, T-M3-04)
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.entities import (
    AIReadinessLog,
    BiometricLog,
    DailyHealthLog,
    MealLog,
    RoutineExercise,
    SupplementSchedule,
    User,
    WorkoutRoutine,
    WorkoutSession,
    WorkoutSet,
)
from app.schemas.core_schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.services.storage_service import StorageService


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


def _issue_token_pair(user: User) -> TokenResponse:
    subject = str(user.id)
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfileResponse.model_validate(user),
    )


class AuthService:
    """Xu ly dang ky, dang nhap, refresh JWT, xuat du lieu va Cascade Delete CH Play."""

    async def register_user(
        self, db: AsyncSession, payload: RegisterRequest
    ) -> TokenResponse:
        if not payload.medical_disclaimer_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn phải chấp nhận Miễn trừ Trách nhiệm Y tế để đăng ký.",
            )

        normalized_email = payload.email.strip().lower()
        existing = await db.execute(
            select(User).where(User.email == normalized_email)
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email này đã được đăng ký.",
            )

        now_utc = datetime.now(timezone.utc)
        user = User(
            email=normalized_email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            gender=payload.gender,
            birth_date=payload.birth_date,
            height_cm=payload.height_cm,
            activity_level=payload.activity_level,
            fitness_goal=payload.fitness_goal,
            avatar_preset=payload.avatar_preset,
            medical_disclaimer_accepted=True,
            disclaimer_accepted_at=now_utc,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return _issue_token_pair(user)

    async def authenticate_user(
        self, db: AsyncSession, payload: LoginRequest
    ) -> TokenResponse:
        normalized_email = payload.email.strip().lower()
        result = await db.execute(select(User).where(User.email == normalized_email))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return _issue_token_pair(user)

    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> TokenResponse:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = uuid.UUID(str(payload["sub"]))
        except (ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không hợp lệ hoặc đã hết hạn.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản không tồn tại hoặc đã bị xóa.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return _issue_token_pair(user)

    async def export_user_data(self, db: AsyncSession, user: User) -> dict[str, Any]:
        """Xuat toan bo du lieu ca nhan cua nguoi dung duoi dang JSON (CH Play Data Portability)."""
        biometrics = (
            await db.execute(
                select(BiometricLog).where(BiometricLog.user_id == user.id)
            )
        ).scalars().all()
        daily_health = (
            await db.execute(
                select(DailyHealthLog).where(DailyHealthLog.user_id == user.id)
            )
        ).scalars().all()
        supplements = (
            await db.execute(
                select(SupplementSchedule).where(SupplementSchedule.user_id == user.id)
            )
        ).scalars().all()
        meals = (
            await db.execute(select(MealLog).where(MealLog.user_id == user.id))
        ).scalars().all()
        routines = (
            await db.execute(
                select(WorkoutRoutine).where(WorkoutRoutine.user_id == user.id)
            )
        ).scalars().all()
        routine_ids = [r.id for r in routines]
        routine_exercises = (
            (
                await db.execute(
                    select(RoutineExercise).where(
                        RoutineExercise.routine_id.in_(routine_ids)
                    )
                )
            )
            .scalars()
            .all()
            if routine_ids
            else []
        )
        sessions = (
            await db.execute(
                select(WorkoutSession).where(WorkoutSession.user_id == user.id)
            )
        ).scalars().all()
        session_ids = [s.id for s in sessions]
        workout_sets = (
            (
                await db.execute(
                    select(WorkoutSet).where(WorkoutSet.session_id.in_(session_ids))
                )
            )
            .scalars()
            .all()
            if session_ids
            else []
        )
        ai_readiness = (
            await db.execute(
                select(AIReadinessLog).where(AIReadinessLog.user_id == user.id)
            )
        ).scalars().all()

        return {
            "exported_at": _iso(datetime.now(timezone.utc)),
            "user": UserProfileResponse.model_validate(user).model_dump(mode="json"),
            "biometric_logs": [
                {
                    "id": str(b.id),
                    "weight_kg": b.weight_kg,
                    "body_fat_pct": b.body_fat_pct,
                    "muscle_mass_kg": b.muscle_mass_kg,
                    "bmi": b.bmi,
                    "circumferences_cm": b.circumferences_cm,
                    "logged_date": _iso(b.logged_date),
                    "updated_at": _iso(b.updated_at),
                    "deleted_at": _iso(b.deleted_at),
                }
                for b in biometrics
            ],
            "daily_health_logs": [
                {
                    "id": str(d.id),
                    "log_date": _iso(d.log_date),
                    "steps_count": d.steps_count,
                    "distance_km": d.distance_km,
                    "active_calories_kcal": d.active_calories_kcal,
                    "water_ml": d.water_ml,
                    "target_water_ml": d.target_water_ml,
                    "sleep_hours": d.sleep_hours,
                    "sleep_quality_score": d.sleep_quality_score,
                    "updated_at": _iso(d.updated_at),
                }
                for d in daily_health
            ],
            "supplement_schedules": [
                {
                    "id": str(s.id),
                    "supplement_name": s.supplement_name,
                    "dosage_label": s.dosage_label,
                    "reminder_time": _iso(s.reminder_time),
                    "workout_days_only": s.workout_days_only,
                    "is_active": s.is_active,
                    "updated_at": _iso(s.updated_at),
                    "deleted_at": _iso(s.deleted_at),
                }
                for s in supplements
            ],
            "meal_logs": [
                {
                    "id": str(m.id),
                    "catalog_food_id": str(m.catalog_food_id)
                    if m.catalog_food_id
                    else None,
                    "meal_type": m.meal_type,
                    "image_url": m.image_url,
                    "ai_detected_items": m.ai_detected_items,
                    "total_calories": m.total_calories,
                    "protein_g": m.protein_g,
                    "carbs_g": m.carbs_g,
                    "fat_g": m.fat_g,
                    "logged_at": _iso(m.logged_at),
                    "updated_at": _iso(m.updated_at),
                    "deleted_at": _iso(m.deleted_at),
                }
                for m in meals
            ],
            "workout_routines": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "split_type": r.split_type,
                    "scheduled_weekdays": r.scheduled_weekdays,
                    "is_template": r.is_template,
                    "updated_at": _iso(r.updated_at),
                    "deleted_at": _iso(r.deleted_at),
                }
                for r in routines
            ],
            "routine_exercises": [
                {
                    "id": str(re.id),
                    "routine_id": str(re.routine_id),
                    "exercise_id": str(re.exercise_id),
                    "order_index": re.order_index,
                    "superset_group_id": re.superset_group_id,
                    "target_sets": re.target_sets,
                    "target_rep_min": re.target_rep_min,
                    "target_rep_max": re.target_rep_max,
                    "default_rest_seconds": re.default_rest_seconds,
                }
                for re in routine_exercises
            ],
            "workout_sessions": [
                {
                    "id": str(ws.id),
                    "routine_id": str(ws.routine_id) if ws.routine_id else None,
                    "session_title": ws.session_title,
                    "started_at": _iso(ws.started_at),
                    "completed_at": _iso(ws.completed_at),
                    "duration_seconds": ws.duration_seconds,
                    "total_volume_kg": ws.total_volume_kg,
                    "status": ws.status,
                    "updated_at": _iso(ws.updated_at),
                    "deleted_at": _iso(ws.deleted_at),
                }
                for ws in sessions
            ],
            "workout_sets": [
                {
                    "id": str(wset.id),
                    "session_id": str(wset.session_id),
                    "exercise_id": str(wset.exercise_id),
                    "set_number": wset.set_number,
                    "set_type": wset.set_type,
                    "weight_kg": wset.weight_kg,
                    "reps": wset.reps,
                    "rpe": wset.rpe,
                    "estimated_1rm": wset.estimated_1rm,
                    "is_pr": wset.is_pr,
                    "completed_at": _iso(wset.completed_at),
                    "updated_at": _iso(wset.updated_at),
                }
                for wset in workout_sets
            ],
            "ai_readiness_logs": [
                {
                    "id": str(ai.id),
                    "target_date": _iso(ai.target_date),
                    "readiness_score": ai.readiness_score,
                    "readiness_level": ai.readiness_level,
                    "muscle_fatigue_map": ai.muscle_fatigue_map,
                    "weight_recommendations": ai.weight_recommendations,
                    "model_version": ai.model_version,
                    "created_at": _iso(ai.created_at),
                }
                for ai in ai_readiness
            ],
        }

    async def delete_user_cascade(self, db: AsyncSession, user: User) -> None:
        """Xoa vinh vien tai khoan va toan bo du lieu DB + Object Storage."""
        storage = StorageService()
        await storage.delete_user_media(str(user.id))
        await db.delete(user)
        await db.commit()

    async def delete_user_by_credentials(
        self, db: AsyncSession, email: str, password: str
    ) -> bool:
        normalized_email = email.strip().lower()
        result = await db.execute(select(User).where(User.email == normalized_email))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password_hash):
            return False
        await self.delete_user_cascade(db, user)
        return True
