# [OWNER: M3] Analytics Aggregation Service Stub (T-M3-10)
class AnalyticsService:
    """Tong hop Volume Load, 6 truc Radar nhom co va ky luc PR."""

    async def build_summary(self, user_id: str) -> dict:
        _ = user_id
        return {"weekly_volume": [], "muscle_radar": {}, "personal_records": []}
