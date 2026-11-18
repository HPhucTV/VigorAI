# [OWNER: M4] Pydantic Schemas cho AI Model B (Food) & AI Model C (Readiness)
from pydantic import BaseModel


class DetectedFoodItem(BaseModel):
    class_code: str
    name_vi: str
    confidence: float
    bbox_norm: list[float]
    estimated_grams: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class TotalNutritionSummary(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class FoodAnalyzeResponse(BaseModel):
    inference_time_ms: int
    model_version: str
    detected_items: list[DetectedFoodItem]
    total_nutrition: TotalNutritionSummary
    disclaimer: str


class WeightRecommendation(BaseModel):
    exercise_code: str
    action: str  # INCREASE | MAINTAIN | DELOAD
    recommended_weight_kg: float
    recommended_reps: str
    reason: str


class ReadinessAndOverloadResponse(BaseModel):
    target_date: str
    model_version: str
    readiness_score: float
    readiness_level: str  # READY | MODERATE | REST_RECOMMENDED
    insights: list[str]
    muscle_fatigue_map: dict[str, float]
    weight_recommendations: list[WeightRecommendation]
    disclaimer: str
