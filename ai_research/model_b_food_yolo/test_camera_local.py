# [OWNER: M4] Cong cu kiem thu truc quan Camera Quet Mon an (F19 / Model B)
"""Chay nhan dien tren 1 anh (hoac thu muc anh) bang ONNX/PyTorch local hoac qua FastAPI HTTP,
in ra ket qua Calo/Macro va ve bounding box + nhan tieng Viet ra anh xem truoc.

Vi du (chay local truc tiep, khong can bat server):
    python test_camera_local.py --image ../datasets/model_b_v2/images/test/<anh>.jpg --save-preview preview.jpg

Vi du (goi truc tiep FastAPI server dang chay):
    python test_camera_local.py --image meal.jpg --api-url http://127.0.0.1:8000/api/v1/ai/food-analyze --save-preview preview.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.seed_catalog_and_exercises import FOOD_CATALOG_SEED
from app.services.ai_food_yolo import FoodYoloService, decode_image

PALETTE = [
    (229, 57, 53),   # Do
    (0, 191, 165),   # Xanh ngoc
    (251, 140, 0),   # Cam
    (21, 101, 192),  # Xanh duong
]


def draw_preview(image_bytes: bytes, payload: dict, save_path: Path) -> None:
    img = decode_image(image_bytes).copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for i, item in enumerate(payload.get("detected_items", [])):
        color = PALETTE[i % len(PALETTE)]
        x1, y1, x2, y2 = item["bbox_norm"]
        rect = [x1 * w, y1 * h, x2 * w, y2 * h]
        draw.rectangle(rect, outline=color, width=max(2, min(w, h) // 180))
        label = f"{item['class_code']} {int(round(item['confidence'] * 100))}% ({item['estimated_grams']:.0f}g)"
        tx, ty = rect[0], max(0.0, rect[1] - 18)
        tb = draw.textbbox((tx, ty), label)
        draw.rectangle([tb[0] - 2, tb[1] - 2, tb[2] + 4, tb[3] + 2], fill=color)
        draw.text((tx + 1, ty), label, fill=(255, 255, 255))

    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path, format="JPEG", quality=92)


def analyze_via_http(image_path: Path, api_url: str, meal_type: str) -> dict:
    import httpx

    with image_path.open("rb") as fh:
        resp = httpx.post(
            api_url,
            files={"image": (image_path.name, fh, "image/jpeg")},
            data={"meal_type": meal_type},
            timeout=30.0,
        )
    resp.raise_for_status()
    return resp.json()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test nhan dien mon an Model B & ve bbox xem truoc")
    parser.add_argument("--image", type=Path, required=True, help="duong dan anh mon an (.jpg/.png)")
    parser.add_argument("--model", type=Path, default=None, help="duong dan weights tuy chon (.onnx/.pt)")
    parser.add_argument("--api-url", default="", help="neu dat, gui HTTP POST thay vi chay local")
    parser.add_argument("--meal-type", default="LUNCH")
    parser.add_argument("--save-preview", type=Path, default=None, help="luu anh da ve bbox")
    args = parser.parse_args(argv)

    if not args.image.is_file():
        print(f"[LOI] Khong tim thay anh: {args.image}", file=sys.stderr)
        return 2

    raw = args.image.read_bytes()
    if args.api_url:
        payload = analyze_via_http(args.image, args.api_url, args.meal_type)
    else:
        svc = FoodYoloService(model_path=args.model)
        catalog = {entry["class_code"]: dict(entry) for entry in FOOD_CATALOG_SEED}
        payload = svc.analyze(raw, catalog)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.save_preview:
        draw_preview(raw, payload, args.save_preview)
        print(f"[OK] Da luu anh xem truoc: {args.save_preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
