"""
AgriSmart AI - Model Evaluation (Section 4.2)

Reports macro-F1 (the primary competition metric), per-class precision/recall/F1,
and a confusion matrix for a trained YOLOv8 classification model.

Usage:
    python model/evaluate.py --data /kaggle/working/dataset/val
    python model/evaluate.py --data data/dataset --weights model/weights/best.pt
"""

import csv
import json
import argparse
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_WEIGHTS = Path(__file__).parent / "weights" / "best.pt"
DEFAULT_REPORT_DIR = Path(__file__).resolve().parents[1] / "report"


def collect_samples(data_dir: Path):
    """Return (image_paths, true_labels) from a folder of class subdirectories."""
    samples = []
    for class_dir in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        for image_path in sorted(class_dir.iterdir()):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                samples.append((image_path, class_dir.name))

    if not samples:
        raise SystemExit(
            f"No images found under {data_dir}. Expected one subdirectory per class."
        )

    paths, labels = zip(*samples)
    return list(paths), list(labels)


def run_inference(model, paths, batch_size: int):
    predictions = []
    for start in range(0, len(paths), batch_size):
        batch = [str(p) for p in paths[start:start + batch_size]]
        for result in model(batch, verbose=False):
            predictions.append(result.names[result.probs.top1])
        print(f"  {min(start + batch_size, len(paths))}/{len(paths)} images", end="\r")
    print()
    return predictions


def save_confusion_matrix(matrix, labels, out_path: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping confusion matrix image")
        return

    size = max(8, len(labels) * 0.4)
    fig, ax = plt.subplots(figsize=(size, size))
    ax.imshow(matrix, interpolation="nearest", cmap="Blues")
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=6)
    ax.set_yticklabels(labels, fontsize=6)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Confusion matrix image : {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="AgriSmart AI - macro-F1 and confusion matrix evaluation"
    )
    parser.add_argument("--data", type=str, required=True,
                        help="Validation directory containing one subfolder per class")
    parser.add_argument("--weights", type=str, default=str(DEFAULT_WEIGHTS),
                        help="Path to trained weights (default: model/weights/best.pt)")
    parser.add_argument("--batch", type=int, default=64, help="Inference batch size")
    parser.add_argument("--out", type=str, default=str(DEFAULT_REPORT_DIR),
                        help="Directory for metric artifacts")
    args = parser.parse_args()

    data_dir = Path(args.data)
    weights_path = Path(args.weights)
    out_dir = Path(args.out)

    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")
    if not weights_path.exists():
        raise SystemExit(
            f"Weights not found: {weights_path}\n"
            "Train the model first, then place best.pt at model/weights/best.pt"
        )

    from ultralytics import YOLO

    print(f"Weights : {weights_path}")
    print(f"Data    : {data_dir}")

    paths, y_true = collect_samples(data_dir)
    print(f"Evaluating {len(paths)} images across {len(set(y_true))} classes\n")

    model = YOLO(str(weights_path))
    y_pred = run_inference(model, paths, args.batch)

    labels = sorted(set(y_true) | set(y_pred))
    macro_f1 = f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)

    print("\n" + "=" * 52)
    print(f"  MACRO-F1 (primary metric) : {macro_f1:.4f}")
    print(f"  Weighted F1               : {weighted_f1:.4f}")
    print(f"  Accuracy                  : {accuracy:.4f}")
    print("=" * 52 + "\n")

    report_text = classification_report(
        y_true, y_pred, labels=labels, zero_division=0, digits=4
    )
    print(report_text)

    out_dir.mkdir(parents=True, exist_ok=True)

    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    with open(out_dir / "confusion_matrix.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["true\\predicted"] + labels)
        for label, row in zip(labels, matrix):
            writer.writerow([label] + row.tolist())

    (out_dir / "classification_report.txt").write_text(report_text, encoding="utf-8")

    summary = {
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "accuracy": round(float(accuracy), 4),
        "num_images": len(paths),
        "num_classes": len(labels),
        "weights": str(weights_path),
        "data": str(data_dir),
    }
    (out_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Metrics JSON           : {out_dir / 'metrics.json'}")
    print(f"Classification report  : {out_dir / 'classification_report.txt'}")
    print(f"Confusion matrix CSV   : {out_dir / 'confusion_matrix.csv'}")
    save_confusion_matrix(matrix, labels, out_dir / "confusion_matrix.png")


if __name__ == "__main__":
    main()
