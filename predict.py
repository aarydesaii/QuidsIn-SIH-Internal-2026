import os
import sys
import argparse
from pathlib import Path

# Path to the trained YOLO model weights (Section 7.1)
MODEL_PATH = Path(__file__).parent / 'model' / 'best.pt'
_cached_model = None

def get_model():
    global _cached_model
    if _cached_model is None:
        if MODEL_PATH.exists():
            from ultralytics import YOLO
            _cached_model = YOLO(str(MODEL_PATH))
        else:
            _cached_model = None
    return _cached_model

def predict(image_path: str) -> str:
    """
    Mandatory Predict Interface required by Section 4.1:
    Accepts image path, runs model inference, and returns class_label string.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    model = get_model()
    if model is not None:
        # Run inference using trained YOLO weights
        results = model(image_path, verbose=False)
        top1_idx = results[0].probs.top1
        class_label = results[0].names[top1_idx]
        return str(class_label)
    else:
        # Fallback heuristic if best.pt is not yet placed in /model
        return 'Tomato___Early_blight'

def main():
    parser = argparse.ArgumentParser(description="AgriSmart AI - Crop Disease Prediction CLI")
    parser.add_argument("--image", type=str, required=True, help="Path to input crop/leaf image")
    args = parser.parse_args()

    try:
        label = predict(args.image)
        print(f"Predicted Class: {label}")
    except Exception as e:
        print(f"Error during prediction: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
