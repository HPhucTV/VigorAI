# [OWNER: M3] Health & Biometrics Router (T-M3-08: F01-F06)
import uuid
from datetime import date, datetime, time, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.seed_catalog_and_exercises import seed_catalog_and_exercises
from app.db.session import get_db
from app.models.entities import (
    BiometricLog,
    DailyHealthLog,
    FoodNutritionCatalog,
    MealLog,
    SupplementSchedule,
    User,
    WorkoutSession,
    WorkoutSet,
)
from app.schemas.core_schemas import (
    BiometricLogCreate,
    DailyHealthUpsert,
    MealLogCreate,
    MessageResponse,
    SupplementScheduleCreate,
)
from app.services.sync_service import parse_iso_date, parse_iso_time

router = APIRouter()


def _classify_asian_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "UNDERWEIGHT"
    if bmi < 23.0:
        return "NORMAL"
    if bmi < 25.0:
        return "OVERWEIGHT"
    return "OBESE"


async def _compute_smart_target_water_ml(
    db: AsyncSession, user: User, target_date: date
) -> int:
    """Cong thuc nuoc thong minh (F03): 35ml * weight_kg + 500ml/750ml neu co buoi tap."""
    latest_bio = (
        await db.execute(
            select(BiometricLog)
            .where(
                BiometricLog.user_id == user.id,
                BiometricLog.deleted_at.is_(None),
            )
            .order_by(desc(BiometricLog.logged_date), desc(BiometricLog.updated_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    weight_kg = latest_bio.weight_kg if latest_bio is not None else 70.0
    base_ml = int(round(35.0 * weight_kg))

    day_start = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
    day_end = datetime.combine(target_date, time.max, tzinfo=timezone.utc)
    sessions = (
        await db.execute(
            select(WorkoutSession).where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.deleted_at.is_(None),
                WorkoutSession.started_at >= day_start,
                WorkoutSession.started_at <= day_end,
            )
        )
    ).scalars().all()

    if not sessions:
        return base_ml

    max_duration_min = max((s.duration_seconds or 0) / 60.0 for s in sessions)
    session_ids = [s.id for s in sessions]
    avg_rpe = (
        await db.execute(
            select(func.avg(WorkoutSet.rpe)).where(
                WorkoutSet.session_id.in_(session_ids)
            )
        )
    ).scalar_one_or_none() or 0.0

    bonus = 750 if (max_duration_min >= 60.0 or float(avg_rpe) >= 7.0) else 500
    return base_ml + bonus


@router.get("/biometrics", summary="Lay lich su can nang, BMI & 7-Day Moving Average (F01)")
async def list_biometrics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=365)] = 90,
) -> dict[str, Any]:
    stmt = (
        select(BiometricLog)
        .where(
            BiometricLog.user_id == current_user.id,
            BiometricLog.deleted_at.is_(None),
        )
        .order_by(desc(BiometricLog.logged_date), desc(BiometricLog.updated_at))
    )
    if start_date is not None:
        stmt = stmt.where(BiometricLog.logged_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(BiometricLog.logged_date <= end_date)
    rows = (await db.execute(stmt.limit(limit))).scalars().all()

    chronological = list(reversed(rows))
    ma_by_id: dict[uuid.UUID, float] = {}
    for idx, row in enumerate(chronological):
        window = chronological[max(0, idx - 6) : idx + 1]
        ma_by_id[row.id] = round(
            sum(w.weight_kg for w in window) / len(window), 2
        )

    return {
        "items": [
            {
                "id": str(b.id),
                "weight_kg": b.weight_kg,
                "body_fat_pct": b.body_fat_pct,
                "muscle_mass_kg": b.muscle_mass_kg,
                "bmi": b.bmi,
                "bmi_category_asian": _classify_asian_bmi(b.bmi),
                "moving_avg_7d_kg": ma_by_id.get(b.id, b.weight_kg),
                "circumferences_cm": b.circumferences_cm,
                "logged_date": b.logged_date.isoformat(),
                "sync_status": "SYNCED",
                "updated_at": b.updated_at.isoformat(),
            }
            for b in rows
        ]
    }


@router.post(
    "/biometrics",
    status_code=status.HTTP_201_CREATED,
    summary="Ghi nhan can nang, BMI WHO Chau A & 5 vong do (F01)",
)
async def create_biometric_log(
    payload: BiometricLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    log_date = payload.logged_date or now_utc.date()
    height_cm = payload.height_cm or current_user.height_cm or 170.0
    if payload.height_cm and payload.height_cm != current_user.height_cm:
        current_user.height_cm = payload.height_cm

    height_m = height_cm / 100.0
    bmi = payload.bmi if payload.bmi is not None else round(payload.weight_kg / (height_m * height_m), 1)
    rec_id = payload.id or uuid.uuid4()

    existing = (
        await db.execute(
            select(BiometricLog).where(
                BiometricLog.id == rec_id,
                BiometricLog.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()

    if existing is None:
        bio = BiometricLog(
            id=rec_id,
            user_id=current_user.id,
            weight_kg=payload.weight_kg,
            body_fat_pct=payload.body_fat_pct,
            muscle_mass_kg=payload.muscle_mass_kg,
            bmi=bmi,
            circumferences_cm=payload.circumferences_cm,
            logged_date=log_date,
            updated_at=now_utc,
            deleted_at=payload.deleted_at,
        )
        db.add(bio)
    else:
        existing.weight_kg = payload.weight_kg
        existing.body_fat_pct = payload.body_fat_pct
        existing.muscle_mass_kg = payload.muscle_mass_kg
        existing.bmi = bmi
        existing.circumferences_cm = payload.circumferences_cm
        existing.logged_date = log_date
        existing.updated_at = now_utc
        existing.deleted_at = payload.deleted_at
        bio = existing

    await db.commit()
    await db.refresh(bio)
    return {
        "id": str(bio.id),
        "weight_kg": bio.weight_kg,
        "body_fat_pct": bio.body_fat_pct,
        "muscle_mass_kg": bio.muscle_mass_kg,
        "bmi": bio.bmi,
        "bmi_category_asian": _classify_asian_bmi(bio.bmi),
        "circumferences_cm": bio.circumferences_cm,
        "logged_date": bio.logged_date.isoformat(),
        "sync_status": "SYNCED",
        "updated_at": bio.updated_at.isoformat(),
    }


@router.get(
    "/daily/{log_date}",
    summary="Lay tong hop buoc chan, nuoc uong thong minh & giac ngu trong ngay (F02, F03, F05)",
)
async def get_daily_health(
    log_date: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    parsed_date = parse_iso_date(log_date)
    row = (
        await db.execute(
            select(DailyHealthLog).where(
                DailyHealthLog.user_id == current_user.id,
                DailyHealthLog.log_date == parsed_date,
            )
        )
    ).scalar_one_or_none()

    smart_target_water = await _compute_smart_target_water_ml(
        db, current_user, parsed_date
    )

    if row is None:
        return {
            "id": f"daily-{parsed_date.isoformat()}",
            "log_date": parsed_date.isoformat(),
            "steps_count": 0,
            "target_steps": 8000,
            "distance_km": 0.0,
            "active_calories_kcal": 0,
            "water_ml": 0,
            "target_water_ml": smart_target_water,
            "sleep_hours": 0.0,
            "sleep_quality_score": None,
            "sync_status": "SYNCED",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "id": str(row.id),
        "log_date": row.log_date.isoformat(),
        "steps_count": row.steps_count,
        "target_steps": 8000,
        "distance_km": row.distance_km,
        "active_calories_kcal": row.active_calories_kcal,
        "water_ml": row.water_ml,
        "target_water_ml": max(row.target_water_ml, smart_target_water),
        "sleep_hours": row.sleep_hours,
        "sleep_quality_score": row.sleep_quality_score,
        "sync_status": "SYNCED",
        "updated_at": row.updated_at.isoformat(),
    }


@router.put(
    "/daily/{log_date}",
    summary="Cap nhat buoc chan, luong nuoc & giac ngu theo ngay (F02, F03, F05)",
)
async def upsert_daily_health(
    log_date: str,
    payload: DailyHealthUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    parsed_date = parse_iso_date(log_date)
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    smart_target_water = await _compute_smart_target_water_ml(
        db, current_user, parsed_date
    )
    target_water = payload.target_water_ml or smart_target_water
    stride_m = (current_user.height_cm or 170.0) * 0.415 / 100.0
    distance_km = (
        payload.distance_km
        if payload.distance_km > 0
        else round(payload.steps_count * stride_m / 1000.0, 2)
    )

    row = (
        await db.execute(
            select(DailyHealthLog).where(
                DailyHealthLog.user_id == current_user.id,
                DailyHealthLog.log_date == parsed_date,
            )
        )
    ).scalar_one_or_none()

    if row is None:
        row = DailyHealthLog(
            id=payload.id or uuid.uuid4(),
            user_id=current_user.id,
            log_date=parsed_date,
            steps_count=payload.steps_count,
            distance_km=distance_km,
            active_calories_kcal=payload.active_calories_kcal,
            water_ml=payload.water_ml,
            target_water_ml=target_water,
            sleep_hours=payload.sleep_hours,
            sleep_quality_score=payload.sleep_quality_score,
            updated_at=now_utc,
        )
        db.add(row)
    else:
        row.steps_count = payload.steps_count
        row.distance_km = distance_km
        row.active_calories_kcal = payload.active_calories_kcal
        row.water_ml = payload.water_ml
        row.target_water_ml = target_water
        row.sleep_hours = payload.sleep_hours
        row.sleep_quality_score = payload.sleep_quality_score
        row.updated_at = now_utc

    await db.commit()
    await db.refresh(row)
    return {
        "id": str(row.id),
        "log_date": row.log_date.isoformat(),
        "steps_count": row.steps_count,
        "target_steps": payload.target_steps,
        "distance_km": row.distance_km,
        "active_calories_kcal": row.active_calories_kcal,
        "water_ml": row.water_ml,
        "target_water_ml": row.target_water_ml,
        "sleep_hours": row.sleep_hours,
        "sleep_quality_score": row.sleep_quality_score,
        "sync_status": "SYNCED",
        "updated_at": row.updated_at.isoformat(),
    }


@router.get(
    "/catalog",
    summary="Tra cuu tu dien dinh duong VNFood / USDA (food_nutrition_catalog) (F04, F19)",
)
async def search_food_catalog(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Annotated[str | None, Query(description="Tu khoa tim kiem ten mon")] = None,
    class_code: Annotated[str | None, Query()] = None,
) -> dict[str, Any]:
    stmt = select(FoodNutritionCatalog).order_by(FoodNutritionCatalog.name_vi)
    rows = (await db.execute(stmt)).scalars().all()
    if not rows:
        await seed_catalog_and_exercises(db)
        rows = (await db.execute(stmt)).scalars().all()

    if class_code:
        code_upper = class_code.strip().upper()
        rows = [r for r in rows if r.class_code.upper() == code_upper]
    if q:
        q_lower = q.strip().lower()
        rows = [
            r
            for r in rows
            if q_lower in r.name_vi.lower()
            or q_lower in r.name_en.lower()
            or q_lower in r.class_code.lower()
        ]

    return {
        "items": [
            {
                "id": str(r.id),
                "class_code": r.class_code,
                "name_vi": r.name_vi,
                "name_en": r.name_en,
                "kcal_per_100g": r.kcal_per_100g,
                "protein_per_100g": r.protein_per_100g,
                "carbs_per_100g": r.carbs_per_100g,
                "fat_per_100g": r.fat_per_100g,
                "default_serving_g": r.default_serving_g,
                "source_standard": r.source_standard,
            }
            for r in rows
        ]
    }


@router.get("/meals", summary="Lay nhat ky bua an & Calo/Macro (F04)")
async def list_meals(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_date: Annotated[date | None, Query()] = None,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    meal_type: Annotated[str | None, Query()] = None,
) -> dict[str, Any]:
    stmt = (
        select(MealLog, FoodNutritionCatalog.name_vi)
        .outerjoin(
            FoodNutritionCatalog,
            FoodNutritionCatalog.id == MealLog.catalog_food_id,
        )
        .where(
            MealLog.user_id == current_user.id,
            MealLog.deleted_at.is_(None),
        )
        .order_by(desc(MealLog.logged_at))
    )
    if log_date is not None:
        d_start = datetime.combine(log_date, time.min, tzinfo=timezone.utc)
        d_end = datetime.combine(log_date, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(MealLog.logged_at >= d_start, MealLog.logged_at <= d_end)
    if start_date is not None:
        stmt = stmt.where(
            MealLog.logged_at
            >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )
    if end_date is not None:
        stmt = stmt.where(
            MealLog.logged_at
            <= datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        )
    if meal_type:
        stmt = stmt.where(MealLog.meal_type == meal_type.strip().upper())

    rows = (await db.execute(stmt)).all()
    items = []
    for meal, cat_name_vi in rows:
        title = cat_name_vi or "Bữa ăn dinh dưỡng"
        if not cat_name_vi and meal.ai_detected_items:
            first_item = meal.ai_detected_items[0]
            if isinstance(first_item, dict):
                title = str(
                    first_item.get("name_vi")
                    or first_item.get("class_code")
                    or title
                )
        items.append(
            {
                "id": str(meal.id),
                "catalog_food_id": str(meal.catalog_food_id)
                if meal.catalog_food_id
                else None,
                "meal_type": meal.meal_type,
                "title": title,
                "image_url": meal.image_url,
                "ai_detected_items": meal.ai_detected_items,
                "total_calories": meal.total_calories,
                "protein_g": meal.protein_g,
                "carbs_g": meal.carbs_g,
                "fat_g": meal.fat_g,
                "logged_at": meal.logged_at.isoformat(),
                "sync_status": "SYNCED",
                "updated_at": meal.updated_at.isoformat(),
            }
        )
    return {"items": items}


@router.post(
    "/meals",
    status_code=status.HTTP_201_CREATED,
    summary="Luu bua an moi (ho tro tu dong tra cuu Macro tu food_nutrition_catalog) (F04, F19)",
)
async def create_meal_log(
    payload: MealLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    logged_at = payload.logged_at or now_utc

    cat_item: FoodNutritionCatalog | None = None
    if payload.catalog_food_id is not None:
        cat_item = (
            await db.execute(
                select(FoodNutritionCatalog).where(
                    FoodNutritionCatalog.id == payload.catalog_food_id
                )
            )
        ).scalar_one_or_none()
    elif payload.class_code:
        cat_item = (
            await db.execute(
                select(FoodNutritionCatalog).where(
                    FoodNutritionCatalog.class_code == payload.class_code.strip().upper()
                )
            )
        ).scalar_one_or_none()

    grams = payload.grams or (cat_item.default_serving_g if cat_item else 100.0)
    factor = grams / 100.0

    total_calories = (
        payload.total_calories
        if payload.total_calories is not None
        else round((cat_item.kcal_per_100g if cat_item else 0.0) * factor, 1)
    )
    protein_g = (
        payload.protein_g
        if payload.protein_g is not None
        else round((cat_item.protein_per_100g if cat_item else 0.0) * factor, 1)
    )
    carbs_g = (
        payload.carbs_g
        if payload.carbs_g is not None
        else round((cat_item.carbs_per_100g if cat_item else 0.0) * factor, 1)
    )
    fat_g = (
        payload.fat_g
        if payload.fat_g is not None
        else round((cat_item.fat_per_100g if cat_item else 0.0) * factor, 1)
    )

    meal = MealLog(
        id=payload.id or uuid.uuid4(),
        user_id=current_user.id,
        catalog_food_id=cat_item.id if cat_item else payload.catalog_food_id,
        meal_type=payload.meal_type.strip().upper(),
        image_url=payload.image_url,
        ai_detected_items=payload.ai_detected_items,
        total_calories=total_calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        logged_at=logged_at,
        updated_at=now_utc,
        deleted_at=payload.deleted_at,
    )
    db.add(meal)
    await db.commit()
    await db.refresh(meal)
    return {
        "id": str(meal.id),
        "catalog_food_id": str(meal.catalog_food_id)
        if meal.catalog_food_id
        else None,
        "meal_type": meal.meal_type,
        "title": payload.title or (cat_item.name_vi if cat_item else "Bữa ăn"),
        "image_url": meal.image_url,
        "ai_detected_items": meal.ai_detected_items,
        "total_calories": meal.total_calories,
        "protein_g": meal.protein_g,
        "carbs_g": meal.carbs_g,
        "fat_g": meal.fat_g,
        "logged_at": meal.logged_at.isoformat(),
        "sync_status": "SYNCED",
        "updated_at": meal.updated_at.isoformat(),
    }


@router.get("/supplements", summary="Lay danh sach lich nhac Thuc pham bo sung (F06)")
async def list_supplements(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    rows = (
        await db.execute(
            select(SupplementSchedule)
            .where(
                SupplementSchedule.user_id == current_user.id,
                SupplementSchedule.deleted_at.is_(None),
            )
            .order_by(SupplementSchedule.reminder_time)
        )
    ).scalars().all()
    return {
        "items": [
            {
                "id": str(s.id),
                "supplement_name": s.supplement_name,
                "dosage_label": s.dosage_label,
                "reminder_time": s.reminder_time.strftime("%H:%M"),
                "workout_days_only": s.workout_days_only,
                "is_active": s.is_active,
                "taken_today": False,
                "sync_status": "SYNCED",
                "updated_at": s.updated_at.isoformat(),
            }
            for s in rows
        ]
    }


@router.post(
    "/supplements",
    status_code=status.HTTP_201_CREATED,
    summary="Tao hoac cap nhat lich nhac Thuc pham bo sung (F06)",
)
async def create_supplement(
    payload: SupplementScheduleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    rec_id = payload.id or uuid.uuid4()
    supp = SupplementSchedule(
        id=rec_id,
        user_id=current_user.id,
        supplement_name=payload.supplement_name.strip(),
        dosage_label=payload.dosage_label.strip(),
        reminder_time=parse_iso_time(payload.reminder_time),
        workout_days_only=payload.workout_days_only,
        is_active=payload.is_active,
        updated_at=now_utc,
        deleted_at=payload.deleted_at,
    )
    db.add(supp)
    await db.commit()
    await db.refresh(supp)
    return {
        "id": str(supp.id),
        "supplement_name": supp.supplement_name,
        "dosage_label": supp.dosage_label,
        "reminder_time": supp.reminder_time.strftime("%H:%M"),
        "workout_days_only": supp.workout_days_only,
        "is_active": supp.is_active,
        "taken_today": False,
        "sync_status": "SYNCED",
        "updated_at": supp.updated_at.isoformat(),
    }


@router.delete(
    "/supplements/{supplement_id}",
    response_model=MessageResponse,
    summary="Xoa mem lich nhac Thuc pham bo sung (F06)",
)
async def delete_supplement(
    supplement_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    supp = (
        await db.execute(
            select(SupplementSchedule).where(
                SupplementSchedule.id == supplement_id,
                SupplementSchedule.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if supp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy lịch nhắc thực phẩm bổ sung.",
        )
    now_utc = datetime.now(timezone.utc)
    supp.is_active = False
    supp.deleted_at = now_utc
    supp.updated_at = now_utc
    await db.commit()
    return MessageResponse(status="deleted", message="Đã xóa lịch nhắc thực phẩm bổ sung.")
