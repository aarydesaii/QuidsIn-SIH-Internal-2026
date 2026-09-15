"""
Re-calibrate the out-of-distribution guard against the current weights.

Run this after any retraining. It reports the separation between in-distribution
leaf photographs and out-of-distribution inputs, verifies that the thresholds in
src/backend/ood_guard.py still sit inside the gap, and prints replacement values
if they do not.

    python scripts/calibrate_guard.py
"""

import sys
import glob
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from PIL import Image

from src.backend import ood_guard
from model.predict import get_model


def synthetic_probes(directory: Path):
    """Stand-in out-of-distribution inputs: noise, flat colour, a plain gradient."""
    directory.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    probes = {
        "noise.jpg": rng.integers(0, 255, (256, 256, 3), dtype=np.uint8),
        "flat_grey.jpg": np.full((256, 256, 3), 128, np.uint8),
    }
    gradient = np.zeros((256, 256, 3), np.uint8)
    gradient[:, :, 1] = np.linspace(60, 200, 256).astype(np.uint8)
    probes["green_gradient.jpg"] = gradient

    paths = []
    for name, array in probes.items():
        path = directory / name
        Image.fromarray(array).save(path)
        paths.append(str(path))
    return paths


def collect(model, paths):
    rows = []
    for path in paths:
        verdict = ood_guard.screen(model, path)
        rows.append((path, verdict))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in-dist", default=str(PROJECT_ROOT / "data" / "dataset" / "*" / "*.jpg"),
                        help="glob of known-good leaf photographs")
    parser.add_argument("--ood", default="", help="optional glob of real out-of-distribution photographs")
    args = parser.parse_args()

    model = get_model()
    if model is None:
        print("No trained weights at model/weights/best.pt - nothing to calibrate.")
        return 1

    in_dist_paths = sorted(glob.glob(args.in_dist))
    if not in_dist_paths:
        print(f"No in-distribution images matched {args.in_dist}")
        return 1

    ood_paths = sorted(glob.glob(args.ood)) if args.ood else synthetic_probes(
        PROJECT_ROOT / "data" / "ood_probes")

    print(f"Scoring {len(in_dist_paths)} in-distribution and {len(ood_paths)} out-of-distribution images...\n")
    in_rows = collect(model, in_dist_paths)
    ood_rows = collect(model, ood_paths)

    def column(rows, key):
        return np.array([r[1]["diagnostics"][key] for r in rows], dtype=float)

    metrics = [
        ("view_mean_confidence", "higher is safer", ood_guard.MIN_VIEW_MEAN_CONFIDENCE, "min"),
        ("normalised_entropy", "lower is safer", ood_guard.MAX_NORMALISED_ENTROPY, "max"),
        ("view_agreement", "higher is safer", ood_guard.MIN_VIEW_AGREEMENT, "min"),
        ("weakest_view_confidence", "higher is safer", ood_guard.MIN_WEAKEST_VIEW_CONFIDENCE, "min"),
    ]

    print(f"{'metric':28s} {'in-dist range':>22s} {'ood range':>22s} {'threshold':>10s}")
    print("-" * 86)
    for key, _, threshold, direction in metrics:
        ins, oods = column(in_rows, key), column(ood_rows, key)
        print(f"{key:28s} {ins.min():9.3f} - {ins.max():8.3f} "
              f"{oods.min():9.3f} - {oods.max():8.3f} {threshold:10.3f}")

    false_rejects = [r for r in in_rows if not r[1]["accepted"]]
    caught = [r for r in ood_rows if not r[1]["accepted"]]

    print(f"\nIn-distribution wrongly rejected : {len(false_rejects)}/{len(in_rows)}")
    for path, verdict in false_rejects:
        print(f"    {Path(path).parent.name}/{Path(path).name} -> {verdict['failed_checks']}")
    print(f"Out-of-distribution correctly caught: {len(caught)}/{len(ood_rows)}")
    for path, verdict in ood_rows:
        state = "caught " if not verdict["accepted"] else "MISSED "
        print(f"    {state} {Path(path).name:22s} conf={verdict['confidence']:.3f} {verdict['failed_checks']}")

    ok = not false_rejects and len(caught) == len(ood_rows)
    print("\nThresholds are still valid." if ok else
          "\nThresholds need review - adjust the constants in src/backend/ood_guard.py.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
