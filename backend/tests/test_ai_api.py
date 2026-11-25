# [OWNER: M4] Pytest cho AI Model B: quy doi gram/dinh duong, service, API /api/v1/ai/food-analyze (T-M4-04, T-M4-13)
import importlib.util
import io
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
    build_items,
    build_response_payload,
    clamp_bbox,
    compute_item_nutrition,
    decode_image,
    estimate_portion_grams,
    summarize,
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
# Dinh duong theo bbox mau
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


def test_unknown_class_and_degenerate_box_are_skipped():
    detections = [
        Detection("PIZZA", 0.99, (0.1, 0.1, 0.9, 0.9)),  # khong co trong catalog
        Detection("WHITE_RICE", 0.9, (0.5, 0.5, 0.5, 0.9)),  # bbox suy bien
        Detection("WHITE_RICE", 0.8, (0.1, 0.1, 0.6, 0.6)),
    ]
    items = build_items(detections, CATALOG)
    assert [i["class_code"] for i in items] == ["WHITE_RICE"]
    assert items[0]["confidence"] == 0.8


def test_no_detections_returns_zero_totals_and_notice():
    payload = build_response_payload([], CATALOG, 15, "v-test")
    assert payload["detected_items"] == []
    assert payload["total_nutrition"] == {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
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
        "calories", "protein_g", "carbs_g", "fat_g",
    }
    assert set(payload["total_nutrition"]) == {"calories", "protein_g", "carbs_g", "fat_g"}


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
    for code in classes.CLASS_CODES:
        assert code in seeded, f"{code} thieu trong food_nutrition_catalog"
        for key in ("name_vi", "kcal_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g", "default_serving_g"):
            assert key in seeded[code]


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
    assert service.model_version == "unavailable"
    with pytest.raises(FoodModelUnavailable):
        service.analyze(_png_bytes(), CATALOG)


def test_decode_image_rejects_garbage():
    pytest.importorskip("PIL")
    with pytest.raises(InvalidImageError):
        decode_image(b"this is not an image")


def test_decode_image_returns_rgb():
    pytest.importorskip("PIL")
    assert decode_image(_png_bytes()).mode == "RGB"


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
        yield None  # load_catalog_map se rơi về catalog seed

    app.dependency_overrides[get_db] = fake_db
    monkeypatch.delenv("VIGOR_FOOD_ALLOW_STUB", raising=False)
    test_client = TestClient(app)
    test_client.ai_router = ai_router
    yield test_client
    app.dependency_overrides.pop(get_db, None)


class _FakeService:
    available = True

    def __init__(self, error=None):
        self.error = error

    def analyze(self, data, catalog):
        if self.error:
            raise self.error
        return build_response_payload(
            [Detection("WHITE_RICE", 0.9, (0.1, 0.1, 0.6, 0.6))], catalog, 12, "fake-v1"
        )


def _post(client, content=b"fake-image-bytes"):
    return client.post(
        "/api/v1/ai/food-analyze",
        files={"image": ("meal.jpg", content, "image/jpeg")},
        data={"meal_type": "LUNCH"},
    )


def test_api_returns_real_payload_when_model_available(client, monkeypatch):
    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: _FakeService())
    response = _post(client)
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "fake-v1"
    assert body["detected_items"][0]["class_code"] == "WHITE_RICE"
    assert body["total_nutrition"]["calories"] == pytest.approx(body["detected_items"][0]["calories"])


def test_api_no_food_returns_empty_list(client, monkeypatch):
    class NoFood(_FakeService):
        def analyze(self, data, catalog):
            return build_response_payload([], catalog, 9, "fake-v1")

    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: NoFood())
    body = _post(client).json()
    assert body["detected_items"] == [] and body["total_nutrition"]["calories"] == 0.0


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
    assert response.json()["model_version"].endswith("-stub")


def test_api_returns_503_without_weights_when_stub_disabled(client, monkeypatch):
    class NoWeights:
        available = False

    monkeypatch.setattr(client.ai_router, "get_food_service", lambda: NoWeights())
    monkeypatch.setenv("VIGOR_FOOD_ALLOW_STUB", "0")
    assert _post(client).status_code == 503
