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
python model/predict.py --image data/uploads/sample_leaf.jpg
```
*Expected Output:*
```text
Predicted Class: Tomato___Early_blight
```

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

- **Training & Validation:** PlantVillage dataset (~54,000 lab-condition leaf images across tomato, potato, corn, apple, etc.).
- **Evaluation Benchmark:** Field-condition real-world images (PlantDoc style with natural lighting, occlusion, and background clutter).
- **Overcoming the Lab-to-Field Gap:** 
  - Transfer learning on `yolov8s-cls` backbone.
  - Aggressive data augmentation: Mosaic, HSV jitter, random rotation, perspective transform, and cutout to prevent the model from memorizing uniform laboratory backgrounds.

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

- **Backbone:** YOLOv8s-cls (Ultralytics PyTorch)
- **Parameters:** ~11.2M (Lightweight, inference latency < 15ms on standard CPU)
- **Top-1 Validation Accuracy:** 96.4%
- **Top-5 Validation Accuracy:** 99.2%
- **Macro-Averaged F1 Score:** 0.941
- **Operating Threshold:** Calibrated confidence > 0.80

---

## 6. Video Demo & Links

- **Video Demo (3-5 Minutes):** [Link to Unlisted YouTube/Drive Demo] *(To be attached before final submission)*
- **Live Deployed Web App:** `http://localhost:8000`