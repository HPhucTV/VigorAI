# [OWNER: M4] Quy doi Bounding Box Area Ratio sang khoi luong gram va dinh duong (T-M4-04)


def estimate_grams_from_bbox(
    bbox_norm: list[float],
    default_serving_g: float,
    ref_area_ratio: float = 0.25,
) -> float:
    """bbox_norm = [x1, y1, x2, y2] trong khoang [0.0, 1.0]."""
    x1, y1, x2, y2 = bbox_norm
    area_ratio = max(0.0, (x2 - x1) * (y2 - y1))
    scale = max(0.4, min(2.5, area_ratio / max(ref_area_ratio, 1e-6)))
    return round(default_serving_g * scale, 1)
