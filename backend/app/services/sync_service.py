# [OWNER: M3] Offline-First LWW Sync Service Stub (T-M3-06)
class SyncService:
    """Dong bo hai chieu theo quy tac Last-Write-Wins (UTC updated_at)."""

    async def apply_push_batch(self, user_id: str, payload: dict) -> dict:
        _ = (user_id, payload)
        return {"synced_ids": []}
