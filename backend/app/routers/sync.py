# [OWNER: M3] Offline-First Two-Way Sync Router (T-M3-07)
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.core_schemas import SyncPushRequest, SyncPushResponse
from app.services.sync_service import SyncService

router = APIRouter()
sync_service = SyncService()


@router.post(
    "/push",
    response_model=SyncPushResponse,
    summary="Dong bo day lo du lieu Offline-First len PostgreSQL theo LWW & max(steps_count)",
)
async def push_sync_batch(
    payload: SyncPushRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SyncPushResponse:
    result = await sync_service.apply_push_batch(db, current_user, payload)
    return SyncPushResponse(**result)


@router.get(
    "/pull",
    summary="Keo toan bo ban ghi thay doi tu moc since (UTC ISO-8601)",
)
async def pull_sync_updates(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    since: Annotated[str | None, Query(description="Moc thoi gian UTC ISO-8601")] = None,
) -> dict[str, Any]:
    return await sync_service.pull_updates(db, current_user, since=since)
