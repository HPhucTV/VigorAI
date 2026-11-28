# [OWNER: M4] Tai va chuyen doi dataset mo (HuggingFace) sang dinh dang YOLO cho AI Model B (T-M4-01)
"""Tai cac bo du lieu cong khai co giay phep ro rang (khong can dang nhap) ve `ai_research/datasets/raw/`:

1. `vn-streetfood`: HoagMin/Vietnamese_StreetFood_Dataset (CC BY 4.0)
   - Dinh dang YOLO san co (~3,500 anh, 14 mon Viet): Banh mi, Bun cha, Com tam, Pho bo...
2. `foodseg103`: EduardoPacheco/FoodSeg103 (Apache 2.0)
   - Segmentation theo nguyen lieu (~7,118 anh khay/dia do an thuc te, 103 lop).
   - Chuyen mask tung lop sang bounding box YOLO gon (gom cum bang gian no hinh thai 3%
     de mot dia tom/bong cai/salad thanh 1 khung thuc te thay vi vo vun).

Chay:
    python fetch_open_datasets.py
    python fetch_open_datasets.py --only vn-streetfood
    python fetch_open_datasets.py --only foodseg103 --max-per-class 300
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE.parent / "datasets" / "raw"
CACHE_DIR = HERE.parent / "datasets" / "_downloads"

VN_STREETFOOD_URL = (
    "https://huggingface.co/datasets/HoagMin/Vietnamese_StreetFood_Dataset"
    "/resolve/main/Vietnamese_StreetFood_14Class.zip"
)

FOODSEG103_BASE = "https://huggingface.co/datasets/EduardoPacheco/FoodSeg103/resolve/main"
FOODSEG103_FILES = (
    ("train", "data/train-00000-of-00003.parquet"),
    ("train", "data/train-00001-of-00003.parquet"),
    ("train", "data/train-00002-of-00003.parquet"),
    ("val", "data/validation-00000-of-00001.parquet"),
)

# Giu cac lop nguyen lieu + do uong + banh snack khop 30 lop v1.2 trong food_classes.py
# (khong gan lop mo ho nhu `egg` vi khong tach luoc/op la, hay `fish` vi lan nhieu loai ca).
FOODSEG103_KEEP: dict[int, str] = {
    1: "candy",
    2: "egg_tart",
    3: "french_fries",
    4: "chocolate",
    5: "biscuit",
    6: "popcorn",
    7: "pudding",
    8: "ice_cream",
    10: "cake",
    12: "milkshake",
    13: "coffee",
    14: "juice",
    15: "milk",
    16: "tea",
    17: "almond",
    19: "cashew",
    23: "peanut",
    25: "apple",
    29: "banana",
    46: "steak",
    48: "chicken_duck",
    56: "shrimp",
    58: "bread",
    60: "hamburg",
    61: "pizza",
    66: "rice",
    67: "pie",
    68: "tofu",
    80: "lettuce",
    87: "broccoli",
    102: "salad",
}

SODA_BOTTLES_BASE = "https://huggingface.co/datasets/Francesco/soda-bottles/resolve/main"
SODA_BOTTLES_FILES = (
    ("train", "data/train-00000-of-00001-7d2a772fa77ad220.parquet"),
    ("val", "data/validation-00000-of-00001-add46243826e216d.parquet"),
    ("test", "data/test-00000-of-00001-ed4dd2462a9652c9.parquet"),
)

COCO_VAL_BASE = "https://huggingface.co/datasets/detection-datasets/coco/resolve/main"
COCO_VAL_FILES = (
    ("val0", "data/val-00000-of-00002-c4f2e391ee4aba11.parquet"),
    ("val1", "data/val-00001-of-00002-7af5414a3b178949.parquet"),
)
COCO_KEEP: dict[int, str] = {
    39: "bottle",
    41: "cup",
    46: "banana",
    47: "apple",
    50: "broccoli",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
}

SNACKS_IMG_URL = "https://huggingface.co/datasets/Matthijs/snacks/resolve/main/images.zip"
SNACKS_CSV_BASE = "https://huggingface.co/datasets/Matthijs/snacks-detection/resolve/main"
SNACKS_CSVS = ("data/train.csv", "data/val.csv", "data/test.csv")
SNACKS_KEEP: set[str] = {
    "apple",
    "banana",
    "cake",
    "candy",
    "cookie",
    "doughnut",
    "hot dog",
    "ice cream",
    "juice",
    "muffin",
    "popcorn",
    "pretzel",
    "waffle",
}

VN_COMBINED_BASE = "https://huggingface.co/datasets/jeandeanny/vn-food-combined-2026/resolve/main"
VN_COMBINED_FILES = (
    ("val0", "data/validation-00000-of-00002.parquet"),
    ("val1", "data/validation-00001-of-00002.parquet"),
    ("test0", "data/test-00000-of-00002.parquet"),
    ("test1", "data/test-00001-of-00002.parquet"),
)
VN_COMBINED_CLASSES: tuple[str, ...] = (
    "baba-nau-chuoi-dau", "banh-bao", "banh-beo", "banh-bo", "banh-bot-loc",
    "banh-can", "banh-canh", "banh-chung", "banh-cong", "banh-cuon",
    "banh-da-cua", "banh-da-lon", "banh-duc", "banh-gai", "banh-giay",
    "banh-gio", "banh-hoi", "banh-khot", "banh-la", "banh-mi",
    "banh-mi-chao", "banh-pia", "banh-tai-heo", "banh-tet", "banh-tieu",
    "banh-tom-ho-tay", "banh-trang-nuong", "banh-troi-nuoc", "banh-trung-thu", "banh-u",
    "banh-xeo", "bo-kho", "bo-la-lot", "bo-luc-lac", "bo-ne",
    "bo-nuong-la-lot", "bun-bo-hue", "bun-cha", "bun-cha-ca", "bun-dau-mam-tom",
    "bun-mam", "bun-rieu", "bun-thit-nuong", "ca-kho-to", "ca-loc-nuong",
    "ca-muoi-xoi", "ca-ri-ga", "ca-sot-ca-chua", "canh-bi-do", "canh-chua",
    "canh-cua", "canh-kho-hoa", "canh-khoai-tim", "cao-lau", "cha-ca-la-vong",
    "cha-com", "cha-lui", "chao-long", "chao-vit", "com-chay-cha-bong",
    "com-chien", "com-ga-xoi-mo", "com-lam", "com-rang-dua-bo", "com-tam",
    "cua-hap-bia", "cut-lon-xao-me", "ga-chien-nuoc-mam", "ga-hap-la-chanh", "goi-ca-chich",
    "goi-cuon", "hu-tieu", "khau-nhuc", "kho-muc-nuong", "kho-quet",
    "lap-xuong", "luon-om-chuoi-dau", "luon-xao-xa-ot", "mam-chung", "mam-tep-chung-thit",
    "mi-quang", "mi-xao-gion", "muc-nhoi-thit", "nam-pia", "nem-chua",
    "nem-nuong-nha-trang", "nui-xao", "oc-buou-hap", "oc-huong-xao", "oc-len-xao-dua",
    "pho", "rau-muong-xao", "sup-cua", "tau-hu-nhoi-thit", "tau-hu-non",
    "thit-dong", "thit-kho-tau", "thit-trau-gac-bep", "tiet-canh", "trung-vit-lon",
    "xoi-gac", "xoi-nep-than", "xoi-xeo",
)
VN_COMBINED_KEEP: set[str] = {
    "banh-cuon",
    "banh-gio",
    "goi-cuon",
    "bun-cha",
    "bun-thit-nuong",
    "rau-muong-xao",
    "canh-chua",
    "banh-xeo",
    "banh-khot",
    "bun-rieu",
    "hu-tieu",
    "banh-canh",
    "banh-bao",
    "banh-chung",
    "banh-tet",
    "thit-kho-tau",
    "ca-kho-to",
    "mi-quang",
    "cao-lau",
    "mi-xao-gion",
    "com-ga-xoi-mo",
    "ga-chien-nuoc-mam",
}

MIN_MASK_PIXELS = 120
MIN_BOX_AREA_RATIO = 0.004  # bo manh nhieu qua nho (< 0.4% dien tich anh)
MIN_BOX_SIDE = 0.02


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        print(f"[SKIP] Da co san: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"[TAI] {url} -> {dest.name}")
    req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-DatasetFetcher/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as fh:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        last_pct = -10
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
            done += len(chunk)
            if total > 0:
                pct = int(done * 100 / total)
                if pct >= last_pct + 20:
                    print(f"  ... {pct}% ({done / 1e6:.1f}/{total / 1e6:.1f} MB)", flush=True)
                    last_pct = pct
    tmp.replace(dest)
    print(f"[XONG] {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def fetch_vn_streetfood(raw_dir: Path, cache_dir: Path, force: bool = False) -> Path:
    out_dir = raw_dir / "vn-streetfood"
    if out_dir.is_dir() and any(out_dir.rglob("*.yaml")) and not force:
        print(f"[SKIP] Da giai nen san: {out_dir}")
        return out_dir

    zip_path = download_file(VN_STREETFOOD_URL, cache_dir / "Vietnamese_StreetFood_14Class.zip")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[GIAI NEN] {zip_path.name} -> {out_dir}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)

    # Neu ben trong chi co 1 thu muc con chua data.yaml, dua noi dung len goc out_dir
    yamls = list(out_dir.rglob("data.yaml"))
    if yamls and yamls[0].parent != out_dir:
        nested = yamls[0].parent
        for item in list(nested.iterdir()):
            target = out_dir / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
        if nested.exists() and not any(nested.iterdir()):
            nested.rmdir()

    yaml_file = out_dir / "data.yaml"
    print(f"[OK] vn-streetfood san sang; data.yaml={yaml_file.is_file()}")
    if yaml_file.is_file():
        print(yaml_file.read_text(encoding="utf-8", errors="replace")[:500])
    return out_dir


def mask_to_yolo_boxes(mask_arr: np.ndarray, cls_id: int) -> list[tuple[float, float, float, float]]:
    """Chuyen mask nhi phan cua 1 lop thanh cac khung YOLO (xc, yc, w, h) chuan hoa.

    Thu nho nhanh mask ve canh dai <= 256px (Nearest) truoc khi gian no hinh thai + gan nhan
    thanh phan lien thong: nhanh gap ~300x so voi chay tren anh goc, do chinh xac bbox van ~0.4%.
    """
    h0, w0 = mask_arr.shape
    max_side = max(h0, w0)
    if max_side > 256:
        step = max(1, max_side // 256)
        small = mask_arr[::step, ::step]
    else:
        small = mask_arr

    binary = small == cls_id
    h, w = binary.shape
    min_px = max(12, int(round(h * w * 0.0015)))
    if int(binary.sum()) < min_px:
        return []

    # Gian no tach biet 1D (ngang + doc ~2.5% canh ngan) de gom mieng cung mon sat nhau
    radius = max(2, min(7, int(round(min(h, w) * 0.025))))
    size = radius * 2 + 1
    merged = ndimage.maximum_filter1d(binary, size=size, axis=1)
    merged = ndimage.maximum_filter1d(merged, size=size, axis=0)
    labeled, num_features = ndimage.label(merged)

    boxes: list[tuple[float, float, float, float]] = []
    for comp_id in range(1, num_features + 1):
        comp_mask = binary & (labeled == comp_id)
        ys, xs = np.where(comp_mask)
        if xs.size < min_px:
            continue
        x1, x2 = float(xs.min()) / w, float(xs.max() + 1) / w
        y1, y2 = float(ys.min()) / h, float(ys.max() + 1) / h
        bw, bh = x2 - x1, y2 - y1
        if bw < MIN_BOX_SIDE or bh < MIN_BOX_SIDE or (bw * bh) < MIN_BOX_AREA_RATIO:
            continue
        boxes.append(((x1 + x2) / 2.0, (y1 + y2) / 2.0, bw, bh))
    return boxes


def _open_hf_image(cell) -> Image.Image:
    if isinstance(cell, dict) and cell.get("bytes"):
        return Image.open(io.BytesIO(cell["bytes"]))
    raise ValueError(f"Khong doc duoc cot anh: {type(cell)}")


def fetch_foodseg103(
    raw_dir: Path,
    cache_dir: Path,
    max_per_class: int = 400,
    force: bool = False,
) -> Path:
    import pyarrow.parquet as pq

    out_dir = raw_dir / "foodseg103"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir

    if out_dir.exists():
        shutil.rmtree(out_dir)

    kept_ids = sorted(FOODSEG103_KEEP)
    id_to_yolo = {orig_id: idx for idx, orig_id in enumerate(kept_ids)}
    names = [FOODSEG103_KEEP[orig_id] for orig_id in kept_ids]

    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    per_class_imgs: Counter = Counter()
    per_class_boxes: Counter = Counter()
    saved_images = 0
    scanned = 0

    for split_tag, rel_path in FOODSEG103_FILES:
        pq_path = download_file(f"{FOODSEG103_BASE}/{rel_path}", cache_dir / "foodseg103" / Path(rel_path).name)
        pf = pq.ParquetFile(pq_path)
        for batch in pf.iter_batches(batch_size=128):
            rows = batch.to_pylist()
            for row in rows:
                scanned += 1
                try:
                    label_img = _open_hf_image(row["label"])
                    mask = np.asarray(label_img)
                except Exception:
                    continue
                if mask.ndim == 3:
                    mask = mask[:, :, 0]

                present = set(np.unique(mask).tolist()) & set(kept_ids)
                if not present:
                    continue
                # Chi giu anh neu it nhat 1 lop muc tieu chua cham tran max_per_class
                if max_per_class > 0 and all(per_class_imgs[cid] >= max_per_class for cid in present):
                    continue

                yolo_lines: list[str] = []
                matched_classes: set[int] = set()
                for cid in sorted(present):
                    boxes = mask_to_yolo_boxes(mask, cid)
                    if not boxes:
                        continue
                    matched_classes.add(cid)
                    yidx = id_to_yolo[cid]
                    for xc, yc, bw, bh in boxes:
                        yolo_lines.append(f"{yidx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
                        per_class_boxes[cid] += 1

                if not yolo_lines:
                    continue

                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                except Exception:
                    continue

                row_id = row.get("id", scanned)
                stem = f"fs103_{split_tag}_{row_id}"
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=92)
                (lbl_out / f"{stem}.txt").write_text("\n".join(yolo_lines) + "\n", encoding="utf-8")
                saved_images += 1
                for cid in matched_classes:
                    per_class_imgs[cid] += 1

        print(f"  Da quet {pq_path.name}: tong anh luu={saved_images} (quet={scanned})", flush=True)

    names_yaml = "\n".join(f"  {i}: {name}" for i, name in enumerate(names))
    (out_dir / "data.yaml").write_text(
        f"train: images\nval: images\nnc: {len(names)}\nnames:\n{names_yaml}\n",
        encoding="utf-8",
    )
    summary = {
        "source": "EduardoPacheco/FoodSeg103",
        "license": "Apache-2.0",
        "images_scanned": scanned,
        "images_saved": saved_images,
        "per_class_images": {FOODSEG103_KEEP[k]: per_class_imgs[k] for k in kept_ids},
        "per_class_boxes": {FOODSEG103_KEEP[k]: per_class_boxes[k] for k in kept_ids},
    }
    (out_dir / "extract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[OK] foodseg103 extract:", json.dumps(summary["per_class_images"], ensure_ascii=False))
    return out_dir


def _write_yolo_dataset_yaml(out_dir: Path, names: list[str]) -> None:
    names_yaml = "\n".join(f"  {i}: {name}" for i, name in enumerate(names))
    (out_dir / "data.yaml").write_text(
        f"train: images\nval: images\nnc: {len(names)}\nnames:\n{names_yaml}\n",
        encoding="utf-8",
    )


def fetch_soda_bottles(
    raw_dir: Path,
    cache_dir: Path,
    max_images: int = 400,
    force: bool = False,
) -> Path:
    import pyarrow.parquet as pq

    out_dir = raw_dir / "soda-bottles"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    # Giu nguyen 4 lop goc cua Francesco/soda-bottles: soda-bottles, coca-cola, fanta, sprite
    names = ["soda-bottles", "coca-cola", "fanta", "sprite"]
    per_cat_crops: Counter = Counter()
    max_crops_per_cat = 140
    saved = 0
    saved_crops = 0

    for split_tag, rel_path in SODA_BOTTLES_FILES:
        pq_path = download_file(
            f"{SODA_BOTTLES_BASE}/{rel_path}",
            cache_dir / "soda_bottles" / Path(rel_path).name,
        )
        pf = pq.ParquetFile(pq_path)
        for batch in pf.iter_batches(batch_size=128):
            for row in batch.to_pylist():
                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                    img_w, img_h = rgb.size
                    w = float(row.get("width") or img_w)
                    h = float(row.get("height") or img_h)
                    objs = row.get("objects") or {}
                    bboxes = objs.get("bbox") or []
                    cats = objs.get("category") or []
                except Exception:
                    continue
                if w <= 0 or h <= 0 or not bboxes:
                    continue
                if not cats:
                    cats = [0] * len(bboxes)

                yolo_lines: list[str] = []
                single_candidates: list[tuple[int, float, float, float, float]] = []
                for cat_raw, box in zip(cats, bboxes):
                    if len(box) < 4:
                        continue
                    cat_idx = int(cat_raw)
                    if not (0 <= cat_idx < len(names)):
                        cat_idx = 0
                    # COCO format [x_min_px, y_min_px, bw_px, bh_px]
                    bx, by, bw_px, bh_px = (float(v) for v in box[:4])
                    x1 = max(0.0, min(1.0, bx / w))
                    y1 = max(0.0, min(1.0, by / h))
                    x2 = max(0.0, min(1.0, (bx + bw_px) / w))
                    y2 = max(0.0, min(1.0, (by + bh_px) / h))
                    bw = x2 - x1
                    bh = y2 - y1
                    if bw < MIN_BOX_SIDE or bh < MIN_BOX_SIDE or (bw * bh) < MIN_BOX_AREA_RATIO:
                        continue
                    yolo_lines.append(f"{cat_idx} {(x1 + x2) / 2.0:.6f} {(y1 + y2) / 2.0:.6f} {bw:.6f} {bh:.6f}")
                    if cat_idx in (1, 2, 3) and bh_px >= 90 and bw_px >= 36:
                        single_candidates.append((cat_idx, x1, y1, x2, y2))

                if not yolo_lines:
                    continue

                # Uu tien anh it chai (<= 8 chai) de giam thien lech anh ke sieu thi chi chit
                if (max_images <= 0 or saved < max_images) and len(yolo_lines) <= 8:
                    stem = f"sb_{split_tag}_{row.get('image_id', saved)}_{saved}"
                    rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=92)
                    (lbl_out / f"{stem}.txt").write_text("\n".join(yolo_lines) + "\n", encoding="utf-8")
                    saved += 1

                # Trich crop don le tung chai coca-cola / fanta / sprite co vien boi canh thuc te
                for c_idx, (cat_idx, x1, y1, x2, y2) in enumerate(single_candidates[:2]):
                    if per_cat_crops[cat_idx] >= max_crops_per_cat:
                        continue
                    bw_n = x2 - x1
                    bh_n = y2 - y1
                    pad_x = max(bw_n * 0.45, 0.08)
                    pad_y = max(bh_n * 0.16, 0.04)
                    cx1 = max(0, int((x1 - pad_x) * img_w))
                    cy1 = max(0, int((y1 - pad_y) * img_h))
                    cx2 = min(img_w, int((x2 + pad_x) * img_w))
                    cy2 = min(img_h, int((y2 + pad_y) * img_h))
                    cw, ch = cx2 - cx1, cy2 - cy1
                    if cw < 64 or ch < 96:
                        continue
                    crop = rgb.crop((cx1, cy1, cx2, cy2))
                    bx1 = max(0.0, (x1 * img_w - cx1) / cw)
                    by1 = max(0.0, (y1 * img_h - cy1) / ch)
                    bx2 = min(1.0, (x2 * img_w - cx1) / cw)
                    by2 = min(1.0, (y2 * img_h - cy1) / ch)
                    c_stem = f"sbcrop_{split_tag}_{row.get('image_id', saved)}_{c_idx}_{saved_crops}"
                    crop.save(img_out / f"{c_stem}.jpg", format="JPEG", quality=92)
                    (lbl_out / f"{c_stem}.txt").write_text(
                        f"{cat_idx} {(bx1 + bx2) / 2.0:.6f} {(by1 + by2) / 2.0:.6f} {bx2 - bx1:.6f} {by2 - by1:.6f}\n",
                        encoding="utf-8",
                    )
                    per_cat_crops[cat_idx] += 1
                    saved_crops += 1

    _write_yolo_dataset_yaml(out_dir, names)
    print(f"[OK] soda-bottles extract: {saved} anh goc (<=8 chai) + {saved_crops} crop don le {dict(per_cat_crops)}")
    return out_dir


def fetch_coco_val_drinks_snacks(
    raw_dir: Path,
    cache_dir: Path,
    max_per_class: int = 280,
    force: bool = False,
) -> Path:
    import pyarrow.parquet as pq

    out_dir = raw_dir / "coco-val"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    kept_ids = sorted(COCO_KEEP)
    id_to_yolo = {orig_id: idx for idx, orig_id in enumerate(kept_ids)}
    names = [COCO_KEEP[orig_id] for orig_id in kept_ids]

    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    per_class_imgs: Counter = Counter()
    saved = 0
    for split_tag, rel_path in COCO_VAL_FILES:
        pq_path = download_file(
            f"{COCO_VAL_BASE}/{rel_path}",
            cache_dir / "coco_val" / Path(rel_path).name,
        )
        pf = pq.ParquetFile(pq_path)
        for batch in pf.iter_batches(batch_size=128):
            for row in batch.to_pylist():
                objs = row.get("objects") or {}
                cats = objs.get("category") or []
                bboxes = objs.get("bbox") or []
                present = {int(c) for c in cats if int(c) in id_to_yolo}
                if not present:
                    continue
                if max_per_class > 0 and all(per_class_imgs[cid] >= max_per_class for cid in present):
                    continue
                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                    img_w, img_h = rgb.size
                    w = float(row.get("width") or img_w)
                    h = float(row.get("height") or img_h)
                except Exception:
                    continue
                if w <= 0 or h <= 0:
                    continue
                yolo_lines: list[str] = []
                matched_cids: set[int] = set()
                for cid_raw, box in zip(cats, bboxes):
                    cid = int(cid_raw)
                    if cid not in id_to_yolo or len(box) < 4:
                        continue
                    # COCO parquet on HF uses Pascal VOC [x1_px, y1_px, x2_px, y2_px]
                    x1_px, y1_px, x2_px, y2_px = (float(v) for v in box[:4])
                    x1 = max(0.0, min(1.0, min(x1_px, x2_px) / w))
                    y1 = max(0.0, min(1.0, min(y1_px, y2_px) / h))
                    x2 = max(0.0, min(1.0, max(x1_px, x2_px) / w))
                    y2 = max(0.0, min(1.0, max(y1_px, y2_px) / h))
                    bw = x2 - x1
                    bh = y2 - y1
                    if bw < MIN_BOX_SIDE or bh < MIN_BOX_SIDE or (bw * bh) < MIN_BOX_AREA_RATIO:
                        continue
                    matched_cids.add(cid)
                    yolo_lines.append(
                        f"{id_to_yolo[cid]} {(x1 + x2) / 2.0:.6f} {(y1 + y2) / 2.0:.6f} {bw:.6f} {bh:.6f}"
                    )
                if not yolo_lines:
                    continue
                stem = f"coco_{split_tag}_{row.get('image_id', saved)}"
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=92)
                (lbl_out / f"{stem}.txt").write_text("\n".join(yolo_lines) + "\n", encoding="utf-8")
                saved += 1
                for cid in matched_cids:
                    per_class_imgs[cid] += 1

    _write_yolo_dataset_yaml(out_dir, names)
    print(
        "[OK] coco-val extract:",
        json.dumps({COCO_KEEP[k]: per_class_imgs[k] for k in kept_ids}, ensure_ascii=False),
    )
    return out_dir


def fetch_matthijs_snacks(
    raw_dir: Path,
    cache_dir: Path,
    max_per_class: int = 220,
    force: bool = False,
) -> Path:
    import csv
    from collections import defaultdict

    out_dir = raw_dir / "matthijs-snacks"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    names = sorted(SNACKS_KEEP)
    name_to_idx = {n: i for i, n in enumerate(names)}
    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    zip_path = download_file(SNACKS_IMG_URL, cache_dir / "matthijs_snacks" / "images.zip")
    boxes_by_id: dict[str, list[tuple[str, float, float, float, float]]] = defaultdict(list)
    for rel_csv in SNACKS_CSVS:
        csv_path = download_file(
            f"{SNACKS_CSV_BASE}/{rel_csv}",
            cache_dir / "matthijs_snacks" / Path(rel_csv).name,
        )
        with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            for row in csv.DictReader(fh):
                cname = (row.get("class_name") or "").strip().lower()
                if cname not in name_to_idx:
                    continue
                img_id = (row.get("image_id") or "").strip()
                if not img_id:
                    continue
                try:
                    x1 = max(0.0, min(1.0, float(row["x_min"])))
                    x2 = max(0.0, min(1.0, float(row["x_max"])))
                    y1 = max(0.0, min(1.0, float(row["y_min"])))
                    y2 = max(0.0, min(1.0, float(row["y_max"])))
                except (KeyError, ValueError):
                    continue
                bw, bh = x2 - x1, y2 - y1
                if bw < MIN_BOX_SIDE or bh < MIN_BOX_SIDE or (bw * bh) < MIN_BOX_AREA_RATIO:
                    continue
                boxes_by_id[img_id].append((cname, (x1 + x2) / 2.0, (y1 + y2) / 2.0, bw, bh))

    per_class_imgs: Counter = Counter()
    saved = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if not member.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            img_id = Path(member).stem
            items = boxes_by_id.get(img_id)
            if not items:
                continue
            present = {cname for cname, *_ in items}
            if max_per_class > 0 and all(per_class_imgs[c] >= max_per_class for c in present):
                continue
            try:
                raw_bytes = zf.read(member)
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    im.convert("RGB").save(img_out / f"snack_{img_id}.jpg", format="JPEG", quality=92)
            except Exception:
                continue
            lines = [f"{name_to_idx[c]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}" for c, xc, yc, bw, bh in items]
            (lbl_out / f"snack_{img_id}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            saved += 1
            for c in present:
                per_class_imgs[c] += 1

    _write_yolo_dataset_yaml(out_dir, names)
    print(f"[OK] matthijs-snacks extract: {saved} anh", dict(per_class_imgs))
    return out_dir


def estimate_dish_bbox(rgb: Image.Image) -> tuple[float, float, float, float]:
    """Uoc luong bounding box gon bam sat dia/to mon an bang saliency mau + bien Sobel."""
    small = rgb.resize((128, 128), Image.Resampling.BILINEAR)
    arr = np.asarray(small, dtype=np.float32) / 255.0
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    # Mau nen uoc luong tu vien 8px xung quanh anh
    pad = 8
    border = np.concatenate(
        [
            arr[:pad, :, :].reshape(-1, 3),
            arr[-pad:, :, :].reshape(-1, 3),
            arr[:, :pad, :].reshape(-1, 3),
            arr[:, -pad:, :].reshape(-1, 3),
        ],
        axis=0,
    )
    bg_color = np.median(border, axis=0)
    color_diff = np.linalg.norm(arr - bg_color, axis=2)

    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)
    grad = np.hypot(gx, gy)
    grad_norm = grad / (float(np.percentile(grad, 95)) + 1e-5)

    # Trong so tam nhe de uu tien mon an nam trung tam anh
    yy, xx = np.mgrid[0:128, 0:128]
    dist_center = np.hypot((xx - 63.5) / 64.0, (yy - 63.5) / 64.0)
    center_w = np.clip(1.15 - 0.55 * dist_center, 0.35, 1.0)

    sal = (0.65 * (color_diff / (float(color_diff.max()) + 1e-5)) + 0.35 * np.clip(grad_norm, 0.0, 1.0)) * center_w
    thresh = max(float(np.percentile(sal, 42)), float(sal.mean()) * 0.85)
    mask = sal >= thresh
    mask = ndimage.binary_closing(mask, structure=np.ones((7, 7)))
    mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))

    labeled, n_feat = ndimage.label(mask)
    if n_feat > 0:
        sizes = ndimage.sum(mask, labeled, range(1, n_feat + 1))
        best_id = int(np.argmax(sizes)) + 1
        ys, xs = np.where(labeled == best_id)
        if xs.size > 0:
            x1 = max(0.0, float(xs.min()) / 128.0 - 0.03)
            y1 = max(0.0, float(ys.min()) / 128.0 - 0.03)
            x2 = min(1.0, float(xs.max() + 1) / 128.0 + 0.03)
            y2 = min(1.0, float(ys.max() + 1) / 128.0 + 0.03)
            bw, bh = x2 - x1, y2 - y1
            area = bw * bh
            if bw >= 0.35 and bh >= 0.35 and 0.20 <= area <= 0.96:
                return ((x1 + x2) / 2.0, (y1 + y2) / 2.0, bw, bh)
    return (0.5, 0.5, 0.92, 0.92)


def fetch_vn_food_combined(
    raw_dir: Path,
    cache_dir: Path,
    max_per_class: int = 180,
    force: bool = False,
) -> Path:
    import pyarrow.parquet as pq

    out_dir = raw_dir / "vn-food-combined"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    names = sorted(VN_COMBINED_KEEP)
    name_to_idx = {n: i for i, n in enumerate(names)}
    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    per_class_imgs: Counter = Counter()
    saved = 0
    scanned = 0

    for split_tag, rel_path in VN_COMBINED_FILES:
        if max_per_class > 0 and all(per_class_imgs[n] >= max_per_class for n in names):
            break
        pq_path = download_file(
            f"{VN_COMBINED_BASE}/{rel_path}",
            cache_dir / "vn_food_combined" / Path(rel_path).name,
        )
        pf = pq.ParquetFile(pq_path)
        for batch in pf.iter_batches(batch_size=128):
            for row in batch.to_pylist():
                scanned += 1
                raw_lbl = row.get("label")
                if isinstance(raw_lbl, int):
                    cname = VN_COMBINED_CLASSES[raw_lbl] if 0 <= raw_lbl < len(VN_COMBINED_CLASSES) else ""
                else:
                    cname = str(raw_lbl or "").strip().lower()
                if cname not in name_to_idx:
                    continue
                if max_per_class > 0 and per_class_imgs[cname] >= max_per_class:
                    continue
                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                except Exception:
                    continue
                w0, h0 = rgb.size
                if min(w0, h0) < 120:
                    continue
                if max(w0, h0) > 800:
                    rgb.thumbnail((800, 800), Image.Resampling.LANCZOS)

                xc, yc, bw, bh = estimate_dish_bbox(rgb)
                stem = f"vncomb_{split_tag}_{scanned}"
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=88)
                (lbl_out / f"{stem}.txt").write_text(
                    f"{name_to_idx[cname]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n",
                    encoding="utf-8",
                )
                saved += 1
                per_class_imgs[cname] += 1

        # Xoa ngay shard parquet da xu ly xong de tiet kiem dung luong o dia
        try:
            pq_path.unlink(missing_ok=True)
        except OSError:
            pass
        print(f"  Da quet xong {pq_path.name}: luu={saved} (quet={scanned})", flush=True)

    _write_yolo_dataset_yaml(out_dir, names)
    summary = {
        "source": "jeandeanny/vn-food-combined-2026",
        "license": "CC-BY-NC-SA-4.0",
        "images_scanned": scanned,
        "images_saved": saved,
        "per_class_images": dict(per_class_imgs),
    }
    (out_dir / "extract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[OK] vn-food-combined extract:", json.dumps(summary["per_class_images"], ensure_ascii=False))
    return out_dir


STPEREZ_TREE_URL = "https://huggingface.co/api/datasets/stperez/beverages"
STPEREZ_RAW_BASE = "https://huggingface.co/datasets/stperez/beverages/resolve/main"
STPEREZ_FOLDER_MAP: dict[str, tuple[str, int]] = {
    "caffeinated_beverages/The Coca-Cola Company/coca-cola": ("drink-cola", 130),
    "caffeinated_beverages/PepsiCo/pepsi": ("drink-cola", 130),
    "caffeinated_beverages/The Coca-Cola Company/sprite": ("drink-citrus-soda", 95),
    "caffeinated_beverages/The Coca-Cola Company/fanta": ("drink-citrus-soda", 95),
    "caffeinated_beverages/PepsiCo/moutaindew": ("drink-citrus-soda", 95),
    "caffeinated_beverages/MonsterBeverageCorporation/monsters": ("drink-energy", 125),
    "caffeinated_beverages/PepsiCo/gatorade": ("drink-sports-isotonic", 120),
    "caffeinated_beverages/The Coca-Cola Company/powerade": ("drink-sports-isotonic", 120),
    "caffeinated_beverages/The Coca-Cola Company/fuzetea": ("drink-bottled-tea", 60),
    "caffeinated_beverages/PepsiCo/liptonbrisk": ("drink-bottled-tea", 60),
    "caffeinated_beverages/PepsiCo/pureleaf": ("drink-bottled-tea", 60),
    "Water/Nestle/Nestea": ("drink-bottled-tea", 60),
    "caffeinated_beverages/Arizona Beverage Company/arizonaTeas": ("drink-bottled-tea", 60),
    "caffeinated_beverages/Starbucks Corporation/Starbucks_Bottled_Frappuccino": ("drink-bottled-coffee", 50),
    "caffeinated_beverages/Starbucks Corporation/Starbucks_Doubleshot": ("drink-bottled-coffee", 50),
    "Water/Nestle/Nestle_Pure_Life": ("drink-mineral-water", 80),
    "Water/ Danone Group/evian": ("drink-mineral-water", 80),
    "Water/Nestle/Perrier": ("drink-mineral-water", 75),
    "Water/Nestle/San_Pellegrino": ("drink-mineral-water", 75),
    "caffeinated_beverages/The Coca-Cola Company/minutemaid": ("juice", 65),
    "caffeinated_beverages/PepsiCo/tropicana": ("juice", 65),
}

OFF_SEARCH_BASE = "https://search.openfoodfacts.org/search"
OFF_QUERIES: dict[str, list[tuple[str, int]]] = {
    "drink-cola": [
        ("coca cola", 45),
        ("pepsi", 45),
        ("coca cola zero", 25),
        ("pepsi black", 25),
    ],
    "drink-citrus-soda": [
        ("7up", 55),
        ("sprite", 45),
        ("fanta orange", 40),
        ("mirinda", 45),
        ("mountain dew", 35),
        ("schweppes", 25),
    ],
    "drink-energy": [
        ("sting", 60),
        ("red bull", 70),
        ("monster energy", 50),
        ("rockstar energy", 30),
        ("lipovitan", 25),
        ("wake up 247", 15),
    ],
    "drink-sports-isotonic": [
        ("revive", 55),
        ("pocari sweat", 50),
        ("aquarius", 45),
        ("100plus", 40),
        ("gatorade", 35),
    ],
    "drink-bottled-tea": [
        ("c2", 35),
        ("tea plus", 30),
        ("olong tea", 25),
        ("pokka tea", 35),
        ("ito en tea", 35),
        ("fuze tea", 35),
        ("lipton ice tea", 40),
    ],
    "drink-bottled-coffee": [
        ("kirin milk tea", 25),
        ("kirin fire", 25),
        ("craft boss", 20),
        ("boss coffee", 45),
        ("nescafe ready to drink", 35),
        ("iced latte", 55),
        ("coffee drink", 55),
        ("mocha drink", 40),
        ("cafe au lait", 35),
        ("milk tea", 55),
        ("royal milk tea", 30),
        ("assam milk tea", 25),
        ("pokka milk coffee", 15),
        ("mr brown coffee", 35),
    ],
    "drink-milk-carton": [
        ("vinamilk", 40),
        ("th true milk", 30),
        ("milo milk", 45),
        ("milo ready", 30),
        ("ovaltine drink", 35),
        ("dutch lady", 35),
        ("yomost", 25),
        ("soy milk", 45),
        ("strawberry milk", 45),
        ("vitasoy", 30),
        ("meiji milk", 25),
    ],
    "drink-mineral-water": [
        ("aquafina", 50),
        ("lavie water", 25),
        ("dasani", 45),
        ("evian", 50),
        ("volvic", 45),
        ("vittel", 35),
    ],
}

OFF_EXCLUDE_WORDS = (
    "beer", "bier", "lager", "stout", "ale", "ichiban", "pilsner", "wine", "vodka", "whisky",
    "powder", "sachet", "sticks", "3in1", "3 in 1", "capsule", "pods", "beans", "ground",
    "biscuit", "cookie", "cracker", "chocolate bar", "cereal", "ice cream", "yogurt cup",
    "kisses", "candy", "pieces", "syrup", "creamer", "drink mix", "tea bag", "teabag", "leaves",
)


def _is_valid_off_rtd_hit(hit: dict) -> bool:
    """Loc bo bia, bot hoa tan, goi 3in1, hop banh de giu lai dung chai/lon/hop nuoc uong."""
    text = f"{hit.get('product_name') or ''} {hit.get('brands') or ''}".lower()
    if any(bad in text for bad in OFF_EXCLUDE_WORDS):
        return False
    qty = str(hit.get("quantity") or "").lower().strip()
    if qty and any(u in qty for u in ("g", "kg")) and not any(v in qty for v in ("ml", "cl", "l")):
        # Cho phep bo qua neu chi la trong luong kho (bot milo 400g, ca phe 3in1 500g)
        if not any(w in text for w in ("drink", "milk", "latte", "tea", "water", "soda")):
            return False
    return True


def estimate_beverage_bbox(im: Image.Image, bg_idx: int = 0) -> tuple[Image.Image, tuple[float, float, float, float]]:
    """Tach nen & uoc luong bbox gon cho chai/lon/hop nuoc (ke ca chai cao, thon, nen trang)."""
    has_alpha = im.mode in ("RGBA", "LA") or ("transparency" in im.info)
    if has_alpha:
        rgba = im.convert("RGBA")
        alpha = np.asarray(rgba.getchannel("A"))
        fg_mask = alpha > 20
        fg_ratio = float(fg_mask.mean())
        if 0.04 <= fg_ratio <= 0.94:
            ys, xs = np.where(fg_mask)
            ah, aw = alpha.shape
            x1 = max(0.0, float(xs.min()) / aw - 0.015)
            y1 = max(0.0, float(ys.min()) / ah - 0.015)
            x2 = min(1.0, float(xs.max() + 1) / aw + 0.015)
            y2 = min(1.0, float(ys.max() + 1) / ah + 0.015)
            palette = [
                (255, 255, 255),
                (255, 255, 255),
                (238, 242, 246),
                (212, 206, 198),
            ]
            bg = Image.new("RGBA", rgba.size, (*palette[bg_idx % len(palette)], 255))
            rgb = Image.alpha_composite(bg, rgba).convert("RGB")
            return rgb, ((x1 + x2) / 2.0, (y1 + y2) / 2.0, x2 - x1, y2 - y1)

    rgb = im.convert("RGB")
    small = rgb.resize((128, 128), Image.Resampling.BILINEAR)
    arr = np.asarray(small, dtype=np.float32) / 255.0
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    pad = 6
    border = np.concatenate(
        [
            arr[:pad, :, :].reshape(-1, 3),
            arr[-pad:, :, :].reshape(-1, 3),
            arr[:, :pad, :].reshape(-1, 3),
            arr[:, -pad:, :].reshape(-1, 3),
        ],
        axis=0,
    )
    bg_color = np.median(border, axis=0)
    border_std = float(np.std(border))
    color_diff = np.linalg.norm(arr - bg_color, axis=2)

    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)
    grad = np.hypot(gx, gy)
    grad_norm = grad / (float(np.percentile(grad, 95)) + 1e-5)

    if border_std < 0.095:
        # Nen dong nhat (nen trang/xam thuong mai dien tu): nhay hon de bat ca nap & co chai trong suot
        mask = (color_diff > 0.042) | ((color_diff > 0.025) & (grad_norm > 0.22))
        mask = ndimage.binary_closing(mask, structure=np.ones((11, 5)))
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
    else:
        yy, xx = np.mgrid[0:128, 0:128]
        dist_center = np.hypot((xx - 63.5) / 64.0, (yy - 63.5) / 64.0)
        center_w = np.clip(1.18 - 0.58 * dist_center, 0.32, 1.0)
        sal = (0.60 * (color_diff / (float(color_diff.max()) + 1e-5)) + 0.40 * np.clip(grad_norm, 0.0, 1.0)) * center_w
        thresh = max(float(np.percentile(sal, 46)), float(sal.mean()) * 0.90)
        mask = ndimage.binary_closing(sal >= thresh, structure=np.ones((9, 5)))
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))

    labeled, n_feat = ndimage.label(mask)
    if n_feat > 0:
        sizes = ndimage.sum(mask, labeled, range(1, n_feat + 1))
        # Uu tien thanh phan lon gan trung tam anh
        best_id = int(np.argmax(sizes)) + 1
        ys, xs = np.where(labeled == best_id)
        if xs.size > 0:
            x1 = max(0.0, float(xs.min()) / 128.0 - 0.025)
            y1 = max(0.0, float(ys.min()) / 128.0 - 0.025)
            x2 = min(1.0, float(xs.max() + 1) / 128.0 + 0.025)
            y2 = min(1.0, float(ys.max() + 1) / 128.0 + 0.025)
            bw, bh = x2 - x1, y2 - y1
            area = bw * bh
            if bw >= 0.12 and bh >= 0.25 and 0.05 <= area <= 0.96:
                return rgb, ((x1 + x2) / 2.0, (y1 + y2) / 2.0, bw, bh)
    return rgb, (0.5, 0.5, 0.86, 0.90)


def _off_front_url(hit: dict) -> str | None:
    if hit.get("image_front_url"):
        return str(hit["image_front_url"])
    code = str(hit.get("code") or "").strip()
    if not code:
        return None
    folder = f"{code.zfill(13)[0:3]}/{code.zfill(13)[3:6]}/{code.zfill(13)[6:9]}/{code.zfill(13)[9:]}" if len(code) > 8 else code
    sel = ((hit.get("selected_images") or {}).get("front") or {})
    if isinstance(sel, dict):
        disp = sel.get("display") or {}
        if isinstance(disp, dict) and disp:
            return str(next(iter(disp.values())))
    if isinstance(sel, list) and sel:
        s0 = sel[0]
        lang = s0.get("lang") or "en"
        rev = s0.get("rev")
        if rev:
            return f"https://images.openfoodfacts.org/images/products/{folder}/front_{lang}.{rev}.400.jpg"
    imgs = (hit.get("images") or {}).get("uploaded") or {}
    if isinstance(imgs, dict) and "1" in imgs:
        return f"https://images.openfoodfacts.org/images/products/{folder}/1.400.jpg"
    return None


def _is_clean_beverage_image(rgb: Image.Image) -> bool:
    """Loai anh qua nho, logo vector phang hoac don sac loi."""
    w, h = rgb.size
    if min(w, h) < 90:
        return False
    ratio = w / float(max(h, 1))
    if ratio < 0.20 or ratio > 2.40:
        return False
    arr = np.asarray(rgb.resize((64, 64), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0
    if float(arr.std()) < 0.06:
        return False
    # Phat hien logo vector phang (it mau doc lap hoac it chuyen sac giua cac pixel)
    quant = (arr * 7.0).astype(np.int32)
    packed = quant[:, :, 0] * 64 + quant[:, :, 1] * 8 + quant[:, :, 2]
    _, counts = np.unique(packed, return_counts=True)
    significant_colors = int((counts >= 12).sum())
    if significant_colors < 8:
        return False
    return True


def _save_with_optional_white_studio(
    rgb: Image.Image,
    bbox: tuple[float, float, float, float],
    cls_idx: int,
    stem: str,
    img_out: Path,
    lbl_out: Path,
    bg_seed: int,
    indoor_bg: bool = False,
) -> int:
    """Luu anh goc + bien the nen trang TMĐT + bien the nen toi trong nha (chung group .rf.)."""
    xc, yc, bw, bh = bbox
    rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=90)
    (lbl_out / f"{stem}.txt").write_text(
        f"{cls_idx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n",
        encoding="utf-8",
    )
    saved = 1
    w, h = rgb.size
    # Neu anh doc hep hoac chai chiem khung chat, tao them ban nen trang ty le ~4:5 giong anh chup man hinh / TMĐT
    if (w / float(max(h, 1)) < 0.72 or bw > 0.72) and bg_seed % 2 == 0:
        canvas_w = max(w + 24, int(round(h * 0.85)))
        canvas_h = max(h + 24, int(round(canvas_w * 1.15)))
        bg_tone = (255, 255, 255) if (bg_seed % 4 == 0) else (240, 244, 248)
        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_tone)
        ox = (canvas_w - w) // 2
        oy = (canvas_h - h) // 2
        canvas.paste(rgb, (ox, oy))
        if max(canvas_w, canvas_h) > 720:
            canvas.thumbnail((720, 720), Image.Resampling.LANCZOS)
        nx1 = max(0.0, (ox + (xc - bw / 2.0) * w) / canvas_w)
        ny1 = max(0.0, (oy + (yc - bh / 2.0) * h) / canvas_h)
        nx2 = min(1.0, (ox + (xc + bw / 2.0) * w) / canvas_w)
        ny2 = min(1.0, (oy + (yc + bh / 2.0) * h) / canvas_h)
        # Cung prefix truoc `.rf.` de prepare_dataset.py giu ca 2 vao cung tap train/val/test (0 leakage)
        w_stem = f"{stem}_jpg.rf.wbg"
        canvas.save(img_out / f"{w_stem}.jpg", format="JPEG", quality=90)
        (lbl_out / f"{w_stem}.txt").write_text(
            f"{cls_idx} {(nx1 + nx2) / 2.0:.6f} {(ny1 + ny2) / 2.0:.6f} {nx2 - nx1:.6f} {ny2 - ny1:.6f}\n",
            encoding="utf-8",
        )
        saved += 1
    if indoor_bg and (bg_seed % 2 == 0):
        # Tao bien the chai thieu sang trong nha (mo phong cam tay chup phong toi)
        arr = np.asarray(rgb, dtype=np.float32)
        bg_med = np.median(
            np.concatenate([arr[:6, :, :].reshape(-1, 3), arr[-6:, :, :].reshape(-1, 3)], axis=0),
            axis=0,
        )
        fg_mask = np.linalg.norm(arr - bg_med, axis=2) > 18.0 if float(np.std(arr[:6])) < 24.0 else np.ones((h, w), dtype=bool)
        if float(fg_mask.mean()) >= 0.08:
            dark_fg = np.clip(arr * (0.80 + 0.04 * (bg_seed % 4)), 0, 255).astype(np.uint8)
            cw = max(w + 48, int(round(h * 0.92)))
            ch = max(h + 48, int(round(cw * 1.15)))
            base = 82 + (bg_seed % 45)
            indoor = Image.new("RGB", (cw, ch), (base, base + 4, base + 2))
            ox = (cw - w) // 2
            oy = (ch - h) // 2
            mask_img = Image.fromarray((fg_mask.astype(np.uint8) * 255), mode="L")
            indoor.paste(Image.fromarray(dark_fg), (ox, oy), mask_img)
            if max(cw, ch) > 720:
                indoor.thumbnail((720, 720), Image.Resampling.LANCZOS)
            nx1 = max(0.0, (ox + (xc - bw / 2.0) * w) / cw)
            ny1 = max(0.0, (oy + (yc - bh / 2.0) * h) / ch)
            nx2 = min(1.0, (ox + (xc + bw / 2.0) * w) / cw)
            ny2 = min(1.0, (oy + (yc + bh / 2.0) * h) / ch)
            i_stem = f"{stem}_jpg.rf.indoor"
            indoor.save(img_out / f"{i_stem}.jpg", format="JPEG", quality=90)
            (lbl_out / f"{i_stem}.txt").write_text(
                f"{cls_idx} {(nx1 + nx2) / 2.0:.6f} {(ny1 + ny2) / 2.0:.6f} {nx2 - nx1:.6f} {ny2 - ny1:.6f}\n",
                encoding="utf-8",
            )
            saved += 1
    return saved


def fetch_branded_beverages(
    raw_dir: Path,
    cache_dir: Path,
    force: bool = False,
) -> Path:
    """Tai du lieu do uong co nhan hieu tu `stperez/beverages` (MIT) & Open Food Facts (CC-BY-SA-3.0)."""
    import urllib.parse
    from concurrent.futures import ThreadPoolExecutor, as_completed

    out_dir = raw_dir / "branded-beverages"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    names = [
        "drink-cola",
        "drink-citrus-soda",
        "drink-energy",
        "drink-sports-isotonic",
        "drink-bottled-tea",
        "drink-bottled-coffee",
        "drink-milk-carton",
        "drink-mineral-water",
        "juice",
    ]
    name_to_idx = {n: i for i, n in enumerate(names)}
    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    tasks: list[tuple[str, str, str]] = []  # (stem_prefix, target_cls, url)

    # 1. Thu thap danh sach file tu stperez/beverages (MIT)
    try:
        req = urllib.request.Request(STPEREZ_TREE_URL, headers={"User-Agent": "VigorAI-DatasetFetcher/1.5"})
        tree = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
        by_folder: dict[str, list[str]] = {}
        for sib in tree.get("siblings", []):
            rf = sib.get("rfilename", "")
            if not rf.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            for folder in STPEREZ_FOLDER_MAP:
                if rf.startswith(folder + "/"):
                    by_folder.setdefault(folder, []).append(rf)
                    break
        for folder, (target_cls, cap) in STPEREZ_FOLDER_MAP.items():
            files = sorted(by_folder.get(folder, []))[:cap]
            for idx, rf in enumerate(files):
                quoted = "/".join(urllib.parse.quote(seg) for seg in rf.split("/"))
                tag = folder.rsplit("/", 1)[-1].lower().replace(" ", "_")
                tasks.append((f"stpz_{tag}_{idx}", target_cls, f"{STPEREZ_RAW_BASE}/{quoted}"))
        print(f"[stperez/beverages] Da lap danh sach {len(tasks)} anh thuong hieu.")
    except Exception as exc:
        print(f"[CANH BAO] Loi doc tree stperez/beverages: {exc}")

    # 2. Thu thap anh san pham Open Food Facts (7Up, Sting, Kirin, Revive, Pocari, Aquafina, C2, Tea+, Milo, Vinamilk...)
    seen_codes: set[str] = set()
    off_count = 0
    for target_cls, q_list in OFF_QUERIES.items():
        for q, cap in q_list:
            try:
                u = f"{OFF_SEARCH_BASE}?q={urllib.parse.quote(q)}&page_size={min(100, cap * 2)}"
                req = urllib.request.Request(
                    u,
                    headers={"User-Agent": "VigorAI-Research/1.5 (https://github.com/HPhucTV/VigorAI)"},
                )
                res = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace"))
                added = 0
                for hit in res.get("hits", []):
                    if added >= cap:
                        break
                    if not _is_valid_off_rtd_hit(hit):
                        continue
                    code = str(hit.get("code") or "").strip()
                    if not code or code in seen_codes:
                        continue
                    img_url = _off_front_url(hit)
                    if not img_url:
                        continue
                    seen_codes.add(code)
                    q_tag = "".join(ch for ch in q if ch.isalnum())[:12]
                    tasks.append((f"off_{q_tag}_{code}", target_cls, img_url))
                    added += 1
                    off_count += 1
            except Exception as exc:
                print(f"  [OFF warn] query={q}: {exc}")
    print(f"[OpenFoodFacts] Da lap them {off_count} anh san pham (tong nhiem vu tai={len(tasks)}).")

    def _download_one(item: tuple[int, str, str, str]) -> tuple[str, str, bytes | None]:
        _i, stem, target_cls, url = item
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "VigorAI-Research/1.5 (https://github.com/HPhucTV/VigorAI)"},
            )
            data = urllib.request.urlopen(req, timeout=15).read()
            return stem, target_cls, data
        except Exception:
            return stem, target_cls, None

    per_class_files: Counter = Counter()
    errors = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(_download_one, (idx, st, cls, u)) for idx, (st, cls, u) in enumerate(tasks)]
        for idx, fut in enumerate(as_completed(futs), 1):
            stem, target_cls, raw_bytes = fut.result()
            if not raw_bytes:
                errors += 1
                continue
            try:
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    rgb, bbox = estimate_beverage_bbox(im, bg_idx=idx)
            except Exception:
                errors += 1
                continue
            if not _is_clean_beverage_image(rgb):
                continue
            if max(rgb.size) > 720:
                rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
            n_saved = _save_with_optional_white_studio(
                rgb=rgb,
                bbox=bbox,
                cls_idx=name_to_idx[target_cls],
                stem=stem,
                img_out=img_out,
                lbl_out=lbl_out,
                bg_seed=idx,
                indoor_bg=(target_cls in ("drink-bottled-coffee", "drink-energy", "drink-cola", "drink-citrus-soda")),
            )
            per_class_files[target_cls] += n_saved
            if idx % 250 == 0:
                print(f"  ... da xu ly {idx}/{len(tasks)} URLs | da luu={sum(per_class_files.values())}", flush=True)

    _write_yolo_dataset_yaml(out_dir, names)
    summary = {
        "sources": ["stperez/beverages (MIT)", "Open Food Facts Search API (CC-BY-SA-3.0)"],
        "urls_attempted": len(tasks),
        "download_or_decode_errors": errors,
        "images_saved_incl_white_studio": sum(per_class_files.values()),
        "per_class_images": dict(per_class_files),
    }
    (out_dir / "extract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[OK] branded-beverages extract:", json.dumps(summary, ensure_ascii=False))
    return out_dir


V16_BEER_FOLDERS: dict[str, int] = {
    "Beer/Anheuser-Busch InBev/corona": 50,
    "Beer/Anheuser-Busch InBev/budweiser": 50,
    "Beer/Anheuser-Busch InBev/stella_artois": 50,
    "Beer/Anheuser-Busch InBev/modelo_especial": 50,
    "Beer/Anheuser-Busch InBev/michelob_ultra": 45,
    "Beer/Anheuser-Busch InBev/castle_lite": 45,
}

V16_OFF_QUERIES: dict[str, list[tuple[str, int]]] = {
    "oatmeal": [("overnight oats", 35), ("oatmeal cup", 35)],
    "greek-yogurt": [("greek yogurt", 65), ("oikos yogurt", 45), ("chobani yogurt", 45), ("fage yogurt", 35), ("plain yogurt", 45)],
    "whey-shake": [("whey protein", 65), ("isolate protein", 45), ("premier protein", 50), ("muscle milk", 45), ("protein shake", 55)],
    "drink-coconut-water": [("coconut water", 80), ("vita coco", 45), ("harmless harvest", 30), ("ufc coconut", 30), ("coco water", 40)],
    "drink-yogurt-probiotic": [("yakult", 55), ("actimel", 65), ("calpis", 30), ("probi", 15), ("betagen", 15), ("probiotic yogurt drink", 50), ("danactive", 30)],
    "drink-beer": [("heineken", 55), ("tiger beer", 20), ("sapporo beer", 20), ("asahi beer", 35), ("strongbow", 35)],
    "drink-citrus-soda": [("7up", 60), ("7up zero", 35), ("sprite can", 35), ("mountain dew can", 30)],
    "drink-bottled-coffee": [("kirin latte", 25), ("bottled iced coffee", 25), ("boss coffee", 25)],
    "drink-sports-isotonic": [("revive drink", 25), ("pocari sweat", 30), ("aquarius drink", 25)],
}

V16_N5K_QUERIES: list[tuple[str, str, int]] = [
    ("brown rice", "brown rice", 220),
    ("oatmeal", "oatmeal", 60),
    ("sweet potato", "sweet potato", 100),
    ("avocado", "avocado", 55),
    ("cucumber", "cucumber", 70),
    ("cherry-tomato", "cherry tomato", 80),
    ("lean-pork", "pork", 30),
]

V16_LVIS_CLASS_MAP: dict[int, str] = {
    0: "almonds",
    5: "avocado",
    24: "cucumber",
    35: "cherry-tomato",
    58: "sweet potato",
    59: "cherry-tomato",
}


def _is_valid_v16_off_hit(hit: dict, target_cls: str) -> bool:
    text = f"{hit.get('product_name') or ''} {hit.get('brands') or ''}".lower()
    if target_cls in ("sweet potato", "brown rice") and any(w in text for w in ("crisps", "chips", "baby food", "puree", "cracker")):
        return False
    if target_cls == "greek-yogurt" and any(w in text for w in ("yakult", "actimel", "probiotic drink")):
        return False
    if target_cls.startswith("drink-") and target_cls != "drink-beer":
        return _is_valid_off_rtd_hit(hit)
    if target_cls == "oatmeal" and any(w in text for w in ("cookie", "biscuit", "quaker", "canister")):
        return False
    return True


def _collect_n5k_tasks(tasks: list[tuple[str, str, str, str]]) -> Counter:
    import urllib.parse

    added = Counter()
    seen_urls: set[str] = set()
    for target_cls, query, cap in V16_N5K_QUERIES:
        count = 0
        req_sub = query.lower()
        for off in (0, 100, 200):
            if count >= cap:
                break
            u = (
                "https://datasets-server.huggingface.co/search"
                f"?dataset=TeeA/nutrition5k-food-name-gemini&config=default&split=train"
                f"&query={urllib.parse.quote(query)}&offset={off}&length=100"
            )
            try:
                res = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "VigorAI-Research/1.6"}), timeout=25).read().decode("utf-8", errors="replace"))
            except Exception as exc:
                print(f"  [N5K warn] {query}@{off}: {exc}")
                break
            rows = res.get("rows", [])
            if not rows:
                break
            for item in rows:
                if count >= cap:
                    break
                row = item.get("row") or {}
                fname = str(row.get("food_name") or "").strip()
                if len(fname) > 55 or req_sub not in fname.lower():
                    continue
                if target_cls == "cherry-tomato" and "tomato" not in fname.lower():
                    continue
                img_url = (row.get("dish_image") or {}).get("src")
                if not img_url or img_url in seen_urls:
                    continue
                seen_urls.add(img_url)
                did = str(row.get("dish_id") or count)
                tasks.append((f"n5k_{target_cls.replace(' ', '')}_{did}_{count}", target_cls, img_url, "dish"))
                count += 1
                added[target_cls] += 1
    print(f"[Nutrition5k] Da lap {sum(added.values())} anh: {dict(added)}")
    return added


def _collect_lvis_yolo_items(
    cache_dir: Path,
    name_to_idx: dict[str, int],
    class_map: dict[int, str] = V16_LVIS_CLASS_MAP,
    min_area: float = 0.04,
    per_class_cap: int | dict[str, int] = 140,
    stem_prefix: str = "lvis",
    max_boxes_per_image: int = 2,
) -> list[tuple[str, str, list[str], str]]:
    """Tai nhan .7z tu Siddhanxt & tra ve danh sach (stem, img_url, yolo_lines, primary_cls)."""
    import urllib.parse

    lvis_cache = cache_dir / "lvis_labels"
    lvis_cache.mkdir(parents=True, exist_ok=True)
    base_sid = "https://huggingface.co/datasets/Siddhanxt/Fruits-And-Vegetables-Detection-Dataset/resolve/main"
    base_lvis = "https://huggingface.co/datasets/henningheyen/LVIS_Fruits_And_Vegetables/resolve/main/images"

    for split in ("train", "val"):
        split_dir = lvis_cache / split
        if not split_dir.is_dir() or not any(split_dir.glob("*.txt")):
            arc = lvis_cache / f"{split}_labels.7z"
            if not arc.is_file():
                print(f"[LVIS] Dang tai {split}_labels.7z ...")
                urllib.request.urlretrieve(f"{base_sid}/{split}_labels.7z", arc)
            subprocess.run(["tar", "-xf", str(arc), "-C", str(lvis_cache)], check=True)

    counts = Counter()
    items: list[tuple[str, str, list[str], str]] = []
    for split in ("train", "val"):
        for txt_path in sorted((lvis_cache / split).glob("*.txt")):
            stem = txt_path.stem.strip()
            if not stem:
                continue
            kept_lines: list[str] = []
            cls_hits: list[str] = []
            for ln in txt_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                parts = ln.split()
                if len(parts) != 5:
                    continue
                try:
                    cid = int(parts[0])
                    xc, yc, bw, bh = (float(x) for x in parts[1:])
                except ValueError:
                    continue
                target_cls = class_map.get(cid)
                if not target_cls or bw * bh < min_area:
                    continue
                kept_lines.append(f"{name_to_idx[target_cls]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
                cls_hits.append(target_cls)
            if not kept_lines or (max_boxes_per_image > 0 and len(kept_lines) > max_boxes_per_image):
                continue
            eligible = [
                c for c in set(cls_hits)
                if counts[c] < (per_class_cap.get(c, 140) if isinstance(per_class_cap, dict) else per_class_cap)
            ]
            if not eligible:
                continue
            primary = min(eligible, key=lambda c: counts[c])
            counts[primary] += 1
            img_url = f"{base_lvis}/{split}/{urllib.parse.quote(txt_path.stem)}.jpg"
            items.append((f"{stem_prefix}_{split}_{len(items):04d}", img_url, kept_lines, primary))
    print(f"[LVIS_Fruits_And_Vegetables] Da chon {len(items)} anh co bbox chuan: {dict(counts)}", flush=True)
    return items


def _collect_food_ingredients_tasks(tasks: list[tuple[str, str, str, str]]) -> Counter:
    import urllib.parse

    folder_map = {
        "Cucumber": ("cucumber", 85),
        "Sweetpotato": ("sweet potato", 79),
        "Tomato": ("cherry-tomato", 85),
    }
    added = Counter()
    try:
        info = json.loads(urllib.request.urlopen("https://huggingface.co/api/datasets/SunnyAgarwal4274/Food_Ingredients", timeout=20).read().decode("utf-8"))
        for sib in info.get("siblings", []):
            rf = sib.get("rfilename", "")
            if not rf.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            parts = rf.split("/")
            if len(parts) < 3 or parts[0] not in ("Train", "Test"):
                continue
            spec = folder_map.get(parts[1])
            if not spec:
                continue
            target_cls, cap = spec
            if added[target_cls] >= cap:
                continue
            quoted = "/".join(urllib.parse.quote(seg) for seg in rf.split("/"))
            url = f"https://huggingface.co/datasets/SunnyAgarwal4274/Food_Ingredients/resolve/main/{quoted}"
            tasks.append((f"fi_{target_cls.replace(' ', '')}_{added[target_cls]:03d}", target_cls, url, "dish"))
            added[target_cls] += 1
    except Exception as exc:
        print(f"[Food_Ingredients warn] {exc}")
    print(f"[Food_Ingredients] Da lap {sum(added.values())} anh: {dict(added)}")
    return added


def _collect_food101_pork_tasks(tasks: list[tuple[str, str, str, str]]) -> int:
    count = 0
    for off, length in ((1500, 100), (1600, 100), (1700, 50)):
        if count >= 200:
            break
        u = f"https://datasets-server.huggingface.co/rows?dataset=ethz/food101&config=default&split=validation&offset={off}&length={length}"
        try:
            res = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "VigorAI-Research/1.6"}), timeout=25).read().decode("utf-8"))
            for item in res.get("rows", []):
                if count >= 200:
                    break
                row = item.get("row") or {}
                if row.get("label") != 77:
                    continue
                img_url = (row.get("image") or {}).get("src")
                if not img_url:
                    continue
                tasks.append((f"f101_porkchop_{count:03d}", "lean-pork", img_url, "dish"))
                count += 1
        except Exception as exc:
            print(f"  [Food101 pork warn] @{off}: {exc}")
    print(f"[Food101 pork_chop] Da lap {count} anh.")
    return count


def _collect_hass_avocado_tasks(tasks: list[tuple[str, str, str, str]]) -> int:
    import urllib.parse

    try:
        info = json.loads(urllib.request.urlopen("https://huggingface.co/api/datasets/c2p-cmd/hass_avocado", timeout=20).read().decode("utf-8"))
        files = sorted(
            s["rfilename"]
            for s in info.get("siblings", [])
            if s["rfilename"].startswith("Avocado Ripening Dataset/") and s["rfilename"].lower().endswith(".jpg")
        )
        if not files:
            return 0
        step = max(1, len(files) // 60)
        picked = files[::step][:60]
        for idx, rf in enumerate(picked):
            quoted = "/".join(urllib.parse.quote(seg) for seg in rf.split("/"))
            url = f"https://huggingface.co/datasets/c2p-cmd/hass_avocado/resolve/main/{quoted}"
            tasks.append((f"hass_avo_{idx:03d}", "avocado", url, "dish"))
        print(f"[c2p-cmd/hass_avocado] Da lap {len(picked)} anh.")
        return len(picked)
    except Exception as exc:
        print(f"[hass_avocado warn] {exc}")
        return 0


def _fetch_wikimedia_category_oatmeal(
    img_out: Path,
    lbl_out: Path,
    cls_idx: int,
    limit: int = 35,
) -> int:
    import time
    import urllib.parse

    skip = ("box", "package", "diagram", "logo", "label", "coat", "flag")
    u = "https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Oatmeal&cmtype=file&cmlimit=50&format=json"
    saved = 0
    try:
        res = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "VigorAI-Research/1.6"}), timeout=15).read().decode("utf-8"))
        titles = [
            m["title"] for m in (res.get("query") or {}).get("categorymembers", [])
            if m.get("title", "").lower().endswith((".jpg", ".jpeg", ".png"))
            and not any(w in m.get("title", "").lower() for w in skip)
        ][:limit]
        for idx, title in enumerate(titles):
            time.sleep(0.3)
            iu = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&iiurlwidth=640&format=json"
            ires = json.loads(urllib.request.urlopen(urllib.request.Request(iu, headers={"User-Agent": "VigorAI-Research/1.6"}), timeout=15).read().decode("utf-8"))
            page = next(iter((ires.get("query") or {}).get("pages", {}).values()), {})
            img_url = ((page.get("imageinfo") or [{}])[0]).get("thumburl") or ((page.get("imageinfo") or [{}])[0]).get("url")
            if not img_url:
                continue
            time.sleep(0.3)
            raw = urllib.request.urlopen(urllib.request.Request(img_url, headers={"User-Agent": "VigorAI-Research/1.6"}), timeout=15).read()
            with Image.open(io.BytesIO(raw)) as im:
                rgb = im.convert("RGB")
                if not _is_clean_beverage_image(rgb):
                    continue
                if max(rgb.size) > 720:
                    rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
                xc, yc, bw, bh = estimate_dish_bbox(rgb)
                stem = f"wikicat_oatmeal_{idx:03d}"
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=90)
                (lbl_out / f"{stem}.txt").write_text(f"{cls_idx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n", encoding="utf-8")
                saved += 1
    except Exception as exc:
        print(f"[Wiki Category:Oatmeal warn] {exc}")
    print(f"[Wikimedia Category:Oatmeal] Da luu bo sung {saved} anh.")
    return saved


def fetch_v16_missing_foods_drinks(
    raw_dir: Path,
    cache_dir: Path,
    force: bool = False,
) -> Path:
    """Tai du lieu sach tu HF curated datasets + stperez + OFF cho 16 lop v1.6."""
    import urllib.parse
    from concurrent.futures import ThreadPoolExecutor, as_completed

    out_dir = raw_dir / "v16-foods-drinks"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    names = [
        "brown rice",
        "sweet potato",
        "avocado",
        "cucumber",
        "cherry-tomato",
        "lean-pork",
        "almonds",
        "oatmeal",
        "greek-yogurt",
        "whey-shake",
        "drink-coconut-water",
        "drink-yogurt-probiotic",
        "drink-beer",
        "drink-citrus-soda",
        "drink-bottled-coffee",
        "drink-sports-isotonic",
    ]
    name_to_idx = {n: i for i, n in enumerate(names)}
    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    per_class_files: Counter = Counter()

    # (stem, target_cls, url, mode: 'dish' | 'pkg')
    tasks: list[tuple[str, str, str, str]] = []

    # 1. stperez/beverages Beer folders (MIT)
    try:
        req = urllib.request.Request(STPEREZ_TREE_URL, headers={"User-Agent": "VigorAI-DatasetFetcher/1.6"})
        tree = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
        by_folder: dict[str, list[str]] = {}
        for sib in tree.get("siblings", []):
            rf = sib.get("rfilename", "")
            if not rf.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            for folder in V16_BEER_FOLDERS:
                if rf.startswith(folder + "/"):
                    by_folder.setdefault(folder, []).append(rf)
                    break
        for folder, cap in V16_BEER_FOLDERS.items():
            files = sorted(by_folder.get(folder, []))[:cap]
            tag = folder.rsplit("/", 1)[-1].lower()
            for idx, rf in enumerate(files):
                quoted = "/".join(urllib.parse.quote(seg) for seg in rf.split("/"))
                tasks.append((f"stpz_{tag}_{idx}", "drink-beer", f"{STPEREZ_RAW_BASE}/{quoted}", "pkg"))
        print(f"[stperez/beverages Beer] Da lap {sum(1 for t in tasks if t[1] == 'drink-beer')} anh.")
    except Exception as exc:
        print(f"[stperez Beer warn] {exc}")

    # 2. Curated HuggingFace datasets (Nutrition5k, Food_Ingredients, Food101 pork_chop, Hass Avocado, LVIS)
    n5k_added = _collect_n5k_tasks(tasks)
    _collect_food_ingredients_tasks(tasks)
    _collect_food101_pork_tasks(tasks)
    _collect_hass_avocado_tasks(tasks)
    lvis_items = _collect_lvis_yolo_items(cache_dir, name_to_idx)

    # 3. Open Food Facts Search v3 (chay song song 8 luong, timeout=10s de tranh nghen)
    seen_off: set[str] = set()
    off_added = 0
    off_oatmeal = 0
    off_jobs = [(target_cls, q, cap) for target_cls, q_list in V16_OFF_QUERIES.items() for q, cap in q_list]

    def _fetch_off_q(job: tuple[str, str, int]) -> tuple[str, str, int, list[dict]]:
        tcls, q, cap = job
        try:
            u = f"{OFF_SEARCH_BASE}?q={urllib.parse.quote(q)}&page_size={min(100, cap * 2)}"
            req = urllib.request.Request(u, headers={"User-Agent": "VigorAI-Research/1.6 (https://github.com/HPhucTV/VigorAI)"})
            res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace"))
            return tcls, q, cap, res.get("hits", [])
        except Exception as exc:
            print(f"  [OFF warn] {q}: {exc}", flush=True)
            return tcls, q, cap, []

    with ThreadPoolExecutor(max_workers=8) as off_pool:
        for target_cls, q, cap, hits in off_pool.map(_fetch_off_q, off_jobs):
            added = 0
            for hit in hits:
                if added >= cap:
                    break
                if not _is_valid_v16_off_hit(hit, target_cls):
                    continue
                code = str(hit.get("code") or "").strip()
                if not code or code in seen_off:
                    continue
                img_url = _off_front_url(hit)
                if not img_url:
                    continue
                seen_off.add(code)
                q_tag = "".join(ch for ch in q if ch.isalnum())[:12]
                tasks.append((f"off16_{q_tag}_{code}", target_cls, img_url, "pkg"))
                added += 1
                off_added += 1
                if target_cls == "oatmeal":
                    off_oatmeal += 1
    print(f"[OpenFoodFacts v1.6] Da lap {off_added} anh (tong URL HF+OFF={len(tasks)} + LVIS={len(lvis_items)}).", flush=True)

    def _dl(item: tuple[int, str, str, str, str]) -> tuple[int, str, str, str, bytes | None]:
        idx, stem, target_cls, url, mode = item
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-Research/1.6 (https://github.com/HPhucTV/VigorAI)"})
            return idx, stem, target_cls, mode, urllib.request.urlopen(req, timeout=18).read()
        except Exception:
            return idx, stem, target_cls, mode, None

    errors = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(_dl, (i, st, cls, u, m)) for i, (st, cls, u, m) in enumerate(tasks)]
        for idx, fut in enumerate(as_completed(futs), 1):
            _i, stem, target_cls, mode, raw_bytes = fut.result()
            if not raw_bytes:
                errors += 1
                continue
            try:
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    if mode == "pkg":
                        rgb, bbox = estimate_beverage_bbox(im, bg_idx=idx)
                    else:
                        rgb = im.convert("RGB")
                        bbox = estimate_dish_bbox(rgb)
            except Exception:
                errors += 1
                continue
            if not _is_clean_beverage_image(rgb):
                continue
            if max(rgb.size) > 720:
                rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
            if mode == "pkg":
                n_saved = _save_with_optional_white_studio(
                    rgb=rgb,
                    bbox=bbox,
                    cls_idx=name_to_idx[target_cls],
                    stem=stem,
                    img_out=img_out,
                    lbl_out=lbl_out,
                    bg_seed=idx,
                    indoor_bg=(target_cls in ("drink-citrus-soda", "drink-yogurt-probiotic", "drink-beer", "whey-shake", "drink-bottled-coffee", "drink-sports-isotonic")),
                )
            else:
                xc, yc, bw, bh = bbox
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=90)
                (lbl_out / f"{stem}.txt").write_text(
                    f"{name_to_idx[target_cls]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n",
                    encoding="utf-8",
                )
                n_saved = 1
            per_class_files[target_cls] += n_saved
            if idx % 250 == 0:
                print(f"  ... da xu ly {idx}/{len(tasks)} URLs | da luu={sum(per_class_files.values())}", flush=True)

    # Download LVIS bounding-box images sequentially/parallel without rate-limit risk
    def _dl_lvis(item: tuple[str, str, list[str], str]) -> tuple[str, list[str], str, bytes | None]:
        stem, url, lines, primary = item
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-Research/1.6"})
            return stem, lines, primary, urllib.request.urlopen(req, timeout=18).read()
        except Exception:
            return stem, lines, primary, None

    lvis_saved = 0
    with ThreadPoolExecutor(max_workers=12) as pool:
        for stem, lines, primary, raw_bytes in pool.map(_dl_lvis, lvis_items):
            if not raw_bytes:
                errors += 1
                continue
            try:
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    rgb = im.convert("RGB")
                if min(rgb.size) < 80:
                    continue
                if max(rgb.size) > 720:
                    rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=90)
                (lbl_out / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
                per_class_files[primary] += 1
                lvis_saved += 1
            except Exception:
                errors += 1
    print(f"[LVIS saved] {lvis_saved}/{len(lvis_items)} anh bbox chuan.")

    # Optional Wikimedia Category:Oatmeal supplement if oatmeal < 100
    if per_class_files["oatmeal"] < 100:
        oat_extra = _fetch_wikimedia_category_oatmeal(img_out, lbl_out, name_to_idx["oatmeal"], limit=35)
        per_class_files["oatmeal"] += oat_extra

    _write_yolo_dataset_yaml(out_dir, names)
    summary = {
        "sources": [
            "stperez/beverages Beer (MIT)",
            "TeeA/nutrition5k-food-name-gemini",
            "henningheyen/LVIS_Fruits_And_Vegetables (Apache-2.0)",
            "SunnyAgarwal4274/Food_Ingredients (CC-BY-4.0)",
            "ethz/food101 pork_chop",
            "c2p-cmd/hass_avocado",
            "Wikimedia Commons Category:Oatmeal (CC-BY / CC0)",
            "Open Food Facts Search v3 (CC-BY-SA-3.0)",
        ],
        "urls_attempted": len(tasks) + len(lvis_items),
        "download_or_decode_errors": errors,
        "images_saved": sum(per_class_files.values()),
        "per_class_images": dict(per_class_files),
    }
    (out_dir / "extract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[OK] v16-foods-drinks extract:", json.dumps(summary, ensure_ascii=False))
    return out_dir


V17_VN_COMBINED_KEEP: set[str] = {
    "bo-luc-lac", "bo-ne", "ga-hap-la-chanh",
    "banh-beo", "banh-bot-loc", "banh-duc", "banh-trang-nuong",
    "bo-kho", "ca-ri-ga", "bun-mam", "bun-cha-ca", "banh-da-cua",
    "nem-chua", "nem-nuong-nha-trang", "bo-la-lot", "sup-cua",
    "ca-loc-nuong", "ca-sot-ca-chua", "cha-ca-la-vong",
    "trung-vit-lon", "cut-lon-xao-me",
    "oc-buou-hap", "oc-huong-xao", "oc-len-xao-dua", "cua-hap-bia",
    "banh-pia", "banh-trung-thu", "banh-troi-nuoc", "banh-da-lon", "banh-bo",
    "nui-xao", "tau-hu-non", "tau-hu-nhoi-thit", "cha-com",
    "xoi-gac", "xoi-nep-than", "xoi-xeo", "chao-long", "chao-vit",
}

V17_VN_EXTRA_SHARDS = (
    ("val0", "data/validation-00000-of-00002.parquet"),
    ("val1", "data/validation-00001-of-00002.parquet"),
    ("test0", "data/test-00000-of-00002.parquet"),
    ("test1", "data/test-00001-of-00002.parquet"),
)

V17_VN_TRAIN_SHARDS = (
    ("tr0", "data/train-00000-of-00008.parquet"),
    ("tr6", "data/train-00006-of-00008.parquet"),
)

TUYENTRUNGLE_VAL_URL = "https://huggingface.co/datasets/TuyenTrungLe/vietnamese_food_images/resolve/main/data/validation-00000-of-00001.parquet"
TUYENTRUNGLE_KEEP_BY_IDX: dict[int, str] = {
    0: "banh-beo",
    1: "banh-bot-loc",
    5: "banh-cuon",
    6: "banh-duc",
    7: "banh-gio",
    10: "banh-pia",
    12: "banh-trang-nuong",
    15: "bun-dau-mam-tom",
    16: "bun-mam",
    22: "chao-long",
    27: "nem-chua",
    29: "xoi-xeo",
}

V17_FOOD_ING_FOLDERS: dict[str, tuple[str, int]] = {
    "Watermelon": ("watermelon", 90),
    "Orange": ("orange-citrus", 75),
    "Mango": ("mango", 90),
    "Pineapple": ("pineapple", 100),
    "Grapes": ("grapes", 100),
    "Dragon_fruit": ("dragon-fruit", 65),
    "Strawberry": ("strawberry-berry", 85),
    "Blueberry": ("strawberry-berry", 40),
    "Corn": ("corn-boiled", 90),
    "Sweetcorn": ("corn-boiled", 90),
    "Carrot": ("carrot-veg", 85),
    "Cabbage": ("cabbage-spinach", 95),
    "Spinach": ("cabbage-spinach", 95),
    "Apple": ("apple", 70),
    "Banana": ("banana", 75),
    "Broccoli": ("broccoli", 80),
}

V17_LVIS_CLASS_MAP: dict[int, str] = {
    14: "carrot-veg",
    21: "orange-citrus",
    23: "corn-boiled",
    30: "strawberry-berry",
    32: "grapes",
    40: "orange-citrus",
    44: "orange-citrus",
    51: "pineapple",
    57: "strawberry-berry",
    61: "watermelon",
}

V17_LVIS_CAPS: dict[str, int] = {
    "carrot-veg": 120,
    "orange-citrus": 170,
    "corn-boiled": 40,
    "strawberry-berry": 85,
    "grapes": 15,
    "pineapple": 50,
    "watermelon": 35,
}

V17_OFF_QUERIES: dict[str, list[tuple[str, int]]] = {
    "tuna-canned": [("canned tuna", 60), ("tuna in water", 50), ("tuna chunks", 50), ("starkist tuna", 40), ("rio mare", 40)],
    "peanut-butter": [("peanut butter", 70), ("skippy peanut butter", 45), ("jif peanut butter", 45), ("crunchy peanut butter", 45)],
    "whole-wheat-bread": [("whole wheat bread", 65), ("wholemeal bread", 55), ("whole grain bread", 55), ("multigrain bread", 45)],
    "drink-soy-nut-milk": [("soy milk", 65), ("soymilk", 50), ("vinasoy", 30), ("fami", 30), ("almond milk", 55), ("oat milk", 50), ("vitasoy", 45)],
    "drink-kombucha-herbal": [("kombucha", 80), ("gt kombucha", 45), ("remedy kombucha", 45), ("herbal tea can", 45), ("winter melon tea", 35)],
    "drink-wine-cider": [("red wine", 65), ("white wine", 55), ("apple cider", 55), ("somersby", 40)],
}


def _is_valid_v17_off_hit(hit: dict, target_cls: str) -> bool:
    text = f"{hit.get('product_name') or ''} {hit.get('brands') or ''}".lower()
    if target_cls == "tuna-canned":
        return not any(w in text for w in ("cat", "pet", "dog", "whiskas", "fancy feast", "friskies"))
    if target_cls == "peanut-butter":
        return not any(w in text for w in ("reese", "cup", "cookie", "bar", "candy", "chocolate", "wafer"))
    if target_cls == "whole-wheat-bread":
        return not any(w in text for w in ("crumb", "flour", "cracker", "pasta", "tortilla"))
    if target_cls in ("drink-soy-nut-milk", "drink-kombucha-herbal"):
        return _is_valid_off_rtd_hit(hit)
    if target_cls == "drink-wine-cider":
        return "vinegar" not in text
    return True


def fetch_v17_missing_foods_drinks(
    raw_dir: Path,
    cache_dir: Path,
    force: bool = False,
) -> Path:
    """Tai du lieu sach cho 31 lop moi + bo sung yeu v1.7 (Mon Viet, Gym, Trai cay, Rau cu, Do uong)."""
    import urllib.parse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import pyarrow.parquet as pq

    out_dir = raw_dir / "v17-foods-drinks"
    if (out_dir / "data.yaml").is_file() and not force:
        print(f"[SKIP] Da tao san: {out_dir}")
        return out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)

    names = sorted(
        V17_VN_COMBINED_KEEP
        | set(TUYENTRUNGLE_KEEP_BY_IDX.values())
        | {cls for cls, _ in V17_FOOD_ING_FOLDERS.values()}
        | set(V17_LVIS_CLASS_MAP.values())
        | set(V17_OFF_QUERIES.keys())
    )
    name_to_idx = {n: i for i, n in enumerate(names)}
    img_out = out_dir / "images"
    lbl_out = out_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    per_class_files: Counter = Counter()

    def _save_dish(rgb: Image.Image, stem: str, cname: str) -> None:
        if max(rgb.size) > 720:
            rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
        xc, yc, bw, bh = estimate_dish_bbox(rgb)
        rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=88)
        (lbl_out / f"{stem}.txt").write_text(
            f"{name_to_idx[cname]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n",
            encoding="utf-8",
        )
        per_class_files[cname] += 1

    # 1. jeandeanny/vn-food-combined-2026 (val+test, them train0/train6 neu nhan < 90, xoa parquet ngay)
    vn_counts: Counter = Counter()
    vn_scanned = 0

    def _scan_jeandeanny_shard(split_tag: str, rel_path: str) -> None:
        nonlocal vn_scanned
        pq_path = download_file(f"{VN_COMBINED_BASE}/{rel_path}", cache_dir / "vn_food_combined_v17" / Path(rel_path).name)
        try:
            pf = pq.ParquetFile(pq_path)
            for batch in pf.iter_batches(batch_size=128):
                for row in batch.to_pylist():
                    vn_scanned += 1
                    raw_lbl = row.get("label")
                    cname = (
                        VN_COMBINED_CLASSES[raw_lbl]
                        if isinstance(raw_lbl, int) and 0 <= raw_lbl < len(VN_COMBINED_CLASSES)
                        else str(raw_lbl or "").strip().lower()
                    )
                    if cname not in V17_VN_COMBINED_KEEP or vn_counts[cname] >= 130:
                        continue
                    try:
                        rgb = _open_hf_image(row["image"]).convert("RGB")
                    except Exception:
                        continue
                    if min(rgb.size) < 120:
                        continue
                    _save_dish(rgb, f"vn17_{split_tag}_{vn_scanned}", cname)
                    vn_counts[cname] += 1
        finally:
            try:
                pq_path.unlink(missing_ok=True)
            except OSError:
                pass
        print(f"  [jeandeanny] {Path(rel_path).name} -> tong luu={sum(vn_counts.values())}", flush=True)

    for st, rp in V17_VN_EXTRA_SHARDS:
        _scan_jeandeanny_shard(st, rp)
    if any(vn_counts[c] < 90 for c in V17_VN_COMBINED_KEEP):
        for st, rp in V17_VN_TRAIN_SHARDS:
            if all(vn_counts[c] >= 90 for c in V17_VN_COMBINED_KEEP):
                break
            _scan_jeandeanny_shard(st, rp)
    print(f"[jeandeanny v1.7] Da luu {sum(vn_counts.values())} anh qua {len(vn_counts)} nhan VN.", flush=True)

    # 2. TuyenTrungLe/vietnamese_food_images validation shard (443 MB -> xoa ngay)
    ttl_pq = download_file(TUYENTRUNGLE_VAL_URL, cache_dir / "tuyentrungle_v17" / "validation-00000-of-00001.parquet")
    ttl_counts: Counter = Counter()
    try:
        pf = pq.ParquetFile(ttl_pq)
        for idx_b, batch in enumerate(pf.iter_batches(batch_size=128)):
            for row_i, row in enumerate(batch.to_pylist()):
                lbl = row.get("label")
                if not isinstance(lbl, int) or lbl not in TUYENTRUNGLE_KEEP_BY_IDX:
                    continue
                cname = TUYENTRUNGLE_KEEP_BY_IDX[lbl]
                if ttl_counts[cname] >= 85:
                    continue
                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                except Exception:
                    continue
                if min(rgb.size) < 120:
                    continue
                _save_dish(rgb, f"ttl17_{idx_b}_{row_i}", cname)
                ttl_counts[cname] += 1
    finally:
        try:
            ttl_pq.unlink(missing_ok=True)
        except OSError:
            pass
    print(f"[TuyenTrungLe] Da luu {sum(ttl_counts.values())} anh: {dict(ttl_counts)}", flush=True)

    # 3. Collect parallel URL tasks from SunnyAgarwal4274/Food_Ingredients + OpenFoodFacts
    tasks: list[tuple[str, str, str, str]] = []
    fi_added: Counter = Counter()
    try:
        info = json.loads(urllib.request.urlopen("https://huggingface.co/api/datasets/SunnyAgarwal4274/Food_Ingredients", timeout=20).read().decode("utf-8"))
        for sib in info.get("siblings", []):
            rf = sib.get("rfilename", "")
            if not rf.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            parts = rf.split("/")
            if len(parts) < 3 or parts[0] not in ("Train", "Test", "Validation"):
                continue
            spec = V17_FOOD_ING_FOLDERS.get(parts[1])
            if not spec:
                continue
            target_cls, cap = spec
            key_c = f"{parts[1]}"
            if fi_added[key_c] >= cap:
                continue
            quoted = "/".join(urllib.parse.quote(seg) for seg in rf.split("/"))
            url = f"https://huggingface.co/datasets/SunnyAgarwal4274/Food_Ingredients/resolve/main/{quoted}"
            tasks.append((f"fi17_{parts[1].lower()}_{fi_added[key_c]:03d}", target_cls, url, "dish"))
            fi_added[key_c] += 1
    except Exception as exc:
        print(f"[Food_Ingredients v17 warn] {exc}", flush=True)
    print(f"[Food_Ingredients v17] Da lap {sum(fi_added.values())} anh: {dict(fi_added)}", flush=True)

    seen_off: set[str] = set()
    off_added = 0
    off_jobs = [(tcls, q, cap) for tcls, qlist in V17_OFF_QUERIES.items() for q, cap in qlist]

    def _fetch_off_q(job: tuple[str, str, int]) -> tuple[str, str, int, list[dict]]:
        tcls, q, cap = job
        try:
            u = f"{OFF_SEARCH_BASE}?q={urllib.parse.quote(q)}&page_size={min(100, cap * 2)}"
            req = urllib.request.Request(u, headers={"User-Agent": "VigorAI-Research/1.7 (https://github.com/HPhucTV/VigorAI)"})
            res = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="replace"))
            return tcls, q, cap, res.get("hits", [])
        except Exception as exc:
            print(f"  [OFF17 warn] {q}: {exc}", flush=True)
            return tcls, q, cap, []

    with ThreadPoolExecutor(max_workers=8) as off_pool:
        for tcls, q, cap, hits in off_pool.map(_fetch_off_q, off_jobs):
            added = 0
            for hit in hits:
                if added >= cap:
                    break
                if not _is_valid_v17_off_hit(hit, tcls):
                    continue
                code = str(hit.get("code") or "").strip()
                if not code or code in seen_off:
                    continue
                img_url = _off_front_url(hit)
                if not img_url:
                    continue
                seen_off.add(code)
                q_tag = "".join(ch for ch in q if ch.isalnum())[:12]
                tasks.append((f"off17_{q_tag}_{code}", tcls, img_url, "pkg"))
                added += 1
                off_added += 1
    print(f"[OpenFoodFacts v1.7] Da lap {off_added} anh (tong URL HF+OFF={len(tasks)}).", flush=True)

    lvis_items = _collect_lvis_yolo_items(
        cache_dir=cache_dir,
        name_to_idx=name_to_idx,
        class_map=V17_LVIS_CLASS_MAP,
        min_area=0.03,
        per_class_cap=V17_LVIS_CAPS,
        stem_prefix="lvis17",
        max_boxes_per_image=1,
    )

    def _dl(item: tuple[int, str, str, str, str]) -> tuple[int, str, str, str, bytes | None]:
        idx, stem, target_cls, url, mode = item
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-Research/1.7 (https://github.com/HPhucTV/VigorAI)"})
            return idx, stem, target_cls, mode, urllib.request.urlopen(req, timeout=18).read()
        except Exception:
            return idx, stem, target_cls, mode, None

    errors = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(_dl, (i, st, cls, u, m)) for i, (st, cls, u, m) in enumerate(tasks)]
        for idx, fut in enumerate(as_completed(futs), 1):
            _i, stem, target_cls, mode, raw_bytes = fut.result()
            if not raw_bytes:
                errors += 1
                continue
            try:
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    if mode == "pkg":
                        rgb, bbox = estimate_beverage_bbox(im, bg_idx=idx)
                    else:
                        rgb = im.convert("RGB")
                        bbox = estimate_dish_bbox(rgb)
            except Exception:
                errors += 1
                continue
            if not _is_clean_beverage_image(rgb):
                continue
            if max(rgb.size) > 720:
                rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
            if mode == "pkg":
                n_saved = _save_with_optional_white_studio(
                    rgb=rgb,
                    bbox=bbox,
                    cls_idx=name_to_idx[target_cls],
                    stem=stem,
                    img_out=img_out,
                    lbl_out=lbl_out,
                    bg_seed=idx,
                    indoor_bg=target_cls.startswith("drink-"),
                )
                per_class_files[target_cls] += n_saved
            else:
                xc, yc, bw, bh = bbox
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=88)
                (lbl_out / f"{stem}.txt").write_text(
                    f"{name_to_idx[target_cls]} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n",
                    encoding="utf-8",
                )
                per_class_files[target_cls] += 1
            if idx % 300 == 0:
                print(f"  ... v17 da xu ly {idx}/{len(tasks)} URLs | tong={sum(per_class_files.values())}", flush=True)

    def _dl_lvis(item: tuple[str, str, list[str], str]) -> tuple[str, list[str], str, bytes | None]:
        stem, url, lines, primary = item
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VigorAI-Research/1.7"})
            return stem, lines, primary, urllib.request.urlopen(req, timeout=18).read()
        except Exception:
            return stem, lines, primary, None

    lvis_saved = 0
    with ThreadPoolExecutor(max_workers=12) as pool:
        for stem, lines, primary, raw_bytes in pool.map(_dl_lvis, lvis_items):
            if not raw_bytes:
                errors += 1
                continue
            try:
                with Image.open(io.BytesIO(raw_bytes)) as im:
                    rgb = im.convert("RGB")
                if min(rgb.size) < 80:
                    continue
                if max(rgb.size) > 720:
                    rgb.thumbnail((720, 720), Image.Resampling.LANCZOS)
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=90)
                (lbl_out / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
                per_class_files[primary] += 1
                lvis_saved += 1
            except Exception:
                errors += 1
    print(f"[LVIS v17 saved] {lvis_saved}/{len(lvis_items)} anh bbox chuan.", flush=True)

    _write_yolo_dataset_yaml(out_dir, names)
    summary = {
        "sources": [
            "jeandeanny/vn-food-combined-2026 (CC-BY-NC-SA-4.0)",
            "TuyenTrungLe/vietnamese_food_images",
            "SunnyAgarwal4274/Food_Ingredients (CC-BY-4.0)",
            "henningheyen/LVIS_Fruits_And_Vegetables (Apache-2.0)",
            "Open Food Facts Search v3 (CC-BY-SA-3.0)",
        ],
        "urls_attempted": len(tasks) + len(lvis_items),
        "download_or_decode_errors": errors,
        "images_saved": sum(per_class_files.values()),
        "per_class_images": dict(per_class_files),
    }
    (out_dir / "extract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[OK] v17-foods-drinks extract:", json.dumps(summary, ensure_ascii=False), flush=True)
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tai dataset mo cho AI Model B (T-M4-01, T-M4-09)")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument(
        "--only",
        choices=("all", "vn-streetfood", "foodseg103", "drinks-snacks", "soda-bottles", "coco-val", "matthijs-snacks", "vn-food-combined", "branded-beverages", "v16-foods-drinks", "v17-foods-drinks"),
        default="all",
    )
    parser.add_argument("--max-per-class", type=int, default=260)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.only in ("all", "vn-streetfood"):
        fetch_vn_streetfood(args.raw_dir, args.cache_dir, force=args.force)
    if args.only in ("all", "foodseg103", "drinks-snacks"):
        fetch_foodseg103(args.raw_dir, args.cache_dir, max_per_class=args.max_per_class, force=args.force)
    if args.only in ("all", "drinks-snacks", "soda-bottles"):
        fetch_soda_bottles(args.raw_dir, args.cache_dir, max_images=max(400, args.max_per_class), force=args.force)
    if args.only in ("all", "drinks-snacks", "coco-val"):
        fetch_coco_val_drinks_snacks(args.raw_dir, args.cache_dir, max_per_class=args.max_per_class, force=args.force)
    if args.only in ("all", "drinks-snacks", "matthijs-snacks"):
        fetch_matthijs_snacks(args.raw_dir, args.cache_dir, max_per_class=args.max_per_class, force=args.force)
    if args.only in ("all", "vn-food-combined"):
        fetch_vn_food_combined(args.raw_dir, args.cache_dir, max_per_class=min(180, args.max_per_class), force=args.force)
    if args.only in ("all", "drinks-snacks", "branded-beverages"):
        fetch_branded_beverages(args.raw_dir, args.cache_dir, force=args.force)
    if args.only in ("all", "v16-foods-drinks"):
        fetch_v16_missing_foods_drinks(args.raw_dir, args.cache_dir, force=args.force)
    if args.only in ("all", "v17-foods-drinks"):
        fetch_v17_missing_foods_drinks(args.raw_dir, args.cache_dir, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
