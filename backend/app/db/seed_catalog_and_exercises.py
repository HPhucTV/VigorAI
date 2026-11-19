# [OWNER: M3] Seed du lieu chuan VNFood/USDA (36 mon) + 30 Bai tap 3D + 4 Giao an mau (T-M3-02)
import asyncio
import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.entities import (
    Exercise,
    FoodNutritionCatalog,
    RoutineExercise,
    WorkoutRoutine,
)

CANONICAL_MUSCLE_MATERIALS = {
    "Mat_Muscle_Chest",
    "Mat_Muscle_Shoulders",
    "Mat_Muscle_Biceps",
    "Mat_Muscle_Triceps",
    "Mat_Muscle_Back_Lats",
    "Mat_Muscle_Traps",
    "Mat_Muscle_Abs_Core",
    "Mat_Muscle_Glutes",
    "Mat_Muscle_Quads",
    "Mat_Muscle_Hamstrings",
    "Mat_Muscle_Calves",
}

# 3 bai tap 3D dong goi san trong APK/AAB (khop 100% assets_3d/exported_glb/assets_manifest.json cua M2)
BUNDLED_MVP_EXERCISES: dict[str, dict[str, str]] = {
    "BARBELL_SQUAT": {
        "model_3d_glb_url": "assets/3d_bundled/barbell_squat.glb",
        "asset_checksum": "3f5fd7f31b48bd49d11a3720176a0c0e9779e1dde39568dea4a35fb9a976e6b0",
    },
    "PUSH_UP": {
        "model_3d_glb_url": "assets/3d_bundled/push_up.glb",
        "asset_checksum": "4b1604053097364a3a65325c39b6b6a2f86e0a4e23ff3d31df372eac0e2ca41d",
    },
    "BARBELL_BENCH_PRESS": {
        "model_3d_glb_url": "assets/3d_bundled/barbell_bench_press.glb",
        "asset_checksum": "59c6f242ff3bf18446240c642b46576f46a342d9dad65fc5eaffcdbad4ab0562",
    },
}

FOOD_CATALOG_SEED: list[dict] = [
    # Protein sources
    {"class_code": "GRILLED_CHICKEN_BREAST", "name_vi": "Ức gà áp chảo", "name_en": "Grilled Chicken Breast", "kcal_per_100g": 165.0, "protein_per_100g": 31.0, "carbs_per_100g": 0.0, "fat_per_100g": 3.6, "default_serving_g": 180.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "BOILED_CHICKEN_BREAST", "name_vi": "Ức gà luộc", "name_en": "Boiled Chicken Breast", "kcal_per_100g": 151.0, "protein_per_100g": 30.5, "carbs_per_100g": 0.0, "fat_per_100g": 2.8, "default_serving_g": 180.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "BEEF_STEAK", "name_vi": "Thịt bò bít tết", "name_en": "Beef Steak", "kcal_per_100g": 217.0, "protein_per_100g": 26.1, "carbs_per_100g": 0.0, "fat_per_100g": 11.8, "default_serving_g": 180.0, "source_standard": "USDA"},
    {"class_code": "STIR_FRIED_BEEF", "name_vi": "Thịt bò xào", "name_en": "Stir-Fried Lean Beef", "kcal_per_100g": 195.0, "protein_per_100g": 24.5, "carbs_per_100g": 2.5, "fat_per_100g": 9.5, "default_serving_g": 150.0, "source_standard": "NIN_VN"},
    {"class_code": "SALMON_FILLET", "name_vi": "Cá hồi áp chảo", "name_en": "Pan-Seared Salmon", "kcal_per_100g": 208.0, "protein_per_100g": 20.4, "carbs_per_100g": 0.0, "fat_per_100g": 13.4, "default_serving_g": 150.0, "source_standard": "USDA"},
    {"class_code": "BOILED_EGG", "name_vi": "Trứng gà luộc", "name_en": "Boiled Egg", "kcal_per_100g": 155.0, "protein_per_100g": 12.6, "carbs_per_100g": 1.1, "fat_per_100g": 10.6, "default_serving_g": 100.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "FRIED_EGG", "name_vi": "Trứng ốp la", "name_en": "Fried Egg", "kcal_per_100g": 196.0, "protein_per_100g": 13.6, "carbs_per_100g": 0.8, "fat_per_100g": 15.0, "default_serving_g": 100.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "EGG_WHITE", "name_vi": "Lòng trắng trứng", "name_en": "Egg White", "kcal_per_100g": 52.0, "protein_per_100g": 10.9, "carbs_per_100g": 0.7, "fat_per_100g": 0.2, "default_serving_g": 120.0, "source_standard": "USDA"},
    {"class_code": "TOFU", "name_vi": "Đậu hũ trắng", "name_en": "Firm Tofu", "kcal_per_100g": 76.0, "protein_per_100g": 8.1, "carbs_per_100g": 1.9, "fat_per_100g": 4.8, "default_serving_g": 150.0, "source_standard": "NIN_VN"},
    {"class_code": "LEAN_PORK", "name_vi": "Thịt heo nạc luộc", "name_en": "Lean Pork Loin", "kcal_per_100g": 143.0, "protein_per_100g": 26.0, "carbs_per_100g": 0.0, "fat_per_100g": 3.5, "default_serving_g": 150.0, "source_standard": "NIN_VN"},
    {"class_code": "STEAMED_SHRIMP", "name_vi": "Tôm hấp", "name_en": "Steamed Shrimp", "kcal_per_100g": 99.0, "protein_per_100g": 24.0, "carbs_per_100g": 0.2, "fat_per_100g": 0.3, "default_serving_g": 150.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "TUNA_CANNED", "name_vi": "Cá ngừ ngâm nước", "name_en": "Canned Tuna in Water", "kcal_per_100g": 116.0, "protein_per_100g": 25.5, "carbs_per_100g": 0.0, "fat_per_100g": 0.8, "default_serving_g": 120.0, "source_standard": "USDA"},
    {"class_code": "WHEY_SHAKE", "name_vi": "Whey Protein Isolate", "name_en": "Whey Protein Shake", "kcal_per_100g": 370.0, "protein_per_100g": 82.0, "carbs_per_100g": 4.0, "fat_per_100g": 2.0, "default_serving_g": 32.0, "source_standard": "USDA"},
    {"class_code": "GREEK_YOGURT", "name_vi": "Sữa chua Hy Lạp không đường", "name_en": "Plain Greek Yogurt", "kcal_per_100g": 59.0, "protein_per_100g": 10.2, "carbs_per_100g": 3.6, "fat_per_100g": 0.4, "default_serving_g": 150.0, "source_standard": "USDA"},
    # Carb & Vietnamese meals
    {"class_code": "WHITE_RICE", "name_vi": "Cơm trắng", "name_en": "Steamed White Rice", "kcal_per_100g": 130.0, "protein_per_100g": 2.7, "carbs_per_100g": 28.2, "fat_per_100g": 0.3, "default_serving_g": 150.0, "source_standard": "NIN_VN"},
    {"class_code": "BROWN_RICE", "name_vi": "Cơm gạo lứt", "name_en": "Steamed Brown Rice", "kcal_per_100g": 112.0, "protein_per_100g": 2.6, "carbs_per_100g": 23.5, "fat_per_100g": 0.9, "default_serving_g": 150.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "SWEET_POTATO", "name_vi": "Khoai lang luộc", "name_en": "Boiled Sweet Potato", "kcal_per_100g": 86.0, "protein_per_100g": 1.6, "carbs_per_100g": 20.1, "fat_per_100g": 0.1, "default_serving_g": 200.0, "source_standard": "NIN_VN"},
    {"class_code": "WHOLE_WHEAT_BREAD", "name_vi": "Bánh mì nguyên cám", "name_en": "Whole Wheat Bread", "kcal_per_100g": 247.0, "protein_per_100g": 13.0, "carbs_per_100g": 41.0, "fat_per_100g": 3.4, "default_serving_g": 80.0, "source_standard": "USDA"},
    {"class_code": "OATMEAL", "name_vi": "Yến mạch cán dẹt", "name_en": "Rolled Oats", "kcal_per_100g": 389.0, "protein_per_100g": 16.9, "carbs_per_100g": 66.3, "fat_per_100g": 6.9, "default_serving_g": 60.0, "source_standard": "USDA"},
    {"class_code": "BEEF_PHO", "name_vi": "Phở bò tái", "name_en": "Vietnamese Beef Pho", "kcal_per_100g": 95.0, "protein_per_100g": 6.2, "carbs_per_100g": 12.5, "fat_per_100g": 2.1, "default_serving_g": 450.0, "source_standard": "NIN_VN"},
    {"class_code": "CHICKEN_PHO", "name_vi": "Phở gà", "name_en": "Vietnamese Chicken Pho", "kcal_per_100g": 88.0, "protein_per_100g": 6.5, "carbs_per_100g": 12.0, "fat_per_100g": 1.5, "default_serving_g": 450.0, "source_standard": "NIN_VN"},
    {"class_code": "BUN_CHA", "name_vi": "Bún chả Hà Nội", "name_en": "Vietnamese Bun Cha", "kcal_per_100g": 142.0, "protein_per_100g": 7.8, "carbs_per_100g": 16.4, "fat_per_100g": 5.1, "default_serving_g": 380.0, "source_standard": "NIN_VN"},
    {"class_code": "COM_TAM_SUON", "name_vi": "Cơm tấm sườn nướng", "name_en": "Broken Rice with Grilled Pork", "kcal_per_100g": 168.0, "protein_per_100g": 8.4, "carbs_per_100g": 22.0, "fat_per_100g": 5.2, "default_serving_g": 350.0, "source_standard": "NIN_VN"},
    {"class_code": "BANH_MI_THIT", "name_vi": "Bánh mì thịt nguội", "name_en": "Vietnamese Pork Banh Mi", "kcal_per_100g": 235.0, "protein_per_100g": 10.2, "carbs_per_100g": 32.0, "fat_per_100g": 7.2, "default_serving_g": 180.0, "source_standard": "NIN_VN"},
    {"class_code": "MIEN_GA", "name_vi": "Miến gà", "name_en": "Chicken Glass Noodle Soup", "kcal_per_100g": 76.0, "protein_per_100g": 5.8, "carbs_per_100g": 11.2, "fat_per_100g": 0.9, "default_serving_g": 400.0, "source_standard": "NIN_VN"},
    # Vegetables, Fruits & Healthy Fats
    {"class_code": "BROCCOLI", "name_vi": "Bông cải xanh luộc", "name_en": "Steamed Broccoli", "kcal_per_100g": 35.0, "protein_per_100g": 2.4, "carbs_per_100g": 7.2, "fat_per_100g": 0.4, "default_serving_g": 120.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "GREEN_SALAD", "name_vi": "Xà lách trộn", "name_en": "Fresh Green Salad", "kcal_per_100g": 20.0, "protein_per_100g": 1.4, "carbs_per_100g": 3.5, "fat_per_100g": 0.2, "default_serving_g": 100.0, "source_standard": "USDA"},
    {"class_code": "CHERRY_TOMATO", "name_vi": "Cà chua bi", "name_en": "Cherry Tomatoes", "kcal_per_100g": 18.0, "protein_per_100g": 0.9, "carbs_per_100g": 3.9, "fat_per_100g": 0.2, "default_serving_g": 80.0, "source_standard": "USDA"},
    {"class_code": "CUCUMBER", "name_vi": "Dưa leo", "name_en": "Cucumber", "kcal_per_100g": 15.0, "protein_per_100g": 0.7, "carbs_per_100g": 3.6, "fat_per_100g": 0.1, "default_serving_g": 100.0, "source_standard": "NIN_VN"},
    {"class_code": "RAU_MUONG_XAO", "name_vi": "Rau muống xào tỏi", "name_en": "Stir-Fried Morning Glory", "kcal_per_100g": 68.0, "protein_per_100g": 2.5, "carbs_per_100g": 5.0, "fat_per_100g": 4.2, "default_serving_g": 150.0, "source_standard": "NIN_VN"},
    {"class_code": "CANH_CHUA_CA", "name_vi": "Canh chua cá lóc", "name_en": "Vietnamese Sour Fish Soup", "kcal_per_100g": 48.0, "protein_per_100g": 4.6, "carbs_per_100g": 4.2, "fat_per_100g": 1.4, "default_serving_g": 250.0, "source_standard": "NIN_VN"},
    {"class_code": "BANANA", "name_vi": "Chuối tiêu chín", "name_en": "Ripe Banana", "kcal_per_100g": 89.0, "protein_per_100g": 1.1, "carbs_per_100g": 22.8, "fat_per_100g": 0.3, "default_serving_g": 120.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "APPLE", "name_vi": "Táo tươi", "name_en": "Fresh Apple", "kcal_per_100g": 52.0, "protein_per_100g": 0.3, "carbs_per_100g": 13.8, "fat_per_100g": 0.2, "default_serving_g": 150.0, "source_standard": "USDA"},
    {"class_code": "AVOCADO", "name_vi": "Quả bơ", "name_en": "Avocado", "kcal_per_100g": 160.0, "protein_per_100g": 2.0, "carbs_per_100g": 8.5, "fat_per_100g": 14.7, "default_serving_g": 80.0, "source_standard": "USDA_NIN_VN"},
    {"class_code": "PEANUT_BUTTER", "name_vi": "Bơ đậu phộng", "name_en": "Peanut Butter", "kcal_per_100g": 588.0, "protein_per_100g": 25.1, "carbs_per_100g": 20.0, "fat_per_100g": 50.0, "default_serving_g": 20.0, "source_standard": "USDA"},
    {"class_code": "ALMONDS", "name_vi": "Hạnh nhân rang", "name_en": "Roasted Almonds", "kcal_per_100g": 579.0, "protein_per_100g": 21.2, "carbs_per_100g": 21.6, "fat_per_100g": 49.9, "default_serving_g": 28.0, "source_standard": "USDA"},
]


def _make_exercise(
    code: str,
    name_vi: str,
    name_en: str,
    equipment_type: str,
    primary: list[str],
    secondary: list[str],
    stabilizer: list[str],
    bad_form_warnings: list[str],
    setup_guide: dict,
) -> dict:
    for m in primary + secondary + stabilizer:
        if m not in CANONICAL_MUSCLE_MATERIALS:
            raise ValueError(f"Ten material co bap khong hop le: {m}")
    slug = code.lower()
    if code in BUNDLED_MVP_EXERCISES:
        glb_url = BUNDLED_MVP_EXERCISES[code]["model_3d_glb_url"]
        checksum = BUNDLED_MVP_EXERCISES[code]["asset_checksum"]
    else:
        glb_url = f"{settings.S3_PUBLIC_BASE_URL}/exercises/{slug}.glb"
        checksum = hashlib.sha256(f"vigorai-3d-{slug}-v1".encode("utf-8")).hexdigest()
    return {
        "code": code,
        "name_vi": name_vi,
        "name_en": name_en,
        "equipment_type": equipment_type,
        "model_3d_glb_url": glb_url,
        "asset_checksum": checksum,
        "primary_muscles": primary,
        "secondary_muscles": secondary,
        "stabilizer_muscles": stabilizer,
        "phase_keyframes": {
            "eccentric": {"start": 0.0, "end": 0.45, "breath": "Hít vào"},
            "isometric": {"start": 0.45, "end": 0.55, "breath": "Giữ lõi"},
            "concentric": {"start": 0.55, "end": 1.0, "breath": "Thở ra"},
        },
        "bad_form_warnings": bad_form_warnings,
        "setup_guide": setup_guide,
    }


EXERCISES_SEED: list[dict] = [
    # Chest (5)
    _make_exercise("BARBELL_BENCH_PRESS", "Đẩy ngực ngang đòn tạ", "Barbell Bench Press", "BARBELL", ["Mat_Muscle_Chest"], ["Mat_Muscle_Shoulders", "Mat_Muscle_Triceps"], ["Mat_Muscle_Abs_Core"], ["Khuỷu tay xòe quá 75 độ gây áp lực khớp vai", "Nhấc mông khỏi ghế khi đẩy tạ nặng"], {"bench_angle_deg": 0, "grip_width": "1.5x vai"}),
    _make_exercise("INCLINE_DUMBBELL_PRESS", "Đẩy ngực trên tạ đơn", "Incline Dumbbell Press", "DUMBBELL", ["Mat_Muscle_Chest"], ["Mat_Muscle_Shoulders", "Mat_Muscle_Triceps"], ["Mat_Muscle_Abs_Core"], ["Góc ghế quá dốc (>45 độ) làm vai trước gánh thay ngực"], {"bench_angle_deg": 30, "grip": "Trung tính / xoay nhẹ"}),
    _make_exercise("PUSH_UP", "Hít đất chuẩn", "Push-Up", "BODYWEIGHT", ["Mat_Muscle_Chest"], ["Mat_Muscle_Triceps", "Mat_Muscle_Shoulders"], ["Mat_Muscle_Abs_Core"], ["Võng lưng dưới do không gồng cơ bụng", "Ngẩng cổ nhìn lên làm căng đốt sống cổ"], {"hand_width": "Rộng hơn vai nhẹ"}),
    _make_exercise("CABLE_CHEST_FLY", "Ép ngực cáp đứng", "Cable Chest Fly", "CABLE", ["Mat_Muscle_Chest"], ["Mat_Muscle_Shoulders"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Biceps"], ["Gập khuỷu tay quá sâu biến thành động tác đẩy", "Dùng đà lưng kéo cáp"], {"pulley_height": "Ngang vai"}),
    _make_exercise("MACHINE_CHEST_PRESS", "Đẩy ngực máy ngồi", "Machine Chest Press", "MACHINE", ["Mat_Muscle_Chest"], ["Mat_Muscle_Triceps", "Mat_Muscle_Shoulders"], [], ["Nhô vai về trước mất khóa xương bả vai"], {"seat_height": "Tay cầm ngang giữa ngực"}),

    # Back (5)
    _make_exercise("BARBELL_DEADLIFT", "Deadlift đòn tạ", "Barbell Deadlift", "BARBELL", ["Mat_Muscle_Back_Lats", "Mat_Muscle_Hamstrings", "Mat_Muscle_Glutes"], ["Mat_Muscle_Traps", "Mat_Muscle_Abs_Core"], ["Mat_Muscle_Quads"], ["Cong lưng dưới khi kéo thanh đòn rời sàn", "Thanh đòn trôi xa ống đồng"], {"bar_position": "Giữa bàn chân", "grip": "Double overhand / Mixed"}),
    _make_exercise("BARBELL_BENT_OVER_ROW", "Kéo lưng đòn tạ", "Barbell Bent-Over Row", "BARBELL", ["Mat_Muscle_Back_Lats", "Mat_Muscle_Traps"], ["Mat_Muscle_Biceps", "Mat_Muscle_Shoulders"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Hamstrings"], ["Giật thân người quá mức để lấy đà", "Gù lưng trên"], {"torso_angle_deg": 45}),
    _make_exercise("LAT_PULLDOWN", "Kéo xô cáp rộng tay", "Lat Pulldown", "CABLE", ["Mat_Muscle_Back_Lats"], ["Mat_Muscle_Biceps", "Mat_Muscle_Traps"], ["Mat_Muscle_Abs_Core"], ["Ngả người ra sau quá sâu (>30 độ)", "Kéo thanh đòn ra sau gáy gây hại khớp vai"], {"thigh_pad": "Khóa chặt đùi"}),
    _make_exercise("SEATED_CABLE_ROW", "Ngồi kéo cáp ngang", "Seated Cable Row", "CABLE", ["Mat_Muscle_Back_Lats", "Mat_Muscle_Traps"], ["Mat_Muscle_Biceps", "Mat_Muscle_Shoulders"], ["Mat_Muscle_Abs_Core"], ["Gập tròn lưng dưới khi duỗi tay về trước"], {"foot_plate": "Gối hơi chùng 10 độ"}),
    _make_exercise("ONE_ARM_DUMBBELL_ROW", "Kéo lưng một tay tạ đơn", "One-Arm Dumbbell Row", "DUMBBELL", ["Mat_Muscle_Back_Lats"], ["Mat_Muscle_Traps", "Mat_Muscle_Biceps"], ["Mat_Muscle_Abs_Core"], ["Xoay vặn cột sống quá mức ở đỉnh động tác"], {"bench_angle_deg": 0}),

    # Shoulders (4)
    _make_exercise("BARBELL_OVERHEAD_PRESS", "Đẩy vai đứng đòn tạ", "Barbell Overhead Press", "BARBELL", ["Mat_Muscle_Shoulders"], ["Mat_Muscle_Triceps", "Mat_Muscle_Traps"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Glutes"], ["Ngả lưng dưới quá mức bù lực vai"], {"grip_width": "Rộng hơn vai một chút"}),
    _make_exercise("DUMBBELL_LATERAL_RAISE", "Dang vai ngang tạ đơn", "Dumbbell Lateral Raise", "DUMBBELL", ["Mat_Muscle_Shoulders"], ["Mat_Muscle_Traps"], ["Mat_Muscle_Abs_Core"], ["Nhún cầu vai lên quá cao", "Vung người dùng đà hông"], {"arm_angle": "Hơi gập khuỷu 15 độ"}),
    _make_exercise("CABLE_FACE_PULL", "Kéo dây thừng về mặt", "Cable Face Pull", "CABLE", ["Mat_Muscle_Shoulders", "Mat_Muscle_Traps"], ["Mat_Muscle_Back_Lats"], ["Mat_Muscle_Abs_Core"], ["Kéo khuỷu tay thấp hơn cổ tay"], {"pulley_height": "Ngang trán"}),
    _make_exercise("DUMBBELL_SHOULDER_PRESS", "Ngồi đẩy vai tạ đơn", "Seated Dumbbell Shoulder Press", "DUMBBELL", ["Mat_Muscle_Shoulders"], ["Mat_Muscle_Triceps"], ["Mat_Muscle_Abs_Core"], ["Hạ tạ quá sâu làm đau khớp vai trước"], {"bench_angle_deg": 80}),

    # Biceps & Triceps (6)
    _make_exercise("BARBELL_BICEP_CURL", "Cuốn tay trước đòn tạ", "Barbell Bicep Curl", "BARBELL", ["Mat_Muscle_Biceps"], [], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Shoulders"], ["Đưa khuỷu tay ra trước quá sớm hoặc lắc lưng"], {"grip_width": "Ngang vai"}),
    _make_exercise("DUMBBELL_HAMMER_CURL", "Cuốn búa tạ đơn", "Dumbbell Hammer Curl", "DUMBBELL", ["Mat_Muscle_Biceps"], [], ["Mat_Muscle_Abs_Core"], ["Thả rơi tạ tự do ở pha hạ tạ"], {"grip": "Trung tính (lòng bàn tay hướng vào nhau)"}),
    _make_exercise("CABLE_BICEP_CURL", "Cuốn tay trước dây cáp", "Cable Bicep Curl", "CABLE", ["Mat_Muscle_Biceps"], [], ["Mat_Muscle_Abs_Core"], ["Nhấc vai theo nhịp kéo cáp"], {"pulley_height": "Thấp nhất"}),
    _make_exercise("CABLE_TRICEP_PUSHDOWN", "Đẩy tay sau cáp", "Cable Tricep Pushdown", "CABLE", ["Mat_Muscle_Triceps"], [], ["Mat_Muscle_Abs_Core"], ["Mở khuỷu tay rời khỏi sườn"], {"pulley_height": "Cao nhất"}),
    _make_exercise("OVERHEAD_DUMBBELL_TRICEP_EXT", "Duỗi tay sau qua đầu tạ đơn", "Overhead Dumbbell Tricep Extension", "DUMBBELL", ["Mat_Muscle_Triceps"], [], ["Mat_Muscle_Abs_Core"], ["Xòe hai khuỷu tay sang ngang quá rộng"], {"elbow_position": "Khép sát đầu"}),
    _make_exercise("CLOSE_GRIP_BENCH_PRESS", "Đẩy tạ hẹp tay", "Close-Grip Bench Press", "BARBELL", ["Mat_Muscle_Triceps", "Mat_Muscle_Chest"], ["Mat_Muscle_Shoulders"], ["Mat_Muscle_Abs_Core"], ["Nắm tay quá sát nhau gây xoắn cổ tay"], {"grip_width": "Ngang vai"}),

    # Legs & Glutes (7)
    _make_exercise("BARBELL_SQUAT", "Squat gánh đòn tạ", "Barbell Back Squat", "BARBELL", ["Mat_Muscle_Quads", "Mat_Muscle_Glutes"], ["Mat_Muscle_Hamstrings"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Back_Lats"], ["Đầu gối chụm vào trong (Knee Valgus) khi đứng lên", "Nhấc gót chân khỏi sàn"], {"rack_height": "Ngang giữa ngực"}),
    _make_exercise("GOBLET_SQUAT", "Squat ôm tạ đơn", "Goblet Squat", "DUMBBELL", ["Mat_Muscle_Quads", "Mat_Muscle_Glutes"], ["Mat_Muscle_Abs_Core"], ["Mat_Muscle_Back_Lats"], ["Gù lưng trên khi giữ tạ trước ngực"], {"stance": "Rộng hơn vai nhẹ"}),
    _make_exercise("ROMANIAN_DEADLIFT", "Deadlift kiểu Romania (RDL)", "Romanian Deadlift", "BARBELL", ["Mat_Muscle_Hamstrings", "Mat_Muscle_Glutes"], ["Mat_Muscle_Back_Lats"], ["Mat_Muscle_Abs_Core"], ["Gập gối quá sâu biến thành Squat", "Cong lưng dưới khi hạ tạ"], {"knee_bend": "Chùng nhẹ 15 độ"}),
    _make_exercise("LEG_PRESS", "Đạp đùi máy", "Machine Leg Press", "MACHINE", ["Mat_Muscle_Quads", "Mat_Muscle_Glutes"], ["Mat_Muscle_Hamstrings"], [], ["Khóa cứng khớp gối ở đỉnh động tác", "Nhấc xương cụt khỏi đệm ghế khi hạ sâu"], {"foot_placement": "Giữa bàn đạp, rộng bằng vai"}),
    _make_exercise("WALKING_LUNGE", "Chùng chân bước tới tạ đơn", "Dumbbell Walking Lunge", "DUMBBELL", ["Mat_Muscle_Quads", "Mat_Muscle_Glutes"], ["Mat_Muscle_Hamstrings"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Calves"], ["Đầu gối trước lao quá mũi chân mất thăng bằng"], {"step_length": "Góc gối 90-90 độ"}),
    _make_exercise("LEG_CURL_MACHINE", "Cuốn đùi sau máy", "Seated/Lying Leg Curl", "MACHINE", ["Mat_Muscle_Hamstrings"], ["Mat_Muscle_Calves"], [], ["Nhấc hông khỏi đệm khi co đùi"], {"pad_position": "Ngay trên gót Achilles"}),
    _make_exercise("STANDING_CALF_RAISE", "Nhón bắp chân đứng", "Standing Calf Raise", "MACHINE", ["Mat_Muscle_Calves"], [], ["Mat_Muscle_Abs_Core"], ["Nhún quá nhanh không giữ 1 giây ở điểm căng nhất"], {"range_of_motion": "Duỗi hết biên độ gót chân"}),

    # Core & Kettlebell (3)
    _make_exercise("PLANK", "Plank giữ lõi", "Forearm Plank", "BODYWEIGHT", ["Mat_Muscle_Abs_Core"], ["Mat_Muscle_Shoulders", "Mat_Muscle_Glutes"], [], ["Võng thắt lưng hoặc đẩy mông lên quá cao"], {"elbow_position": "Thẳng dưới vai"}),
    _make_exercise("HANGING_LEG_RAISE", "Treo người nâng chân", "Hanging Leg Raise", "BODYWEIGHT", ["Mat_Muscle_Abs_Core"], ["Mat_Muscle_Back_Lats"], ["Mat_Muscle_Quads"], ["Đung đưa thân người dùng đà thay vì cuộn xương chậu"], {"grip": "Nắm chắc xà ngang vai"}),
    _make_exercise("KETTLEBELL_SWING", "Vung tạ ấm Kettlebell", "Kettlebell Swing", "KETTLEBELL", ["Mat_Muscle_Glutes", "Mat_Muscle_Hamstrings"], ["Mat_Muscle_Abs_Core", "Mat_Muscle_Shoulders"], ["Mat_Muscle_Back_Lats"], ["Dùng tay nâng tạ thay vì phát lực từ khớp hông (Hip Hinge)"], {"stance": "Rộng hơn vai"}),
]


TEMPLATE_ROUTINES: list[dict] = [
    {
        "name": "PPL — Ngày Đẩy (Ngực, Vai, Tay sau)",
        "split_type": "PUSH_PULL_LEGS",
        "scheduled_weekdays": [1, 4],
        "exercises": [
            ("BARBELL_BENCH_PRESS", 4, 6, 8, 150),
            ("INCLINE_DUMBBELL_PRESS", 3, 8, 12, 120),
            ("DUMBBELL_SHOULDER_PRESS", 3, 8, 12, 120),
            ("DUMBBELL_LATERAL_RAISE", 3, 12, 15, 75),
            ("CABLE_TRICEP_PUSHDOWN", 3, 10, 14, 75),
        ],
    },
    {
        "name": "PPL — Ngày Kéo (Lưng, Cầu vai, Tay trước)",
        "split_type": "PUSH_PULL_LEGS",
        "scheduled_weekdays": [2, 5],
        "exercises": [
            ("BARBELL_BENT_OVER_ROW", 4, 6, 10, 150),
            ("LAT_PULLDOWN", 3, 8, 12, 120),
            ("SEATED_CABLE_ROW", 3, 10, 12, 90),
            ("CABLE_FACE_PULL", 3, 12, 15, 75),
            ("BARBELL_BICEP_CURL", 3, 10, 12, 75),
        ],
    },
    {
        "name": "PPL — Ngày Chân & Bụng (Đùi, Mông, Bắp chân)",
        "split_type": "PUSH_PULL_LEGS",
        "scheduled_weekdays": [3, 6],
        "exercises": [
            ("BARBELL_SQUAT", 4, 6, 8, 180),
            ("ROMANIAN_DEADLIFT", 3, 8, 10, 150),
            ("LEG_PRESS", 3, 10, 12, 120),
            ("LEG_CURL_MACHINE", 3, 10, 14, 90),
            ("STANDING_CALF_RAISE", 4, 12, 15, 60),
            ("PLANK", 3, 45, 60, 60),
        ],
    },
    {
        "name": "Full Body Nền tảng (3 Buổi/Tuần)",
        "split_type": "FULL_BODY",
        "scheduled_weekdays": [1, 3, 5],
        "exercises": [
            ("BARBELL_SQUAT", 3, 8, 10, 150),
            ("BARBELL_BENCH_PRESS", 3, 8, 10, 120),
            ("LAT_PULLDOWN", 3, 10, 12, 90),
            ("BARBELL_OVERHEAD_PRESS", 3, 8, 10, 120),
            ("PLANK", 3, 45, 60, 60),
        ],
    },
]


async def seed_catalog_and_exercises(db: AsyncSession) -> dict[str, int]:
    """Idempotent seed cho food_nutrition_catalog, exercises va 4 giao an mau."""
    foods_inserted = 0
    for item in FOOD_CATALOG_SEED:
        res = await db.execute(
            select(FoodNutritionCatalog).where(
                FoodNutritionCatalog.class_code == item["class_code"]
            )
        )
        if res.scalar_one_or_none() is None:
            db.add(FoodNutritionCatalog(id=uuid.uuid4(), **item))
            foods_inserted += 1

    exercises_inserted = 0
    exercise_id_by_code: dict[str, uuid.UUID] = {}
    for ex_data in EXERCISES_SEED:
        res = await db.execute(
            select(Exercise).where(Exercise.code == ex_data["code"])
        )
        existing_ex = res.scalar_one_or_none()
        if existing_ex is None:
            new_ex = Exercise(id=uuid.uuid4(), **ex_data)
            db.add(new_ex)
            exercise_id_by_code[ex_data["code"]] = new_ex.id
            exercises_inserted += 1
        else:
            if (
                existing_ex.model_3d_glb_url != ex_data["model_3d_glb_url"]
                or existing_ex.asset_checksum != ex_data["asset_checksum"]
            ):
                existing_ex.model_3d_glb_url = ex_data["model_3d_glb_url"]
                existing_ex.asset_checksum = ex_data["asset_checksum"]
            exercise_id_by_code[ex_data["code"]] = existing_ex.id

    await db.flush()

    routines_inserted = 0
    for tpl in TEMPLATE_ROUTINES:
        res = await db.execute(
            select(WorkoutRoutine).where(
                WorkoutRoutine.user_id.is_(None),
                WorkoutRoutine.is_template.is_(True),
                WorkoutRoutine.name == tpl["name"],
            )
        )
        if res.scalar_one_or_none() is None:
            routine = WorkoutRoutine(
                id=uuid.uuid4(),
                user_id=None,
                name=tpl["name"],
                split_type=tpl["split_type"],
                scheduled_weekdays=tpl["scheduled_weekdays"],
                is_template=True,
            )
            db.add(routine)
            await db.flush()
            for idx, (ex_code, sets, r_min, r_max, rest_s) in enumerate(
                tpl["exercises"]
            ):
                db.add(
                    RoutineExercise(
                        id=uuid.uuid4(),
                        routine_id=routine.id,
                        exercise_id=exercise_id_by_code[ex_code],
                        order_index=idx,
                        target_sets=sets,
                        target_rep_min=r_min,
                        target_rep_max=r_max,
                        default_rest_seconds=rest_s,
                    )
                )
            routines_inserted += 1

    await db.commit()
    return {
        "foods_inserted": foods_inserted,
        "exercises_inserted": exercises_inserted,
        "template_routines_inserted": routines_inserted,
        "total_foods": len(FOOD_CATALOG_SEED),
        "total_exercises": len(EXERCISES_SEED),
    }


async def main() -> None:
    async with AsyncSessionLocal() as db:
        stats = await seed_catalog_and_exercises(db)
        print("Seed catalog & exercises hoan tat:", stats)


if __name__ == "__main__":
    asyncio.run(main())
