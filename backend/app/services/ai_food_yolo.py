# [OWNER: M4] AI Model B Service — YOLOv8 Food Detection & Macro Estimator (T-M4-10)
class FoodYoloService:
    """Nap trong so YOLOv8s/m tu backend/ai_models/weights/ va suy luan mon an."""

    def estimate_portion_grams(
        self,
        default_serving_g: float,
        bbox_area_ratio: float,
        ref_area_ratio: float = 0.25,
    ) -> float:
        scale = max(0.4, min(2.5, bbox_area_ratio / max(ref_area_ratio, 1e-6)))
        return round(default_serving_g * scale, 1)
