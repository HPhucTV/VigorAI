# [OWNER: M4] Loc, gop nhan, kiem tra va chia dataset YOLO cho AI Model B v1.0 (T-M4-01)
"""Bien cac dataset tai tu Roboflow Universe / Kaggle (dinh dang YOLO) thanh 1 dataset chuan.

Cac buoc: doc nhan -> gop ve 18 class_code (food_classes.py) -> bo bbox loi/lech chuan ->
bo anh trung (SHA-1) -> chia 70/20/10 co phan tang -> ghi data.yaml + dataset_report.json.

Vi du:
    python prepare_dataset.py \\
        --src ../datasets/raw/vietnamese-food --src ../datasets/raw/gym-meals \\
        --out ../datasets/model_b_v1

    python prepare_dataset.py --validate-only --out ../datasets/model_b_v1

Moi nguon la thu muc xuat YOLO (Roboflow "YOLOv8") co data.yaml (hoac classes.txt) va cac
thu muc images/labels theo bat ky bo cuc nao (train/valid/test hoac images/ + labels/).
Chi dung thu vien chuan cua Python.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from food_classes import CLASS_CODES, resolve_class

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLIT_RATIOS = (0.70, 0.20, 0.10)  # train / val / test
SPLIT_NAMES = ("train", "val", "test")
MIN_BOX_SIDE = 0.005  # canh bbox chuan hoa nho hon nguong nay coi la lech chuan
CLIP_TOLERANCE = 0.005  # cho phep tran bien toi da 0.5% roi cat ve [0, 1]
MIN_CLASSES, MAX_CLASSES = 15, 20


# --------------------------------------------------------------------------- #
# Doc ten lop
# --------------------------------------------------------------------------- #
def parse_names(yaml_text: str) -> list[str]:
    """Doc khoa `names` cua data.yaml: dang list [..], danh sach '- x' hoac dict '0: x'."""
    lines = yaml_text.splitlines()
    for i, raw in enumerate(lines):
        if not raw.startswith("names:"):
            continue
        rest = raw[len("names:"):].strip()
        if rest.startswith("["):
            inner = rest.strip("[]")
            return [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
        items: dict[int, str] = {}
        seq: list[str] = []
        for line in lines[i + 1:]:
            if not line.strip():
                continue
            if not line.startswith((" ", "\t", "-")):
                break
            stripped = line.strip()
            if stripped.startswith("- "):
                seq.append(stripped[2:].strip().strip("'\""))
            elif ":" in stripped:
                key, _, value = stripped.partition(":")
                if key.strip().isdigit():
                    items[int(key)] = value.strip().strip("'\"")
        if seq:
            return seq
        if items:
            return [items[k] for k in sorted(items)]
    return []


def load_source_names(src: Path) -> list[str]:
    data_yaml = src / "data.yaml"
    if data_yaml.is_file():
        names = parse_names(data_yaml.read_text(encoding="utf-8"))
        if names:
            return names
    classes_txt = src / "classes.txt"
    if classes_txt.is_file():
        return [ln.strip() for ln in classes_txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
    raise SystemExit(f"[LOI] {src}: khong tim thay data.yaml (khoa names) hoac classes.txt")


# --------------------------------------------------------------------------- #
# Nhan YOLO
# --------------------------------------------------------------------------- #
def label_path_for(image: Path) -> Path | None:
    parts = list(image.parts)
    if "images" in parts:
        idx = len(parts) - 1 - parts[::-1].index("images")
        candidate = Path(*parts[:idx], "labels", *parts[idx + 1:]).with_suffix(".txt")
        if candidate.is_file():
            return candidate
    same_dir = image.with_suffix(".txt")
    return same_dir if same_dir.is_file() else None


def _box_from_tokens(tokens: list[str]) -> tuple[float, float, float, float] | None:
    """5 token -> (xc, yc, w, h); nhieu hon 5 token (polygon) -> bbox bao quanh."""
    try:
        nums = [float(t) for t in tokens[1:]]
    except ValueError:
        return None
    if len(nums) == 4:
        return nums[0], nums[1], nums[2], nums[3]
    if len(nums) >= 6 and len(nums) % 2 == 0:
        xs, ys = nums[0::2], nums[1::2]
        x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
        return (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
    return None


def normalize_box(box: tuple[float, float, float, float]) -> tuple[float, float, float, float] | None:
    xc, yc, w, h = box
    x1, x2 = xc - w / 2, xc + w / 2
    y1, y2 = yc - h / 2, yc + h / 2
    if min(x1, y1) < -CLIP_TOLERANCE or max(x2, y2) > 1 + CLIP_TOLERANCE:
        return None
    x1, y1, x2, y2 = (max(0.0, x1), max(0.0, y1), min(1.0, x2), min(1.0, y2))
    nw, nh = x2 - x1, y2 - y1
    if nw < MIN_BOX_SIDE or nh < MIN_BOX_SIDE:
        return None
    return (x1 + x2) / 2, (y1 + y2) / 2, nw, nh


def convert_labels(
    label_file: Path | None, names: list[str], stats: Counter, unmapped: Counter
) -> list[str]:
    if label_file is None:
        stats["images_without_label_file"] += 1
        return []
    out: list[str] = []
    for raw in label_file.read_text(encoding="utf-8", errors="replace").splitlines():
        tokens = raw.split()
        if not tokens:
            continue
        try:
            class_idx = int(tokens[0])
        except ValueError:
            stats["boxes_invalid"] += 1
            continue
        if not 0 <= class_idx < len(names):
            stats["boxes_invalid"] += 1
            continue
        code = resolve_class(names[class_idx])
        if code is None:
            unmapped[names[class_idx]] += 1
            stats["boxes_dropped_unmapped"] += 1
            continue
        raw_box = _box_from_tokens(tokens)
        box = normalize_box(raw_box) if raw_box else None
        if box is None:
            stats["boxes_invalid"] += 1
            continue
        new_idx = CLASS_CODES.index(code)
        out.append(f"{new_idx} {box[0]:.6f} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f}")
    return out


# --------------------------------------------------------------------------- #
# Gop, chia, ghi
# --------------------------------------------------------------------------- #
def collect_items(sources: list[Path]) -> tuple[list[dict], Counter, Counter]:
    stats: Counter = Counter()
    unmapped: Counter = Counter()
    seen_hashes: set[str] = set()
    items: list[dict] = []
    for src in sources:
        names = load_source_names(src)
        images = sorted(p for p in src.rglob("*") if p.suffix.lower() in IMAGE_EXTS)
        for image in images:
            stats["images_scanned"] += 1
            digest = hashlib.sha1(image.read_bytes()).hexdigest()
            if digest in seen_hashes:
                stats["images_duplicate_dropped"] += 1
                continue
            seen_hashes.add(digest)
            lines = convert_labels(label_path_for(image), names, stats, unmapped)
            if not lines:
                stats["images_dropped_no_valid_box"] += 1
                continue
            items.append({"image": image, "hash": digest, "lines": lines})
    return items, stats, unmapped


def stratified_split(items: list[dict], seed: int) -> dict[str, list[dict]]:
    """Chia 70/20/10 theo lop hiem nhat trong anh de moi lop co mat o ca 3 tap khi du anh."""
    image_count: Counter = Counter()
    for it in items:
        it["classes"] = {int(ln.split()[0]) for ln in it["lines"]}
        image_count.update(it["classes"])
    groups: dict[int, list[dict]] = defaultdict(list)
    for it in items:
        rarest = min(it["classes"], key=lambda c: (image_count[c], c))
        groups[rarest].append(it)

    rng = random.Random(seed)
    splits: dict[str, list[dict]] = {name: [] for name in SPLIT_NAMES}
    for cls in sorted(groups):
        group = groups[cls]
        rng.shuffle(group)
        n = len(group)
        if n < 3:
            splits["train"].extend(group)
            continue
        n_val = max(1, round(n * SPLIT_RATIOS[1]))
        n_test = max(1, round(n * SPLIT_RATIOS[2]))
        n_train = n - n_val - n_test
        splits["train"].extend(group[:n_train])
        splits["val"].extend(group[n_train:n_train + n_val])
        splits["test"].extend(group[n_train + n_val:])
    return splits


def write_data_yaml(out: Path) -> None:
    names_block = "\n".join(f"  {i}: {code}" for i, code in enumerate(CLASS_CODES))
    out.joinpath("data.yaml").write_text(
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        f"nc: {len(CLASS_CODES)}\n"
        f"names:\n{names_block}\n",
        encoding="utf-8",
    )


def write_dataset(splits: dict[str, list[dict]], out: Path) -> None:
    for split, items in splits.items():
        img_dir = out / "images" / split
        lbl_dir = out / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        for it in items:
            stem = f"{it['hash'][:12]}_{it['image'].stem}"
            shutil.copy2(it["image"], img_dir / f"{stem}{it['image'].suffix.lower()}")
            (lbl_dir / f"{stem}.txt").write_text("\n".join(it["lines"]) + "\n", encoding="utf-8")
    write_data_yaml(out)


def build_report(
    splits: dict[str, list[dict]], stats: Counter, unmapped: Counter, min_images: int
) -> dict:
    per_class: dict[str, dict[str, dict[str, int]]] = {}
    total_images: Counter = Counter()
    for split, items in splits.items():
        for it in items:
            for ln in it["lines"]:
                code = CLASS_CODES[int(ln.split()[0])]
                cell = per_class.setdefault(code, {}).setdefault(split, {"images": 0, "boxes": 0})
                cell["boxes"] += 1
            for cls in it["classes"]:
                per_class[CLASS_CODES[cls]][split]["images"] += 1
        total_images[split] = len(items)
    warnings = []
    for code in CLASS_CODES:
        images = sum(per_class.get(code, {}).get(s, {}).get("images", 0) for s in SPLIT_NAMES)
        if images == 0:
            warnings.append(f"{code}: KHONG co anh nao")
        elif images < min_images:
            warnings.append(f"{code}: chi co {images} anh (< {min_images} khuyen nghi)")
        else:
            missing = [s for s in SPLIT_NAMES if per_class[code].get(s, {}).get("images", 0) == 0]
            if missing:
                warnings.append(f"{code}: thieu tap {', '.join(missing)}")
    return {
        "classes": CLASS_CODES,
        "images_per_split": dict(total_images),
        "stats": dict(stats),
        "per_class": per_class,
        "unmapped_source_classes": dict(unmapped.most_common()),
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- #
# Kiem tra dataset da dung (Definition of Done T-M4-01)
# --------------------------------------------------------------------------- #
def validate_dataset(out: Path) -> list[str]:
    errors: list[str] = []
    yaml_path = out / "data.yaml"
    if not yaml_path.is_file():
        return [f"thieu {yaml_path}"]
    text = yaml_path.read_text(encoding="utf-8")
    names = parse_names(text)
    nc_line = next((ln for ln in text.splitlines() if ln.startswith("nc:")), "")
    try:
        nc = int(nc_line.split(":")[1])
    except (IndexError, ValueError):
        nc = -1
        errors.append("data.yaml thieu hoac sai 'nc'")
    if nc != len(names):
        errors.append(f"nc={nc} khong khop so ten lop {len(names)}")
    if not MIN_CLASSES <= len(names) <= MAX_CLASSES:
        errors.append(f"so lop {len(names)} ngoai khoang {MIN_CLASSES}-{MAX_CLASSES}")

    split_hashes: dict[str, set[str]] = {}
    for split in SPLIT_NAMES:
        img_dir, lbl_dir = out / "images" / split, out / "labels" / split
        if not img_dir.is_dir() or not any(img_dir.iterdir()):
            errors.append(f"tap '{split}' rong hoac khong ton tai")
            continue
        images = {p.stem: p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS}
        labels = {p.stem: p for p in lbl_dir.glob("*.txt")} if lbl_dir.is_dir() else {}
        for stem in images.keys() - labels.keys():
            errors.append(f"{split}/{stem}: anh khong co file nhan")
        for stem in labels.keys() - images.keys():
            errors.append(f"{split}/{stem}: nhan khong co anh")
        split_hashes[split] = {stem.split("_")[0] for stem in images}
        for stem, lbl in labels.items():
            lines = [ln for ln in lbl.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if not lines:
                errors.append(f"{split}/{stem}: file nhan rong")
            for ln in lines:
                tok = ln.split()
                try:
                    cls = int(tok[0])
                    xc, yc, w, h = (float(t) for t in tok[1:])
                except (ValueError, IndexError):
                    errors.append(f"{split}/{stem}: dong sai dinh dang '{ln}'")
                    continue
                if len(tok) != 5 or not 0 <= cls < len(names):
                    errors.append(f"{split}/{stem}: class/so truong sai '{ln}'")
                elif not (0 <= xc - w / 2 and xc + w / 2 <= 1 + 1e-6 and 0 <= yc - h / 2 and yc + h / 2 <= 1 + 1e-6):
                    errors.append(f"{split}/{stem}: bbox ra ngoai khung '{ln}'")
                elif w < MIN_BOX_SIDE or h < MIN_BOX_SIDE:
                    errors.append(f"{split}/{stem}: bbox lech chuan (qua nho) '{ln}'")
    names_seen = list(split_hashes)
    for i, a in enumerate(names_seen):
        for b in names_seen[i + 1:]:
            overlap = split_hashes[a] & split_hashes[b]
            if overlap:
                errors.append(f"ro ri du lieu: {len(overlap)} anh trung giua '{a}' va '{b}'")
    return errors


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", type=Path, action="append", default=[], help="thu muc dataset YOLO nguon (lap lai nhieu lan)")
    parser.add_argument("--out", type=Path, required=True, help="thu muc dau ra (nen nam trong ai_research/datasets/)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-images-per-class", type=int, default=100)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    if not args.validate_only:
        if not args.src:
            parser.error("can it nhat 1 --src (hoac dung --validate-only)")
        if args.out.exists() and any(args.out.iterdir()):
            parser.error(f"{args.out} da co du lieu; chon thu muc moi de tranh tron dataset cu")
        items, stats, unmapped = collect_items(args.src)
        if not items:
            print("[LOI] khong con anh hop le nao sau khi loc.", file=sys.stderr)
            return 1
        splits = stratified_split(items, args.seed)
        args.out.mkdir(parents=True, exist_ok=True)
        write_dataset(splits, args.out)
        report = build_report(splits, stats, unmapped, args.min_images_per_class)
        (args.out / "dataset_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Anh moi tap: {report['images_per_split']}")
        print(f"Thong ke loc: {report['stats']}")
        if report["unmapped_source_classes"]:
            print(f"Lop nguon chua gan duoc (them alias vao food_classes.py neu can): {report['unmapped_source_classes']}")
        for w in report["warnings"]:
            print(f"[CANH BAO] {w}")

    errors = validate_dataset(args.out)
    if errors:
        print(f"[KHONG HOP LE] {len(errors)} loi, vi du:")
        for e in errors[:20]:
            print(" -", e)
        return 1
    print("[OK] data.yaml hop le, khong co bbox rong/lech chuan, khong ro ri giua cac tap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
