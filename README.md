# 🌿 AgriSmart AI: Intelligent Agriculture for a Sustainable Future
**Smart India Hackathon (SIH 2026) — Internal Hackathon Submission**  
**Institution:** L. J. Institute of Engineering and Technology [C-433]  
**Problem Statement 1:** AgriSmart AI (Crop Disease Detection & Autonomous Farm Advisory)

---

## 1. Modules Implemented

| Module | Status | Description |
| :--- | :---: | :--- |
| **3.1 Core Task (Mandatory)** |  Built | Leaf Disease Detection using Transfer-Learned YOLOv8 with full precautionary guidance |
| **3.2 Bonus Module B** |  Built | Smart Irrigation Advisory combining soil moisture, rain forecast, and crop stage |
| **3.2 Bonus Module C** |  Built | Weather-Based Intelligence & safe spray-window recommendations |
| **3.2 Bonus Module D** |  Built | Quantified Farm Sustainability Score & resource savings formula (Water, Fungicide, CO2) |
| **3.2 Bonus Module E** |  Built | Kisan Sahayak GenAI Assistant with Voice/TTS & multilingual capability |
| **3.2 Bonus Module F** |  Built | Soil Analytics — simulated agronomic model (Soil Moisture, Temp, Humidity, pH, NPK). Software only, no hardware |
| **4.1 Predict CLI Interface** |  Built | Standalone reproducible CLI (`python model/predict.py --image <path>`) |

---

## 2. Quick Setup & Run Instructions (< 5 Minutes)

Judges can verify and run this system on standard CPU laptops with zero setup friction:

### Prerequisites
- Python 3.10 or 3.11 installed
- Git installed (optional)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test Core Predict Interface (Section 4.1 Requirement)
```bash
python model/predict.py --image data/dataset/Tomato___Early_blight/sample_1.jpg
```
*Expected Output:*
```text
Predicted Class: Tomato___Early_blight
```
The true label is the containing folder name, so the prediction can be checked directly.
Any image under `data/dataset/<class>/` works the same way.

### Step 3: Launch Full Web Dashboard
Run from the repository root:
```bash
python -m uvicorn src.backend.main:app --reload
```
Open your browser at: **`http://localhost:8000`**

### Repository Structure
```text
src/
    backend/      FastAPI application (main.py, disease_kb.py)
    frontend/     Jinja2 templates and static assets
model/
    predict.py    MANDATORY predict interface (Section 4.1)
    train.py      Training script
    weights/      Trained weights (best.pt) — not committed
data/             Datasets and uploads — gitignored
report/           Model report
```

---

## 3. Dataset & Training Methodology

- **Training & Validation:** PlantVillage dataset, `color` variant — 54,305 lab-condition
  leaf images across 38 classes (tomato, potato, corn, apple, grape, and others).
  Split 80/20 stratified per class with `random.seed(42)`: 43,456 train / 10,849 validation.
- **Evaluation:** Macro-F1 on the held-out 20% validation split. This split is drawn from
  the same lab distribution as training, so it measures in-distribution performance.
  No field-condition benchmark was evaluated locally — the organizers' held-out field
  set is the official test.
- **Addressing the Lab-to-Field Gap:**
  - Transfer learning from the ImageNet-pretrained `yolov8s-cls` backbone.
  - The `color` variant was chosen over `segmented` deliberately: segmented images have
    their backgrounds removed, which does not match photographs taken by farmers.
  - Augmentation aimed at outdoor capture conditions — HSV jitter (lighting and white
    balance), ±15° rotation (hand-held angles), translation and scaling (framing and
    distance), shear and perspective (off-axis capture), and flips. Mosaic and cutout
    were not used.

---

## 4. Architecture Overview

```
[Leaf Image Input] ──> [Pre-processing & Augmentation] ──> [YOLOv8 Feature Backbone]
                                                                    │
                                                                    ▼
                                                            [Class Verdict]
                                                                    │
                 ┌──────────────────────────┬───────────────────────┼──────────────────────┐
                 ▼                          ▼                       ▼                      ▼
       [Disease Symptoms]         [Organic Remedies]      [Chemical Dosage]     [Irrigation Precaution]
                 │                          │                       │                      │
                 └──────────────────────────┴───────────────────────┴──────────────────────┘
                                                    │
                                                    ▼
                             [Interactive Responsive Web Dashboard & Voice TTS]
                                                    ▲
                                                    │
      [Simulated Soil Analytics] ──── [Micro-Climate Weather] ──── [Kisan Sahayak AI Chat]
```

---

## 5. Model Metrics & Evaluation

Trained on the PlantVillage `color` dataset (54,305 images, 38 classes), split
80/20 stratified per class with `random.seed(42)`.

| Metric | Value |
| :--- | :--- |
| **Macro-F1 (primary metric)** | **0.9915** |
| Macro precision | 0.9918 |
| Macro recall | 0.9912 |
| Top-1 accuracy | 0.9942 |
| Weighted F1 | 0.9942 |
| Validation images | 10,849 |

- **Backbone:** YOLOv8s-cls (Ultralytics), ImageNet-pretrained, transfer-learned
- **Parameters:** 5,123,878 fused / 5,129,414 unfused (12.4 GFLOPs) — 0.3 ms per image on a T4
- **Training:** 8 epochs at 224×224, batch 64, ~29 minutes on a Tesla T4
- **Out-of-distribution screening:** a single confidence cutoff cannot work here, because
  the two populations overlap — a blank white frame scores **84.8%** on this model while a
  genuinely blurred leaf scores **57.8%**. Each upload is averaged over five views
  (original, two flips, centre crop, flipped crop) and graded into three tiers by
  [`src/backend/ood_guard.py`](src/backend/ood_guard.py):

  | Tier | Condition | Behaviour |
  | :--- | :--- | :--- |
  | **Reject** | edge density < 1.5, or confidence < 0.45, or entropy > 0.60 | No diagnosis; photo guidance shown |
  | **Provisional** | passes the floor but not all confirmed checks | Diagnosis shown with a "verify before spraying" warning |
  | **Confirmed** | confidence ≥ 0.85, entropy ≤ 0.25, view agreement ≥ 0.80, weakest view ≥ 0.60 | Diagnosis shown normally |

  The edge-density floor is structural rather than probabilistic: flat frames (a wall, the
  sky, a lens cap) carry almost no edge energy, while every real leaf photograph measured
  carries at least 1.63. This catches the blank-image case that confidence alone misses.
  Thresholds are checked by `scripts/calibrate_guard.py` and must be re-run after retraining.

### Reproducing these numbers

```bash
python model/evaluate.py --data <validation_directory>
```

Writes `metrics.json`, `classification_report.txt`, `confusion_matrix.csv` and
`confusion_matrix.png` into `report/`.

### Known limitations

Macro-F1 of 0.9915 is measured **in-distribution** on held-out PlantVillage
images. PlantVillage is laboratory photography — single detached leaves, plain
backgrounds, controlled lighting — so this figure should not be read as a
field-performance estimate, and a drop on field photographs is expected.

The weakest class is Corn Cercospora/Gray leaf spot (F1 0.9029), which is most
often confused with Corn Northern Leaf Blight (F1 0.9490); both present as
elongated grey-brown lesions along the leaf veins and are genuinely hard to
separate from a photograph. Tomato Early blight (0.9600) and Target Spot
(0.9695) show the same pattern.

The model predicts 38 classes while the agronomic knowledge base holds detailed
remedies for 15; the remaining classes return a generic advisory.

Full analysis: [`report/model_report.md`](report/model_report.md)

---

## 6. Video Demo & Links

- **Video Demo (3-5 Minutes):** [Link to Unlisted YouTube/Drive Demo] *(To be attached before final submission)*
- **Live Deployed Web App:** `http://localhost:8000`