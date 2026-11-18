# [OWNER: M3] Offline-First Two-Way Sync Router (T-M3-06)
from fastapi import APIRouter

router = APIRouter()


@router.post("/push")
async def push_sync_batch() -> dict[str, str]:
    return {"status": "ok", "message": "Sync push stub (T-M3-06)"}


@router.get("/pull")
async def pull_sync_updates(since: str | None = None) -> dict:
    return {"since": since, "records": {}}
