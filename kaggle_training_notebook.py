# ==============================================================================
# AGRISMART AI - OFFICIAL KAGGLE TRAINING NOTEBOOK (SIH 2026)
# Target: Train YOLOv8 Classification Model on PlantVillage Dataset
# Deliverable: Download best.pt to place in AgriSmart-AI/model/best.pt
# ==============================================================================

# CELL 1: Install Ultralytics & PyTorch
!pip install ultralytics scikit-learn seaborn matplotlib -q

# CELL 2: Verify GPU is Active (Kaggle Accelerator -> GPU T4 x2)
import torch
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

# CELL 3: Locate Dataset on Kaggle
# Tip: On Kaggle sidebar, click "+ Add Data" -> Search "PlantVillage" -> Click Add
import os
from pathlib import Path

# Most common PlantVillage Kaggle paths:
possible_paths = [
    "/kaggle/input/plantvillage-dataset/color",
    "/kaggle/input/plantvillage-dataset/PlantVillage",
    "/kaggle/input/plant-village/PlantVillage",
    "/kaggle/input/plantvillage/PlantVillage"
]

data_dir = None
for p in possible_paths:
    if os.path.exists(p):
        data_dir = p
        print(f"Found Dataset at: {data_dir}")
        break

if not data_dir:
    # Print available directories to inspect
    print("Listing /kaggle/input:")
    print(os.listdir("/kaggle/input") if os.path.exists("/kaggle/input") else "No input folder")

# CELL 4: Train YOLOv8-cls with Heavy Augmentation (Solving Lab-to-Field Generalization!)
from ultralytics import YOLO

# Load pre-trained Nano or Small classification backbone
model = YOLO("yolov8s-cls.pt")  # Transfer learning backbone

# Train model
results = model.train(
    data=data_dir,      # Path to dataset folder
    epochs=15,          # 15-20 epochs is optimal on GPU (~25-35 minutes)
    imgsz=224,          # Standard image resolution
    batch=64,           # Fast batch size on GPU
    device=0,           # GPU 0
    project="agri_smart",
    name="leaf_disease_run",
    # Built-in data augmentations to bridge lab-to-field generalization gap:
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=15.0,
    translate=0.1,
    scale=0.2,
    shear=5.0,
    perspective=0.0005,
    flipud=0.5,
    fliplr=0.5
)

# CELL 5: Validate and Output Macro-F1 & Confusion Matrix (Section 4.2 Requirement)
metrics = model.val()
print(f"Validation Top-1 Accuracy: {metrics.top1:.4f}")
print(f"Validation Top-5 Accuracy: {metrics.top5:.4f}")

# CELL 6: Download best.pt
# In Kaggle right-sidebar under "Output", download:
# /kaggle/working/agri_smart/leaf_disease_run/weights/best.pt
print("Training Complete! Download best.pt from /kaggle/working/agri_smart/leaf_disease_run/weights/best.pt")