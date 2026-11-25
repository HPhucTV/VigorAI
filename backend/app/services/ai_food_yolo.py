# [OWNER: M4] AI Model B Service - YOLOv8 Food Detection & Macro Estimator (T-M4-04, T-M4-06)
"""Nhan dien mon an tu anh, quy doi bbox -> gram -> Calo/Macro (tra `food_nutrition_catalog`).

Phan tinh toan (quy doi gram, dinh duong, tong) la ham thuan, khong can ultralytics/PIL de import
hoac test. Phan suy luan (`FoodYoloService`) chi nap thu vien nang khi that su co anh can xu ly.

Bien moi truong (deu tuy chon):
    VIGOR_FOOD_MODEL_PATH     duong dan weights (.pt hoac .onnx); mac dinh ai_models/weights/food_yolo_v1.pt
    VIGOR_FOOD_MODEL_VERSION  chuoi phien ban tra ve cho client; mac dinh = ten file weights
    VIGOR_FOOD_CONF           nguong tin cay toi thieu, mac dinh 0.30
    VIGOR_FOOD_IOU            nguong NMS, mac dinh 0.50
    VIGOR_FOOD_IMGSZ          kich thuoc anh suy luan, mac dinh 640
    VIGOR_FOOD_DEVICE         cpu (mac dinh) | 0 (GPU)
"""
from __future__ import annotations

import io
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Quy doi khau phan: gram = default_serving_g * clamp(area_ratio / REF_AREA_RATIO, 0.4, 2.5)
MIN_SCALE = 0.4
MAX_SCALE = 2.5
REF_AREA_RATIO = 0.25
MAX_ITEMS = 20
MIN_BOX_SIDE = 0.01  # bo bbox qua nho (< 1% canh anh), thuong la nhieu

DISCLAIMER = (
    "Giá trị dinh dưỡng được AI ước tính dựa trên hình ảnh, "
    "vui lòng kiểm tra lại khẩu phần gram trước khi lưu."
)
EMPTY_DISCLAIMER = (
    "Chưa nhận diện được món ăn nào trong ảnh. Hãy chụp gần hơn, đủ sáng, "
    "hoặc thêm món thủ công."
)

DEFAULT_WEIGHTS_DIR = Path(__file__).resolve().parents[2] / "ai_models" / "weights"
DEFAULT_WEIGHT_FILES = ("food_yolo_v1.pt", "food_yolo_v1.onnx")


class FoodModelUnavailable(RuntimeError):
    """Chua co file trong so (hoac khong nap duoc)."""


class InvalidImageError(ValueError):
    """Du lieu tai len khong phai anh doc duoc."""


@dataclass(frozen=True)
class Detection:
    class_code: str
    confidence: float
    bbox_norm: tuple[float, float, float, float]  # x1, y1, x2, y2 trong [0, 1]


# --------------------------------------------------------------------------- #
# Ham thuan: quy doi gram & dinh duong (T-M4-04)
# --------------------------------------------------------------------------- #
def clamp_bbox(bbox: list[float] | tuple[float, ...]) -> tuple[float, float, float, float] | None:
    """Cat bbox ve [0, 1], doi cho neu nguoc; tra None neu suy bien hoac qua nho."""
    x1, y1, x2, y2 = (float(v) for v in bbox)
    x1, x2 = sorted((min(max(x1, 0.0), 1.0), min(max(x2, 0.0), 1.0)))
    y1, y2 = sorted((min(max(y1, 0.0), 1.0), min(max(y2, 0.0), 1.0)))
    if (x2 - x1) < MIN_BOX_SIDE or (y2 - y1) < MIN_BOX_SIDE:
        return None
    return (x1, y1, x2, y2)


def bbox_area_ratio(bbox: list[float] | tuple[float, ...]) -> float:
    x1, y1, x2, y2 = bbox
    return max(0.0, (x2 - x1) * (y2 - y1))


def estimate_portion_grams(
    default_serving_g: float,
    area_ratio: float,
    ref_area_ratio: float = REF_AREA_RATIO,
) -> float:
    scale = max(MIN_SCALE, min(MAX_SCALE, area_ratio / max(ref_area_ratio, 1e-6)))
    return round(default_serving_g * scale, 1)


def compute_item_nutrition(entry: dict[str, Any], grams: float) -> dict[str, float]:
    factor = grams / 100.0
    return {
        "calories": round(float(entry["kcal_per_100g"]) * factor, 1),
        "protein_g": round(float(entry["protein_per_100g"]) * factor, 1),
        "carbs_g": round(float(entry["carbs_per_100g"]) * factor, 1),
        "fat_g": round(float(entry["fat_per_100g"]) * factor, 1),
    }


def build_items(
    detections: list[Detection],
    catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Moi Detection -> 1 DetectedFoodItem (dict). Bo qua lop khong co trong catalog."""
    items: list[dict[str, Any]] = []
    for det in sorted(detections, key=lambda d: d.confidence, reverse=True):
        entry = catalog.get(det.class_code)
        box = clamp_bbox(det.bbox_norm)
        if entry is None or box is None:
            continue
        grams = estimate_portion_grams(float(entry["default_serving_g"]), bbox_area_ratio(box))
        items.append(
            {
                "class_code": det.class_code,
                "name_vi": entry["name_vi"],
                "confidence": round(float(det.confidence), 3),
                "bbox_norm": [round(v, 4) for v in box],
                "estimated_grams": grams,
                **compute_item_nutrition(entry, grams),
            }
        )
        if len(items) >= MAX_ITEMS:
            break
    return items


def summarize(items: list[dict[str, Any]]) -> dict[str, float]:
    """Tong = tong cac gia tri da lam tron cua tung mon, de man hinh cong lai khop tung dong."""
    return {
        key: round(sum(item[key] for item in items), 1)
        for key in ("calories", "protein_g", "carbs_g", "fat_g")
    }


def build_response_payload(
    detections: list[Detection],
    catalog: dict[str, dict[str, Any]],
    inference_ms: int,
    model_version: str,
) -> dict[str, Any]:
    """Dict khop `FoodAnalyzeResponse` (app/schemas/ai_schema.py)."""
    items = build_items(detections, catalog)
    return {
        "inference_time_ms": int(inference_ms),
        "model_version": model_version,
        "detected_items": items,
        "total_nutrition": summarize(items),
        "disclaimer": DISCLAIMER if items else EMPTY_DISCLAIMER,
    }


# --------------------------------------------------------------------------- #
# Suy luan YOLOv8
# --------------------------------------------------------------------------- #
def decode_image(data: bytes):
    """Bytes -> anh PIL RGB, xoay dung chieu theo EXIF (anh chup bang dien thoai)."""
    from PIL import Image, ImageOps

    try:
        with Image.open(io.BytesIO(data)) as raw:
            raw.load()
            return ImageOps.exif_transpose(raw).convert("RGB")
    except Exception as exc:  # PIL nem nhieu loai loi khac nhau
        raise InvalidImageError("Không đọc được ảnh tải lên.") from exc


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


class FoodYoloService:
    """Nap trong so YOLOv8 va suy luan mon an. Khong nap model cho toi khi co yeu cau dau tien."""

    def __init__(self, model_path: str | os.PathLike[str] | None = None) -> None:
        self._explicit_path = model_path
        self._model: Any = None
        self._lock = threading.Lock()
        self.conf = _env_float("VIGOR_FOOD_CONF", 0.30)
        self.iou = _env_float("VIGOR_FOOD_IOU", 0.50)
        self.imgsz = int(_env_float("VIGOR_FOOD_IMGSZ", 640))
        self.device = os.environ.get("VIGOR_FOOD_DEVICE", "cpu")

    # ----- duong dan & phien ban ----- #
    @property
    def model_path(self) -> Path | None:
        explicit = self._explicit_path or os.environ.get("VIGOR_FOOD_MODEL_PATH")
        if explicit:
            path = Path(explicit)
            return path if path.is_file() else None
        for name in DEFAULT_WEIGHT_FILES:
            candidate = DEFAULT_WEIGHTS_DIR / name
            if candidate.is_file():
                return candidate
        return None

    @property
    def available(self) -> bool:
        return self.model_path is not None

    @property
    def model_version(self) -> str:
        override = os.environ.get("VIGOR_FOOD_MODEL_VERSION")
        if override:
            return override
        path = self.model_path
        return path.stem if path else "unavailable"

    # ----- suy luan ----- #
    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        path = self.model_path
        if path is None:
            raise FoodModelUnavailable("Chưa có file trọng số Model B.")
        try:
            from ultralytics import YOLO

            self._model = YOLO(str(path))
        except Exception as exc:
            raise FoodModelUnavailable(f"Không nạp được model: {exc}") from exc
        return self._model

    def detect(self, image) -> list[Detection]:
        model = self._load()
        with self._lock:  # predictor cua ultralytics khong an toan khi goi dong thoi
            result = model.predict(
                source=image,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz,
                device=self.device,
                verbose=False,
            )[0]
        names = result.names
        detections: list[Detection] = []
        for box in result.boxes:
            class_code = str(names[int(box.cls[0])])
            x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0].tolist())
            detections.append(Detection(class_code, float(box.conf[0]), (x1, y1, x2, y2)))
        return detections

    def analyze(self, image_bytes: bytes, catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Bytes anh -> payload `FoodAnalyzeResponse`. Ham dong bo, goi qua threadpool."""
        image = decode_image(image_bytes)
        started = time.perf_counter()
        detections = self.detect(image)
        inference_ms = int(round((time.perf_counter() - started) * 1000))
        return build_response_payload(detections, catalog, inference_ms, self.model_version)

    # Giu tuong thich voi ban stub cu
    @staticmethod
    def estimate_portion_grams(
        default_serving_g: float,
        bbox_area_ratio: float,
        ref_area_ratio: float = REF_AREA_RATIO,
    ) -> float:
        return estimate_portion_grams(default_serving_g, bbox_area_ratio, ref_area_ratio)


_service: FoodYoloService | None = None


def get_food_service() -> FoodYoloService:
    global _service
    if _service is None:
        _service = FoodYoloService()
    return _service
