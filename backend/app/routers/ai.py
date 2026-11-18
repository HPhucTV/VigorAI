# [OWNER: M4] AI Router (Model B Food YOLOv8 & Model C Readiness/Overload)
from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.ai_schema import (
    DetectedFoodItem,
    FoodAnalyzeResponse,
    ReadinessAndOverloadResponse,
    TotalNutritionSummary,
    WeightRecommendation,
)

router = APIRouter()


@router.post("/food-analyze", response_model=FoodAnalyzeResponse)
async def analyze_food_image(
    image: UploadFile = File(...),
    meal_type: str = Form(default="LUNCH"),
) -> FoodAnalyzeResponse:
    """Stub chuan hop dong JSON cho AI Model B (T-M4-03 / T-M4-10)."""
    _ = (image.filename, meal_type)
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
                protein_g=4.0,
                carbs_g=42.3,
                fat_g=0.4,
            ),
        ],
        total_nutrition=TotalNutritionSummary(
            calories=492.0,
            protein_g=59.8,
            carbs_g=42.3,
            fat_g=6.9,
        ),
        disclaimer=(
            "Giá trị dinh dưỡng được AI ước tính dựa trên hình ảnh, "
            "vui lòng kiểm tra lại khẩu phần gram trước khi lưu."
        ),
    )


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
