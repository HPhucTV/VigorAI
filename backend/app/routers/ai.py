# [OWNER: M4] AI Router (Model B Food YOLOv8 & Model C Readiness/Overload)
import logging
import os
from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed_catalog_and_exercises import FOOD_CATALOG_SEED
from app.db.session import get_db
from app.models.entities import FoodNutritionCatalog
from app.schemas.ai_schema import (
    DetectedFoodItem,
    FoodAnalyzeResponse,
    FoodModelInfoResponse,
    ReadinessAndOverloadResponse,
    TotalNutritionSummary,
    WeightRecommendation,
)
from app.services.ai_food_yolo import (
    EXTENDED_BEVERAGE_SNACK_CATALOG,
    FoodModelUnavailable,
    InvalidImageError,
    get_food_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # app gui anh < 300KB, 5MB la tran an toan
VALID_MEAL_TYPES = {"BREAKFAST", "LUNCH", "DINNER", "SNACK"}
DEFAULT_RAILWAY_AI_UPSTREAM = "https://vigorai-api-production.up.railway.app"
FORWARDED_HEADER = "X-Vigor-AI-Forwarded"
UPSTREAM_TIMEOUT_SEC = 25.0


async def load_catalog_map(db: AsyncSession | None) -> dict[str, dict]:
    """Bang tra dinh duong theo class_code: gop seed M3 + nhom nuoc uong/snack M4 + DB override."""
    catalog = {entry["class_code"]: dict(entry) for entry in FOOD_CATALOG_SEED}
    for entry in EXTENDED_BEVERAGE_SNACK_CATALOG:
        catalog.setdefault(entry["class_code"], dict(entry))
    if db is None:
        return catalog
    try:
        rows = (await db.execute(select(FoodNutritionCatalog))).scalars().all()
    except Exception:  # DB loi hoac khong co: van dung duoc ban seed
        logger.warning("Khong doc duoc food_nutrition_catalog tu DB, dung ban seed.")
        return catalog
    for row in rows:
        catalog[row.class_code] = {
            "class_code": row.class_code,
            "name_vi": row.name_vi,
            "kcal_per_100g": row.kcal_per_100g,
            "protein_per_100g": row.protein_per_100g,
            "carbs_per_100g": row.carbs_per_100g,
            "fat_per_100g": row.fat_per_100g,
            "default_serving_g": row.default_serving_g,
        }
    return catalog


def _stub_food_response() -> FoodAnalyzeResponse:
    """Du lieu gia chuan hop dong JSON, dung khi chua co trong so Model B (cho M1 test giao dien)."""
    return FoodAnalyzeResponse(
        inference_time_ms=112,
        model_version="yolov8s-gymfood-stub",
        detected_items=[
            DetectedFoodItem(
                class_code="GRILLED_CHICKEN_BREAST",
                name_vi="Ức gà áp chảo",
                confidence=0.93,
                bbox_norm=[0.18, 0.25, 0.52, 0.61],
                estimated_grams=180.0,
                calories=297.0,
                calories_min=240,
                calories_max=360,
                calories_range_label="~240 \u2013 360 kcal",
                protein_g=55.8,
                carbs_g=0.0,
                fat_g=6.5,
            ),
            DetectedFoodItem(
                class_code="WHITE_RICE",
                name_vi="Cơm trắng",
                confidence=0.91,
                bbox_norm=[0.54, 0.30, 0.88, 0.72],
                estimated_grams=150.0,
                calories=195.0,
                calories_min=150,
                calories_max=240,
                calories_range_label="~150 \u2013 240 kcal",
                protein_g=4.0,
                carbs_g=42.3,
                fat_g=0.4,
            ),
        ],
        total_nutrition=TotalNutritionSummary(
            calories=492.0,
            calories_min=390,
            calories_max=600,
            calories_range_label="~390 \u2013 600 kcal",
            protein_g=59.8,
            carbs_g=42.3,
            fat_g=6.9,
        ),
        disclaimer=(
            "Giá trị dinh dưỡng được AI ước tính dựa trên hình ảnh, "
            "vui lòng kiểm tra lại khẩu phần gram trước khi lưu."
        ),
    )


def _is_production_runtime(request: Request | None = None) -> bool:
    """Nhan biet container dang chay tren Railway Production."""
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
        return True
    if request is not None:
        host = (request.url.hostname or "").strip().lower()
        if host.endswith(".up.railway.app"):
            return True
    return False


def _stub_allowed(request: Request | None = None) -> bool:
    """Cho phep stub khi dev/test local; tren Production mac dinh tat de khong tra Com trang + Uc ga gia."""
    raw = os.environ.get("VIGOR_FOOD_ALLOW_STUB")
    if raw is not None and raw.strip() != "":
        return raw.strip().lower() not in {"0", "false", "no", "off"}
    if _is_production_runtime(request):
        return False
    return True


def _normalize_host(raw: str) -> str:
    val = (raw or "").strip().lower()
    if not val:
        return ""
    if "://" in val:
        return (urlsplit(val).hostname or "").strip().lower()
    return val.split("/", 1)[0].split(":", 1)[0].strip()


def _resolve_ai_upstream_url(request: Request | None = None) -> str:
    """Neu container hien tai chua co file .onnx cuc bo, chuyen tiep sang cum AI ONNX chung."""
    if request is not None and request.headers.get(FORWARDED_HEADER):
        return ""

    raw = os.environ.get("VIGOR_AI_UPSTREAM_URL")
    if raw is not None:
        cleaned = raw.strip().rstrip("/")
        if cleaned.lower() in {"", "0", "false", "no", "off", "none"}:
            return ""
        candidate = cleaned
    elif _is_production_runtime(request):
        candidate = DEFAULT_RAILWAY_AI_UPSTREAM
    else:
        return ""

    target_host = _normalize_host(candidate)
    if not target_host:
        return ""

    self_hosts = {
        _normalize_host(os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")),
        _normalize_host(request.url.hostname if request is not None and request.url.hostname else ""),
    }
    if target_host in self_hosts:
        return ""
    return candidate


async def _fetch_upstream_model_info(upstream_url: str) -> FoodModelInfoResponse | None:
    url = f"{upstream_url}/api/v1/ai/food-model/info"
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            resp = await http_client.get(url, headers={FORWARDED_HEADER: "1"})
        if resp.status_code == status.HTTP_200_OK:
            return FoodModelInfoResponse(**resp.json())
        logger.warning("Upstream food-model/info %s tra ma %s", url, resp.status_code)
    except Exception as exc:
        logger.warning("Khong goi duoc upstream food-model/info (%s): %s", url, exc)
    return None


async def _forward_food_analyze(
    upstream_url: str,
    data: bytes,
    filename: str,
    content_type: str,
    meal_type: str,
) -> FoodAnalyzeResponse | None:
    url = f"{upstream_url}/api/v1/ai/food-analyze"
    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT_SEC) as http_client:
            resp = await http_client.post(
                url,
                headers={FORWARDED_HEADER: "1"},
                files={"image": (filename, data, content_type)},
                data={"meal_type": meal_type},
            )
    except Exception as exc:
        logger.warning("Khong chuyen tiep duoc food-analyze sang %s: %s", url, exc)
        return None

    if resp.status_code == status.HTTP_200_OK:
        payload = resp.json()
        logger.info(
            "food-analyze upstream=%s meal=%s version=%s items=%d ms=%s",
            upstream_url,
            meal_type,
            payload.get("model_version", "unknown"),
            len(payload.get("detected_items", [])),
            payload.get("inference_time_ms", -1),
        )
        return FoodAnalyzeResponse(**payload)

    if resp.status_code in {
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    }:
        detail = "Không đọc được ảnh tải lên."
        try:
            err_body = resp.json()
            if isinstance(err_body, dict) and err_body.get("detail"):
                detail = str(err_body["detail"])
        except Exception:
            pass
        raise HTTPException(resp.status_code, detail)

    logger.warning("Upstream food-analyze %s tra ma %s", url, resp.status_code)
    return None


@router.get("/food-model/info", response_model=FoodModelInfoResponse)
async def get_food_model_info(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> FoodModelInfoResponse:
    """Thong tin trang thai & phien ban AI Model B dang nap tren Server."""
    service = get_food_service()
    if not service.available:
        upstream_url = _resolve_ai_upstream_url(request)
        if upstream_url:
            upstream_info = await _fetch_upstream_model_info(upstream_url)
            if upstream_info is not None:
                return upstream_info

    catalog = await load_catalog_map(db)
    return FoodModelInfoResponse(
        **service.info(catalog_size=len(catalog), stub_allowed=_stub_allowed(request))
    )


@router.post("/food-analyze", response_model=FoodAnalyzeResponse)
async def analyze_food_image(
    request: Request,
    image: UploadFile = File(...),
    meal_type: str = Form(default="LUNCH"),
    db: AsyncSession = Depends(get_db),
) -> FoodAnalyzeResponse:
    """Nhan dien mon an (YOLOv8 ONNX/PyTorch) -> uoc luong gram -> Calo/Macro (T-M4-04 / T-M4-06)."""
    normalized_meal = (meal_type or "LUNCH").strip().upper()
    if normalized_meal not in VALID_MEAL_TYPES:
        normalized_meal = "LUNCH"

    data = await image.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ảnh tải lên bị rỗng.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Ảnh vượt quá 5MB.")

    service = get_food_service()
    if not service.available:
        upstream_url = _resolve_ai_upstream_url(request)
        if upstream_url:
            forwarded = await _forward_food_analyze(
                upstream_url=upstream_url,
                data=data,
                filename=image.filename or "meal.jpg",
                content_type=image.content_type or "image/jpeg",
                meal_type=normalized_meal,
            )
            if forwarded is not None:
                return forwarded
        if _stub_allowed(request):
            return _stub_food_response()
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model nhận diện món ăn chưa sẵn sàng.")

    catalog = await load_catalog_map(db)
    try:
        payload = await run_in_threadpool(service.analyze, data, catalog)
    except InvalidImageError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Không đọc được ảnh tải lên.")
    except FoodModelUnavailable:
        if _stub_allowed(request):
            return _stub_food_response()
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model nhận diện món ăn chưa sẵn sàng.")

    logger.info(
        "food-analyze meal=%s backend=%s version=%s items=%d ms=%d",
        normalized_meal,
        getattr(service, "backend_name", "unknown"),
        payload["model_version"],
        len(payload["detected_items"]),
        payload["inference_time_ms"],
    )
    return FoodAnalyzeResponse(**payload)


@router.get("/readiness-and-overload", response_model=ReadinessAndOverloadResponse)
async def get_readiness_and_overload() -> ReadinessAndOverloadResponse:
    """Stub chuan hop dong JSON cho AI Model C (T-M4-03 / T-M4-11)."""
    return ReadinessAndOverloadResponse(
        target_date="2026-11-18",
        model_version="xgb-readiness-stub",
        readiness_score=78.5,
        readiness_level="READY",
        insights=[
            "Ngủ đủ 7.5 giờ và lượng đạm 3 ngày qua đạt 96% mục tiêu.",
            "Nhóm cơ Đùi trước và Mông còn dư âm mỏi nhẹ (42%) từ buổi Squat 36 giờ trước.",
        ],
        muscle_fatigue_map={
            "Mat_Muscle_Chest": 0.12,
            "Mat_Muscle_Shoulders": 0.15,
            "Mat_Muscle_Biceps": 0.08,
            "Mat_Muscle_Triceps": 0.10,
            "Mat_Muscle_Back_Lats": 0.20,
            "Mat_Muscle_Traps": 0.18,
            "Mat_Muscle_Abs_Core": 0.25,
            "Mat_Muscle_Glutes": 0.42,
            "Mat_Muscle_Quads": 0.45,
            "Mat_Muscle_Hamstrings": 0.38,
            "Mat_Muscle_Calves": 0.22,
        },
        weight_recommendations=[
            WeightRecommendation(
                exercise_code="BARBELL_BENCH_PRESS",
                action="INCREASE",
                recommended_weight_kg=72.5,
                recommended_reps="8-10",
                reason="Nhóm cơ Ngực đã hồi phục 88% và buổi trước đạt RPE 7.5.",
            ),
            WeightRecommendation(
                exercise_code="BARBELL_SQUAT",
                action="MAINTAIN",
                recommended_weight_kg=100.0,
                recommended_reps="6-8",
                reason="Cơ đùi trước còn 45% độ mỏi, giữ nguyên mức tạ để tránh quá tải khớp gối.",
            ),
        ],
        disclaimer=(
            "Gợi ý tải trọng do AI phân tích phục vụ mục đích tập luyện thể hình, "
            "hãy dừng tập ngay nếu thấy đau khớp bất thường."
        ),
    )
