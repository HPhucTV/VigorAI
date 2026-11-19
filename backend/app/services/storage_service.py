# [OWNER: M3] Object Storage / CDN Service (MinIO / S3) (T-M3-04, T-M3-09, T-M3-12)
import asyncio
import hashlib
import logging
from typing import Any

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.db.seed_catalog_and_exercises import BUNDLED_MVP_EXERCISES

logger = logging.getLogger(__name__)


class StorageService:
    """Quan ly bucket S3/MinIO cho file 3D .glb va anh mon an kem SHA-256 checksum."""

    def __init__(self) -> None:
        self._bucket = settings.S3_BUCKET_NAME
        self._endpoint_url = (settings.S3_ENDPOINT_URL or "").strip()
        self._public_base = (
            settings.S3_PUBLIC_BASE_URL or "https://cdn.vigorai.app"
        ).rstrip("/")
        self._client = (
            boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=BotoConfig(
                    signature_version="s3v4",
                    connect_timeout=2,
                    read_timeout=5,
                    retries={"max_attempts": 1},
                ),
            )
            if self._endpoint_url
            else None
        )

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def resolve_exercise_glb_metadata(
        self, code: str, db_url: str, db_checksum: str
    ) -> dict[str, Any]:
        """Dam bao 3 bai tap bundled MVP luon tra ve duong dan assets/3d_bundled/ va SHA-256 that."""
        upper_code = code.upper()
        if upper_code in BUNDLED_MVP_EXERCISES:
            bundled_meta = BUNDLED_MVP_EXERCISES[upper_code]
            return {
                "model_3d_glb_url": bundled_meta["model_3d_glb_url"],
                "asset_checksum": bundled_meta["asset_checksum"],
                "bundled": True,
                "clips": ["Anim_GoodForm", "Anim_BadForm"],
            }

        is_bundled = db_url.startswith("assets/")
        url = (
            db_url
            if is_bundled
            else f"{self._public_base}/exercises/{upper_code.lower()}.glb"
        )
        return {
            "model_3d_glb_url": url,
            "asset_checksum": db_checksum,
            "bundled": is_bundled,
            "clips": ["Anim_GoodForm", "Anim_BadForm"]
            if is_bundled
            else ["Anim_GoodForm"],
        }

    def _upload_bytes_sync(
        self, object_key: str, data: bytes, content_type: str
    ) -> None:
        if self._client is None:
            return
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)
        self._client.put_object(
            Bucket=self._bucket,
            Key=object_key,
            Body=data,
            ContentType=content_type,
        )

    async def upload_glb_asset(self, exercise_code: str, data: bytes) -> dict[str, str]:
        """Upload file .glb nen Draco len bucket S3/MinIO va tra ve URL + SHA-256 checksum."""
        slug = exercise_code.strip().lower()
        object_key = f"exercises/{slug}.glb"
        checksum = self.compute_sha256(data)
        if self._client is not None:
            try:
                await asyncio.to_thread(
                    self._upload_bytes_sync,
                    object_key,
                    data,
                    "model/gltf-binary",
                )
            except (BotoCoreError, ClientError, OSError) as exc:
                logger.warning("Khong the upload .glb len MinIO/S3 (%s): %s", object_key, exc)

        return {
            "object_key": object_key,
            "model_3d_glb_url": f"{self._public_base}/{object_key}",
            "asset_checksum": checksum,
        }

    def _delete_prefix_sync(self, prefix: str) -> int:
        if self._client is None:
            return 0
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
        if self._client is None:
            return 0
        prefix = f"users/{user_id}/"
        try:
            return await asyncio.to_thread(self._delete_prefix_sync, prefix)
        except (BotoCoreError, ClientError, OSError) as exc:
            logger.warning(
                "Bo qua loi ket noi Object Storage khi xoa prefix %s: %s",
                prefix,
                exc,
            )
            return 0
