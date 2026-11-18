# [OWNER: M4] AI Model C Service — XGBoost/LightGBM/MLP Readiness Predictor (T-M4-11)
class ReadinessMlService:
    """Suy luan diem San sang (0-100) & ban do moi co, co Fallback cho user moi < 3 ngay."""

    DEFAULT_NEW_USER_READINESS = 85.0

    def classify_readiness_level(self, score: float) -> str:
        if score >= 75.0:
            return "READY"
        if score >= 45.0:
            return "MODERATE"
        return "REST_RECOMMENDED"
