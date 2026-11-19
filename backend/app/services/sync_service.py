# [OWNER: M3] Offline-First Two-Way LWW Sync Engine (T-M3-07)
import uuid
from datetime import date, datetime, time, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import (
    BiometricLog,
    DailyHealthLog,
    Exercise,
    MealLog,
    RoutineExercise,
    SupplementSchedule,
    User,
    WorkoutRoutine,
    WorkoutSession,
    WorkoutSet,
)
from app.schemas.core_schemas import SyncPushRequest


def parse_utc_datetime(raw: Any, default_now: bool = True) -> datetime | None:
    if raw is None or raw == "":
        return datetime.now(timezone.utc) if default_now else None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo is not None else raw.replace(tzinfo=timezone.utc)
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def parse_iso_date(raw: Any) -> date:
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    text = str(raw).strip().split("T")[0]
    return date.fromisoformat(text)


def parse_iso_time(raw: Any) -> time:
    if isinstance(raw, time):
        return raw
    text = str(raw).strip()
    parts = text.split(":")
    hour = int(parts[0]) if len(parts) > 0 else 8
    minute = int(parts[1]) if len(parts) > 1 else 0
    return time(hour=hour % 24, minute=minute % 60)


def parse_uuid_or_deterministic(raw: Any, namespace_prefix: str = "vigorai") -> uuid.UUID:
    if raw is None or str(raw).strip() == "":
        return uuid.uuid4()
    if isinstance(raw, uuid.UUID):
        return raw
    text = str(raw).strip()
    try:
        return uuid.UUID(text)
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"{namespace_prefix}:{text}")


def calculate_1rm_epley_brzycki(weight_kg: float, reps: int) -> float:
    """Cong thuc uoc tinh 1RM chuan Epley (1985) & Brzycki (1993) (F17)."""
    if weight_kg <= 0 or reps <= 0:
        return 0.0
    if reps == 1:
        return round(weight_kg, 2)
    epley = weight_kg * (1.0 + reps / 30.0)
    if reps <= 10:
        brzycki = weight_kg * (36.0 / (37.0 - reps))
        return round((epley + brzycki) / 2.0, 2)
    return round(epley, 2)


def _as_utc(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


class SyncService:
    """Dong bo hai chieu theo quy tac Last-Write-Wins (UTC updated_at) & max(steps_count)."""

    async def _resolve_exercise_maps(
        self, db: AsyncSession
    ) -> tuple[dict[str, uuid.UUID], dict[uuid.UUID, str]]:
        rows = (await db.execute(select(Exercise))).scalars().all()
        by_code = {e.code.upper(): e.id for e in rows}
        by_id = {e.id: e.code for e in rows}
        return by_code, by_id

    async def apply_push_batch(
        self,
        db: AsyncSession,
        user: User,
        payload: SyncPushRequest,
    ) -> dict[str, Any]:
        synced_ids: dict[str, list[str]] = {
            "biometric_logs": [],
            "daily_health_logs": [],
            "supplement_schedules": [],
            "meal_logs": [],
            "workout_routines": [],
            "workout_sessions": [],
            "workout_sets": [],
        }
        total_applied = 0
        ex_by_code, _ = await self._resolve_exercise_maps(db)

        # 1. Biometric Logs (LWW by updated_at)
        for item in payload.biometric_logs:
            raw_id = item.get("id")
            rec_id = parse_uuid_or_deterministic(raw_id, f"bio:{user.id}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_deleted = parse_utc_datetime(item.get("deleted_at"), default_now=False)
            weight_kg = float(item.get("weight_kg", 70.0))
            height_m = (user.height_cm or 170.0) / 100.0
            bmi_val = float(item.get("bmi") or round(weight_kg / (height_m * height_m), 1))
            logged_date = parse_iso_date(item.get("logged_date") or incoming_updated.date())

            existing = (
                await db.execute(
                    select(BiometricLog).where(
                        BiometricLog.id == rec_id, BiometricLog.user_id == user.id
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    BiometricLog(
                        id=rec_id,
                        user_id=user.id,
                        weight_kg=weight_kg,
                        body_fat_pct=float(item["body_fat_pct"])
                        if item.get("body_fat_pct") is not None
                        else None,
                        muscle_mass_kg=float(item["muscle_mass_kg"])
                        if item.get("muscle_mass_kg") is not None
                        else None,
                        bmi=bmi_val,
                        circumferences_cm=item.get("circumferences_cm") or {},
                        logged_date=logged_date,
                        updated_at=incoming_updated,
                        deleted_at=incoming_deleted,
                    )
                )
                total_applied += 1
            elif incoming_updated >= _as_utc(existing.updated_at):
                existing.weight_kg = weight_kg
                if "body_fat_pct" in item:
                    existing.body_fat_pct = (
                        float(item["body_fat_pct"])
                        if item["body_fat_pct"] is not None
                        else None
                    )
                if "muscle_mass_kg" in item:
                    existing.muscle_mass_kg = (
                        float(item["muscle_mass_kg"])
                        if item["muscle_mass_kg"] is not None
                        else None
                    )
                existing.bmi = bmi_val
                if "circumferences_cm" in item and item["circumferences_cm"] is not None:
                    existing.circumferences_cm = item["circumferences_cm"]
                existing.logged_date = logged_date
                existing.updated_at = incoming_updated
                existing.deleted_at = incoming_deleted
                total_applied += 1

            synced_ids["biometric_logs"].append(str(raw_id or rec_id))

        # 2. Daily Health Logs (LWW + max(steps_count) & max(active_calories_kcal))
        for item in payload.daily_health_logs:
            raw_id = item.get("id")
            log_date = parse_iso_date(item.get("log_date") or datetime.now(timezone.utc).date())
            rec_id = parse_uuid_or_deterministic(raw_id, f"daily:{user.id}:{log_date.isoformat()}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_steps = int(item.get("steps_count", 0))
            incoming_kcal = int(item.get("active_calories_kcal", 0))

            existing = (
                await db.execute(
                    select(DailyHealthLog).where(
                        DailyHealthLog.user_id == user.id,
                        DailyHealthLog.log_date == log_date,
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    DailyHealthLog(
                        id=rec_id,
                        user_id=user.id,
                        log_date=log_date,
                        steps_count=incoming_steps,
                        distance_km=float(
                            item.get("distance_km", round(incoming_steps * 0.00071, 2))
                        ),
                        active_calories_kcal=incoming_kcal,
                        water_ml=int(item.get("water_ml", 0)),
                        target_water_ml=int(item.get("target_water_ml", 2450)),
                        sleep_hours=float(item.get("sleep_hours", 0.0)),
                        sleep_quality_score=int(item["sleep_quality_score"])
                        if item.get("sleep_quality_score") is not None
                        else None,
                        updated_at=incoming_updated,
                    )
                )
                total_applied += 1
            else:
                best_steps = max(existing.steps_count, incoming_steps)
                existing.steps_count = best_steps
                existing.active_calories_kcal = max(
                    existing.active_calories_kcal, incoming_kcal
                )
                if incoming_updated >= _as_utc(existing.updated_at):
                    existing.distance_km = max(
                        existing.distance_km,
                        float(item.get("distance_km", existing.distance_km)),
                    )
                    if "water_ml" in item:
                        existing.water_ml = int(item["water_ml"])
                    if "target_water_ml" in item and item["target_water_ml"] is not None:
                        existing.target_water_ml = int(item["target_water_ml"])
                    if "sleep_hours" in item:
                        existing.sleep_hours = float(item["sleep_hours"])
                    if "sleep_quality_score" in item:
                        existing.sleep_quality_score = (
                            int(item["sleep_quality_score"])
                            if item["sleep_quality_score"] is not None
                            else None
                        )
                    existing.updated_at = incoming_updated
                total_applied += 1

            synced_ids["daily_health_logs"].append(str(raw_id or rec_id))

        # 3. Supplement Schedules (LWW)
        for item in payload.supplement_schedules:
            raw_id = item.get("id")
            rec_id = parse_uuid_or_deterministic(raw_id, f"supp:{user.id}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_deleted = parse_utc_datetime(item.get("deleted_at"), default_now=False)

            existing = (
                await db.execute(
                    select(SupplementSchedule).where(
                        SupplementSchedule.id == rec_id,
                        SupplementSchedule.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    SupplementSchedule(
                        id=rec_id,
                        user_id=user.id,
                        supplement_name=str(item.get("supplement_name", "Supplement")),
                        dosage_label=str(item.get("dosage_label", "1 liều")),
                        reminder_time=parse_iso_time(item.get("reminder_time", "08:00")),
                        workout_days_only=bool(item.get("workout_days_only", False)),
                        is_active=bool(item.get("is_active", True)),
                        updated_at=incoming_updated,
                        deleted_at=incoming_deleted,
                    )
                )
                total_applied += 1
            elif incoming_updated >= _as_utc(existing.updated_at):
                existing.supplement_name = str(
                    item.get("supplement_name", existing.supplement_name)
                )
                existing.dosage_label = str(
                    item.get("dosage_label", existing.dosage_label)
                )
                if "reminder_time" in item:
                    existing.reminder_time = parse_iso_time(item["reminder_time"])
                if "workout_days_only" in item:
                    existing.workout_days_only = bool(item["workout_days_only"])
                if "is_active" in item:
                    existing.is_active = bool(item["is_active"])
                existing.updated_at = incoming_updated
                existing.deleted_at = incoming_deleted
                total_applied += 1

            synced_ids["supplement_schedules"].append(str(raw_id or rec_id))

        # 4. Meal Logs (LWW)
        for item in payload.meal_logs:
            raw_id = item.get("id")
            rec_id = parse_uuid_or_deterministic(raw_id, f"meal:{user.id}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_deleted = parse_utc_datetime(item.get("deleted_at"), default_now=False)
            logged_at = parse_utc_datetime(item.get("logged_at")) or incoming_updated

            cat_id: uuid.UUID | None = None
            if item.get("catalog_food_id"):
                try:
                    cat_id = uuid.UUID(str(item["catalog_food_id"]))
                except ValueError:
                    cat_id = None

            existing = (
                await db.execute(
                    select(MealLog).where(
                        MealLog.id == rec_id, MealLog.user_id == user.id
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    MealLog(
                        id=rec_id,
                        user_id=user.id,
                        catalog_food_id=cat_id,
                        meal_type=str(item.get("meal_type", "LUNCH")),
                        image_url=item.get("image_url"),
                        ai_detected_items=item.get("ai_detected_items") or [],
                        total_calories=float(item.get("total_calories", 0.0)),
                        protein_g=float(item.get("protein_g", 0.0)),
                        carbs_g=float(item.get("carbs_g", 0.0)),
                        fat_g=float(item.get("fat_g", 0.0)),
                        logged_at=logged_at,
                        updated_at=incoming_updated,
                        deleted_at=incoming_deleted,
                    )
                )
                total_applied += 1
            elif incoming_updated >= _as_utc(existing.updated_at):
                existing.meal_type = str(item.get("meal_type", existing.meal_type))
                if "image_url" in item:
                    existing.image_url = item["image_url"]
                if "ai_detected_items" in item and item["ai_detected_items"] is not None:
                    existing.ai_detected_items = item["ai_detected_items"]
                existing.total_calories = float(
                    item.get("total_calories", existing.total_calories)
                )
                existing.protein_g = float(item.get("protein_g", existing.protein_g))
                existing.carbs_g = float(item.get("carbs_g", existing.carbs_g))
                existing.fat_g = float(item.get("fat_g", existing.fat_g))
                existing.logged_at = logged_at
                existing.updated_at = incoming_updated
                existing.deleted_at = incoming_deleted
                total_applied += 1

            synced_ids["meal_logs"].append(str(raw_id or rec_id))

        # 5. Workout Routines (+ nested exercises)
        for item in payload.workout_routines:
            raw_id = item.get("id")
            rec_id = parse_uuid_or_deterministic(raw_id, f"routine:{user.id}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_deleted = parse_utc_datetime(item.get("deleted_at"), default_now=False)

            existing = (
                await db.execute(
                    select(WorkoutRoutine).where(
                        WorkoutRoutine.id == rec_id,
                        WorkoutRoutine.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()

            should_replace_exercises = False
            if existing is None:
                routine = WorkoutRoutine(
                    id=rec_id,
                    user_id=user.id,
                    name=str(item.get("name", "Giáo án cá nhân")),
                    split_type=str(item.get("split_type", "CUSTOM")),
                    scheduled_weekdays=item.get("scheduled_weekdays") or [],
                    is_template=False,
                    updated_at=incoming_updated,
                    deleted_at=incoming_deleted,
                )
                db.add(routine)
                await db.flush()
                should_replace_exercises = True
                total_applied += 1
            elif incoming_updated >= _as_utc(existing.updated_at):
                existing.name = str(item.get("name", existing.name))
                existing.split_type = str(item.get("split_type", existing.split_type))
                if "scheduled_weekdays" in item:
                    existing.scheduled_weekdays = item["scheduled_weekdays"] or []
                existing.updated_at = incoming_updated
                existing.deleted_at = incoming_deleted
                should_replace_exercises = "exercises" in item
                total_applied += 1

            if should_replace_exercises and isinstance(item.get("exercises"), list):
                old_links = (
                    await db.execute(
                        select(RoutineExercise).where(
                            RoutineExercise.routine_id == rec_id
                        )
                    )
                ).scalars().all()
                for link in old_links:
                    await db.delete(link)
                for idx, ex_item in enumerate(item["exercises"]):
                    ex_id = None
                    if ex_item.get("exercise_id"):
                        try:
                            ex_id = uuid.UUID(str(ex_item["exercise_id"]))
                        except ValueError:
                            ex_id = None
                    if ex_id is None and ex_item.get("exercise_code"):
                        ex_id = ex_by_code.get(str(ex_item["exercise_code"]).upper())
                    if ex_id is None:
                        continue
                    db.add(
                        RoutineExercise(
                            id=uuid.uuid4(),
                            routine_id=rec_id,
                            exercise_id=ex_id,
                            order_index=int(ex_item.get("order_index", idx)),
                            superset_group_id=int(ex_item["superset_group_id"])
                            if ex_item.get("superset_group_id") is not None
                            else None,
                            target_sets=int(ex_item.get("target_sets", 3)),
                            target_rep_min=int(ex_item.get("target_rep_min", 8)),
                            target_rep_max=int(ex_item.get("target_rep_max", 12)),
                            default_rest_seconds=int(
                                ex_item.get("default_rest_seconds", 90)
                            ),
                        )
                    )

            synced_ids["workout_routines"].append(str(raw_id or rec_id))

        # 6. Workout Sessions & 7. Workout Sets
        all_incoming_sets: list[dict[str, Any]] = list(payload.workout_sets)
        touched_session_ids: set[uuid.UUID] = set()

        for item in payload.workout_sessions:
            raw_id = item.get("id")
            rec_id = parse_uuid_or_deterministic(raw_id, f"session:{user.id}")
            incoming_updated = parse_utc_datetime(item.get("updated_at")) or datetime.now(timezone.utc)
            incoming_deleted = parse_utc_datetime(item.get("deleted_at"), default_now=False)
            started_at = parse_utc_datetime(item.get("started_at")) or incoming_updated
            completed_at = parse_utc_datetime(item.get("completed_at"), default_now=False)

            routine_id: uuid.UUID | None = None
            if item.get("routine_id"):
                try:
                    routine_id = uuid.UUID(str(item["routine_id"]))
                except ValueError:
                    routine_id = None

            existing = (
                await db.execute(
                    select(WorkoutSession).where(
                        WorkoutSession.id == rec_id,
                        WorkoutSession.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()

            if existing is None:
                db.add(
                    WorkoutSession(
                        id=rec_id,
                        user_id=user.id,
                        routine_id=routine_id,
                        session_title=str(item.get("session_title", "Buổi tập Gym")),
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_seconds=int(item.get("duration_seconds", 0)),
                        total_volume_kg=float(item.get("total_volume_kg", 0.0)),
                        status=str(item.get("status", "COMPLETED")),
                        updated_at=incoming_updated,
                        deleted_at=incoming_deleted,
                    )
                )
                total_applied += 1
            elif incoming_updated >= _as_utc(existing.updated_at):
                existing.session_title = str(
                    item.get("session_title", existing.session_title)
                )
                existing.started_at = started_at
                existing.completed_at = completed_at
                existing.duration_seconds = int(
                    item.get("duration_seconds", existing.duration_seconds)
                )
                existing.total_volume_kg = float(
                    item.get("total_volume_kg", existing.total_volume_kg)
                )
                existing.status = str(item.get("status", existing.status))
                existing.updated_at = incoming_updated
                existing.deleted_at = incoming_deleted
                total_applied += 1

            touched_session_ids.add(rec_id)
            synced_ids["workout_sessions"].append(str(raw_id or rec_id))

            if isinstance(item.get("sets"), list):
                for s_item in item["sets"]:
                    s_copy = dict(s_item)
                    s_copy.setdefault("session_id", str(rec_id))
                    all_incoming_sets.append(s_copy)

        await db.flush()

        for s_item in all_incoming_sets:
            raw_set_id = s_item.get("id")
            set_id = parse_uuid_or_deterministic(raw_set_id, f"set:{user.id}")
            session_id = parse_uuid_or_deterministic(
                s_item.get("session_id"), f"session:{user.id}"
            )

            ex_id: uuid.UUID | None = None
            if s_item.get("exercise_id"):
                try:
                    ex_id = uuid.UUID(str(s_item["exercise_id"]))
                except ValueError:
                    ex_id = ex_by_code.get(str(s_item["exercise_id"]).upper())
            if ex_id is None and s_item.get("exercise_code"):
                ex_id = ex_by_code.get(str(s_item["exercise_code"]).upper())
            if ex_id is None:
                continue

            incoming_updated = parse_utc_datetime(s_item.get("updated_at")) or datetime.now(timezone.utc)
            completed_at = parse_utc_datetime(s_item.get("completed_at")) or incoming_updated
            weight_kg = float(s_item.get("weight_kg", 0.0))
            reps = int(s_item.get("reps", 0))
            set_type = str(s_item.get("set_type", "NORMAL")).upper()
            est_1rm = calculate_1rm_epley_brzycki(weight_kg, reps)

            prev_max_1rm = (
                await db.execute(
                    select(func.max(WorkoutSet.estimated_1rm))
                    .join(
                        WorkoutSession,
                        WorkoutSession.id == WorkoutSet.session_id,
                    )
                    .where(
                        WorkoutSession.user_id == user.id,
                        WorkoutSet.exercise_id == ex_id,
                        WorkoutSet.id != set_id,
                    )
                )
            ).scalar_one_or_none() or 0.0

            is_pr = bool(
                s_item.get("is_pr")
                or (set_type != "WARMUP" and est_1rm > 0 and est_1rm > float(prev_max_1rm))
            )

            existing_set = (
                await db.execute(select(WorkoutSet).where(WorkoutSet.id == set_id))
            ).scalar_one_or_none()

            if existing_set is None:
                db.add(
                    WorkoutSet(
                        id=set_id,
                        session_id=session_id,
                        exercise_id=ex_id,
                        set_number=int(s_item.get("set_number", 1)),
                        set_type=set_type,
                        weight_kg=weight_kg,
                        reps=reps,
                        rpe=float(s_item["rpe"])
                        if s_item.get("rpe") is not None
                        else None,
                        estimated_1rm=est_1rm,
                        is_pr=is_pr,
                        completed_at=completed_at,
                        updated_at=incoming_updated,
                    )
                )
                total_applied += 1
            elif incoming_updated >= _as_utc(existing_set.updated_at):
                existing_set.set_number = int(
                    s_item.get("set_number", existing_set.set_number)
                )
                existing_set.set_type = set_type
                existing_set.weight_kg = weight_kg
                existing_set.reps = reps
                if "rpe" in s_item:
                    existing_set.rpe = (
                        float(s_item["rpe"]) if s_item["rpe"] is not None else None
                    )
                existing_set.estimated_1rm = est_1rm
                existing_set.is_pr = is_pr
                existing_set.completed_at = completed_at
                existing_set.updated_at = incoming_updated
                total_applied += 1

            touched_session_ids.add(session_id)
            synced_ids["workout_sets"].append(str(raw_set_id or set_id))

        await db.flush()

        for sess_id in touched_session_ids:
            sess = (
                await db.execute(
                    select(WorkoutSession).where(
                        WorkoutSession.id == sess_id,
                        WorkoutSession.user_id == user.id,
                    )
                )
            ).scalar_one_or_none()
            if sess is None:
                continue
            sets_rows = (
                await db.execute(
                    select(WorkoutSet).where(WorkoutSet.session_id == sess_id)
                )
            ).scalars().all()
            if sets_rows:
                sess.total_volume_kg = round(
                    sum(
                        s.weight_kg * s.reps
                        for s in sets_rows
                        if s.set_type != "WARMUP"
                    ),
                    1,
                )

        await db.commit()
        return {
            "status": "ok",
            "synced_ids": synced_ids,
            "total_applied": total_applied,
            "server_time_utc": datetime.now(timezone.utc),
        }

    async def pull_updates(
        self,
        db: AsyncSession,
        user: User,
        since: str | None = None,
    ) -> dict[str, Any]:
        since_dt = parse_utc_datetime(since, default_now=False)
        _, ex_code_by_id = await self._resolve_exercise_maps(db)

        bio_stmt = select(BiometricLog).where(BiometricLog.user_id == user.id)
        daily_stmt = select(DailyHealthLog).where(DailyHealthLog.user_id == user.id)
        supp_stmt = select(SupplementSchedule).where(SupplementSchedule.user_id == user.id)
        meal_stmt = select(MealLog).where(MealLog.user_id == user.id)
        routine_stmt = select(WorkoutRoutine).where(WorkoutRoutine.user_id == user.id)
        session_stmt = select(WorkoutSession).where(WorkoutSession.user_id == user.id)

        if since_dt is not None:
            bio_stmt = bio_stmt.where(BiometricLog.updated_at >= since_dt)
            daily_stmt = daily_stmt.where(DailyHealthLog.updated_at >= since_dt)
            supp_stmt = supp_stmt.where(SupplementSchedule.updated_at >= since_dt)
            meal_stmt = meal_stmt.where(MealLog.updated_at >= since_dt)
            routine_stmt = routine_stmt.where(WorkoutRoutine.updated_at >= since_dt)
            session_stmt = session_stmt.where(WorkoutSession.updated_at >= since_dt)

        biometrics = (await db.execute(bio_stmt)).scalars().all()
        daily_logs = (await db.execute(daily_stmt)).scalars().all()
        supplements = (await db.execute(supp_stmt)).scalars().all()
        meals = (await db.execute(meal_stmt)).scalars().all()
        routines = (await db.execute(routine_stmt)).scalars().all()
        sessions = (await db.execute(session_stmt)).scalars().all()

        routine_ids = [r.id for r in routines]
        routine_ex_rows = (
            (
                await db.execute(
                    select(RoutineExercise)
                    .where(RoutineExercise.routine_id.in_(routine_ids))
                    .order_by(RoutineExercise.order_index)
                )
            )
            .scalars()
            .all()
            if routine_ids
            else []
        )
        routine_ex_map: dict[uuid.UUID, list[dict[str, Any]]] = {}
        for rx in routine_ex_rows:
            routine_ex_map.setdefault(rx.routine_id, []).append(
                {
                    "id": str(rx.id),
                    "exercise_id": str(rx.exercise_id),
                    "exercise_code": ex_code_by_id.get(rx.exercise_id, ""),
                    "order_index": rx.order_index,
                    "superset_group_id": rx.superset_group_id,
                    "target_sets": rx.target_sets,
                    "target_rep_min": rx.target_rep_min,
                    "target_rep_max": rx.target_rep_max,
                    "default_rest_seconds": rx.default_rest_seconds,
                }
            )

        set_stmt = (
            select(WorkoutSet)
            .join(WorkoutSession, WorkoutSession.id == WorkoutSet.session_id)
            .where(WorkoutSession.user_id == user.id)
        )
        if since_dt is not None:
            set_stmt = set_stmt.where(WorkoutSet.updated_at >= since_dt)
        workout_sets = (await db.execute(set_stmt)).scalars().all()

        return {
            "since": since,
            "server_time_utc": datetime.now(timezone.utc).isoformat(),
            "records": {
                "biometric_logs": [
                    {
                        "id": str(b.id),
                        "weight_kg": b.weight_kg,
                        "body_fat_pct": b.body_fat_pct,
                        "muscle_mass_kg": b.muscle_mass_kg,
                        "bmi": b.bmi,
                        "circumferences_cm": b.circumferences_cm,
                        "logged_date": b.logged_date.isoformat(),
                        "sync_status": "SYNCED",
                        "updated_at": b.updated_at.isoformat(),
                        "deleted_at": b.deleted_at.isoformat() if b.deleted_at else None,
                    }
                    for b in biometrics
                ],
                "daily_health_logs": [
                    {
                        "id": str(d.id),
                        "log_date": d.log_date.isoformat(),
                        "steps_count": d.steps_count,
                        "target_steps": 8000,
                        "distance_km": d.distance_km,
                        "active_calories_kcal": d.active_calories_kcal,
                        "water_ml": d.water_ml,
                        "target_water_ml": d.target_water_ml,
                        "sleep_hours": d.sleep_hours,
                        "sleep_quality_score": d.sleep_quality_score,
                        "sync_status": "SYNCED",
                        "updated_at": d.updated_at.isoformat(),
                    }
                    for d in daily_logs
                ],
                "supplement_schedules": [
                    {
                        "id": str(s.id),
                        "supplement_name": s.supplement_name,
                        "dosage_label": s.dosage_label,
                        "reminder_time": s.reminder_time.strftime("%H:%M"),
                        "workout_days_only": s.workout_days_only,
                        "is_active": s.is_active,
                        "sync_status": "SYNCED",
                        "updated_at": s.updated_at.isoformat(),
                        "deleted_at": s.deleted_at.isoformat() if s.deleted_at else None,
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
                        "logged_at": m.logged_at.isoformat(),
                        "sync_status": "SYNCED",
                        "updated_at": m.updated_at.isoformat(),
                        "deleted_at": m.deleted_at.isoformat() if m.deleted_at else None,
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
                        "exercises": routine_ex_map.get(r.id, []),
                        "sync_status": "SYNCED",
                        "updated_at": r.updated_at.isoformat(),
                        "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
                    }
                    for r in routines
                ],
                "workout_sessions": [
                    {
                        "id": str(ws.id),
                        "routine_id": str(ws.routine_id) if ws.routine_id else None,
                        "session_title": ws.session_title,
                        "started_at": ws.started_at.isoformat(),
                        "completed_at": ws.completed_at.isoformat()
                        if ws.completed_at
                        else None,
                        "duration_seconds": ws.duration_seconds,
                        "total_volume_kg": ws.total_volume_kg,
                        "status": ws.status,
                        "sync_status": "SYNCED",
                        "updated_at": ws.updated_at.isoformat(),
                        "deleted_at": ws.deleted_at.isoformat()
                        if ws.deleted_at
                        else None,
                    }
                    for ws in sessions
                ],
                "workout_sets": [
                    {
                        "id": str(wset.id),
                        "session_id": str(wset.session_id),
                        "exercise_id": str(wset.exercise_id),
                        "exercise_code": ex_code_by_id.get(wset.exercise_id, ""),
                        "set_number": wset.set_number,
                        "set_type": wset.set_type,
                        "weight_kg": wset.weight_kg,
                        "reps": wset.reps,
                        "rpe": wset.rpe,
                        "estimated_1rm": wset.estimated_1rm,
                        "is_pr": wset.is_pr,
                        "completed_at": wset.completed_at.isoformat(),
                        "sync_status": "SYNCED",
                        "updated_at": wset.updated_at.isoformat(),
                    }
                    for wset in workout_sets
                ],
            },
        }
