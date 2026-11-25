# [OWNER: M4] Danh gia & benchmark toc do CPU (ONNX Runtime) cho AI Model B (T-M4-06, T-M4-12)
"""Do chinh xac (Precision, Recall, F1, mAP@0.5, AP50 tung lop) va toc do suy luan CPU thuc te
(ms/anh, p50, p95) cho file trong so `.onnx` tren tap `test` cua dataset YOLO.

Khong can PyTorch hay Ultralytics — chay truc tiep qua `FoodYoloService` (backend/app/services/ai_food_yolo.py)
de dam bao ket qua danh gia KHOP 100% voi luong suy luan that tren FastAPI Server.

Vi du:
    python evaluate_model.py \\
        --model ../../backend/ai_models/weights/food_yolo_v1.onnx \\
        --data ../datasets/model_b_v2/data.yaml \\
        --split test \\
        --out ../evaluation_reports/model_b_v1_onnx_eval.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.seed_catalog_and_exercises import FOOD_CATALOG_SEED
from app.services.ai_food_yolo import (
    FoodYoloService,
    bbox_iou,
    compute_file_sha256,
    decode_image,
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
KPI = {
    "map50": 0.80,
    "precision": 0.82,
    "recall": 0.78,
    "f1": 0.80,
    "inference_ms": 150.0,
}


def parse_yaml_names(yaml_path: Path) -> list[str]:
    lines = yaml_path.read_text(encoding="utf-8").splitlines()
    for i, raw in enumerate(lines):
        if not raw.startswith("names:"):
            continue
        rest = raw[len("names:") :].strip()
        if rest.startswith("["):
            return [p.strip().strip("'\"") for p in rest.strip("[]").split(",") if p.strip()]
        items: dict[int, str] = {}
        seq: list[str] = []
        for ln in lines[i + 1 :]:
            if not ln.strip():
                continue
            if not ln.startswith((" ", "\t", "-")):
                break
            s = ln.strip()
            if s.startswith("- "):
                seq.append(s[2:].strip().strip("'\""))
            elif ":" in s:
                k, _, v = s.partition(":")
                if k.strip().isdigit():
                    items[int(k)] = v.strip().strip("'\"")
        if seq:
            return seq
        if items:
            return [items[k] for k in sorted(items)]
    raise ValueError(f"Khong doc duoc danh sach names trong {yaml_path}")


def load_gt_boxes(label_path: Path, names: list[str]) -> list[tuple[str, tuple[float, float, float, float]]]:
    if not label_path.is_file():
        return []
    gts: list[tuple[str, tuple[float, float, float, float]]] = []
    for raw in label_path.read_text(encoding="utf-8").splitlines():
        tok = raw.split()
        if len(tok) != 5:
            continue
        cls_id = int(tok[0])
        if not 0 <= cls_id < len(names):
            continue
        xc, yc, w, h = (float(x) for x in tok[1:])
        x1 = max(0.0, xc - w / 2.0)
        y1 = max(0.0, yc - h / 2.0)
        x2 = min(1.0, xc + w / 2.0)
        y2 = min(1.0, yc + h / 2.0)
        gts.append((names[cls_id], (x1, y1, x2, y2)))
    return gts


def compute_ap_101(recalls: np.ndarray, precisions: np.ndarray) -> float:
    """Tinh Average Precision (COCO 101-point interpolation)."""
    mrec = np.concatenate(([0.0], recalls, [1.0]))
    mpre = np.concatenate(([1.0], precisions, [0.0]))
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))
    x = np.linspace(0.0, 1.0, 101)
    return float(np.trapezoid(np.interp(x, mrec, mpre), x))


def evaluate_predictions(
    preds_by_cls: dict[str, list[tuple[str, float, tuple[float, float, float, float]]]],
    gts_by_cls_img: dict[str, dict[str, list[tuple[float, float, float, float]]]],
    iou_thresh: float = 0.50,
    conf_op: float = 0.30,
) -> dict:
    active_classes = sorted(gts_by_cls_img.keys())
    per_class_ap50: dict[str, float] = {}
    per_class_op: dict[str, dict[str, float]] = {}

    total_tp = total_fp = total_fn = 0

    for cls in active_classes:
        gt_map = gts_by_cls_img[cls]
        n_gt = sum(len(v) for v in gt_map.values())
        if n_gt == 0:
            continue

        preds = sorted(preds_by_cls.get(cls, []), key=lambda x: x[1], reverse=True)
        matched = {img_id: [False] * len(boxes) for img_id, boxes in gt_map.items()}
        tp_flags = np.zeros(len(preds), dtype=np.float64)
        fp_flags = np.zeros(len(preds), dtype=np.float64)

        for idx, (img_id, _conf, pbox) in enumerate(preds):
            gt_boxes = gt_map.get(img_id, [])
            best_iou = 0.0
            best_j = -1
            for j, gbox in enumerate(gt_boxes):
                iou = bbox_iou(pbox, gbox)
                if iou > best_iou:
                    best_iou = iou
                    best_j = j
            if best_iou >= iou_thresh and best_j >= 0 and not matched[img_id][best_j]:
                matched[img_id][best_j] = True
                tp_flags[idx] = 1.0
            else:
                fp_flags[idx] = 1.0

        cum_tp = np.cumsum(tp_flags)
        cum_fp = np.cumsum(fp_flags)
        rec = cum_tp / max(n_gt, 1)
        prec = cum_tp / np.maximum(cum_tp + cum_fp, 1e-9)
        ap50 = compute_ap_101(rec, prec) if len(preds) > 0 else 0.0
        per_class_ap50[cls] = round(ap50, 4)

        # Tai nguong van hanh `conf_op`
        op_mask = np.array([p[1] >= conf_op for p in preds], dtype=bool)
        cls_tp = int(tp_flags[op_mask].sum()) if len(preds) else 0
        cls_fp = int(fp_flags[op_mask].sum()) if len(preds) else 0
        cls_fn = n_gt - cls_tp
        cls_p = cls_tp / (cls_tp + cls_fp) if (cls_tp + cls_fp) else 0.0
        cls_r = cls_tp / n_gt if n_gt else 0.0
        cls_f1 = (2 * cls_p * cls_r / (cls_p + cls_r)) if (cls_p + cls_r) else 0.0
        per_class_op[cls] = {
            "gt_boxes": n_gt,
            "tp": cls_tp,
            "fp": cls_fp,
            "fn": cls_fn,
            "precision": round(cls_p, 4),
            "recall": round(cls_r, 4),
            "f1": round(cls_f1, 4),
            "ap50": round(ap50, 4),
        }
        total_tp += cls_tp
        total_fp += cls_fp
        total_fn += cls_fn

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    map50 = float(np.mean(list(per_class_ap50.values()))) if per_class_ap50 else 0.0

    return {
        "operating_conf": conf_op,
        "active_classes": len(per_class_ap50),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "map50": round(map50, 4),
        "per_class_ap50": per_class_ap50,
        "per_class_details": per_class_op,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Danh gia ONNX Model B + do do tre CPU thuc te")
    parser.add_argument(
        "--model",
        type=Path,
        default=BACKEND_DIR / "ai_models" / "weights" / "food_yolo_v1.onnx",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=HERE.parent / "datasets" / "model_b_v2" / "data.yaml",
    )
    parser.add_argument("--split", choices=("val", "test"), default="test")
    parser.add_argument("--conf", type=float, default=0.30, help="nguong tin cay van hanh")
    parser.add_argument("--iou", type=float, default=0.45, help="nguong NMS")
    parser.add_argument("--warmup", type=int, default=3, help="so luot chay lam nong CPU truoc khi do")
    parser.add_argument(
        "--out",
        type=Path,
        default=HERE.parent / "evaluation_reports" / "model_b_v1_onnx_eval.json",
    )
    args = parser.parse_args(argv)

    if not args.model.is_file():
        print(f"[LOI] Khong tim thay trong so: {args.model}", file=sys.stderr)
        return 2
    if not args.data.is_file():
        print(f"[LOI] Khong tim thay data.yaml: {args.data}", file=sys.stderr)
        return 2

    names = parse_yaml_names(args.data)
    data_root = args.data.parent
    img_dir = data_root / "images" / args.split
    lbl_dir = data_root / "labels" / args.split
    images = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not images:
        print(f"[LOI] Khong co anh trong {img_dir}", file=sys.stderr)
        return 2

    # Dung chung 1 InferenceSession duy nhat de tranh 2 threadpool ONNX tranh chap CPU
    service = FoodYoloService(model_path=args.model)
    service.iou = args.iou
    catalog = {entry["class_code"]: dict(entry) for entry in FOOD_CATALOG_SEED}

    # Lam nong ONNX session
    sample_bytes = images[0].read_bytes()
    service.conf = args.conf
    for _ in range(max(1, args.warmup)):
        service.analyze(sample_bytes, catalog)

    gts_by_cls_img: dict[str, dict[str, list[tuple[float, float, float, float]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    preds_by_cls: dict[str, list[tuple[str, float, tuple[float, float, float, float]]]] = defaultdict(list)

    infer_times_ms: list[float] = []
    e2e_times_ms: list[float] = []
    sample_outputs: list[dict] = []

    # Luot 1: do latency & output thuc te tai nguong van hanh args.conf
    service.conf = args.conf
    for idx, img_path in enumerate(images):
        raw_bytes = img_path.read_bytes()
        gts = load_gt_boxes(lbl_dir / f"{img_path.stem}.txt", names)
        for cls_name, box in gts:
            gts_by_cls_img[cls_name][img_path.stem].append(box)

        t0 = time.perf_counter()
        payload = service.analyze(raw_bytes, catalog)
        t_e2e = (time.perf_counter() - t0) * 1000.0
        infer_times_ms.append(float(payload["inference_time_ms"]))
        e2e_times_ms.append(t_e2e)
        if idx < 5:
            sample_outputs.append({"image": img_path.name, **payload})

    # Luot 2: thu thap prediction conf >= 0.01 de tinh PR curve & mAP@0.5
    service.conf = 0.01
    for img_path in images:
        dets = service.detect(decode_image(img_path.read_bytes()))
        for d in dets:
            preds_by_cls[d.class_code].append((img_path.stem, d.confidence, d.bbox_norm))
    service.conf = args.conf

    # Quet nguong tin cay de tim nguong toi uu F1
    conf_sweep: list[dict] = []
    for c in (0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50):
        res_c = evaluate_predictions(preds_by_cls, gts_by_cls_img, iou_thresh=0.50, conf_op=c)
        conf_sweep.append(
            {
                "conf": c,
                "precision": res_c["precision"],
                "recall": res_c["recall"],
                "f1_score": res_c["f1_score"],
            }
        )

    main_metrics = evaluate_predictions(preds_by_cls, gts_by_cls_img, iou_thresh=0.50, conf_op=args.conf)
    best_conf_row = max(conf_sweep, key=lambda r: r["f1_score"])

    sorted_inf = sorted(infer_times_ms)
    sorted_e2e = sorted(e2e_times_ms)
    p95_idx = min(len(sorted_inf) - 1, int(round(0.95 * (len(sorted_inf) - 1))))

    latency = {
        "samples": len(images),
        "inference_mean_ms": round(statistics.mean(sorted_inf), 2),
        "inference_median_ms": round(statistics.median(sorted_inf), 2),
        "inference_p95_ms": round(sorted_inf[p95_idx], 2),
        "e2e_mean_ms": round(statistics.mean(sorted_e2e), 2),
        "e2e_p95_ms": round(sorted_e2e[p95_idx], 2),
    }

    kpi_pass = {
        "map50>=0.80": main_metrics["map50"] >= KPI["map50"],
        "precision>=0.82": main_metrics["precision"] >= KPI["precision"],
        "recall>=0.78": main_metrics["recall"] >= KPI["recall"],
        "f1>=0.80": main_metrics["f1_score"] >= KPI["f1"],
        "cpu_inference_mean<150ms": latency["inference_mean_ms"] < KPI["inference_ms"],
        "e2e<3000ms": latency["e2e_p95_ms"] < 3000.0,
    }

    report = {
        "model_file": args.model.name,
        "model_sha256": compute_file_sha256(args.model),
        "backend": service.backend_name,
        "dataset": str(args.data),
        "split": args.split,
        "num_images": len(images),
        "metrics_at_operating_conf": main_metrics,
        "recommended_conf_by_f1": best_conf_row,
        "conf_threshold_sweep": conf_sweep,
        "cpu_latency": latency,
        "kpi_target": KPI,
        "kpi_pass": kpi_pass,
        "sample_api_outputs": sample_outputs,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== KET QUA DANH GIA ONNX RUNTIME (CPU) ===")
    print(f"Model      : {args.model.name} ({service.backend_name}) | {len(images)} anh ({args.split})")
    print(f"mAP@0.5    : {main_metrics['map50']:.4f}")
    print(
        f"P / R / F1 : {main_metrics['precision']:.4f} / {main_metrics['recall']:.4f} / {main_metrics['f1_score']:.4f} "
        f"(conf={args.conf})"
    )
    print(f"Best F1    : {best_conf_row}")
    print(
        f"CPU Latency: infer mean={latency['inference_mean_ms']}ms "
        f"(p50={latency['inference_median_ms']}ms, p95={latency['inference_p95_ms']}ms) | "
        f"e2e mean={latency['e2e_mean_ms']}ms"
    )
    print("AP50/lop   :", main_metrics["per_class_ap50"])
    print("KPI        :", kpi_pass)
    print(f"Bao cao    : {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
