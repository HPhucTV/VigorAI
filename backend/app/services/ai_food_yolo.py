# [OWNER: M4] AI Model B Service - YOLOv8 Food Detection & Macro Estimator (T-M4-04, T-M4-06)
"""Nhan dien mon an tu anh, quy doi bbox -> gram -> Calo/Macro (tra `food_nutrition_catalog`).

Ho tro 2 backend suy luan:
1. ONNX Runtime thuan (`onnxruntime` + `numpy` + `PIL`) cho file `.onnx`:
   - Khong can PyTorch/OpenCV/Ultralytics tren server Production (nhe RAM, nhanh CPU).
   - Tu doc danh sach ten lop tu metadata ONNX hoac `backend/ai_models/model_b_manifest.json`.
   - Letterbox dung chuan YOLOv8 + NMS theo lop + loc trung cheo lop (`cross_class_iou`).
2. Ultralytics (`ultralytics.YOLO`) cho file `.pt` (hoac model gia trong unit test).

Phan tinh toan thuan (quy doi gram, dinh duong, NMS, decode output) khong can onnxruntime/ultralytics
de import hay chay unit test.

Bien moi truong (deu tuy chon):
    VIGOR_FOOD_MODEL_PATH     duong dan weights (.onnx hoac .pt); uu tien manifest / weights/
    VIGOR_FOOD_MODEL_URL      URL HTTPS de tu dong tai weights neu chua co tren dia (Railway/Docker)
    VIGOR_FOOD_MODEL_SHA256   SHA-256 kiem tra toan ven khi tai tu URL
    VIGOR_FOOD_MODEL_VERSION  chuoi phien ban tra ve cho client
    VIGOR_FOOD_CONF           nguong tin cay toi thieu (mac dinh 0.30 hoac theo manifest)
    VIGOR_FOOD_IOU            nguong NMS cung lop (mac dinh 0.45 hoac theo manifest)
    VIGOR_FOOD_CROSS_IOU      nguong loai trung cheo lop (mac dinh 0.75; 0 de tat)
    VIGOR_FOOD_IMGSZ          kich thuoc anh suy luan (mac dinh 640)
    VIGOR_FOOD_DEVICE         cpu (mac dinh) | 0 (GPU cho .pt)
    VIGOR_FOOD_ORT_THREADS    so luong CPU cho ONNX Runtime (mac dinh tu dong)
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import logging
import os
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional when scientific deps omitted
    np = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Quy doi khau phan: gram = default_serving_g * clamp(area_ratio / REF_AREA_RATIO, 0.4, 2.5)
MIN_SCALE = 0.4
MAX_SCALE = 2.5
REF_AREA_RATIO = 0.25
MAX_ITEMS = 20
MIN_BOX_SIDE = 0.01  # bo bbox qua nho (< 1% canh anh), thuong la nhieu
MAX_IMAGE_PIXELS = 40_000_000  # chan decompression bomb (~40 MP)
LETTERBOX_PAD_VALUE = 114

DISCLAIMER = (
    "Lượng calo được AI ước chừng trong khoảng tham khảo từ hình ảnh "
    "(nước lọc đóng chai không đường ~0 kcal); bạn có thể kéo thanh trượt để chỉnh khẩu phần."
)
EMPTY_DISCLAIMER = (
    "Chưa nhận diện được món ăn hay đồ uống nào trong ảnh. Hãy chụp rõ hơn, đủ sáng, "
    "hoặc thêm món thủ công."
)

# Catalog bo sung cho nhom Nuoc uong & Banh snack / Do an nhanh (khop food_classes.py v1.2)
EXTENDED_BEVERAGE_SNACK_CATALOG: list[dict[str, Any]] = [
    {
        "class_code": "BOTTLED_DRINK",
        "name_vi": "Nước đóng chai / Nước giải khát",
        "kcal_per_100g": 28.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 7.0,
        "fat_per_100g": 0.0,
        "default_serving_g": 450.0,
        "kcal_spread_ratio": 0.40,
    },
    {
        "class_code": "COFFEE_MILK_TEA",
        "name_vi": "Cà phê sữa / Latte / Trà sữa",
        "kcal_per_100g": 54.0,
        "protein_per_100g": 1.8,
        "carbs_per_100g": 9.2,
        "fat_per_100g": 1.6,
        "default_serving_g": 350.0,
        "kcal_spread_ratio": 0.30,
    },
    {
        "class_code": "FRUIT_JUICE_SMOOTHIE",
        "name_vi": "Nước ép / Sinh tố trái cây",
        "kcal_per_100g": 46.0,
        "protein_per_100g": 0.6,
        "carbs_per_100g": 10.8,
        "fat_per_100g": 0.2,
        "default_serving_g": 300.0,
        "kcal_spread_ratio": 0.28,
    },
    {
        "class_code": "COOKIE_BISCUIT",
        "name_vi": "Bánh quy / Biscuit",
        "kcal_per_100g": 480.0,
        "protein_per_100g": 5.5,
        "carbs_per_100g": 64.0,
        "fat_per_100g": 22.0,
        "default_serving_g": 45.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "CAKE_MUFFIN_PASTRY",
        "name_vi": "Bánh ngọt / Bánh kem / Muffin",
        "kcal_per_100g": 345.0,
        "protein_per_100g": 5.0,
        "carbs_per_100g": 48.0,
        "fat_per_100g": 15.0,
        "default_serving_g": 90.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "DONUT_WAFFLE_PANCAKE",
        "name_vi": "Bánh Donut / Pancake / Waffle",
        "kcal_per_100g": 360.0,
        "protein_per_100g": 5.8,
        "carbs_per_100g": 47.0,
        "fat_per_100g": 16.5,
        "default_serving_g": 85.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "CROISSANT_SWEET_BREAD",
        "name_vi": "Bánh sừng bò / Bánh mì ngọt",
        "kcal_per_100g": 385.0,
        "protein_per_100g": 7.8,
        "carbs_per_100g": 46.0,
        "fat_per_100g": 18.5,
        "default_serving_g": 75.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "CHIPS_POPCORN_SNACK",
        "name_vi": "Bánh snack / Bỏng ngô / Hạt ăn vặt",
        "kcal_per_100g": 510.0,
        "protein_per_100g": 6.5,
        "carbs_per_100g": 53.0,
        "fat_per_100g": 30.0,
        "default_serving_g": 45.0,
        "kcal_spread_ratio": 0.25,
    },
    {
        "class_code": "CHOCOLATE_CANDY",
        "name_vi": "Sô-cô-la / Kẹo ngọt",
        "kcal_per_100g": 525.0,
        "protein_per_100g": 5.2,
        "carbs_per_100g": 59.0,
        "fat_per_100g": 29.0,
        "default_serving_g": 40.0,
        "kcal_spread_ratio": 0.25,
    },
    {
        "class_code": "ICE_CREAM_DESSERT",
        "name_vi": "Kem / Pudding tráng miệng",
        "kcal_per_100g": 207.0,
        "protein_per_100g": 3.5,
        "carbs_per_100g": 24.0,
        "fat_per_100g": 11.0,
        "default_serving_g": 100.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "FRENCH_FRIES",
        "name_vi": "Khoai tây chiên",
        "kcal_per_100g": 312.0,
        "protein_per_100g": 3.4,
        "carbs_per_100g": 41.0,
        "fat_per_100g": 15.0,
        "default_serving_g": 110.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BURGER_PIZZA_FASTFOOD",
        "name_vi": "Hamburger / Pizza / Đồ ăn nhanh",
        "kcal_per_100g": 266.0,
        "protein_per_100g": 12.5,
        "carbs_per_100g": 30.0,
        "fat_per_100g": 10.5,
        "default_serving_g": 180.0,
        "kcal_spread_ratio": 0.22,
    },
    # Mon Viet pho bien bo sung cho v1.3 (RAU_MUONG_XAO da co trong FOOD_CATALOG_SEED)
    {
        "class_code": "BUN_BO_HUE",
        "name_vi": "Bún bò Huế",
        "kcal_per_100g": 108.0,
        "protein_per_100g": 6.8,
        "carbs_per_100g": 13.5,
        "fat_per_100g": 3.0,
        "default_serving_g": 480.0,
        "kcal_spread_ratio": 0.20,
    },
    {
        "class_code": "COM_CHIEN",
        "name_vi": "Cơm chiên / Cơm rang",
        "kcal_per_100g": 168.0,
        "protein_per_100g": 5.8,
        "carbs_per_100g": 24.5,
        "fat_per_100g": 5.2,
        "default_serving_g": 300.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "XOI_MAN",
        "name_vi": "Xôi / Xôi mặn",
        "kcal_per_100g": 215.0,
        "protein_per_100g": 5.5,
        "carbs_per_100g": 37.0,
        "fat_per_100g": 5.0,
        "default_serving_g": 220.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "GOI_CUON_NEM",
        "name_vi": "Gỏi cuốn / Chả giò",
        "kcal_per_100g": 155.0,
        "protein_per_100g": 7.5,
        "carbs_per_100g": 20.0,
        "fat_per_100g": 5.0,
        "default_serving_g": 180.0,
        "kcal_spread_ratio": 0.25,
    },
    {
        "class_code": "BUN_DAU",
        "name_vi": "Bún đậu mắm tôm",
        "kcal_per_100g": 162.0,
        "protein_per_100g": 8.5,
        "carbs_per_100g": 18.5,
        "fat_per_100g": 6.0,
        "default_serving_g": 400.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "CHAO_THIT",
        "name_vi": "Cháo lòng / Cháo thịt",
        "kcal_per_100g": 78.0,
        "protein_per_100g": 5.2,
        "carbs_per_100g": 9.8,
        "fat_per_100g": 2.0,
        "default_serving_g": 380.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BANH_CUON",
        "name_vi": "Bánh cuốn nóng",
        "kcal_per_100g": 145.0,
        "protein_per_100g": 5.2,
        "carbs_per_100g": 22.5,
        "fat_per_100g": 3.8,
        "default_serving_g": 250.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BANH_GIO",
        "name_vi": "Bánh giò",
        "kcal_per_100g": 165.0,
        "protein_per_100g": 6.5,
        "carbs_per_100g": 21.0,
        "fat_per_100g": 6.0,
        "default_serving_g": 200.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "COM_XANH",
        "name_vi": "Cốm / Bánh cốm",
        "kcal_per_100g": 310.0,
        "protein_per_100g": 6.2,
        "carbs_per_100g": 67.0,
        "fat_per_100g": 1.8,
        "default_serving_g": 100.0,
        "kcal_spread_ratio": 0.22,
    },
    # Them 9 mon Viet bo sung cho v1.4 (CANH_CHUA_CA da co trong FOOD_CATALOG_SEED)
    {
        "class_code": "BANH_XEO",
        "name_vi": "Bánh xèo / Bánh khọt",
        "kcal_per_100g": 205.0,
        "protein_per_100g": 6.5,
        "carbs_per_100g": 24.0,
        "fat_per_100g": 9.2,
        "default_serving_g": 220.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BUN_RIEU",
        "name_vi": "Bún riêu cua",
        "kcal_per_100g": 92.0,
        "protein_per_100g": 6.0,
        "carbs_per_100g": 11.8,
        "fat_per_100g": 2.3,
        "default_serving_g": 450.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "HU_TIEU",
        "name_vi": "Hủ tiếu / Bánh canh",
        "kcal_per_100g": 96.0,
        "protein_per_100g": 6.0,
        "carbs_per_100g": 13.5,
        "fat_per_100g": 2.0,
        "default_serving_g": 450.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BANH_BAO",
        "name_vi": "Bánh bao",
        "kcal_per_100g": 245.0,
        "protein_per_100g": 8.5,
        "carbs_per_100g": 37.5,
        "fat_per_100g": 6.5,
        "default_serving_g": 140.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "BANH_CHUNG_TET",
        "name_vi": "Bánh chưng / Bánh tét",
        "kcal_per_100g": 215.0,
        "protein_per_100g": 6.2,
        "carbs_per_100g": 34.0,
        "fat_per_100g": 6.0,
        "default_serving_g": 200.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "THIT_KHO_TRUNG",
        "name_vi": "Thịt kho tàu (Thịt kho trứng)",
        "kcal_per_100g": 235.0,
        "protein_per_100g": 13.5,
        "carbs_per_100g": 4.5,
        "fat_per_100g": 18.0,
        "default_serving_g": 180.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "CA_KHO_TO",
        "name_vi": "Cá kho tộ",
        "kcal_per_100g": 175.0,
        "protein_per_100g": 19.5,
        "carbs_per_100g": 4.0,
        "fat_per_100g": 8.8,
        "default_serving_g": 150.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "MI_QUANG_XAO",
        "name_vi": "Mì Quảng / Cao lầu / Mì xào",
        "kcal_per_100g": 142.0,
        "protein_per_100g": 7.2,
        "carbs_per_100g": 19.0,
        "fat_per_100g": 4.2,
        "default_serving_g": 360.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "COM_GA_XOI_MO",
        "name_vi": "Cơm gà xối mỡ",
        "kcal_per_100g": 182.0,
        "protein_per_100g": 10.5,
        "carbs_per_100g": 22.0,
        "fat_per_100g": 5.8,
        "default_serving_g": 360.0,
        "kcal_spread_ratio": 0.22,
    },
    # 8 nhom Nuoc uong nhan hieu & bao bi cho v1.5 (50..57)
    {
        "class_code": "DRINK_COLA",
        "name_vi": "Nước ngọt Cola (Coca-Cola / Pepsi)",
        "kcal_per_100g": 42.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 10.6,
        "fat_per_100g": 0.0,
        "default_serving_g": 330.0,
        "kcal_spread_ratio": 0.20,
    },
    {
        "class_code": "DRINK_CITRUS_SODA",
        "name_vi": "Nước ngọt có gas (7Up / Sprite / Fanta / Mirinda)",
        "kcal_per_100g": 41.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 10.2,
        "fat_per_100g": 0.0,
        "default_serving_g": 330.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "DRINK_ENERGY",
        "name_vi": "Nước tăng lực (Sting / Red Bull / Monster)",
        "kcal_per_100g": 62.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 15.5,
        "fat_per_100g": 0.0,
        "default_serving_g": 330.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "DRINK_SPORTS_ISOTONIC",
        "name_vi": "Nước điện giải / Thể thao (Revive / Pocari)",
        "kcal_per_100g": 26.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 6.5,
        "fat_per_100g": 0.0,
        "default_serving_g": 500.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "DRINK_BOTTLED_TEA",
        "name_vi": "Trà đóng chai (C2 / Trà xanh 0 Độ / Tea+)",
        "kcal_per_100g": 28.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 7.0,
        "fat_per_100g": 0.0,
        "default_serving_g": 455.0,
        "kcal_spread_ratio": 0.32,
    },
    {
        "class_code": "DRINK_BOTTLED_COFFEE",
        "name_vi": "Cà phê sữa đóng chai / lon (Kirin Latte / Nescafé)",
        "kcal_per_100g": 58.0,
        "protein_per_100g": 1.6,
        "carbs_per_100g": 9.5,
        "fat_per_100g": 1.5,
        "default_serving_g": 345.0,
        "kcal_spread_ratio": 0.25,
    },
    {
        "class_code": "DRINK_MILK_CARTON",
        "name_vi": "Sữa hộp / Sữa lúa mạch (Vinamilk / TH / Milo)",
        "kcal_per_100g": 72.0,
        "protein_per_100g": 3.1,
        "carbs_per_100g": 9.5,
        "fat_per_100g": 2.5,
        "default_serving_g": 220.0,
        "kcal_spread_ratio": 0.22,
    },
    {
        "class_code": "DRINK_MINERAL_WATER",
        "name_vi": "Nước suối / Nước khoáng (Aquafina / LaVie)",
        "kcal_per_100g": 0.0,
        "protein_per_100g": 0.0,
        "carbs_per_100g": 0.0,
        "fat_per_100g": 0.0,
        "default_serving_g": 500.0,
        "kcal_spread_ratio": 0.0,
    },
    # 3 nhom do uong bo sung cho v1.6 (cac lop Gym/healthy con lai dung san FOOD_CATALOG_SEED cua M3)
    {
        "class_code": "DRINK_COCONUT_WATER",
        "name_vi": "Nước dừa (tươi / đóng hộp)",
        "kcal_per_100g": 19.0,
        "protein_per_100g": 0.7,
        "carbs_per_100g": 3.7,
        "fat_per_100g": 0.2,
        "default_serving_g": 330.0,
        "kcal_spread_ratio": 0.25,
    },
    {
        "class_code": "DRINK_YOGURT_PROBIOTIC",
        "name_vi": "Sữa chua uống men sống (Yakult / Probi / Betagen)",
        "kcal_per_100g": 68.0,
        "protein_per_100g": 1.3,
        "carbs_per_100g": 15.0,
        "fat_per_100g": 0.1,
        "default_serving_g": 130.0,
        "kcal_spread_ratio": 0.30,
    },
    {
        "class_code": "DRINK_BEER",
        "name_vi": "Bia (Heineken / Tiger / Sài Gòn)",
        "kcal_per_100g": 43.0,
        "protein_per_100g": 0.5,
        "carbs_per_100g": 3.6,
        "fat_per_100g": 0.0,
        "default_serving_g": 330.0,
        "kcal_spread_ratio": 0.20,
    },
]

AI_MODELS_DIR = Path(__file__).resolve().parents[2] / "ai_models"
DEFAULT_MANIFEST_PATH = AI_MODELS_DIR / "model_b_manifest.json"
DEFAULT_WEIGHTS_DIR = AI_MODELS_DIR / "weights"
DEFAULT_WEIGHT_FILES = ("food_yolo_v1.onnx", "food_yolo_v1.pt")


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
# Ham thuan: quy doi gram, dinh duong & NMS (T-M4-04)
# --------------------------------------------------------------------------- #
def normalize_class_code(raw: str) -> str:
    return raw.strip().upper().replace(" ", "_").replace("-", "_")


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


def bbox_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, (a[2] - a[0]) * (a[3] - a[1]))
    area_b = max(0.0, (b[2] - b[0]) * (b[3] - b[1]))
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


def suppress_cross_class_duplicates(
    detections: list[Detection],
    cross_iou_threshold: float = 0.75,
) -> list[Detection]:
    """Loai bo truong hop 2 lop khac nhau de chong cung 1 mon an (tranh cong doi Calo)."""
    if cross_iou_threshold <= 0.0 or len(detections) <= 1:
        return list(detections)
    ordered = sorted(detections, key=lambda d: d.confidence, reverse=True)
    kept: list[Detection] = []
    for det in ordered:
        duplicate = False
        for prev in kept:
            if prev.class_code != det.class_code and bbox_iou(prev.bbox_norm, det.bbox_norm) >= cross_iou_threshold:
                duplicate = True
                break
        if not duplicate:
            kept.append(det)
    return kept


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


def compute_calorie_range(calories: float, spread_ratio: float = 0.20) -> tuple[int, int, str]:
    """Quy doi muc calo diem sang khoang uoc chung (`~min - max kcal`) lam tron de doc."""
    if calories <= 0.0:
        return 0, 0, "0 kcal"
    step = 5 if calories < 120.0 else 10
    raw_min = max(0.0, calories * (1.0 - spread_ratio))
    raw_max = max(raw_min + step, calories * (1.0 + spread_ratio))
    c_min = int((raw_min // step) * step)
    c_max = int(((raw_max + step - 1e-6) // step) * step)
    if c_min == 0 and calories >= 10.0:
        c_min = step
    if c_max <= c_min:
        c_max = c_min + step
    return c_min, c_max, f"~{c_min} \u2013 {c_max} kcal"


def build_items(
    detections: list[Detection],
    catalog: dict[str, dict[str, Any]],
    cross_class_iou: float = 0.75,
) -> list[dict[str, Any]]:
    """Moi Detection -> 1 DetectedFoodItem (dict). Bo qua lop khong co trong catalog."""
    filtered = suppress_cross_class_duplicates(detections, cross_class_iou)
    items: list[dict[str, Any]] = []
    for det in sorted(filtered, key=lambda d: d.confidence, reverse=True):
        code = normalize_class_code(det.class_code)
        entry = catalog.get(code)
        box = clamp_bbox(det.bbox_norm)
        if entry is None or box is None:
            continue
        grams = estimate_portion_grams(float(entry["default_serving_g"]), bbox_area_ratio(box))
        macros = compute_item_nutrition(entry, grams)
        spread = float(entry.get("kcal_spread_ratio", 0.20))
        c_min, c_max, range_label = compute_calorie_range(macros["calories"], spread_ratio=spread)
        items.append(
            {
                "class_code": code,
                "name_vi": entry["name_vi"],
                "confidence": round(float(det.confidence), 3),
                "bbox_norm": [round(v, 4) for v in box],
                "estimated_grams": grams,
                **macros,
                "calories_min": c_min,
                "calories_max": c_max,
                "calories_range_label": range_label,
            }
        )
        if len(items) >= MAX_ITEMS:
            break
    return items


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Tong = tong cac gia tri da lam tron cua tung mon + khoang Calo uoc chung."""
    totals: dict[str, Any] = {
        key: round(sum(item[key] for item in items), 1)
        for key in ("calories", "protein_g", "carbs_g", "fat_g")
    }
    if not items or totals["calories"] <= 0.0:
        totals["calories_min"] = 0
        totals["calories_max"] = 0
        totals["calories_range_label"] = "0 kcal"
    else:
        c_min = sum(int(item.get("calories_min", round(item["calories"] * 0.8))) for item in items)
        c_max = sum(int(item.get("calories_max", round(item["calories"] * 1.2))) for item in items)
        totals["calories_min"] = c_min
        totals["calories_max"] = c_max
        totals["calories_range_label"] = f"~{c_min} \u2013 {c_max} kcal"
    return totals


def build_response_payload(
    detections: list[Detection],
    catalog: dict[str, dict[str, Any]],
    inference_ms: int,
    model_version: str,
    cross_class_iou: float = 0.75,
) -> dict[str, Any]:
    """Dict khop `FoodAnalyzeResponse` (app/schemas/ai_schema.py)."""
    items = build_items(detections, catalog, cross_class_iou=cross_class_iou)
    return {
        "inference_time_ms": int(inference_ms),
        "model_version": model_version,
        "detected_items": items,
        "total_nutrition": summarize(items),
        "disclaimer": DISCLAIMER if items else EMPTY_DISCLAIMER,
    }


# --------------------------------------------------------------------------- #
# Tien xu ly & Hau xu ly ONNX YOLOv8 (khong phu thuoc PyTorch / OpenCV)
# --------------------------------------------------------------------------- #
def decode_image(data: bytes):
    """Bytes -> anh PIL RGB, xoay dung chieu theo EXIF (anh chup bang dien thoai)."""
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise FoodModelUnavailable("Thiếu thư viện Pillow để giải mã ảnh.") from exc

    try:
        with Image.open(io.BytesIO(data)) as raw:
            w, h = raw.size
            if w <= 0 or h <= 0 or (w * h) > MAX_IMAGE_PIXELS:
                raise InvalidImageError("Kích thước ảnh không hợp lệ.")
            raw.load()
            return ImageOps.exif_transpose(raw).convert("RGB")
    except InvalidImageError:
        raise
    except Exception as exc:
        raise InvalidImageError("Không đọc được ảnh tải lên.") from exc


def letterbox_image(image, target_size: int = 640) -> tuple[np.ndarray, float, int, int, int, int]:
    """Resize giu ty le + dem vien xam 114 dung chuan YOLOv8 -> tensor float32 (1, 3, H, W)."""
    if np is None:
        raise FoodModelUnavailable("Thiếu thư viện NumPy để tiền xử lý ảnh.")
    try:
        from PIL import Image
    except ImportError as exc:
        raise FoodModelUnavailable("Thiếu thư viện Pillow để giải mã ảnh.") from exc

    orig_w, orig_h = image.size
    scale = min(target_size / float(orig_w), target_size / float(orig_h))
    new_w = max(1, int(round(orig_w * scale)))
    new_h = max(1, int(round(orig_h * scale)))

    if (new_w, new_h) != (orig_w, orig_h):
        resized = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        resized = image

    pad_x = (target_size - new_w) / 2.0
    pad_y = (target_size - new_h) / 2.0
    left = int(round(pad_x - 0.1))
    top = int(round(pad_y - 0.1))

    canvas = np.full((target_size, target_size, 3), LETTERBOX_PAD_VALUE, dtype=np.uint8)
    canvas[top : top + new_h, left : left + new_w] = np.asarray(resized, dtype=np.uint8)
    blob = np.ascontiguousarray(canvas.transpose(2, 0, 1), dtype=np.float32) * (1.0 / 255.0)
    return blob[None, ...], scale, left, top, orig_w, orig_h


def _nms_numpy(boxes_xyxy: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    """Greedy Non-Maximum Suppression thuan NumPy."""
    if boxes_xyxy.size == 0:
        return []
    x1 = boxes_xyxy[:, 0]
    y1 = boxes_xyxy[:, 1]
    x2 = boxes_xyxy[:, 2]
    y2 = boxes_xyxy[:, 3]
    areas = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    order = scores.argsort()[::-1]

    keep: list[int] = []
    while order.size > 0:
        idx = int(order[0])
        keep.append(idx)
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(x1[idx], x1[rest])
        yy1 = np.maximum(y1[idx], y1[rest])
        xx2 = np.minimum(x2[idx], x2[rest])
        yy2 = np.minimum(y2[idx], y2[rest])
        inter = np.maximum(0.0, xx2 - xx1) * np.maximum(0.0, yy2 - yy1)
        union = areas[idx] + areas[rest] - inter
        ious = np.where(union > 0.0, inter / union, 0.0)
        order = rest[ious <= iou_threshold]
    return keep


def parse_onnx_names(raw_meta: str | None, fallback_classes: list[str]) -> dict[int, str]:
    """Doc bang anh xa {idx: class_code} tu custom_metadata_map['names'] cua ONNX Ultralytics."""
    if raw_meta:
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(raw_meta)
                if isinstance(parsed, dict):
                    return {int(k): str(v) for k, v in parsed.items()}
                if isinstance(parsed, list):
                    return {i: str(v) for i, v in enumerate(parsed)}
            except Exception:
                continue
    return {i: code for i, code in enumerate(fallback_classes)}


def decode_yolov8_output(
    raw_output: np.ndarray,
    names: dict[int, str],
    scale: float,
    pad_left: int,
    pad_top: int,
    orig_w: int,
    orig_h: int,
    conf_threshold: float,
    iou_threshold: float,
) -> list[Detection]:
    """Giai ma tensor dau ra YOLOv8 ONNX (`[1, 4+C, N]` hoac `[1, N, 6]` end2end) -> list[Detection]."""
    arr = np.asarray(raw_output, dtype=np.float32)
    if arr.ndim == 3:
        arr = arr[0]
    if arr.ndim != 2 or arr.size == 0:
        return []

    # Dang end2end NMS [N, 6]: [x1, y1, x2, y2, conf, cls]
    expected_dim = (4 + len(names)) if names else 0
    if arr.shape[1] == 6 and expected_dim != 6:
        detections: list[Detection] = []
        for row in arr:
            conf = float(row[4])
            if conf < conf_threshold:
                continue
            cls_idx = int(round(float(row[5])))
            class_code = names.get(cls_idx)
            if not class_code:
                continue
            x1 = float(np.clip((row[0] - pad_left) / scale / orig_w, 0.0, 1.0))
            y1 = float(np.clip((row[1] - pad_top) / scale / orig_h, 0.0, 1.0))
            x2 = float(np.clip((row[2] - pad_left) / scale / orig_w, 0.0, 1.0))
            y2 = float(np.clip((row[3] - pad_top) / scale / orig_h, 0.0, 1.0))
            detections.append(Detection(class_code, conf, (x1, y1, x2, y2)))
        return detections

    # Chuan YOLOv8 ONNX: [4 + C, N] -> chuyen vi thanh [N, 4 + C]
    if expected_dim > 0 and arr.shape[0] == expected_dim and arr.shape[1] != expected_dim:
        arr = arr.T
    elif expected_dim > 0 and arr.shape[1] == expected_dim:
        pass
    elif arr.shape[0] < arr.shape[1]:
        arr = arr.T

    if arr.shape[1] <= 4:
        return []

    boxes_xywh = arr[:, :4]
    class_scores = arr[:, 4:]
    class_ids = np.argmax(class_scores, axis=1)
    confidences = class_scores[np.arange(class_scores.shape[0]), class_ids]

    mask = confidences >= conf_threshold
    if not np.any(mask):
        return []

    boxes_xywh = boxes_xywh[mask]
    class_ids = class_ids[mask]
    confidences = confidences[mask]

    # xywh (letterbox pixels) -> xyxy (original image normalized [0, 1])
    half_w = boxes_xywh[:, 2] * 0.5
    half_h = boxes_xywh[:, 3] * 0.5
    x1 = np.clip((boxes_xywh[:, 0] - half_w - pad_left) / scale / orig_w, 0.0, 1.0)
    y1 = np.clip((boxes_xywh[:, 1] - half_h - pad_top) / scale / orig_h, 0.0, 1.0)
    x2 = np.clip((boxes_xywh[:, 0] + half_w - pad_left) / scale / orig_w, 0.0, 1.0)
    y2 = np.clip((boxes_xywh[:, 1] + half_h - pad_top) / scale / orig_h, 0.0, 1.0)
    boxes_norm = np.stack([x1, y1, x2, y2], axis=1)

    # NMS rieng theo tung lop (giong Ultralytics class-aware NMS)
    detections = []
    for cls_idx in np.unique(class_ids):
        cls_mask = class_ids == cls_idx
        cls_boxes = boxes_norm[cls_mask]
        cls_confs = confidences[cls_mask]
        keep = _nms_numpy(cls_boxes, cls_confs, iou_threshold)
        class_code = names.get(int(cls_idx))
        if not class_code:
            continue
        for k in keep:
            bx = cls_boxes[k]
            detections.append(
                Detection(
                    class_code=class_code,
                    confidence=float(cls_confs[k]),
                    bbox_norm=(float(bx[0]), float(bx[1]), float(bx[2]), float(bx[3])),
                )
            )
    return detections


# --------------------------------------------------------------------------- #
# Manifest & Tu dong tai trong so (Railway / Docker deploy)
# --------------------------------------------------------------------------- #
def load_model_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("Khong doc duoc %s: %s", manifest_path, exc)
        return {}


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int | None) -> int | None:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _download_s3_uri(s3_uri: str, dest_tmp: Path) -> None:
    """Tai trong so tu private S3 / Railway Storage Bucket (`s3://bucket/key`)."""
    import boto3
    from botocore.client import Config as BotoConfig

    raw_path = s3_uri[5:] if s3_uri.lower().startswith("s3://") else s3_uri
    bucket_part, _, key_part = raw_path.partition("/")
    bucket = bucket_part.strip() or (
        os.environ.get("S3_BUCKET_NAME") or os.environ.get("AWS_S3_BUCKET_NAME") or ""
    ).strip()
    key = key_part.lstrip("/")
    if not bucket or not key:
        raise ValueError(f"S3 URI khong hop le: {s3_uri}")

    endpoint_url = (
        os.environ.get("S3_ENDPOINT_URL") or os.environ.get("AWS_ENDPOINT_URL") or ""
    ).strip() or None
    access_key = (
        os.environ.get("S3_ACCESS_KEY") or os.environ.get("AWS_ACCESS_KEY_ID") or ""
    ).strip()
    secret_key = (
        os.environ.get("S3_SECRET_KEY") or os.environ.get("AWS_SECRET_ACCESS_KEY") or ""
    ).strip()
    region = (os.environ.get("S3_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "auto").strip()
    addr_style = (os.environ.get("S3_ADDRESSING_STYLE") or "").strip()
    if not addr_style and endpoint_url and "railway.app" in endpoint_url.lower():
        addr_style = "virtual"

    cfg_kwargs: dict[str, Any] = {"signature_version": "s3v4"}
    if addr_style:
        cfg_kwargs["s3"] = {"addressing_style": addr_style}

    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key or None,
        aws_secret_access_key=secret_key or None,
        region_name=region,
        config=BotoConfig(**cfg_kwargs),
    )
    client.download_file(bucket, key, str(dest_tmp))


# --------------------------------------------------------------------------- #
# Service suy luan Model B (ONNX Runtime uu tien, fallback Ultralytics .pt)
# --------------------------------------------------------------------------- #
class FoodYoloService:
    """Nap trong so YOLOv8 (.onnx hoac .pt) va suy luan mon an, an toan da luong."""

    def __init__(
        self,
        model_path: str | os.PathLike[str] | None = None,
        manifest_path: Path = DEFAULT_MANIFEST_PATH,
    ) -> None:
        self._explicit_path = model_path
        self._manifest_path = manifest_path
        self._manifest = load_model_manifest(manifest_path)
        self._model: Any = None  # Ultralytics YOLO hoac mock trong unit test
        self._onnx_session: Any = None
        self._onnx_input_name: str = "images"
        self._onnx_names: dict[int, str] = {}
        self._loaded_backend: str | None = None
        self._lock = threading.Lock()
        self._download_attempted = False

        self.conf = _env_float("VIGOR_FOOD_CONF", float(self._manifest.get("conf_threshold", 0.30)))
        self.iou = _env_float("VIGOR_FOOD_IOU", float(self._manifest.get("iou_threshold", 0.45)))
        self.cross_class_iou = _env_float(
            "VIGOR_FOOD_CROSS_IOU",
            float(self._manifest.get("cross_class_iou_threshold", 0.75)),
        )
        self.imgsz = int(_env_float("VIGOR_FOOD_IMGSZ", float(self._manifest.get("imgsz", 640))))
        self.device = os.environ.get("VIGOR_FOOD_DEVICE", "cpu")

    # ----- duong dan, phien ban & trang thai ----- #
    def _manifest_candidate_files(self) -> list[str]:
        candidates: list[str] = []
        for key in ("active_file", "fallback_file"):
            val = str(self._manifest.get(key) or "").strip()
            if val and val not in candidates:
                candidates.append(val)
        for name in DEFAULT_WEIGHT_FILES:
            if name not in candidates:
                candidates.append(name)
        return candidates

    def _remote_download_spec(self) -> tuple[str, str | None, str]:
        url = (os.environ.get("VIGOR_FOOD_MODEL_URL") or str(self._manifest.get("download_url") or "")).strip()
        sha = (os.environ.get("VIGOR_FOOD_MODEL_SHA256") or str(self._manifest.get("sha256") or "")).strip() or None
        filename = str(self._manifest.get("active_file") or DEFAULT_WEIGHT_FILES[0]).strip()
        if url:
            tail = url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
            if tail.endswith((".onnx", ".pt")):
                filename = tail
        return url, sha, filename

    def _maybe_download_weights(self) -> Path | None:
        if self._explicit_path or os.environ.get("VIGOR_FOOD_MODEL_PATH") or self._download_attempted:
            return None
        url, expected_sha, filename = self._remote_download_spec()
        if not url:
            return None
        with self._lock:
            if self._download_attempted:
                candidate = DEFAULT_WEIGHTS_DIR / filename
                return candidate if candidate.is_file() else None
            self._download_attempted = True
            dest = DEFAULT_WEIGHTS_DIR / filename
            if dest.is_file():
                return dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".part")
            try:
                logger.info("Dang tai trong so Model B tu %s -> %s", url, dest)
                if url.lower().startswith("s3://"):
                    _download_s3_uri(url, tmp)
                else:
                    req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-Backend/1.0"})
                    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as fh:
                        while True:
                            chunk = resp.read(1024 * 1024)
                            if not chunk:
                                break
                            fh.write(chunk)
                if expected_sha:
                    actual = compute_file_sha256(tmp)
                    if actual.lower() != expected_sha.lower():
                        tmp.unlink(missing_ok=True)
                        logger.error("SHA-256 khong khop cho %s: ky vong %s, thuc te %s", filename, expected_sha, actual)
                        return None
                tmp.replace(dest)
                logger.info("Da tai xong trong so Model B (%d bytes).", dest.stat().st_size)
                return dest
            except Exception as exc:
                tmp.unlink(missing_ok=True)
                logger.warning("Khong tai duoc trong so Model B tu %s: %s", url, exc)
                return None

    @property
    def model_path(self) -> Path | None:
        explicit = self._explicit_path or os.environ.get("VIGOR_FOOD_MODEL_PATH")
        if explicit:
            path = Path(explicit)
            return path if path.is_file() else None
        for name in self._manifest_candidate_files():
            candidate = DEFAULT_WEIGHTS_DIR / name
            if candidate.is_file():
                return candidate
        return self._maybe_download_weights()

    @property
    def available(self) -> bool:
        if self._model is not None or self._onnx_session is not None:
            return True
        path = self.model_path
        if path is None:
            return False
        if path.suffix.lower() == ".onnx" and np is None:
            return False
        return True

    @property
    def backend_name(self) -> str:
        if self._loaded_backend:
            return self._loaded_backend
        if self._model is not None:
            return "ultralytics"
        if self._onnx_session is not None:
            return "onnxruntime"
        path = self.model_path
        if path is None:
            return "stub"
        return "onnxruntime" if path.suffix.lower() == ".onnx" else "ultralytics"

    @property
    def model_version(self) -> str:
        override = os.environ.get("VIGOR_FOOD_MODEL_VERSION")
        if override:
            return override
        path = self.model_path
        if path is None:
            return "unavailable"
        # Neu dung file trong manifest (khong truyen explicit path tu test), uu tien ten phien ban trong manifest
        if self._explicit_path is None and not os.environ.get("VIGOR_FOOD_MODEL_PATH"):
            manifest_ver = str(self._manifest.get("model_version") or "").strip()
            if manifest_ver:
                return manifest_ver
        return path.stem

    @property
    def supported_classes(self) -> list[str]:
        if self._onnx_names:
            return [self._onnx_names[k] for k in sorted(self._onnx_names)]
        manifest_classes = self._manifest.get("classes")
        if isinstance(manifest_classes, list) and manifest_classes:
            return [str(c) for c in manifest_classes]
        return []

    # ----- nap model (double-checked locking) ----- #
    def _load_onnx(self, path: Path) -> None:
        if np is None:
            raise FoodModelUnavailable("Thiếu thư viện NumPy để suy luận ONNX.")
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise FoodModelUnavailable("Thiếu thư viện onnxruntime để chạy file .onnx.") from exc
        try:
            opts = ort.SessionOptions()
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            threads = _env_int("VIGOR_FOOD_ORT_THREADS", None)
            if threads and threads > 0:
                opts.intra_op_num_threads = threads
            session = ort.InferenceSession(
                str(path),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            inp = session.get_inputs()[0]
            if len(inp.shape) == 4 and isinstance(inp.shape[2], int) and inp.shape[2] > 0:
                self.imgsz = int(inp.shape[2])
            meta_map = session.get_modelmeta().custom_metadata_map
            fallback_classes = [str(c) for c in self._manifest.get("classes", [])]
            self._onnx_names = parse_onnx_names(meta_map.get("names"), fallback_classes)
            self._onnx_input_name = inp.name
            self._onnx_session = session
            self._loaded_backend = "onnxruntime"
        except FoodModelUnavailable:
            raise
        except Exception as exc:
            raise FoodModelUnavailable(f"Không nạp được model ONNX: {exc}") from exc

    def _load_ultralytics(self, path: Path) -> None:
        try:
            from ultralytics import YOLO

            self._model = YOLO(str(path))
            self._loaded_backend = "ultralytics"
        except Exception as exc:
            raise FoodModelUnavailable(f"Không nạp được model PyTorch/Ultralytics: {exc}") from exc

    def _ensure_loaded(self) -> None:
        if self._model is not None or self._onnx_session is not None:
            return
        with self._lock:
            if self._model is not None or self._onnx_session is not None:
                return
            path = self.model_path
            if path is None:
                raise FoodModelUnavailable("Chưa có file trọng số Model B.")
            if path.suffix.lower() == ".onnx":
                self._load_onnx(path)
            else:
                self._load_ultralytics(path)

    # ----- suy luan ----- #
    def _detect_onnx(self, image) -> list[Detection]:
        blob, scale, left, top, orig_w, orig_h = letterbox_image(image, self.imgsz)
        with self._lock:
            raw = self._onnx_session.run(None, {self._onnx_input_name: blob})[0]
        return decode_yolov8_output(
            raw_output=raw,
            names=self._onnx_names,
            scale=scale,
            pad_left=left,
            pad_top=top,
            orig_w=orig_w,
            orig_h=orig_h,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
        )

    def _detect_ultralytics(self, image) -> list[Detection]:
        with self._lock:  # predictor cua ultralytics khong an toan khi goi dong thoi
            result = self._model.predict(
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

    def detect(self, image) -> list[Detection]:
        self._ensure_loaded()
        if self._onnx_session is not None:
            return self._detect_onnx(image)
        return self._detect_ultralytics(image)

    def analyze(self, image_bytes: bytes, catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Bytes anh -> payload `FoodAnalyzeResponse`. Ham dong bo, goi qua threadpool."""
        image = decode_image(image_bytes)
        self._ensure_loaded()
        started = time.perf_counter()
        detections = self.detect(image)
        inference_ms = int(round((time.perf_counter() - started) * 1000))
        return build_response_payload(
            detections,
            catalog,
            inference_ms,
            self.model_version,
            cross_class_iou=self.cross_class_iou,
        )

    def info(self, catalog_size: int, stub_allowed: bool) -> dict[str, Any]:
        path = self.model_path
        return {
            "available": self.available,
            "backend": self.backend_name,
            "model_version": self.model_version if self.available else "yolov8s-gymfood-stub",
            "model_file": path.name if path else None,
            "imgsz": self.imgsz,
            "conf_threshold": self.conf,
            "iou_threshold": self.iou,
            "cross_class_iou_threshold": self.cross_class_iou,
            "supported_classes": self.supported_classes,
            "catalog_size": catalog_size,
            "stub_fallback_enabled": stub_allowed,
        }

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


def reset_food_service() -> None:
    """Dung cho test khi doi bien moi truong hoac thay file trong so."""
    global _service
    _service = None
