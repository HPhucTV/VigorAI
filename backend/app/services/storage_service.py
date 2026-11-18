# [OWNER: M3] Object Storage / CDN Service Stub (T-M3-08, T-M3-12)
class StorageService:
    """Quan ly bucket S3/MinIO cho file 3D .glb va anh mon an."""

    async def delete_user_media(self, user_id: str) -> None:
        _ = user_id
