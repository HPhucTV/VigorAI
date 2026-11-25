# [OWNER: M4] Huan luyen AI Model B (YOLOv8) tren dataset do prepare_dataset.py tao (T-M4-06)
"""Huan luyen -> danh gia tren tap test -> xuat ONNX -> ghi bao cao KPI.

Chay (can `pip install ultralytics`, nen dung GPU / Google Colab):

    python train_yolo.py --data ../datasets/model_b_v2/data.yaml --model yolov8s.pt --epochs 100

Ket qua nam trong `--project` (mac dinh ../datasets/runs, da bi .gitignore). Weights (*.pt, *.onnx)
KHONG commit len Git. Bao cao JSON ghi vao ai_research/evaluation_reports/model_b_train_report.json.

LUU Y: data.yaml co 18 lop nhung lop chua co anh se khong xuat hien trong thong ke. Cac chi so
tong (mAP, P, R) chi tinh tren lop co du lieu o tap test; neu tap test chi co vai chuc anh thi
so do rat nhieu, khong dung de ket luan dat KPI.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / "datasets" / "model_b_v2" / "data.yaml"
DEFAULT_PROJECT = HERE.parent / "datasets" / "runs"
REPORT_PATH = HERE.parent / "evaluation_reports" / "model_b_train_report.json"

KPI = {"map50": 0.80, "precision": 0.82, "recall": 0.78, "inference_ms": 150.0}


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
    return {
        "precision": round(float(box.mp), 4),
        "recall": round(float(box.mr), 4),
        "map50": round(float(box.map50), 4),
        "map50_95": round(float(box.map), 4),
        "per_class_ap50": per_class,
        "speed_ms_per_image": {k: round(float(v), 2) for k, v in metrics.speed.items()},
    }


def judge(result: dict) -> dict:
    inference = result["speed_ms_per_image"].get("inference", float("inf"))
    return {
        "map50>=0.80": result["map50"] >= KPI["map50"],
        "precision>=0.82": result["precision"] >= KPI["precision"],
        "recall>=0.78": result["recall"] >= KPI["recall"],
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
    )

    best = Path(model.trainer.best)
    print(f"Weights tot nhat: {best}")
    best_model = YOLO(str(best))
    test_metrics = best_model.val(
        data=str(data_yaml), split="test", imgsz=args.imgsz, device=device, plots=True, project=str(args.project),
        name=f"{args.name}_test",
    )
    result = collect_metrics(test_metrics, best_model.names)
    verdict = judge(result)

    onnx_path = None
    if not args.no_export:
        onnx_path = str(best_model.export(format="onnx", imgsz=args.imgsz))

    report = {
        "model": args.model,
        "device": device,
        "epochs_requested": args.epochs,
        "imgsz": args.imgsz,
        "images_per_split": split_counts,
        "weights": str(best),
        "onnx": onnx_path,
        "test_metrics": result,
        "kpi_target": KPI,
        "kpi_pass": verdict,
        "caveat": (
            "Tap test nho va chi gom cac lop co du lieu; so lieu chi dung de kiem chung pipeline, "
            "khong phai KPI cuoi cung. Toc do do tren thiet bi huan luyen, can do lai tren server that."
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== KET QUA TREN TAP TEST ===")
    for key in ("precision", "recall", "map50", "map50_95"):
        print(f"{key:>10}: {result[key]}")
    print(f"toc do (ms/anh): {result['speed_ms_per_image']}")
    print("AP50 theo lop:", result["per_class_ap50"])
    print("KPI:", verdict)
    print(f"Bao cao: {args.report}")
    print(f"Thu muc ket qua (confusion matrix, results.png): {run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
