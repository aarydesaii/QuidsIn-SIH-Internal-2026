"""
AgriSmart AI - PlantVillage Dataset Downloader
Downloads sample and benchmark evaluation leaf images from the official PlantVillage dataset.
"""

import os
import sys
import json
import argparse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "data" / "dataset"

KEY_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
]

def download_samples(samples_per_class: int = 3):
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[+] Installing PlantVillage Dataset Samples into: {DATASET_DIR}")
    print(f"Target classes: {len(KEY_CLASSES)} classes, {samples_per_class} sample images each\n")

    total_downloaded = 0

    for cls_name in KEY_CLASSES:
        cls_dir = DATASET_DIR / cls_name
        cls_dir.mkdir(parents=True, exist_ok=True)
        print(f"[*] Fetching index for: {cls_name}...")

        api_url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{cls_name}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "AgriSmart-AI-Downloader/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                file_list = json.loads(response.read().decode("utf-8"))
                
                # Filter for image files
                img_files = [f for f in file_list if f["name"].lower().endswith(('.jpg', '.jpeg', '.png'))]
                selected = img_files[:samples_per_class]

                for idx, item in enumerate(selected, 1):
                    download_url = item["download_url"]
                    file_name = f"sample_{idx}.jpg"
                    dest_path = cls_dir / file_name

                    if not dest_path.exists():
                        img_req = urllib.request.Request(download_url, headers={"User-Agent": "AgriSmart-AI-Downloader/1.0"})
                        with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                            dest_path.write_bytes(img_resp.read())
                        print(f"    -> Saved {file_name} ({len(dest_path.read_bytes()) // 1024} KB)")
                    else:
                        print(f"    -> Already exists: {file_name}")

                    total_downloaded += 1

        except Exception as e:
            print(f"    [!] Failed to fetch {cls_name}: {e}")

    print("\n" + "=" * 60)
    print(f"[OK] Dataset installation complete! Total images: {total_downloaded}")
    print(f"Location: {DATASET_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install PlantVillage Dataset Samples for AgriSmart-AI")
    parser.add_argument("--samples-per-class", type=int, default=3, help="Number of samples to download per disease class (default: 3)")
    args = parser.parse_args()

    download_samples(samples_per_class=args.samples_per_class)
