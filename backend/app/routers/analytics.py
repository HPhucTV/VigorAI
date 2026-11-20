# [OWNER: M3] Analytics Summary Router (T-M3-11: F22, F24, F25)
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()


@router.get(
    "/summary",
    summary="Tong hop Volume Load theo tuan, Radar 6 nhom co & Bang ky luc PR (F22, F24, F25)",
)
async def get_analytics_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: Annotated[int, Query(ge=7, le=365)] = 90,
) -> dict[str, Any]:
    return await analytics_service.build_summary(db, current_user, days=days)
