# [OWNER: M4] Huan luyen AI Model B (YOLOv8) tren dataset do prepare_dataset.py tao (T-M4-06, T-M4-10)
"""Huan luyen -> danh gia tren tap test -> xuat ONNX -> tinh SHA-256 -> ghi bao cao KPI & manifest.

Chay (can `pip install ultralytics`, nen dung GPU / Google Colab T4):

    python train_yolo.py --data ../datasets/model_b_v3/data.yaml --model yolov8s.pt --epochs 100

Ket qua nam trong `--project` (mac dinh ../datasets/runs, da bi .gitignore). Weights (*.pt, *.onnx)
KHONG commit len Git. Bao cao JSON ghi vao ai_research/evaluation_reports/model_b_train_report.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / "datasets" / "model_b_v3" / "data.yaml"
DEFAULT_PROJECT = HERE.parent / "datasets" / "runs"
REPORT_PATH = HERE.parent / "evaluation_reports" / "model_b_train_report.json"

KPI = {
    "map50": 0.80,
    "map50_95": 0.58,
    "precision": 0.82,
    "recall": 0.78,
    "f1": 0.80,
    "inference_ms": 150.0,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Huan luyen YOLOv8 cho nhan dien mon an (Model B)")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA, help="data.yaml do prepare_dataset.py tao")
    p.add_argument("--model", default="yolov8s.pt", help="yolov8n.pt / yolov8s.pt / yolov8m.pt (tai tu dong)")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16, help="-1 de tu chon theo VRAM")
    p.add_argument("--device", default="auto", help="auto | cpu | 0 (GPU dau tien)")
    p.add_argument("--patience", type=int, default=30, help="dung som neu khong cai thien")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    p.add_argument("--name", default="model_b_v1")
    p.add_argument("--version", default="yolov8s-gymfood-v1.1", help="ten phien ban ghi vao manifest")
    p.add_argument("--report", type=Path, default=REPORT_PATH)
    p.add_argument("--no-export", action="store_true", help="bo qua buoc xuat ONNX")
    return p.parse_args(argv)


def resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import torch

        return "0" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_runtime_yaml(data_yaml: Path, run_dir: Path) -> Path:
    """Ghi ban sao data.yaml co `path:` tuyet doi, de chay duoc tu bat ky thu muc nao."""
    text = data_yaml.read_text(encoding="utf-8")
    kept = [ln for ln in text.splitlines() if not ln.startswith("path:")]
    out = run_dir / "data_runtime.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"path: {data_yaml.parent.resolve().as_posix()}\n" + "\n".join(kept) + "\n", encoding="utf-8")
    return out


def count_split_images(data_dir: Path) -> dict[str, int]:
    counts = {}
    for split in ("train", "val", "test"):
        folder = data_dir / "images" / split
        counts[split] = sum(1 for f in folder.glob("*") if f.is_file()) if folder.is_dir() else 0
    return counts


def collect_metrics(metrics, names: dict[int, str]) -> dict:
    box = metrics.box
    per_class = {}
    for idx, ap50 in zip(box.ap_class_index.tolist(), box.ap50.tolist()):
        per_class[names.get(int(idx), str(idx))] = round(float(ap50), 4)
    p = float(box.mp)
    r = float(box.mr)
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1_score": round(f1, 4),
        "map50": round(float(box.map50), 4),
        "map50_95": round(float(box.map), 4),
        "per_class_ap50": per_class,
        "speed_ms_per_image": {k: round(float(v), 2) for k, v in metrics.speed.items()},
    }


def judge(result: dict) -> dict:
    inference = result["speed_ms_per_image"].get("inference", float("inf"))
    return {
        "map50>=0.80": result["map50"] >= KPI["map50"],
        "map50_95>=0.58": result["map50_95"] >= KPI["map50_95"],
        "precision>=0.82": result["precision"] >= KPI["precision"],
        "recall>=0.78": result["recall"] >= KPI["recall"],
        "f1>=0.80": result["f1_score"] >= KPI["f1"],
        "inference<150ms": inference < KPI["inference_ms"],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.data.is_file():
        print(f"[LOI] khong thay {args.data}. Chay prepare_dataset.py truoc.", file=sys.stderr)
        return 2
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[LOI] thieu thu vien: pip install ultralytics", file=sys.stderr)
        return 2

    device = resolve_device(args.device)
    if device == "cpu":
        print("[CANH BAO] Dang chay CPU: rat cham. Nen dung GPU/Colab, hoac --model yolov8n.pt --imgsz 416 --epochs 30.")

    run_root = args.project / args.name
    data_yaml = write_runtime_yaml(args.data, args.project / f"{args.name}_cfg")
    split_counts = count_split_images(args.data.parent)
    print(f"Anh moi tap: {split_counts} | thiet bi: {device} | model: {args.model}")

    model = YOLO(args.model)
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        patience=args.patience,
        seed=args.seed,
        project=str(args.project),
        name=args.name,
        exist_ok=False,
        plots=True,  # confusion matrix, PR curve, results.png cho bao cao (T-M4-12)
        hsv_h=0.015,
        hsv_s=0.6,
        hsv_v=0.4,
        degrees=10.0,
        fliplr=0.5,
        mosaic=1.0,
    )

    best = Path(model.trainer.best)
    print(f"Weights tot nhat: {best}")
    best_model = YOLO(str(best))
    test_metrics = best_model.val(
        data=str(data_yaml),
        split="test",
        imgsz=args.imgsz,
        device=device,
        plots=True,
        project=str(args.project),
        name=f"{args.name}_test",
    )
    result = collect_metrics(test_metrics, best_model.names)
    verdict = judge(result)

    onnx_path = None
    onnx_sha256 = None
    if not args.no_export:
        onnx_path = str(best_model.export(format="onnx", imgsz=args.imgsz, opset=17, simplify=True))
        if Path(onnx_path).is_file():
            onnx_sha256 = file_sha256(Path(onnx_path))

    report = {
        "model": args.model,
        "model_version": args.version,
        "device": device,
        "epochs_requested": args.epochs,
        "imgsz": args.imgsz,
        "images_per_split": split_counts,
        "weights": str(best),
        "weights_sha256": file_sha256(best) if best.is_file() else None,
        "onnx": onnx_path,
        "onnx_sha256": onnx_sha256,
        "test_metrics": result,
        "kpi_target": KPI,
        "kpi_pass": verdict,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Sinh luon ban mau model_b_manifest.json ben canh report de copy nhanh vao backend/ai_models/
    manifest_out = args.report.parent / "model_b_manifest_generated.json"
    all_classes = [best_model.names[k] for k in sorted(best_model.names)]
    manifest_payload = {
        "schema_version": 1,
        "model_version": args.version,
        "architecture": Path(args.model).stem.upper(),
        "active_file": "food_yolo_v1.onnx",
        "fallback_file": "food_yolo_v1.pt",
        "sha256": onnx_sha256 or "",
        "download_url": "",
        "imgsz": args.imgsz,
        "conf_threshold": 0.30,
        "iou_threshold": 0.45,
        "cross_class_iou_threshold": 0.75,
        "classes": all_classes,
        "trained_classes": list(result["per_class_ap50"].keys()),
        "metrics": {
            "precision": result["precision"],
            "recall": result["recall"],
            "f1_score": result["f1_score"],
            "map50": result["map50"],
            "map50_95": result["map50_95"],
        },
    }
    manifest_out.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== KET QUA TREN TAP TEST ===")
    for key in ("precision", "recall", "f1_score", "map50", "map50_95"):
        print(f"{key:>10}: {result[key]}")
    print(f"toc do (ms/anh): {result['speed_ms_per_image']}")
    print("AP50 theo lop:", result["per_class_ap50"])
    print("KPI:", verdict)
    print(f"ONNX SHA-256: {onnx_sha256}")
    print(f"Bao cao: {args.report}")
    print(f"Manifest mau: {manifest_out}")
    print(f"Thu muc ket qua (confusion matrix, results.png): {run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
