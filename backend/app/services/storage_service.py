# [OWNER: M3] Object Storage / CDN Service (MinIO / S3) (T-M3-04, T-M3-08, T-M3-12)
import asyncio
import logging
from typing import Any

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Quan ly bucket S3/MinIO cho file 3D .glb va anh mon an."""

    def __init__(self) -> None:
        self._bucket = settings.S3_BUCKET_NAME
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=BotoConfig(signature_version="s3v4", connect_timeout=2, read_timeout=5),
        )

    def _delete_prefix_sync(self, prefix: str) -> int:
        deleted_count = 0
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
            contents: list[dict[str, Any]] = page.get("Contents", [])
            if not contents:
                continue
            objects = [{"Key": item["Key"]} for item in contents]
            self._client.delete_objects(
                Bucket=self._bucket,
                Delete={"Objects": objects, "Quiet": True},
            )
            deleted_count += len(objects)
        return deleted_count

    async def delete_user_media(self, user_id: str) -> int:
        """Xoa toan bo anh mon an / tai nguyen cua user tren S3/MinIO khi Cascade Delete."""
        prefix = f"users/{user_id}/"
        try:
            return await asyncio.to_thread(self._delete_prefix_sync, prefix)
        except (BotoCoreError, ClientError, OSError) as exc:
            # Trong moi truong test/offline khong co MinIO, ghi log canh bao thay vi chan xoa DB.
            logger.warning(
                "Bo qua loi ket noi Object Storage khi xoa prefix %s: %s",
                prefix,
                exc,
            )
            return 0
