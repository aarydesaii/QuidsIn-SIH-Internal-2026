# 🌿 AgriSmart AI: Intelligent Agriculture for a Sustainable Future
**Smart India Hackathon (SIH 2026) — Internal Hackathon Submission**  
**Institution:** L. J. Institute of Engineering and Technology [C-433]  
**Problem Statement 1:** AgriSmart AI (Crop Disease Detection & Autonomous Farm Advisory)

---

## 1. Modules Implemented

| Module | Status | Description |
| :--- | :---: | :--- |
| **3.1 Core Task (Mandatory)** |  Built | Leaf Disease Detection using Transfer-Learned YOLOv8 with full precautionary guidance |
| **3.2 Bonus Module B** |  Built | Smart Irrigation Advisory deriving schedule and volume from soil texture, crop season length and application efficiency |
| **3.2 Bonus Module C** |  Built | Weather-Based Intelligence & safe spray-window recommendations |
| **3.2 Bonus Module D** |  Built | Quantified Farm Sustainability Score scored across irrigation efficiency, organic carbon, pH and fertiliser precision, with water / fertiliser / CO2 / rupee savings |
| **3.2 Bonus Module E** |  Built | Kisan Sahayak GenAI Assistant with Voice/TTS & multilingual capability |
| **3.2 Bonus Module F** |  Built | Soil Health Card advisory — converts the farmer's own N/P/K/pH card reading into bag-level fertiliser doses, a pH amendment and an irrigation schedule. Software only, no hardware |
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

### Step 4: Run the Test Suite
```bash
python -m unittest discover -s tests -v
```
51 tests covering the three pages, the soil advisory engine, every API endpoint,
upload validation, out-of-distribution screening, the knowledge base, and the
Section 4.1 predict CLI. It uses only the standard library plus what
`requirements.txt` already installs, so no extra test dependency is needed.
Tests that need inference skip themselves when `model/weights/best.pt` is absent,
so a clean checkout still passes.

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
     [Soil Health Card Advisory] ──── [Micro-Climate Weather] ──── [Kisan Sahayak AI Chat]
```

---

## 5. Model Metrics & Evaluation

Trained on the PlantVillage `color` dataset (54,305 images, 38 classes), split
80/20 stratified per class with `random.seed(42)`.

| Metric | Value |
| :--- | :--- |
| **Macro-F1 (primary metric)** | **0.9967** |
| Macro precision | 0.9970 |
| Macro recall | 0.9964 |
| Top-1 accuracy | 0.9980 |
| Weighted F1 | 0.9980 |
| Validation images | 10,849 |

- **Backbone:** YOLOv8s-cls (Ultralytics), ImageNet-pretrained, transfer-learned
- **Parameters:** 5,123,878 fused / 5,129,414 unfused (12.4 GFLOPs) — 0.3 ms per image on a T4
- **Training:** 20 epochs at 224×224, batch 64, on a Tesla T4. The train split is
  enlarged with blur and sensor-noise copies of 25% of the images (~65,000 total),
  because Ultralytics classification exposes no blur or noise augmentation parameter.
- **Out-of-distribution screening:** a single confidence cutoff cannot work here, because
  the two populations overlap — a blank white frame scores **84.8%** on this model while a
  genuinely blurred leaf scores **57.8%**. Each upload is averaged over five views
  (original, two flips, centre crop, flipped crop) and graded into three tiers by
  [`src/backend/ood_guard.py`](src/backend/ood_guard.py):

  | Tier | Condition | Behaviour |
  | :--- | :--- | :--- |
  | **Reject** | edge density outside 2.0–60.0, or confidence < 0.45, or entropy > 0.60 | No diagnosis; photo guidance shown |
  | **Provisional** | passes the floor but not all confirmed checks | Diagnosis shown with a "verify before spraying" warning |
  | **Confirmed** | confidence ≥ 0.85, entropy ≤ 0.25, view agreement ≥ 0.80, weakest view ≥ 0.60 | Diagnosis shown normally |

  The edge-density bounds are structural rather than probabilistic, so they hold whichever
  weights are loaded. Measured over 105 real leaf photographs (clean and degraded) against
  8 junk inputs: real leaves span **1.63–48.81**, flat frames (a wall, the sky, a lens cap,
  a solid colour) sit at **0.00–1.66**, and random sensor noise reaches **97.5**. The floor
  catches the blank-frame case that confidence alone misses — a white frame scored 84.8% on
  the previous model — and the ceiling catches static. Together they reject all 8 junk
  inputs at the cost of one heavily-darkened real frame.
  Thresholds are checked by `scripts/calibrate_guard.py` and must be re-run after retraining.

### Reproducing these numbers

```bash
python model/evaluate.py --data <validation_directory>
```

Writes `metrics.json`, `classification_report.txt`, `confusion_matrix.csv` and
`confusion_matrix.png` into `report/`.

### Known limitations

Macro-F1 of 0.9967 is measured **in-distribution** on held-out PlantVillage
images. PlantVillage is laboratory photography — single detached leaves, plain
backgrounds, controlled lighting — so this figure should not be read as a
field-performance estimate, and a drop on field photographs is expected.

The weakest class remains Corn Cercospora/Gray leaf spot (F1 0.9655), most often
confused with Corn Northern Leaf Blight (F1 0.9823); both present as elongated
grey-brown lesions along the leaf veins and are genuinely hard to separate from a
photograph. Tomato Early blight (0.9850) shows the same pattern.

### Degradation robustness

Because the official test set is field photography, the model was measured against
the sample set under nine capture conditions. The first training run was accurate
on clean images but collapsed on blur, so the train split was enlarged with blur
and sensor-noise copies and retrained:

| Condition | 8-epoch run | Current model |
| :--- | ---: | ---: |
| Clean | 100.0% | 100.0% |
| **Blur** | **44.4%** | **100.0%** |
| **Sensor noise** | **53.3%** | **95.6%** |
| Background clutter | 93.3% | 97.8% |
| Low light / bright / low contrast | 100.0% | 100.0% |
| Rotation 25° | 100.0% | 100.0% |
| JPEG quality 20 | 100.0% | 100.0% |
| **Mean** | **87.9%** | **99.3%** |

The earlier run failed *confidently* on blurred images (mean 80.3% confidence while
only 44.4% correct), which is the most dangerous failure mode for a farmer-facing
tool. Reproduce with `scripts/` against `data/dataset`.

The model predicts 38 classes and the agronomic knowledge base now covers all 38.

Full analysis: [`report/model_report.md`](report/model_report.md)

---

## 6. Video Demo & Links

- **Video Demo:** [Open the AgriSmart AI demo](demo/agri_smart_demo.mp4)
- **Live Deployed Web App:** `http://localhost:8000`
