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

    saved = 0
    for split_tag, rel_path in SODA_BOTTLES_FILES:
        if max_images > 0 and saved >= max_images:
            break
        pq_path = download_file(
            f"{SODA_BOTTLES_BASE}/{rel_path}",
            cache_dir / "soda_bottles" / Path(rel_path).name,
        )
        pf = pq.ParquetFile(pq_path)
        for batch in pf.iter_batches(batch_size=128):
            for row in batch.to_pylist():
                if max_images > 0 and saved >= max_images:
                    break
                try:
                    rgb = _open_hf_image(row["image"]).convert("RGB")
                    img_w, img_h = rgb.size
                    w = float(row.get("width") or img_w)
                    h = float(row.get("height") or img_h)
                    objs = row.get("objects") or {}
                    bboxes = objs.get("bbox") or []
                except Exception:
                    continue
                if w <= 0 or h <= 0 or not bboxes:
                    continue
                yolo_lines: list[str] = []
                for box in bboxes:
                    if len(box) < 4:
                        continue
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
                    yolo_lines.append(f"0 {(x1 + x2) / 2.0:.6f} {(y1 + y2) / 2.0:.6f} {bw:.6f} {bh:.6f}")
                if not yolo_lines:
                    continue
                stem = f"sb_{split_tag}_{row.get('image_id', saved)}_{saved}"
                rgb.save(img_out / f"{stem}.jpg", format="JPEG", quality=92)
                (lbl_out / f"{stem}.txt").write_text("\n".join(yolo_lines) + "\n", encoding="utf-8")
                saved += 1

    _write_yolo_dataset_yaml(out_dir, ["soda-bottles"])
    print(f"[OK] soda-bottles extract: {saved} anh")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tai dataset mo cho AI Model B (T-M4-01, T-M4-09)")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument(
        "--only",
        choices=("all", "vn-streetfood", "foodseg103", "drinks-snacks", "soda-bottles", "coco-val", "matthijs-snacks"),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
