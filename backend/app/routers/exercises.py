# [OWNER: M3] 3D Exercises, Alternatives & CDN Metadata Router (T-M3-09: F07-F12, F25)
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.seed_catalog_and_exercises import EXERCISES_SEED, seed_catalog_and_exercises
from app.db.session import get_db
from app.models.entities import Exercise
from app.services.storage_service import StorageService

router = APIRouter()
storage_service = StorageService()


def _resolve_api_base(request: Request) -> str:
    if settings.resolved_api_public_base_url:
        return settings.resolved_api_public_base_url
    base = str(request.base_url).rstrip("/")
    fwd_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
    if fwd_proto == "https" and base.startswith("http://"):
        base = "https://" + base[len("http://") :]
    return base


def _serialize_exercise(ex: Exercise, api_base_url: str | None = None) -> dict[str, Any]:
    glb_meta = storage_service.resolve_exercise_glb_metadata(
        code=ex.code,
        db_url=ex.model_3d_glb_url,
        db_checksum=ex.asset_checksum,
        api_base_url=api_base_url,
    )
    return {
        "id": str(ex.id),
        "code": ex.code,
        "name_vi": ex.name_vi,
        "name_en": ex.name_en,
        "equipment_type": ex.equipment_type,
        "model_3d_glb_url": glb_meta["model_3d_glb_url"],
        "asset_checksum": glb_meta["asset_checksum"],
        "primary_muscles": ex.primary_muscles,
        "secondary_muscles": ex.secondary_muscles,
        "stabilizer_muscles": ex.stabilizer_muscles,
        "phase_keyframes": ex.phase_keyframes,
        "bad_form_warnings": ex.bad_form_warnings,
        "setup_guide": ex.setup_guide,
        "bundled": glb_meta["bundled"],
        "clips": glb_meta["clips"],
    }


async def _ensure_exercises_loaded(db: AsyncSession) -> list[Exercise]:
    rows = (
        await db.execute(select(Exercise).order_by(Exercise.code))
    ).scalars().all()
    if len(rows) < len(EXERCISES_SEED):
        await seed_catalog_and_exercises(db)
        rows = (
            await db.execute(select(Exercise).order_by(Exercise.code))
        ).scalars().all()
    return list(rows)


@router.get("", summary="Lay danh sach kho bai tap 3D kem SHA-256 & 11 Mat_Muscle_* (F07-F12)")
async def list_exercises(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    muscle: Annotated[
        str | None,
        Query(description="Loc theo ten Material co bap, VD: Mat_Muscle_Chest"),
    ] = None,
    equipment_type: Annotated[
        str | None,
        Query(description="Loc theo dung cu: BARBELL, DUMBBELL, CABLE, MACHINE, BODYWEIGHT, KETTLEBELL"),
    ] = None,
    q: Annotated[str | None, Query(description="Tu khoa tim kiem")] = None,
) -> dict[str, Any]:
    rows = await _ensure_exercises_loaded(db)
    api_base = _resolve_api_base(request)

    if muscle:
        target_muscle = muscle.strip()
        rows = [
            e
            for e in rows
            if target_muscle in (e.primary_muscles or [])
            or target_muscle in (e.secondary_muscles or [])
        ]
    if equipment_type:
        eq_upper = equipment_type.strip().upper()
        rows = [e for e in rows if e.equipment_type.upper() == eq_upper]
    if q:
        q_low = q.strip().lower()
        rows = [
            e
            for e in rows
            if q_low in e.name_vi.lower()
            or q_low in e.name_en.lower()
            or q_low in e.code.lower()
        ]

    return {"items": [_serialize_exercise(e, api_base_url=api_base) for e in rows]}


@router.get(
    "/{code}/glb",
    summary="Tai file 3D .glb cho bai tap (S3 Presigned Redirect hoac HTTPS FileResponse)",
)
async def download_exercise_glb(code: str) -> Any:
    code_upper = code.strip().upper()
    presigned = await storage_service.get_presigned_glb_url(code_upper)
    if presigned:
        return RedirectResponse(
            url=presigned,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Cache-Control": "public, max-age=300"},
        )

    local_path = storage_service.get_local_glb_path(code_upper)
    if local_path is not None:
        sha = storage_service.get_manifest_sha256(code_upper)
        headers = {"Cache-Control": "public, max-age=86400"}
        if sha:
            headers["X-Asset-Sha256"] = sha
        return FileResponse(
            path=str(local_path),
            media_type="model/gltf-binary",
            filename=f"{code_upper.lower()}.glb",
            headers=headers,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Không tìm thấy tệp 3D .glb cho bài tập '{code}'.",
    )


@router.get("/{code}", summary="Lay chi tiet 1 bai tap 3D theo ma code (F07)")
async def get_exercise_detail(
    code: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    await _ensure_exercises_loaded(db)
    ex = (
        await db.execute(
            select(Exercise).where(Exercise.code == code.strip().upper())
        )
    ).scalar_one_or_none()
    if ex is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài tập 3D với mã '{code}'.",
        )
    return _serialize_exercise(ex, api_base_url=_resolve_api_base(request))


@router.get(
    "/{code}/alternatives",
    summary="Goi y top 5 bai tap thay the cung nhom co chinh (>=80% overlap, uu tien khac dung cu) (F25)",
)
async def get_exercise_alternatives(
    code: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    all_exercises = await _ensure_exercises_loaded(db)
    api_base = _resolve_api_base(request)
    code_upper = code.strip().upper()
    target = next((e for e in all_exercises if e.code == code_upper), None)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài tập '{code}'.",
        )

    target_primary = set(target.primary_muscles or [])
    target_secondary = set(target.secondary_muscles or [])
    candidates: list[tuple[tuple[int, float, int, float], dict[str, Any]]] = []

    for cand in all_exercises:
        if cand.code == target.code:
            continue
        cand_primary = set(cand.primary_muscles or [])
        cand_secondary = set(cand.secondary_muscles or [])
        shared_primary = sorted(target_primary & cand_primary)
        if not shared_primary:
            continue

        denom = max(1, min(len(target_primary), len(cand_primary)))
        overlap_ratio = round(len(shared_primary) / denom, 2)
        secondary_overlap = len(target_secondary & (cand_primary | cand_secondary))
        diff_equipment = cand.equipment_type != target.equipment_type

        score_key = (
            1 if overlap_ratio >= 0.8 else 0,
            overlap_ratio,
            1 if diff_equipment else 0,
            float(secondary_overlap),
        )
        serialized = _serialize_exercise(cand, api_base_url=api_base)
        serialized["overlap_ratio"] = overlap_ratio
        serialized["shared_primary_muscles"] = shared_primary
        serialized["different_equipment"] = diff_equipment
        candidates.append((score_key, serialized))

    candidates.sort(key=lambda item: item[0], reverse=True)
    top_5 = [item[1] for item in candidates[:5]]
    return {
        "exercise_code": target.code,
        "primary_muscles": list(target_primary),
        "equipment_type": target.equipment_type,
        "alternatives": top_5,
    }
