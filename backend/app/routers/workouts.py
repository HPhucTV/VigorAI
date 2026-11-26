# [OWNER: M3] Workout Sessions, 1RM (Epley/Brzycki) & PR Detection Router (T-M3-10: F15-F18, F25)
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
    DailyHealthLog,
    Exercise,
    User,
    WorkoutSession,
    WorkoutSet,
)
from app.schemas.core_schemas import WorkoutSessionCreate
from app.services.sync_service import calculate_1rm_epley_brzycki

router = APIRouter()


async def _load_exercises_lookup(
    db: AsyncSession,
) -> tuple[dict[str, Exercise], dict[uuid.UUID, Exercise]]:
    rows = (await db.execute(select(Exercise))).scalars().all()
    if not rows:
        await seed_catalog_and_exercises(db)
        rows = (await db.execute(select(Exercise))).scalars().all()
    return {e.code.upper(): e for e in rows}, {e.id: e for e in rows}


async def _serialize_sessions(
    db: AsyncSession,
    sessions: list[WorkoutSession],
    ex_by_id: dict[uuid.UUID, Exercise],
) -> list[dict[str, Any]]:
    if not sessions:
        return []
    session_ids = [s.id for s in sessions]
    set_rows = (
        await db.execute(
            select(WorkoutSet)
            .where(WorkoutSet.session_id.in_(session_ids))
            .order_by(WorkoutSet.set_number)
        )
    ).scalars().all()

    sets_by_session: dict[uuid.UUID, list[dict[str, Any]]] = {}
    for wset in set_rows:
        ex_obj = ex_by_id.get(wset.exercise_id)
        sets_by_session.setdefault(wset.session_id, []).append(
            {
                "id": str(wset.id),
                "session_id": str(wset.session_id),
                "exercise_id": str(wset.exercise_id),
                "exercise_code": ex_obj.code if ex_obj else "",
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
        )

    return [
        {
            "id": str(s.id),
            "user_id": str(s.user_id),
            "routine_id": str(s.routine_id) if s.routine_id else None,
            "session_title": s.session_title,
            "started_at": s.started_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "duration_seconds": s.duration_seconds,
            "total_volume_kg": s.total_volume_kg,
            "status": s.status,
            "sets": sets_by_session.get(s.id, []),
            "sync_status": "SYNCED",
            "updated_at": s.updated_at.isoformat(),
            "deleted_at": s.deleted_at.isoformat() if s.deleted_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions", summary="Lay lich su cac buoi tap Gym kem hiep tap & 1RM/PR (F15, F17)")
async def list_workout_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    _, ex_by_id = await _load_exercises_lookup(db)
    stmt = (
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.deleted_at.is_(None),
        )
        .order_by(desc(WorkoutSession.started_at))
    )
    if start_date is not None:
        stmt = stmt.where(
            WorkoutSession.started_at
            >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )
    if end_date is not None:
        stmt = stmt.where(
            WorkoutSession.started_at
            <= datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        )

    rows = (await db.execute(stmt.limit(limit))).scalars().all()
    return {"items": await _serialize_sessions(db, list(rows), ex_by_id)}


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="Ghi nhan buoi tap, tu dong tinh total_volume_kg, 1RM (Epley/Brzycki) & ky luc PR (F15, F17, F25)",
)
async def create_workout_session(
    payload: WorkoutSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    ex_by_code, ex_by_id = await _load_exercises_lookup(db)
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    started_at = payload.started_at or now_utc
    completed_at = payload.completed_at or (
        now_utc if payload.status.upper() == "COMPLETED" else None
    )
    session_id = payload.id or uuid.uuid4()

    hist_rows = (
        await db.execute(
            select(WorkoutSet.exercise_id, func.max(WorkoutSet.estimated_1rm))
            .join(WorkoutSession, WorkoutSession.id == WorkoutSet.session_id)
            .where(
                WorkoutSession.user_id == current_user.id,
                WorkoutSession.deleted_at.is_(None),
                WorkoutSession.id != session_id,
                WorkoutSet.set_type != "WARMUP",
            )
            .group_by(WorkoutSet.exercise_id)
        )
    ).all()
    running_best_1rm: dict[uuid.UUID, float] = {
        ex_id: float(max_1rm or 0.0) for ex_id, max_1rm in hist_rows
    }

    existing_session = (
        await db.execute(
            select(WorkoutSession).where(
                WorkoutSession.id == session_id,
                WorkoutSession.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()

    if existing_session is not None:
        old_sets = (
            await db.execute(
                select(WorkoutSet).where(WorkoutSet.session_id == session_id)
            )
        ).scalars().all()
        for old_set in old_sets:
            await db.delete(old_set)
        await db.flush()
        session = existing_session
        session.routine_id = payload.routine_id
        session.session_title = payload.session_title.strip()
        session.started_at = started_at
        session.completed_at = completed_at
        session.duration_seconds = payload.duration_seconds
        session.status = payload.status.strip().upper()
        session.updated_at = now_utc
        session.deleted_at = payload.deleted_at
    else:
        session = WorkoutSession(
            id=session_id,
            user_id=current_user.id,
            routine_id=payload.routine_id,
            session_title=payload.session_title.strip(),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=payload.duration_seconds,
            total_volume_kg=0.0,
            status=payload.status.strip().upper(),
            updated_at=now_utc,
            deleted_at=payload.deleted_at,
        )
        db.add(session)
        await db.flush()

    total_volume_kg = 0.0
    rpe_values: list[float] = []

    for idx, set_in in enumerate(payload.sets, start=1):
        ex_obj = None
        if set_in.exercise_id and set_in.exercise_id in ex_by_id:
            ex_obj = ex_by_id[set_in.exercise_id]
        elif set_in.exercise_code:
            ex_obj = ex_by_code.get(set_in.exercise_code.strip().upper())
        if ex_obj is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bài tập trong hiệp {idx} không tồn tại: {set_in.exercise_code or set_in.exercise_id}",
            )

        set_type = set_in.set_type.strip().upper()
        est_1rm = calculate_1rm_epley_brzycki(set_in.weight_kg, set_in.reps)
        prev_best = running_best_1rm.get(ex_obj.id, 0.0)
        is_pr = False
        if set_type != "WARMUP" and est_1rm > 0 and est_1rm > prev_best:
            is_pr = True
            running_best_1rm[ex_obj.id] = est_1rm

        if set_type != "WARMUP":
            total_volume_kg += set_in.weight_kg * set_in.reps
        if set_in.rpe is not None:
            rpe_values.append(set_in.rpe)

        db.add(
            WorkoutSet(
                id=set_in.id or uuid.uuid4(),
                session_id=session.id,
                exercise_id=ex_obj.id,
                set_number=set_in.set_number or idx,
                set_type=set_type,
                weight_kg=set_in.weight_kg,
                reps=set_in.reps,
                rpe=set_in.rpe,
                estimated_1rm=est_1rm,
                is_pr=is_pr,
                completed_at=set_in.completed_at or now_utc,
                updated_at=set_in.updated_at or now_utc,
            )
        )

    session.total_volume_kg = round(total_volume_kg, 1)

    session_date = started_at.date()
    daily_log = (
        await db.execute(
            select(DailyHealthLog).where(
                DailyHealthLog.user_id == current_user.id,
                DailyHealthLog.log_date == session_date,
            )
        )
    ).scalar_one_or_none()
    if daily_log is not None:
        avg_rpe = (sum(rpe_values) / len(rpe_values)) if rpe_values else 0.0
        duration_min = (payload.duration_seconds or 0) / 60.0
        bonus_ml = 750 if (duration_min >= 60.0 or avg_rpe >= 7.0) else 500
        if daily_log.target_water_ml < 2450 + bonus_ml:
            daily_log.target_water_ml = max(
                daily_log.target_water_ml, 2450 + bonus_ml
            )

    await db.commit()
    await db.refresh(session)
    serialized = await _serialize_sessions(db, [session], ex_by_id)
    return serialized[0]
