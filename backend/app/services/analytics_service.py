# [OWNER: M3] Analytics Aggregation Service (T-M3-11: F22, F24, F25)
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import (
    BiometricLog,
    Exercise,
    MealLog,
    User,
    WorkoutSession,
    WorkoutSet,
)

# Anh xa 11 Material chuan sang 6 truc Radar can bang co bap (F24)
MUSCLE_TO_RADAR_AXIS: dict[str, str] = {
    "Mat_Muscle_Chest": "chest",
    "Mat_Muscle_Back_Lats": "back",
    "Mat_Muscle_Traps": "back",
    "Mat_Muscle_Shoulders": "shoulders",
    "Mat_Muscle_Biceps": "arms",
    "Mat_Muscle_Triceps": "arms",
    "Mat_Muscle_Glutes": "legs",
    "Mat_Muscle_Quads": "legs",
    "Mat_Muscle_Hamstrings": "legs",
    "Mat_Muscle_Calves": "legs",
    "Mat_Muscle_Abs_Core": "core",
}


class AnalyticsService:
    """Tong hop Volume Load, 6 truc Radar nhom co va ky luc PR trong < 150ms."""

    async def build_summary(
        self,
        db: AsyncSession,
        user: User,
        days: int = 90,
    ) -> dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        cutoff_dt = now_utc - timedelta(days=days)
        radar_cutoff_dt = now_utc - timedelta(days=30)

        sessions = (
            await db.execute(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == user.id,
                    WorkoutSession.deleted_at.is_(None),
                    WorkoutSession.started_at >= cutoff_dt,
                )
                .order_by(WorkoutSession.started_at)
            )
        ).scalars().all()

        session_ids = [s.id for s in sessions]
        set_rows = (
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

        exercises = (await db.execute(select(Exercise))).scalars().all()
        ex_by_id = {e.id: e for e in exercises}

        # 1. Weekly Volume Load + Avg Weight + Daily Calories (F22)
        biometrics = (
            await db.execute(
                select(BiometricLog)
                .where(
                    BiometricLog.user_id == user.id,
                    BiometricLog.deleted_at.is_(None),
                    BiometricLog.logged_date >= cutoff_dt.date(),
                )
                .order_by(BiometricLog.logged_date)
            )
        ).scalars().all()

        meals = (
            await db.execute(
                select(MealLog)
                .where(
                    MealLog.user_id == user.id,
                    MealLog.deleted_at.is_(None),
                    MealLog.logged_at >= cutoff_dt,
                )
            )
        ).scalars().all()

        weekly_buckets: dict[str, dict[str, Any]] = {}
        for sess in sessions:
            iso_year, iso_week, _ = sess.started_at.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            bucket = weekly_buckets.setdefault(
                week_key,
                {
                    "week": week_key,
                    "total_volume_kg": 0.0,
                    "sessions_count": 0,
                    "weights": [],
                    "calories_total": 0.0,
                },
            )
            bucket["total_volume_kg"] = round(
                bucket["total_volume_kg"] + float(sess.total_volume_kg or 0.0), 1
            )
            bucket["sessions_count"] += 1

        for bio in biometrics:
            iso_year, iso_week, _ = bio.logged_date.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            bucket = weekly_buckets.setdefault(
                week_key,
                {
                    "week": week_key,
                    "total_volume_kg": 0.0,
                    "sessions_count": 0,
                    "weights": [],
                    "calories_total": 0.0,
                },
            )
            bucket["weights"].append(bio.weight_kg)

        for meal in meals:
            iso_year, iso_week, _ = meal.logged_at.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            if week_key in weekly_buckets:
                weekly_buckets[week_key]["calories_total"] = round(
                    weekly_buckets[week_key]["calories_total"]
                    + float(meal.total_calories or 0.0),
                    1,
                )

        weekly_volume = []
        for week_key in sorted(weekly_buckets.keys()):
            b = weekly_buckets[week_key]
            weights = b["weights"]
            weekly_volume.append(
                {
                    "week": b["week"],
                    "total_volume_kg": b["total_volume_kg"],
                    "sessions_count": b["sessions_count"],
                    "avg_weight_kg": round(sum(weights) / len(weights), 1)
                    if weights
                    else None,
                    "total_calories": b["calories_total"],
                }
            )

        # 2. 6-Axis Muscle Balance Radar (Effective Sets RPE >= 6 trong 30 ngay qua) (F24)
        radar_counts: dict[str, int] = {
            "chest": 0,
            "back": 0,
            "shoulders": 0,
            "arms": 0,
            "legs": 0,
            "core": 0,
        }
        session_start_by_id = {s.id: s.started_at for s in sessions}

        for wset in set_rows:
            if wset.set_type == "WARMUP":
                continue
            if wset.rpe is not None and wset.rpe < 6.0:
                continue
            sess_dt = session_start_by_id.get(wset.session_id)
            if sess_dt is None or sess_dt < radar_cutoff_dt:
                continue
            ex_obj = ex_by_id.get(wset.exercise_id)
            if ex_obj is None:
                continue
            counted_axes: set[str] = set()
            for m in ex_obj.primary_muscles or []:
                axis = MUSCLE_TO_RADAR_AXIS.get(m)
                if axis and axis not in counted_axes:
                    radar_counts[axis] += 1
                    counted_axes.add(axis)

        # 3. Personal Records (PR Wall) & Workout Streak (F25)
        all_pr_sets = (
            await db.execute(
                select(WorkoutSet)
                .join(WorkoutSession, WorkoutSession.id == WorkoutSet.session_id)
                .where(
                    WorkoutSession.user_id == user.id,
                    WorkoutSession.deleted_at.is_(None),
                    WorkoutSet.set_type != "WARMUP",
                )
                .order_by(desc(WorkoutSet.estimated_1rm))
            )
        ).scalars().all()

        best_by_exercise: dict[str, dict[str, Any]] = {}
        for wset in all_pr_sets:
            ex_obj = ex_by_id.get(wset.exercise_id)
            if ex_obj is None or wset.estimated_1rm <= 0:
                continue
            if ex_obj.code not in best_by_exercise:
                best_by_exercise[ex_obj.code] = {
                    "exercise_code": ex_obj.code,
                    "exercise_name_vi": ex_obj.name_vi,
                    "best_1rm_kg": round(wset.estimated_1rm, 1),
                    "best_weight_kg": round(wset.weight_kg, 1),
                    "best_reps": wset.reps,
                    "achieved_at": wset.completed_at.isoformat(),
                }

        workout_dates = sorted({s.started_at.date() for s in sessions}, reverse=True)
        streak_days = 0
        if workout_dates:
            cursor_date = workout_dates[0]
            if (now_utc.date() - cursor_date).days <= 2:
                for d in workout_dates:
                    if (cursor_date - d).days <= 2:
                        streak_days += 1
                        cursor_date = d
                    else:
                        break

        return {
            "period_days": days,
            "weekly_volume": weekly_volume,
            "muscle_radar": radar_counts,
            "personal_records": list(best_by_exercise.values())[:15],
            "streak_days": streak_days,
        }
