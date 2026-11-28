# [OWNER: M4] Pytest cho AI Model B (ONNX/Ultralytics, quy doi gram/dinh duong, API) & Model C stub (T-M4-03, T-M4-04, T-M4-06, T-M4-13)
import importlib.util
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pytest

from app.services import ai_food_yolo as food
from app.services.ai_food_yolo import (
    Detection,
    FoodModelUnavailable,
    FoodYoloService,
    InvalidImageError,
    bbox_iou,
    build_items,
    build_response_payload,
    clamp_bbox,
    compute_file_sha256,
    compute_item_nutrition,
    decode_image,
    decode_yolov8_output,
    estimate_portion_grams,
    letterbox_image,
    normalize_class_code,
    parse_onnx_names,
    summarize,
    suppress_cross_class_duplicates,
)

# Gia tri lay dung tu FOOD_CATALOG_SEED (M3), de test khong can DB
CATALOG = {
    "WHITE_RICE": {
        "class_code": "WHITE_RICE", "name_vi": "Cơm trắng", "kcal_per_100g": 130.0,
        "protein_per_100g": 2.7, "carbs_per_100g": 28.2, "fat_per_100g": 0.3, "default_serving_g": 150.0,
    },
    "GRILLED_CHICKEN_BREAST": {
        "class_code": "GRILLED_CHICKEN_BREAST", "name_vi": "Ức gà áp chảo", "kcal_per_100g": 165.0,
        "protein_per_100g": 31.0, "carbs_per_100g": 0.0, "fat_per_100g": 3.6, "default_serving_g": 180.0,
    },
    "BOILED_EGG": {
        "class_code": "BOILED_EGG", "name_vi": "Trứng gà luộc", "kcal_per_100g": 155.0,
        "protein_per_100g": 12.6, "carbs_per_100g": 1.1, "fat_per_100g": 10.6, "default_serving_g": 100.0,
    },
    "FRIED_EGG": {
        "class_code": "FRIED_EGG", "name_vi": "Trứng ốp la", "kcal_per_100g": 196.0,
        "protein_per_100g": 13.6, "carbs_per_100g": 0.8, "fat_per_100g": 15.0, "default_serving_g": 100.0,
    },
}
TOL = 0.06  # sai so lam tron 1 chu so thap phan


def _load_by_path(name: str, path: Path):
    if not path.is_file():
        pytest.skip(f"khong co {path} (vi du khi chay trong Docker)")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# Quy doi gram (clamp 0.4 - 2.5)
# --------------------------------------------------------------------------- #
def test_portion_at_reference_area_returns_default_serving():
    assert estimate_portion_grams(150.0, 0.25) == 150.0


def test_portion_is_clamped_to_min_and_max_scale():
    assert estimate_portion_grams(150.0, 0.0) == 60.0  # 0.4x
    assert estimate_portion_grams(150.0, 0.01) == 60.0
    assert estimate_portion_grams(150.0, 1.0) == 375.0  # 2.5x
    assert estimate_portion_grams(150.0, 5.0) == 375.0


def test_portion_scales_linearly_between_clamps():
    assert estimate_portion_grams(100.0, 0.125) == 50.0
    assert estimate_portion_grams(100.0, 0.5) == 200.0


def test_clamp_bbox_clips_swaps_and_rejects_tiny():
    assert clamp_bbox([-0.2, 0.1, 1.4, 0.9]) == (0.0, 0.1, 1.0, 0.9)
    assert clamp_bbox([0.6, 0.7, 0.2, 0.3]) == (0.2, 0.3, 0.6, 0.7)
    assert clamp_bbox([0.5, 0.5, 0.505, 0.9]) is None  # canh < 1% anh
    assert clamp_bbox([0.3, 0.3, 0.3, 0.3]) is None


# --------------------------------------------------------------------------- #
# Dinh duong theo bbox mau & khu trung cheo lop
# --------------------------------------------------------------------------- #
def test_item_nutrition_from_catalog_per_100g():
    out = compute_item_nutrition(CATALOG["WHITE_RICE"], 150.0)
    assert out["calories"] == pytest.approx(195.0, abs=TOL)
    assert out["protein_g"] == pytest.approx(4.05, abs=TOL)
    assert out["carbs_g"] == pytest.approx(42.3, abs=TOL)
    assert out["fat_g"] == pytest.approx(0.45, abs=TOL)


def test_sample_bboxes_give_expected_grams_and_macros():
    detections = [
        Detection("GRILLED_CHICKEN_BREAST", 0.93, (0.18, 0.25, 0.52, 0.61)),  # dien tich 0.1224
        Detection("WHITE_RICE", 0.91, (0.54, 0.30, 0.88, 0.72)),  # dien tich 0.1428
    ]
    items = build_items(detections, CATALOG)
    chicken, rice = items  # da sap xep theo do tin cay giam dan

    assert chicken["class_code"] == "GRILLED_CHICKEN_BREAST"
    assert chicken["estimated_grams"] == pytest.approx(88.1, abs=TOL)  # 180 * 0.1224/0.25
    assert chicken["calories"] == pytest.approx(145.4, abs=0.1)
    assert chicken["protein_g"] == pytest.approx(27.3, abs=0.1)
    assert chicken["carbs_g"] == 0.0
    assert chicken["fat_g"] == pytest.approx(3.2, abs=0.1)

    assert rice["estimated_grams"] == pytest.approx(85.7, abs=TOL)  # 150 * 0.1428/0.25
    assert rice["calories"] == pytest.approx(111.4, abs=0.1)
    assert rice["carbs_g"] == pytest.approx(24.2, abs=0.1)
    assert rice["name_vi"] == "Cơm trắng"


def test_totals_equal_sum_of_rounded_items():
    detections = [
        Detection("WHITE_RICE", 0.9, (0.1, 0.1, 0.6, 0.6)),
        Detection("BOILED_EGG", 0.8, (0.6, 0.6, 0.8, 0.8)),
        Detection("BOILED_EGG", 0.7, (0.0, 0.7, 0.2, 0.9)),
    ]
    items = build_items(detections, CATALOG)
    total = summarize(items)
    for key in ("calories", "protein_g", "carbs_g", "fat_g"):
        assert total[key] == pytest.approx(sum(i[key] for i in items), abs=1e-6)
    assert len(items) == 3  # hai qua trung la hai muc rieng


def test_cross_class_suppression_prevents_double_counting_same_food():
    detections = [
        Detection("FRIED_EGG", 0.88, (0.20, 0.20, 0.50, 0.50)),
        Detection("BOILED_EGG", 0.62, (0.21, 0.21, 0.49, 0.49)),  # chong lap > 85%
        Detection("WHITE_RICE", 0.91, (0.55, 0.20, 0.90, 0.60)),  # tach biet
    ]
    kept = suppress_cross_class_duplicates(detections, cross_iou_threshold=0.75)
    assert [d.class_code for d in kept] == ["WHITE_RICE", "FRIED_EGG"]
    items = build_items(detections, CATALOG)
    assert [i["class_code"] for i in items] == ["WHITE_RICE", "FRIED_EGG"]


def test_unknown_class_and_degenerate_box_are_skipped():
    detections = [
        Detection("PIZZA", 0.99, (0.1, 0.1, 0.9, 0.9)),  # khong co trong catalog
        Detection("WHITE_RICE", 0.9, (0.5, 0.5, 0.5, 0.9)),  # bbox suy bien
        Detection("white-rice", 0.8, (0.1, 0.1, 0.6, 0.6)),  # tu chuan hoa class_code
    ]
    items = build_items(detections, CATALOG)
    assert [i["class_code"] for i in items] == ["WHITE_RICE"]
    assert items[0]["confidence"] == 0.8


def test_no_detections_returns_zero_totals_and_notice():
    payload = build_response_payload([], CATALOG, 15, "v-test")
    assert payload["detected_items"] == []
    assert payload["total_nutrition"] == {
        "calories": 0.0,
        "calories_min": 0,
        "calories_max": 0,
        "calories_range_label": "0 kcal",
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
    }
    assert payload["disclaimer"] == food.EMPTY_DISCLAIMER
    assert payload["inference_time_ms"] == 15 and payload["model_version"] == "v-test"


def test_items_are_capped():
    detections = [Detection("WHITE_RICE", 0.9 - i * 0.001, (0.1, 0.1, 0.5, 0.5)) for i in range(40)]
    assert len(build_items(detections, CATALOG)) == food.MAX_ITEMS


def test_payload_matches_response_schema_fields():
    payload = build_response_payload(
        [Detection("WHITE_RICE", 0.9, (0.1, 0.1, 0.6, 0.6))], CATALOG, 20, "v1"
    )
    assert set(payload) == {"inference_time_ms", "model_version", "detected_items", "total_nutrition", "disclaimer"}
    assert set(payload["detected_items"][0]) == {
        "class_code", "name_vi", "confidence", "bbox_norm", "estimated_grams",
        "calories", "calories_min", "calories_max", "calories_range_label",
        "protein_g", "carbs_g", "fat_g",
    }
    assert set(payload["total_nutrition"]) == {
        "calories", "calories_min", "calories_max", "calories_range_label",
        "protein_g", "carbs_g", "fat_g",
    }
    item = payload["detected_items"][0]
    assert 0 < item["calories_min"] <= item["calories"] <= item["calories_max"]
    assert item["calories_range_label"].startswith("~") and item["calories_range_label"].endswith("kcal")


# --------------------------------------------------------------------------- #
# ONNX letterbox & decode YOLOv8 output
# --------------------------------------------------------------------------- #
def test_letterbox_preserves_aspect_ratio_and_pads_114():
    Image = pytest.importorskip("PIL.Image")
    img = Image.new("RGB", (800, 400), (255, 0, 0))  # ty le 2:1 -> resize thanh 640x320, pad top/bot 160px
    blob, scale, left, top, orig_w, orig_h = letterbox_image(img, target_size=640)
    assert blob.shape == (1, 3, 640, 640)
    assert blob.dtype == np.float32
    assert scale == pytest.approx(0.8)
    assert left == 0 and top == 160
    assert (orig_w, orig_h) == (800, 400)
    # Vung dem tren/duoi = 114/255, vung giua = do (1.0, 0.0, 0.0)
    assert blob[0, 0, 10, 10] == pytest.approx(114 / 255.0, abs=1e-3)
    assert blob[0, 0, 320, 320] == pytest.approx(1.0, abs=1e-3)
    assert blob[0, 1, 320, 320] == pytest.approx(0.0, abs=1e-3)


def test_decode_yolov8_output_unletterboxes_and_runs_nms():
    # Gia lap anh 800x400 letterbox ve 640x640 (scale=0.8, left=0, top=160)
    # Box 1 & 2 trung nhau cung lop WHITE_RICE (cls=0): NMS giu box tin cay hon (0.92)
    # Box 3 lop BOILED_EGG (cls=1) tach biet, conf=0.80
    # Box 4 duoi nguong conf=0.15 -> bi loai
    raw = np.zeros((1, 4 + 2, 4), dtype=np.float32)
    raw[0, :, 0] = [320.0, 320.0, 320.0, 160.0, 0.92, 0.02]  # -> x=[0.25, 0.75], y=[0.25, 0.75]
    raw[0, :, 1] = [324.0, 322.0, 318.0, 158.0, 0.71, 0.05]  # trung box 0 -> NMS loai
    raw[0, :, 2] = [80.0, 240.0, 160.0, 160.0, 0.01, 0.80]   # -> x=[0.0, 0.25], y=[0.0, 0.5]
    raw[0, :, 3] = [500.0, 320.0, 80.0, 80.0, 0.15, 0.10]    # < conf 0.30 -> loai

    dets = decode_yolov8_output(
        raw_output=raw,
        names={0: "WHITE_RICE", 1: "BOILED_EGG"},
        scale=0.8,
        pad_left=0,
        pad_top=160,
        orig_w=800,
        orig_h=400,
        conf_threshold=0.30,
        iou_threshold=0.45,
    )
    assert len(dets) == 2
    by_cls = {d.class_code: d for d in dets}
    assert by_cls["WHITE_RICE"].confidence == pytest.approx(0.92, abs=1e-4)
    assert by_cls["WHITE_RICE"].bbox_norm == pytest.approx((0.25, 0.25, 0.75, 0.75), abs=1e-3)
    assert by_cls["BOILED_EGG"].bbox_norm == pytest.approx((0.0, 0.0, 0.25, 0.5), abs=1e-3)


def test_parse_onnx_names_supports_python_dict_json_and_fallback():
    assert parse_onnx_names("{0: 'WHITE_RICE', 1: 'BEEF_PHO'}", []) == {0: "WHITE_RICE", 1: "BEEF_PHO"}
    assert parse_onnx_names('{"0": "TOFU"}', []) == {0: "TOFU"}
    assert parse_onnx_names(None, ["APPLE", "BANANA"]) == {0: "APPLE", 1: "BANANA"}
    assert normalize_class_code("grilled-chicken breast") == "GRILLED_CHICKEN_BREAST"
    assert bbox_iou((0.0, 0.0, 0.5, 0.5), (0.0, 0.0, 0.5, 0.5)) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Doi chieu voi ban nghien cuu & catalog
# --------------------------------------------------------------------------- #
def test_matches_research_portion_estimator():
    research = _load_by_path(
        "portion_estimator", REPO_ROOT / "ai_research" / "model_b_food_yolo" / "portion_estimator.py"
    )
    for bbox in ([0, 0, 1, 1], [0.1, 0.1, 0.5, 0.5], [0.2, 0.2, 0.25, 0.25], [0.0, 0.0, 0.5, 0.5]):
        for serving in (60.0, 150.0, 350.0):
            area = research.bbox_area_ratio(bbox)
            assert research.estimate_grams_from_bbox(bbox, serving) == estimate_portion_grams(serving, area)
    assert research.macros_for_grams(150.0, 130.0, 2.7, 28.2, 0.3) == compute_item_nutrition(
        CATALOG["WHITE_RICE"], 150.0
    )


def test_seed_catalog_covers_all_core_classes():
    try:
        from app.db.seed_catalog_and_exercises import FOOD_CATALOG_SEED
    except ImportError:
        pytest.skip("khong nap duoc seed (thieu thu vien backend)")
    classes = _load_by_path(
        "food_classes", REPO_ROOT / "ai_research" / "model_b_food_yolo" / "food_classes.py"
    )
    seeded = {e["class_code"]: e for e in FOOD_CATALOG_SEED}
    for e in food.EXTENDED_BEVERAGE_SNACK_CATALOG:
        seeded.setdefault(e["class_code"], e)
    assert len(classes.CLASS_CODES) == 100
    for code in classes.CLASS_CODES:
        assert code in seeded, f"{code} thieu trong catalog"
        for key in ("name_vi", "kcal_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g", "default_serving_g"):
            assert key in seeded[code]


def test_branded_beverages_and_zero_calorie_mineral_water():
    seeded = {e["class_code"]: e for e in food.EXTENDED_BEVERAGE_SNACK_CATALOG}
    water_items = build_items([Detection("DRINK_MINERAL_WATER", 0.92, (0.3, 0.1, 0.7, 0.9))], seeded)
    assert len(water_items) == 1
    assert water_items[0]["calories"] == 0.0
    assert water_items[0]["calories_min"] == 0
    assert water_items[0]["calories_max"] == 0
    assert water_items[0]["calories_range_label"] == "0 kcal"

    for code in ("DRINK_COLA", "DRINK_CITRUS_SODA", "DRINK_ENERGY", "DRINK_SPORTS_ISOTONIC", "DRINK_BOTTLED_TEA", "DRINK_BOTTLED_COFFEE", "DRINK_MILK_CARTON", "DRINK_COCONUT_WATER", "DRINK_YOGURT_PROBIOTIC", "DRINK_BEER", "DRINK_SOY_NUT_MILK", "DRINK_KOMBUCHA_HERBAL", "DRINK_WINE_CIDER"):
        items = build_items([Detection(code, 0.9, (0.3, 0.1, 0.7, 0.9))], seeded)
        assert len(items) == 1
        item = items[0]
        assert 0 < item["calories_min"] <= item["calories"] <= item["calories_max"]
        assert item["calories_range_label"].startswith("~")
    coffee_items = build_items([Detection("DRINK_BOTTLED_COFFEE", 0.9, (0.25, 0.1, 0.75, 0.9))], seeded)
    assert coffee_items[0]["protein_g"] > 0 and coffee_items[0]["fat_g"] > 0
    milk_items = build_items([Detection("DRINK_MILK_CARTON", 0.9, (0.25, 0.1, 0.75, 0.9))], seeded)
    assert milk_items[0]["protein_g"] > 0 and milk_items[0]["carbs_g"] > 0


def test_manifest_json_is_valid_and_matches_core_classes():
    manifest_path = PROJECT_ROOT / "ai_models" / "model_b_manifest.json"
    assert manifest_path.is_file()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["model_version"]
    assert data["active_file"].endswith(".onnx")
    assert len(data["classes"]) in (18, 30, 40, 50, 58, 69, 100)
    assert data["imgsz"] == 640


# --------------------------------------------------------------------------- #
# Service (khong can ultralytics: dung model gia)
# --------------------------------------------------------------------------- #
def _png_bytes(size=(64, 48), color=(200, 30, 30)) -> bytes:
    Image = pytest.importorskip("PIL.Image")
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


class _FakeModel:
    """Gia lap ket qua ultralytics: result.names, result.boxes[*].cls/conf/xyxyn."""

    def __init__(self, boxes):
        self._boxes = boxes

    def predict(self, **kwargs):
        self.kwargs = kwargs
        names = {0: "WHITE_RICE", 1: "BOILED_EGG"}
        boxes = [
            SimpleNamespace(cls=[cls], conf=[conf], xyxyn=[np.array(xyxy, dtype=float)])
            for cls, conf, xyxy in self._boxes
        ]
        return [SimpleNamespace(names=names, boxes=boxes)]


def test_service_reports_unavailable_without_weights(tmp_path):
    service = FoodYoloService(model_path=tmp_path / "missing.pt")
    assert service.available is False
    assert service.backend_name == "stub"
    assert service.model_version == "unavailable"
    with pytest.raises(FoodModelUnavailable):
        service.analyze(_png_bytes(), CATALOG)


def test_decode_image_rejects_garbage():
    pytest.importorskip("PIL")
    with pytest.raises(InvalidImageError):
        decode_image(b"this is not an image")


def test_decode_image_returns_rgb_and_applies_exif_rotation():
    Image = pytest.importorskip("PIL.Image")
    assert decode_image(_png_bytes()).mode == "RGB"

    # Tao JPEG 80x40 co EXIF Orientation=6 (xoay 90 do CW -> sau transpose phai thanh 40x80)
    img = Image.new("RGB", (80, 40), (10, 120, 200))
    exif = img.getexif()
    exif[274] = 6  # Orientation = Rotate 90 CW
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    rotated = decode_image(buf.getvalue())
    assert rotated.size == (40, 80)


def test_service_analyze_parses_model_output(tmp_path):
    weights = tmp_path / "food_yolo_test.pt"
    weights.write_bytes(b"x")
    service = FoodYoloService(model_path=weights)
    service._model = _FakeModel([(0, 0.91, [0.1, 0.1, 0.6, 0.6]), (1, 0.55, [0.6, 0.6, 0.8, 0.8])])

    payload = service.analyze(_png_bytes(), CATALOG)

    assert service.available and payload["model_version"] == "food_yolo_test"
    assert [i["class_code"] for i in payload["detected_items"]] == ["WHITE_RICE", "BOILED_EGG"]
    assert payload["detected_items"][0]["estimated_grams"] == pytest.approx(150.0, abs=TOL)  # dien tich 0.25
    assert payload["inference_time_ms"] >= 0
    assert service._model.kwargs["conf"] == service.conf and service._model.kwargs["verbose"] is False


def test_service_remote_download_verifies_sha256(tmp_path, monkeypatch):
    payload_bytes = b"dummy-onnx-model-bytes"
    expected_sha = compute_file_sha256_bytes(payload_bytes)
    weights_dir = tmp_path / "weights"
    monkeypatch.setattr(food, "DEFAULT_WEIGHTS_DIR", weights_dir)
    monkeypatch.setenv("VIGOR_FOOD_MODEL_URL", "https://example.invalid/food_yolo_v1.onnx")
    monkeypatch.setenv("VIGOR_FOOD_MODEL_SHA256", expected_sha)

    class _FakeResp(io.BytesIO):
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    monkeypatch.setattr(food.urllib.request, "urlopen", lambda req, timeout=120: _FakeResp(payload_bytes))
    svc = FoodYoloService(manifest_path=tmp_path / "no_manifest.json")
    resolved = svc.model_path
    assert resolved is not None and resolved.is_file()
    assert compute_file_sha256(resolved) == expected_sha

    # SHA-256 sai -> tu choi va xoa file tam
    weights_dir_bad = tmp_path / "weights_bad"
    monkeypatch.setattr(food, "DEFAULT_WEIGHTS_DIR", weights_dir_bad)
    monkeypatch.setenv("VIGOR_FOOD_MODEL_SHA256", "0" * 64)
    svc_bad = FoodYoloService(manifest_path=tmp_path / "no_manifest.json")
    assert svc_bad.model_path is None
    assert not list(weights_dir_bad.glob("*.onnx"))


def test_service_s3_download_verifies_sha256(tmp_path, monkeypatch):
    payload_bytes = b"dummy-s3-onnx-model-bytes"
    expected_sha = compute_file_sha256_bytes(payload_bytes)
    weights_dir = tmp_path / "weights_s3"
    monkeypatch.setattr(food, "DEFAULT_WEIGHTS_DIR", weights_dir)
    monkeypatch.setenv("VIGOR_FOOD_MODEL_URL", "s3://gym3d-assets/ai_models/food_yolo_v1.onnx")
    monkeypatch.setenv("VIGOR_FOOD_MODEL_SHA256", expected_sha)
    monkeypatch.setenv("S3_ENDPOINT_URL", "https://t3.storage.dev")
    monkeypatch.setenv("S3_ACCESS_KEY", "ak")
    monkeypatch.setenv("S3_SECRET_KEY", "sk")

    seen_uris = []

    def _fake_s3_download(uri, dest_tmp):
        seen_uris.append(uri)
        dest_tmp.write_bytes(payload_bytes)

    monkeypatch.setattr(food, "_download_s3_uri", _fake_s3_download)
    svc = FoodYoloService(manifest_path=tmp_path / "no_manifest.json")
    resolved = svc.model_path
    assert resolved is not None and resolved.is_file()
    assert seen_uris == ["s3://gym3d-assets/ai_models/food_yolo_v1.onnx"]
    assert compute_file_sha256(resolved) == expected_sha

    # SHA-256 sai -> tu choi va xoa file tam
    weights_dir_bad = tmp_path / "weights_s3_bad"
    monkeypatch.setattr(food, "DEFAULT_WEIGHTS_DIR", weights_dir_bad)
    monkeypatch.setenv("VIGOR_FOOD_MODEL_SHA256", "0" * 64)
    svc_bad = FoodYoloService(manifest_path=tmp_path / "no_manifest.json")
    assert svc_bad.model_path is None
    assert not list(weights_dir_bad.glob("*.onnx"))


def compute_file_sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- #
# API (can fastapi + httpx; dung dich vu gia, khong can DB hay trong so)
# --------------------------------------------------------------------------- #
@pytest.fixture
def client(monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    try:
        from fastapi.testclient import TestClient

        from app.db.session import get_db
        from app.main import app
        from app.routers import ai as ai_router
    except ImportError as exc:
        pytest.skip(f"khong nap duoc ung dung: {exc}")

    async def fake_db():
        yield None  # load_catalog_map se roi ve catalog seed

    app.dependency_overrides[get_db] = fake_db
    monkeypatch.delenv("VIGOR_FOOD_ALLOW_STUB", raising=False)
    test_client = TestClient(app)
    test_client.ai_router = ai_router
    yield test_client
    app.dependency_overrides.pop(get_db, None)


class _FakeService:
    available = True
    backend_name = "onnxruntime"

    def __init__(self, error=None):
        self.error = error

    def analyze(self, data, catalog):
        if self.error:
            raise self.error
        return build_response_payload(
            [Detection("WHITE_RICE", 0.9, (0.1, 0.1, 0.6, 0.6))], catalog, 12, "fake-v1"
        )

    def info(self, catalog_size, stub_allowed):
        return {
            "available": True,
            "backend": "onnxruntime",
            "model_version": "fake-v1",
            "model_file": "food_yolo_v1.onnx",
            "imgsz": 640,
            "conf_threshold": 0.30,
            "iou_threshold": 0.45,
            "cross_class_iou_threshold": 0.75,
            "supported_classes": ["WHITE_RICE"],
            "catalog_size": catalog_size,
            "stub_fallback_enabled": stub_allowed,
        }


def _post(client, content=b"fake-image-bytes", meal_type="LUNCH"):
    return client.post(
        "/api/v1/ai/food-analyze",
        files={"image": ("meal.jpg", content, "image/jpeg")},
        data={"meal_type": meal_type},
    )


def test_api_food_model_info(client, monkeypatch):
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: _FakeService())
    resp = client.get("/api/v1/ai/food-model/info")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert body["backend"] == "onnxruntime"
    assert body["catalog_size"] >= 18


def test_api_returns_real_payload_when_model_available(client, monkeypatch):
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: _FakeService())
    response = _post(client)
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "fake-v1"
    assert body["detected_items"][0]["class_code"] == "WHITE_RICE"
    assert body["total_nutrition"]["calories"] == pytest.approx(body["detected_items"][0]["calories"])
    assert body["disclaimer"]


def test_api_no_food_returns_empty_list(client, monkeypatch):
    class NoFood(_FakeService):
        def analyze(self, data, catalog):
            return build_response_payload([], catalog, 9, "fake-v1")

    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: NoFood())
    body = _post(client).json()
    assert body["detected_items"] == [] and body["total_nutrition"]["calories"] == 0.0
    assert body["disclaimer"] == food.EMPTY_DISCLAIMER


def test_api_rejects_empty_upload(client, monkeypatch):
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: _FakeService())
    assert _post(client, b"").status_code == 400


def test_api_rejects_oversized_upload(client, monkeypatch):
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: _FakeService())
    too_big = b"0" * (client.ai_router.MAX_UPLOAD_BYTES + 10)
    assert _post(client, too_big).status_code == 413


def test_api_maps_invalid_image_to_400(client, monkeypatch):
    monkeypatch.setattr(
        client.ai_router, "get_food_service", lambda: _FakeService(error=InvalidImageError("bad"))
    )
    assert _post(client).status_code == 400


def test_api_falls_back_to_stub_without_weights(client, monkeypatch):
    class NoWeights:
        available = False

    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: NoWeights())
    response = _post(client)
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"].endswith("-stub")
    assert body["disclaimer"]


def test_api_returns_503_without_weights_when_stub_disabled(client, monkeypatch):
    class NoWeights:
        available = False

    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: NoWeights())
    monkeypatch.setenv("VIGOR_FOOD_ALLOW_STUB", "0")
    assert _post(client).status_code == 503


def test_api_readiness_and_overload_contract(client):
    resp = client.get("/api/v1/ai/readiness-and-overload")
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["readiness_score"] <= 100.0
    assert body["readiness_level"] in {"READY", "MODERATE", "REST_RECOMMENDED"}
    assert len(body["muscle_fatigue_map"]) == 11
    assert all(k.startswith("Mat_Muscle_") for k in body["muscle_fatigue_map"])
    assert body["disclaimer"]


# --------------------------------------------------------------------------- #
# Kiem thu tich hop ONNX Runtime that (chay khi co file food_yolo_v1.onnx)
# --------------------------------------------------------------------------- #
def test_real_onnx_inference_end_to_end(client, monkeypatch):
    pytest.importorskip("onnxruntime")
    onnx_file = PROJECT_ROOT / "ai_models" / "weights" / "food_yolo_v1.onnx"
    if not onnx_file.is_file():
        pytest.skip("Chua dat food_yolo_v1.onnx vao backend/ai_models/weights/")

    manifest_path = PROJECT_ROOT / "ai_models" / "model_b_manifest.json"
    expected_version = (
        json.loads(manifest_path.read_text(encoding="utf-8")).get("model_version")
        if manifest_path.is_file()
        else "yolov8s-gymfood-v1.1"
    )

    real_svc = FoodYoloService()
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: real_svc)
    monkeypatch.setenv("VIGOR_FOOD_ALLOW_STUB", "0")

    # 0. Endpoint /food-model/info phan anh dung version & backend ONNX that
    info_resp = client.get("/api/v1/ai/food-model/info")
    assert info_resp.status_code == 200
    info_body = info_resp.json()
    assert info_body["available"] is True
    assert info_body["backend"] == "onnxruntime"
    assert info_body["model_version"] == expected_version

    # 1. Anh trang khong co do an -> tra mang rong + EMPTY_DISCLAIMER, khong crash
    blank_resp = _post(client, _png_bytes((320, 240), (245, 245, 245)))
    assert blank_resp.status_code == 200
    blank_body = blank_resp.json()
    assert blank_body["model_version"] == expected_version
    assert blank_body["disclaimer"]

    # 2. Anh mon an that tu tap test (uu tien model_b_v8 69 lop, fallback v7/v6/v5/v4/v3/v2)
    test_dir = next(
        (
            REPO_ROOT / "ai_research" / "datasets" / name / "images" / "test"
            for name in ("model_b_v9", "model_b_v8", "model_b_v7", "model_b_v6", "model_b_v5", "model_b_v4", "model_b_v3", "model_b_v2")
            if (REPO_ROOT / "ai_research" / "datasets" / name / "images" / "test").is_dir()
        ),
        REPO_ROOT / "ai_research" / "datasets" / "model_b_v2" / "images" / "test",
    )
    if test_dir.is_dir():
        test_imgs = sorted(test_dir.glob("*.jpg"))[:8]
        detected_any = False
        for img_path in test_imgs:
            resp = _post(client, img_path.read_bytes())
            assert resp.status_code == 200
            body = resp.json()
            assert body["inference_time_ms"] < 3000
            assert body["disclaimer"]
            if body["detected_items"]:
                detected_any = True
                item = body["detected_items"][0]
                x1, y1, x2, y2 = item["bbox_norm"]
                assert 0.0 <= x1 < x2 <= 1.0
                assert 0.0 <= y1 < y2 <= 1.0
                assert item["estimated_grams"] > 0
                assert item["calories"] >= 0
        assert detected_any, "Model ONNX khong phat hien duoc mon nao trong 5 anh test dau tien"
