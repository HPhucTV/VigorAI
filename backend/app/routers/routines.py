# [OWNER: M3] Workout Routines & Split Builder Router (T-M3-10: F14)
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.seed_catalog_and_exercises import seed_catalog_and_exercises
from app.db.session import get_db
from app.models.entities import Exercise, RoutineExercise, User, WorkoutRoutine
from app.schemas.core_schemas import MessageResponse, WorkoutRoutineUpsert

router = APIRouter()


async def _load_exercise_maps(
    db: AsyncSession,
) -> tuple[dict[str, Exercise], dict[uuid.UUID, Exercise]]:
    rows = (await db.execute(select(Exercise))).scalars().all()
    if not rows:
        await seed_catalog_and_exercises(db)
        rows = (await db.execute(select(Exercise))).scalars().all()
    by_code = {e.code.upper(): e for e in rows}
    by_id = {e.id: e for e in rows}
    return by_code, by_id


async def _serialize_routines(
    db: AsyncSession,
    routines: list[WorkoutRoutine],
    ex_by_id: dict[uuid.UUID, Exercise],
) -> list[dict[str, Any]]:
    if not routines:
        return []
    routine_ids = [r.id for r in routines]
    rx_rows = (
        await db.execute(
            select(RoutineExercise)
            .where(RoutineExercise.routine_id.in_(routine_ids))
            .order_by(RoutineExercise.order_index)
        )
    ).scalars().all()

    rx_by_routine: dict[uuid.UUID, list[dict[str, Any]]] = {}
    for rx in rx_rows:
        ex_obj = ex_by_id.get(rx.exercise_id)
        rx_by_routine.setdefault(rx.routine_id, []).append(
            {
                "id": str(rx.id),
                "routine_id": str(rx.routine_id),
                "exercise_id": str(rx.exercise_id),
                "exercise_code": ex_obj.code if ex_obj else "",
                "exercise_name_vi": ex_obj.name_vi if ex_obj else "",
                "order_index": rx.order_index,
                "superset_group_id": rx.superset_group_id,
                "target_sets": rx.target_sets,
                "target_rep_min": rx.target_rep_min,
                "target_rep_max": rx.target_rep_max,
                "default_rest_seconds": rx.default_rest_seconds,
            }
        )

    return [
        {
            "id": str(r.id),
            "user_id": str(r.user_id) if r.user_id else None,
            "name": r.name,
            "split_type": r.split_type,
            "scheduled_weekdays": r.scheduled_weekdays,
            "is_template": r.is_template,
            "exercises": rx_by_routine.get(r.id, []),
            "sync_status": "SYNCED",
            "updated_at": r.updated_at.isoformat(),
            "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
        }
        for r in routines
    ]


@router.get("", summary="Lay danh sach giao an ca nhan va 4 giao an mau he thong (F14)")
async def list_routines(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_templates: Annotated[bool, Query()] = True,
) -> dict[str, Any]:
    _, ex_by_id = await _load_exercise_maps(db)
    conditions = [WorkoutRoutine.user_id == current_user.id]
    if include_templates:
        conditions.append(
            (WorkoutRoutine.user_id.is_(None))
            & (WorkoutRoutine.is_template.is_(True))
        )

    rows = (
        await db.execute(
            select(WorkoutRoutine)
            .where(
                WorkoutRoutine.deleted_at.is_(None),
                or_(*conditions),
            )
            .order_by(WorkoutRoutine.is_template.desc(), WorkoutRoutine.updated_at.desc())
        )
    ).scalars().all()

    return {"items": await _serialize_routines(db, list(rows), ex_by_id)}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Tao giao an tap luyen tuan kem danh sach bai tap & Superset (F14)",
)
async def create_routine(
    payload: WorkoutRoutineUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    ex_by_code, ex_by_id = await _load_exercise_maps(db)
    now_utc = payload.updated_at or datetime.now(timezone.utc)
    routine = WorkoutRoutine(
        id=payload.id or uuid.uuid4(),
        user_id=current_user.id,
        name=payload.name.strip(),
        split_type=payload.split_type.strip().upper(),
        scheduled_weekdays=payload.scheduled_weekdays,
        is_template=False,
        updated_at=now_utc,
        deleted_at=payload.deleted_at,
    )
    db.add(routine)
    await db.flush()

    for idx, item in enumerate(payload.exercises):
        ex_obj = None
        if item.exercise_id and item.exercise_id in ex_by_id:
            ex_obj = ex_by_id[item.exercise_id]
        elif item.exercise_code:
            ex_obj = ex_by_code.get(item.exercise_code.strip().upper())
        if ex_obj is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bai tap khong ton tai: {item.exercise_code or item.exercise_id}",
            )
        db.add(
            RoutineExercise(
                id=item.id or uuid.uuid4(),
                routine_id=routine.id,
                exercise_id=ex_obj.id,
                order_index=item.order_index if item.order_index > 0 else idx,
                superset_group_id=item.superset_group_id,
                target_sets=item.target_sets,
                target_rep_min=item.target_rep_min,
                target_rep_max=item.target_rep_max,
                default_rest_seconds=item.default_rest_seconds,
            )
        )

    await db.commit()
    await db.refresh(routine)
    serialized = await _serialize_routines(db, [routine], ex_by_id)
    return serialized[0]


@router.put(
    "/{routine_id}",
    summary="Cap nhat giao an va thu tu bai tap / Superset (F14)",
)
async def update_routine(
    routine_id: uuid.UUID,
    payload: WorkoutRoutineUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    ex_by_code, ex_by_id = await _load_exercise_maps(db)
    routine = (
        await db.execute(
            select(WorkoutRoutine).where(
                WorkoutRoutine.id == routine_id,
                WorkoutRoutine.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if routine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay giao an cua nguoi dung.",
        )

    now_utc = payload.updated_at or datetime.now(timezone.utc)
    routine.name = payload.name.strip()
    routine.split_type = payload.split_type.strip().upper()
    routine.scheduled_weekdays = payload.scheduled_weekdays
    routine.updated_at = now_utc
    routine.deleted_at = payload.deleted_at

    old_links = (
        await db.execute(
            select(RoutineExercise).where(RoutineExercise.routine_id == routine.id)
        )
    ).scalars().all()
    for link in old_links:
        await db.delete(link)
    await db.flush()

    for idx, item in enumerate(payload.exercises):
        ex_obj = None
        if item.exercise_id and item.exercise_id in ex_by_id:
            ex_obj = ex_by_id[item.exercise_id]
        elif item.exercise_code:
            ex_obj = ex_by_code.get(item.exercise_code.strip().upper())
        if ex_obj is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bai tap khong ton tai: {item.exercise_code or item.exercise_id}",
            )
        db.add(
            RoutineExercise(
                id=item.id or uuid.uuid4(),
                routine_id=routine.id,
                exercise_id=ex_obj.id,
                order_index=item.order_index if item.order_index > 0 else idx,
                superset_group_id=item.superset_group_id,
                target_sets=item.target_sets,
                target_rep_min=item.target_rep_min,
                target_rep_max=item.target_rep_max,
                default_rest_seconds=item.default_rest_seconds,
            )
        )

    await db.commit()
    await db.refresh(routine)
    serialized = await _serialize_routines(db, [routine], ex_by_id)
    return serialized[0]


@router.delete(
    "/{routine_id}",
    response_model=MessageResponse,
    summary="Xoa mem giao an ca nhan (F14)",
)
async def delete_routine(
    routine_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    routine = (
        await db.execute(
            select(WorkoutRoutine).where(
                WorkoutRoutine.id == routine_id,
                WorkoutRoutine.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if routine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay giao an cua nguoi dung.",
        )

    now_utc = datetime.now(timezone.utc)
    routine.deleted_at = now_utc
    routine.updated_at = now_utc
    await db.commit()
    return MessageResponse(status="deleted", message="Da xoa giao an tap luyen.")
