# [OWNER: M3] Seed 30 ngay lich su tap luyen / dinh duong / sinh trac cho M4 train & test AI (T-M3-05)
import asyncio
import random
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.seed_catalog_and_exercises import (
    CANONICAL_MUSCLE_MATERIALS,
    seed_catalog_and_exercises,
)
from app.db.session import AsyncSessionLocal
from app.models.entities import (
    AIReadinessLog,
    BiometricLog,
    DailyHealthLog,
    Exercise,
    FoodNutritionCatalog,
    MealLog,
    RoutineExercise,
    SupplementSchedule,
    User,
    WorkoutRoutine,
    WorkoutSession,
    WorkoutSet,
)

DEMO_EMAIL = "demo@vigorai.app"
DEMO_USER_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")


def _epley_brzycki_1rm(weight_kg: float, reps: int) -> float:
    if reps <= 1:
        return round(weight_kg, 2)
    epley = weight_kg * (1.0 + reps / 30.0)
    if reps <= 10:
        brzycki = weight_kg * (36.0 / (37.0 - reps))
        return round((epley + brzycki) / 2.0, 2)
    return round(epley, 2)


async def seed_demo_history(db: AsyncSession, days: int = 30) -> dict[str, int]:
    """Tao user demo@vigorai.app cung 30 ngay du lieu lien hoan khop khoa ngoai."""
    await seed_catalog_and_exercises(db)

    res = await db.execute(select(User).where(User.email == DEMO_EMAIL))
    user = res.scalar_one_or_none()
    now_utc = datetime.now(timezone.utc)

    if user is None:
        user = User(
            id=DEMO_USER_ID,
            email=DEMO_EMAIL,
            password_hash=hash_password("VigorAI@2026"),
            full_name="Nguyễn Văn An",
            gender="MALE",
            birth_date=date(2002, 5, 14),
            height_cm=172.0,
            activity_level="MODERATE",
            fitness_goal="BULK",
            avatar_preset="MALE_FIT",
            medical_disclaimer_accepted=True,
            disclaimer_accepted_at=now_utc - timedelta(days=days),
        )
        db.add(user)
        await db.flush()

    existing_bio = (
        await db.execute(select(BiometricLog).where(BiometricLog.user_id == user.id))
    ).scalars().first()
    if existing_bio is not None:
        return {"status": 0, "message_already_seeded": 1}

    foods = {
        f.class_code: f
        for f in (await db.execute(select(FoodNutritionCatalog))).scalars().all()
    }
    exercises = {
        e.code: e
        for e in (await db.execute(select(Exercise))).scalars().all()
    }

    # 1. Supplement schedules
    for name, dosage, hr, only_w in [
        ("Whey Protein Isolate", "1 muỗng (32g)", time(17, 30), True),
        ("Creatine Monohydrate", "5g mỗi ngày", time(8, 30), False),
        ("Omega-3 Fish Oil", "2 viên sau bữa tối", time(20, 0), False),
    ]:
        db.add(
            SupplementSchedule(
                id=uuid.uuid4(),
                user_id=user.id,
                supplement_name=name,
                dosage_label=dosage,
                reminder_time=hr,
                workout_days_only=only_w,
                is_active=True,
            )
        )

    # 2. User routines (Push / Pull / Legs)
    push_routine = WorkoutRoutine(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Giáo án Push Cá nhân",
        split_type="PUSH_PULL_LEGS",
        scheduled_weekdays=[1, 4],
        is_template=False,
    )
    pull_routine = WorkoutRoutine(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Giáo án Pull Cá nhân",
        split_type="PUSH_PULL_LEGS",
        scheduled_weekdays=[2, 5],
        is_template=False,
    )
    leg_routine = WorkoutRoutine(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Giáo án Legs Cá nhân",
        split_type="PUSH_PULL_LEGS",
        scheduled_weekdays=[3, 6],
        is_template=False,
    )
    db.add_all([push_routine, pull_routine, leg_routine])
    await db.flush()

    routine_plan = [
        (
            push_routine,
            "Buổi Đẩy — Ngực & Vai",
            [("BARBELL_BENCH_PRESS", 70.0, 8), ("INCLINE_DUMBBELL_PRESS", 24.0, 10), ("DUMBBELL_LATERAL_RAISE", 10.0, 12), ("CABLE_TRICEP_PUSHDOWN", 25.0, 12)],
        ),
        (
            pull_routine,
            "Buổi Kéo — Lưng & Tay trước",
            [("BARBELL_BENT_OVER_ROW", 65.0, 8), ("LAT_PULLDOWN", 55.0, 10), ("SEATED_CABLE_ROW", 50.0, 10), ("BARBELL_BICEP_CURL", 30.0, 10)],
        ),
        (
            leg_routine,
            "Buổi Chân — Squat & Đùi sau",
            [("BARBELL_SQUAT", 95.0, 6), ("ROMANIAN_DEADLIFT", 80.0, 8), ("LEG_PRESS", 140.0, 10), ("PLANK", 0.0, 60)],
        ),
    ]

    for routine_obj, _, ex_items in routine_plan:
        for idx, (ex_code, _, reps) in enumerate(ex_items):
            db.add(
                RoutineExercise(
                    id=uuid.uuid4(),
                    routine_id=routine_obj.id,
                    exercise_id=exercises[ex_code].id,
                    order_index=idx,
                    target_sets=3,
                    target_rep_min=max(5, reps - 2),
                    target_rep_max=reps + 2,
                    default_rest_seconds=120,
                )
            )

    rng = random.Random(20261118)
    today = now_utc.date()
    meal_templates = [
        ("BREAKFAST", "OATMEAL", 70.0),
        ("LUNCH", "GRILLED_CHICKEN_BREAST", 200.0),
        ("LUNCH", "WHITE_RICE", 180.0),
        ("DINNER", "BEEF_STEAK", 180.0),
        ("SNACK", "WHEY_SHAKE", 32.0),
    ]

    sessions_created = 0
    sets_created = 0
    meals_created = 0

    for offset in range(days, 0, -1):
        day_date = today - timedelta(days=offset)
        progress_ratio = (days - offset) / days
        weight_kg = round(68.8 + 1.2 * progress_ratio + rng.uniform(-0.2, 0.2), 1)
        bmi = round(weight_kg / ((1.72) ** 2), 1)

        db.add(
            BiometricLog(
                id=uuid.uuid4(),
                user_id=user.id,
                weight_kg=weight_kg,
                body_fat_pct=round(16.8 - 0.6 * progress_ratio, 1),
                muscle_mass_kg=round(33.2 + 0.8 * progress_ratio, 1),
                bmi=bmi,
                circumferences_cm={
                    "chest": round(97.5 + progress_ratio, 1),
                    "waist": round(78.2 - 0.5 * progress_ratio, 1),
                    "hips": 95.0,
                    "arm": round(35.8 + 0.4 * progress_ratio, 1),
                    "thigh": round(56.0 + 0.5 * progress_ratio, 1),
                },
                logged_date=day_date,
            )
        )

        is_workout_day = (offset % 4) != 0
        steps = rng.randint(6500, 11200)
        sleep_hours = round(rng.uniform(6.2, 8.3), 1)
        target_water = int(35 * weight_kg + (500 if is_workout_day else 0))

        db.add(
            DailyHealthLog(
                id=uuid.uuid4(),
                user_id=user.id,
                log_date=day_date,
                steps_count=steps,
                distance_km=round(steps * 0.71 / 1000.0, 2),
                active_calories_kcal=rng.randint(250, 520),
                water_ml=int(target_water * rng.uniform(0.82, 1.05)),
                target_water_ml=target_water,
                sleep_hours=sleep_hours,
                sleep_quality_score=4 if sleep_hours >= 7.0 else 3,
            )
        )

        for meal_type, food_code, grams in meal_templates:
            cat = foods[food_code]
            factor = (grams * rng.uniform(0.9, 1.1)) / 100.0
            kcal = round(cat.kcal_per_100g * factor, 1)
            prot = round(cat.protein_per_100g * factor, 1)
            carb = round(cat.carbs_per_100g * factor, 1)
            fat = round(cat.fat_per_100g * factor, 1)
            db.add(
                MealLog(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    catalog_food_id=cat.id,
                    meal_type=meal_type,
                    ai_detected_items=[
                        {
                            "class_code": cat.class_code,
                            "confidence": 0.92,
                            "estimated_grams": round(factor * 100.0, 1),
                        }
                    ],
                    total_calories=kcal,
                    protein_g=prot,
                    carbs_g=carb,
                    fat_g=fat,
                    logged_at=datetime.combine(
                        day_date, time(12, 0), tzinfo=timezone.utc
                    ),
                )
            )
            meals_created += 1

        if is_workout_day:
            routine_obj, title, ex_items = routine_plan[(days - offset) % 3]
            start_dt = datetime.combine(day_date, time(17, 30), tzinfo=timezone.utc)
            end_dt = start_dt + timedelta(minutes=58)
            session_id = uuid.uuid4()
            session_vol = 0.0
            session_sets: list[WorkoutSet] = []

            for ex_code, base_w, base_r in ex_items:
                ex_obj = exercises[ex_code]
                w_today = round(base_w + (2.5 if offset <= 7 and base_w > 0 else 0.0), 1)
                for s_num in range(1, 4):
                    est_1rm = _epley_brzycki_1rm(w_today, base_r) if w_today > 0 else 0.0
                    session_vol += w_today * base_r
                    session_sets.append(
                        WorkoutSet(
                            id=uuid.uuid4(),
                            session_id=session_id,
                            exercise_id=ex_obj.id,
                            set_number=s_num,
                            set_type="NORMAL",
                            weight_kg=w_today,
                            reps=base_r,
                            rpe=round(rng.uniform(7.0, 8.5), 1),
                            estimated_1rm=est_1rm,
                            is_pr=(offset <= 3 and s_num == 3 and w_today > 0),
                            completed_at=start_dt + timedelta(minutes=s_num * 5),
                        )
                    )
                    sets_created += 1

            db.add(
                WorkoutSession(
                    id=session_id,
                    user_id=user.id,
                    routine_id=routine_obj.id,
                    session_title=title,
                    started_at=start_dt,
                    completed_at=end_dt,
                    duration_seconds=3480,
                    total_volume_kg=round(session_vol, 1),
                    status="COMPLETED",
                )
            )
            db.add_all(session_sets)
            sessions_created += 1

        fatigue_map = {
            m: round(rng.uniform(0.08, 0.45), 2) for m in sorted(CANONICAL_MUSCLE_MATERIALS)
        }
        readiness = round(min(95.0, max(55.0, 62.0 + (sleep_hours - 6.0) * 10.0)), 1)
        db.add(
            AIReadinessLog(
                id=uuid.uuid4(),
                user_id=user.id,
                target_date=day_date,
                readiness_score=readiness,
                readiness_level="READY" if readiness >= 75 else "MODERATE",
                muscle_fatigue_map=fatigue_map,
                weight_recommendations=[],
                feature_snapshot={
                    "sleep_hours_last_night": sleep_hours,
                    "steps_ratio_yesterday": round(steps / 8000.0, 2),
                },
                model_version="seed-banister-v1.0",
            )
        )

    await db.commit()
    return {
        "days_seeded": days,
        "sessions_created": sessions_created,
        "sets_created": sets_created,
        "meals_created": meals_created,
    }


async def main() -> None:
    async with AsyncSessionLocal() as db:
        stats = await seed_demo_history(db)
        print("Seed 30 ngay lich su hoan tat:", stats)


if __name__ == "__main__":
    asyncio.run(main())
