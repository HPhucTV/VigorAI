# [OWNER: M3] Object Storage / CDN Service (MinIO / S3 / HTTPS Local Fallback) (T-M3-04, T-M3-09, T-M3-12)
import asyncio
import hashlib
import logging
import re
from pathlib import Path
from typing import Any

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.db.seed_catalog_and_exercises import (
    BASE_MANNEQUIN_FALLBACK,
    BUNDLED_MVP_EXERCISES,
    load_manifest_assets,
    resolve_local_glb_dir,
)

logger = logging.getLogger(__name__)
_SAFE_CODE_RE = re.compile(r"^[a-z0-9_]+$")


class StorageService:
    """Quan ly bucket S3/MinIO cho file 3D .glb va anh mon an kem SHA-256 checksum."""

    def __init__(self) -> None:
        self._bucket = settings.S3_BUCKET_NAME
        self._endpoint_url = (settings.S3_ENDPOINT_URL or "").strip()
        self._public_base = (
            settings.S3_PUBLIC_BASE_URL or "https://cdn.vigorai.app"
        ).rstrip("/")
        self._local_glb_dir = resolve_local_glb_dir()
        self._manifest_by_code = load_manifest_assets()
        self._s3_verified_keys: set[str] = set()

        boto_kwargs: dict[str, Any] = {
            "signature_version": "s3v4",
            "connect_timeout": 2,
            "read_timeout": 5,
            "retries": {"max_attempts": 1},
        }
        if settings.S3_ADDRESSING_STYLE.strip():
            boto_kwargs["s3"] = {"addressing_style": settings.S3_ADDRESSING_STYLE.strip()}

        self._client = (
            boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=BotoConfig(**boto_kwargs),
            )
            if self._endpoint_url and settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY
            else None
        )

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_manifest_sha256(self, exercise_code: str) -> str | None:
        item = self._manifest_by_code.get(exercise_code.strip().upper())
        if item is None:
            return None
        sha = item.get("sha256")
        return str(sha) if sha else None

    def get_local_glb_path(self, exercise_code: str) -> Path | None:
        """Tra ve duong dan file .glb cuc bo trong assets_3d/exported_glb/ hoac /app/assets_3d_glb/."""
        if self._local_glb_dir is None:
            return None
        slug = exercise_code.strip().lower()
        if not slug or not _SAFE_CODE_RE.match(slug):
            return None
        candidate = (self._local_glb_dir / f"{slug}.glb").resolve()
        if candidate.parent != self._local_glb_dir.resolve() or not candidate.is_file():
            return None
        return candidate

    def resolve_exercise_glb_metadata(
        self,
        code: str,
        db_url: str,
        db_checksum: str,
        api_base_url: str | None = None,
    ) -> dict[str, Any]:
        """Tra ve URL & SHA-256 that cho 3 bai MVP bundled, 28 bai CDN HTTPS va fallback mannequin."""
        upper_code = code.strip().upper()
        if upper_code in BUNDLED_MVP_EXERCISES:
            bundled_meta = BUNDLED_MVP_EXERCISES[upper_code]
            return {
                "model_3d_glb_url": bundled_meta["model_3d_glb_url"],
                "asset_checksum": bundled_meta["asset_checksum"],
                "bundled": True,
                "clips": ["Anim_GoodForm", "Anim_BadForm"],
            }

        manifest_item = self._manifest_by_code.get(upper_code)
        if manifest_item is not None:
            base = (
                settings.resolved_api_public_base_url
                or (api_base_url or "").strip().rstrip("/")
            )
            url = (
                f"{base}/api/v1/exercises/{upper_code}/glb"
                if base
                else f"{self._public_base}/exercises/{upper_code.lower()}.glb"
            )
            clips = manifest_item.get("clips") or ["Anim_GoodForm", "Anim_BadForm"]
            return {
                "model_3d_glb_url": url,
                "asset_checksum": manifest_item.get("sha256") or db_checksum,
                "bundled": False,
                "clips": list(clips),
            }

        # Cac bai tap chua co .glb rieng: dung base_mannequin.glb de tranh loi 404 tren mobile
        return {
            "model_3d_glb_url": BASE_MANNEQUIN_FALLBACK["model_3d_glb_url"],
            "asset_checksum": BASE_MANNEQUIN_FALLBACK["asset_checksum"],
            "bundled": False,
            "clips": [],
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
            CacheControl="public, max-age=31536000, immutable",
        )

    def _sync_local_glbs_sync(self) -> dict[str, int]:
        if self._client is None or self._local_glb_dir is None:
            return {"uploaded": 0, "skipped": 0, "failed": 0}

        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

        existing_keys: set[str] = set()
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix="exercises/"):
            for item in page.get("Contents", []):
                if item.get("Key"):
                    existing_keys.add(str(item["Key"]))

        uploaded = 0
        skipped = 0
        failed = 0
        for glb_file in sorted(self._local_glb_dir.glob("*.glb")):
            key = f"exercises/{glb_file.name}"
            if key in existing_keys:
                self._s3_verified_keys.add(key)
                skipped += 1
                continue
            try:
                self._client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=glb_file.read_bytes(),
                    ContentType="model/gltf-binary",
                    CacheControl="public, max-age=31536000, immutable",
                )
                self._s3_verified_keys.add(key)
                uploaded += 1
            except (BotoCoreError, ClientError, OSError) as exc:
                logger.warning("Khong the dong bo %s len S3: %s", key, exc)
                failed += 1
        return {"uploaded": uploaded, "skipped": skipped, "failed": failed}

    async def sync_local_glb_assets_to_s3(self) -> dict[str, int]:
        """Dong bo toan bo file .glb trong assets_3d_glb len S3/MinIO (idempotent)."""
        if self._client is None or self._local_glb_dir is None:
            return {"uploaded": 0, "skipped": 0, "failed": 0}
        try:
            return await asyncio.to_thread(self._sync_local_glbs_sync)
        except (BotoCoreError, ClientError, OSError) as exc:
            logger.warning("Bo qua dong bo S3 khi khoi dong: %s", exc)
            return {"uploaded": 0, "skipped": 0, "failed": 1}

    def _presign_if_present_sync(self, key: str, expires_in: int) -> str | None:
        if self._client is None:
            return None
        if key not in self._s3_verified_keys:
            try:
                self._client.head_object(Bucket=self._bucket, Key=key)
                self._s3_verified_keys.add(key)
            except (BotoCoreError, ClientError, OSError):
                return None
        return str(
            self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        )

    async def get_presigned_glb_url(
        self, exercise_code: str, expires_in: int = 3600
    ) -> str | None:
        """Sinh presigned GET URL neu object .glb da ton tai tren S3/MinIO."""
        if self._client is None:
            return None
        slug = exercise_code.strip().lower()
        if not slug or not _SAFE_CODE_RE.match(slug):
            return None
        key = f"exercises/{slug}.glb"
        try:
            return await asyncio.to_thread(
                self._presign_if_present_sync, key, expires_in
            )
        except (BotoCoreError, ClientError, OSError):
            return None

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
