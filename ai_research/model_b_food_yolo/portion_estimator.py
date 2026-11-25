# [OWNER: M4] Quy doi Bounding Box Area Ratio sang khoi luong gram va dinh duong (T-M4-04)
"""Ban nghien cuu cua logic khau phan, dung de chinh tham so khi kiem thu thuc te (T-M4-11).

Logic chay that tren server nam o `backend/app/services/ai_food_yolo.py` (backend khong import
duoc thu muc ai_research khi dong goi Docker). Hai ban phai cho cung ket qua: co test doi chieu
trong `backend/tests/test_ai_api.py`. Sua cong thuc o day thi sua ca ben kia.

gram = default_serving_g * clamp(area_ratio / ref_area_ratio, 0.4, 2.5)
"""
from __future__ import annotations

MIN_SCALE = 0.4
MAX_SCALE = 2.5
REF_AREA_RATIO = 0.25


def bbox_area_ratio(bbox_norm: list[float]) -> float:
    """bbox_norm = [x1, y1, x2, y2] trong khoang [0.0, 1.0]."""
    x1, y1, x2, y2 = bbox_norm
    return max(0.0, (x2 - x1) * (y2 - y1))


def estimate_grams_from_bbox(
    bbox_norm: list[float],
    default_serving_g: float,
    ref_area_ratio: float = REF_AREA_RATIO,
) -> float:
    area_ratio = bbox_area_ratio(bbox_norm)
    scale = max(MIN_SCALE, min(MAX_SCALE, area_ratio / max(ref_area_ratio, 1e-6)))
    return round(default_serving_g * scale, 1)


def macros_for_grams(
    grams: float,
    kcal_per_100g: float,
    protein_per_100g: float,
    carbs_per_100g: float,
    fat_per_100g: float,
) -> dict[str, float]:
    factor = grams / 100.0
    return {
        "calories": round(kcal_per_100g * factor, 1),
        "protein_g": round(protein_per_100g * factor, 1),
        "carbs_g": round(carbs_per_100g * factor, 1),
        "fat_g": round(fat_per_100g * factor, 1),
    }
