# AgriSmart AI — Project Specification

**Challenge:** SIH 2026 Internal Hackathon, Problem Statement 1 — AgriSmart AI
**Institute:** L. J. Institute of Engineering and Technology [C-433]
**Repository:** `aarydesaii/QuidsIn-SIH-Internal-2026` (must be **public** at submission)
**Commit window:** 10 – 15 September 2026 — **hard rule**
**Status:** Active — see [Section 14](#14-open-questions--missing-data)

---

## 1. Executive Summary

Build an AI-powered crop-disease detection tool that classifies plant diseases from
leaf/crop images, reports macro-F1 on an organizer-held field test set, and presents the
result to a farmer in a simple, actionable way. Optionally extend into a broader
smart-agriculture advisor.

Three facts drive every decision in this document:

1. **The primary metric is macro-F1, not accuracy**, on a test set we never see.
2. **The test set is field photographs while training data is lab photographs.** The
   challenge is *generalisation*, not fitting. Models scoring high-90s on lab images
   degrade sharply on field images — this is stated as deliberate.
3. **The commit window is 10 – 15 September.** Work committed outside it does not count.

### Scope — Software Only

This project is **entirely software**. It ships no microcontrollers, sensors, or other
physical devices, and nothing in the codebase talks to hardware. The soil figures in
Bonus Module F come from a simulated agronomic model and are labelled as simulated
everywhere they appear in the interface. Section 6 records that the brief scores a
simulated feed equally with real sensor data, so this costs no marks.

---

## 2. Timeline — Critical

| | |
|---|---|
| Window opens | 10 September 2026 |
| **Today** | **11 September 2026** |
| Window closes | **15 September 2026** |
| Working days remaining | **~4** |

All substantive work must be committed inside this window, and commit history must
reflect genuine development across it. Repos created before kickoff with pre-built
solutions are **disqualified**. A steady commit trail from all six members is therefore
itself a compliance artifact — commit little and often, not in one dump at the end.

This timeline makes scope discipline the single highest-value decision the team makes.
See [Section 11](#11-execution-plan) for the day-by-day plan.

---

## 3. Scoring Model — What Actually Earns Points

Judging is out of 100. This table drives prioritization; nothing gets built without a
line here justifying it.

| Axis | Points | What earns it |
|------|-------:|---------------|
| AI/ML Implementation | 25 | Held-out macro-F1 vs baseline bands; honest split, no leakage, correct metric reporting. Bonus models add here. |
| Technical Implementation | 20 | **Reproducibility from README**, code quality, integration, deployment. **Gated: unreproducible core caps this axis.** |
| Innovation & Creativity | 15 | 12–15 novel capability; 7–11 thoughtful extension; 0–6 tutorial-level |
| Sustainability & Social Impact | 15 | 12–15 **quantified** benefit with stated method; 7–11 qualitative; 0–6 asserted only |
| User Experience | 10 | Farmer-friendliness, clarity, accessibility, regional language, shown in the demo |
| Problem Understanding | 10 | Framing, appropriate module choice, **honest limitations** |
| Presentation & Demo | 5 | The 3–5 minute video |
| **Total** | **100** | |

### 3.1 Strategic Reading

- **45 points (Technical + Sustainability + UX) require no additional model accuracy.**
  They are earned by reproducibility, a quantified impact method, and a clear farmer UI.
  These are the cheapest points available and they are where most teams under-invest.
- **Sustainability at 15 points explicitly rewards a published formula.** A qualitative
  claim caps at 11; a reproducible calculation reaches 15. Bonus Module D is therefore
  unusually high value per hour.
- **Problem Understanding rewards honest limitations.** Documenting where the model fails
  on field images scores; hiding it does not.
- **Tie-breaks run: macro-F1 → reproducibility → bonus depth → innovation.** Reproducibility
  is second, ahead of every bonus module.

---

## 4. Mandatory Core Task

Non-negotiable. *A submission that does not deliver the core task is incomplete
regardless of how many bonus modules it includes.*

### 4.1 Minimum Bar

- [ ] A trained model (transfer learning encouraged)
- [ ] An honest train / validation / test split, with no leakage
- [ ] Reported **macro-F1** on the held-out test set
- [ ] A **confusion matrix** and per-class precision/recall
- [ ] A minimal interface that runs a prediction on a new image
- [ ] Clear result plus basic precautionary guidance surfaced to the user

### 4.2 The Predict Interface — Mandatory Contract

The organizers compute our official score by running **our** interface against **their**
data. It must work with no manual steps.

Expose **either**:

```python
predict(image_path) -> class_label
```

**or** a documented CLI:

```bash
python predict.py --image path/to/leaf.jpg
```

Requirements:

- Loads trained weights itself
- Runs on a single new image
- Prints/returns the predicted class in the exact published label-string format
- **No manual steps, no notebook cells to run in order, no hardcoded paths**

> The exact signature and label-string format ship with the kickoff data. Confirm ours
> matches character-for-character — a label format mismatch scores zero on a working model.

---

## 5. Data & Evaluation Protocol

### 5.1 The Deliberate Difficulty

| | Training / validation | Held-out test |
|---|---|---|
| **Source** | PlantVillage — lab conditions, uniform background | Field-condition set, PlantDoc-style — natural lighting, clutter, occlusion |
| **Scale** | ~54,000 images across the shared class list, released at kickoff | Separate unseen set, used only at judging; small public sample shared at kickoff for format checks |
| **Role** | Train and validate here; other public data may be added if cited | **Never train on it.** Organizers compute our core metric here |

**Shared class list:** ~15–20 crop–disease classes plus "healthy" — e.g. Tomato Early
Blight, Tomato Late Blight, Tomato Leaf Mould, Tomato Bacterial Spot, Potato Early/Late
Blight, Corn Common Rust, Corn Grey Leaf Spot, Apple Scab, Apple Black Rot, Grape Black
Rot, Bell Pepper Bacterial Spot, plus matching healthy classes. The final list ships with
kickoff data and is used **verbatim**.

### 5.2 Primary Metric

**Macro-averaged F1** on the held-out field test set. Macro-F1 rather than accuracy
because the disease classes are imbalanced.

Practical consequence: **every class counts equally regardless of size.** A model that
nails the five large classes and fails the three small ones scores badly on macro-F1
while looking fine on accuracy. Rare classes must be handled deliberately — class
weighting, oversampling, or targeted augmentation — and validation must be scored with
macro-F1 from the very first training run.

### 5.3 Data Rules — Compliance

- Extra **public** data may be added to training, **if cited** in the README
- Any data may be used for bonus modules
- **Training on the held-out set forfeits the entire AI/ML axis (25 points)**
- **Substituting our own test data for the core score is non-compliant**

### 5.4 Generalisation Strategy — The Core Technical Problem

Training on lab images and testing on field images is a domain-shift problem. Planned
countermeasures, in priority order:

1. **Aggressive domain-randomising augmentation** — random backgrounds, occlusion/cutout,
   heavy colour jitter, motion blur, varied lighting, random rotation and perspective.
   This is the single highest-leverage intervention available.
2. **Validate on field-like images, not lab images.** The kickoff public field sample is
   used as a sanity check — for *format*, and as a rough generalisation signal. Our own
   phone photos of real leaves serve the same purpose.
3. **Test-time augmentation** — average predictions over a few transforms.
4. **Avoid over-training.** High lab validation accuracy is a warning sign of memorisation,
   not a success signal.
5. **Backbone choice** — a strong pretrained backbone generalises better than a small one
   trained longer. Consider EfficientNet-B0 or a ViT if compute allows.

---

## 6. Optional Bonus Modules (Section 3.2 of the brief)

Each adds points. Built **only after the core task is complete and reproducible.**

| ID | Module | What it adds | Requirement stated in brief |
|----|--------|--------------|------------------------------|
| A | Crop Recommendation | Suitable crops from soil type, pH, temperature, humidity, rainfall, water availability, season, location, previous crop | Report metric **and data source** |
| B | Smart Irrigation | Predict irrigation need from soil moisture, forecast, crop type, growth stage | State the logic/model and **how it was validated** |
| C | Weather-Based Intelligence | Live/forecast weather + farm conditions → actions ("delay irrigation — rain likely") | **Name the weather data source** |
| D | Sustainability Score | Indicative score from water efficiency, resource use, crop health, with improvements | **Publish the exact formula so it is reproducible** |
| E | Farmer Assistant (GenAI) | Conversational/voice interface explaining recommendations in plain language, ideally regional-language | **Grounded answers score higher than free-form** |
| F | Soil Analytics | Soil moisture, temperature, humidity and pH presented as an advisory feed. **Implemented as a software simulation — this project ships no hardware.** | **Simulated/streamed feed is fully acceptable and scored equally** |
| G | Agentic Advisor | Autonomous agent that analyses, reasons, checks data, decides, notifies | Show the decision loop and ≥1 end-to-end automated recommendation |

### 6.1 Recommended Priority

Given four days, chosen for points-per-hour and rubric alignment:

| Rank | Module | Rationale |
|------|--------|-----------|
| 1 | **D — Sustainability Score** | Directly targets a 15-point axis. A published formula moves the score from ≤11 to 12–15. Pure logic, no model training, no external API. |
| 2 | **C — Weather Intelligence** | One free API. Feeds D with real numbers and produces visibly actionable output for the UX axis. |
| 3 | **E — Farmer Assistant** | Serves UX (10) and regional-language credit. Must be **grounded** in the detection result and knowledge base, not free-form. |
| 4 | **B — Smart Irrigation** | Rule-based version is cheap once C exists; feeds D's water-efficiency term. |
| 5 | **F — Soil Analytics (simulated)** | The brief awards a simulated feed full marks, so no physical devices are required. Cheap if B exists. |
| 6 | **A — Crop Recommendation** | Needs a separate dataset and model. Real cost. |
| 7 | **G — Agentic Advisor** | Highest innovation ceiling, highest risk. Only if everything else is done. |

**Modules D → C → E form a coherent chain**: detection feeds weather context feeds a
quantified sustainability number explained in plain language. That narrative scores
across AI/ML, Sustainability, UX and Innovation simultaneously, which scattered
unconnected modules do not.

---

## 7. Submission Contract — Mandatory

A submission is **judged only if** it meets these requirements. Reproducibility is a
scored gate.

### 7.1 Required Repository Structure

The brief mandates this layout. **Our repo must conform.**

```
/README.md              entry point — see 7.2
/src  or  /app          source code
/model                  training + inference code, the predict interface, weights
/report                 one-page model report — see 7.3
requirements.txt        environment file + clear run instructions
```

Adopted structure:

```
/README.md
/requirements.txt
/src
    /backend            FastAPI application
    /frontend           React + Vite PWA
/model
    train.py            or train.ipynb
    predict.py          MANDATORY predict interface
    evaluate.py         macro-F1, confusion matrix, per-class metrics
    weights/            via release or link if large
/report
    model_report.md     one-page report
/data                   gitignored — datasets never committed
specs.md
```

> Note: this replaces the earlier `/backend` `/frontend` `/ml` layout. The submission
> contract is explicit and non-negotiable; our own preferences yield to it.

### 7.2 Required README Contents

1. Which core + bonus modules were built
2. Setup and run instructions — **a judge must reproduce a prediction in under ~10 minutes**
3. Dataset used, with source and licence
4. Reported metrics for every model — core: macro-F1 + confusion matrix
5. Architecture overview and known limitations
6. Link to the demo video and any deployed app
7. **Originality declaration** listing all third-party code and notebooks referenced

### 7.3 Required Model Report (`/report`, one page)

| Field | Content |
|-------|---------|
| Task | Crop-disease image classification, N classes |
| Dataset & split | Source, sizes, exact train/validation/test split |
| Model / approach | Architecture, backbone, key hyperparameters |
| Metric & result | Macro-F1 (primary) + accuracy, confusion matrix, per-class precision/recall |
| Baseline | The provided baseline number and how we compare |
| Limitations | Honest failure cases — e.g. real-field vs lab images |

### 7.4 Demo Video — Primary Evidence

A **3–5 minute** recorded demo (unlisted link acceptable) is the *primary*
demonstration. It must show the core task running on a new image, plus any bonus modules.

This is worth 5 points directly but is also how the UX axis (10) is assessed. It is a
scheduled deliverable, not an afterthought — see [Section 11](#11-execution-plan).

### 7.5 Originality Rules

- Open-source libraries, pretrained backbones and public datasets are **encouraged**, but
  must be cited
- **Copying a public notebook or solution wholesale is prohibited**
- An originality declaration is required in the README
- **AI coding assistants are explicitly permitted** — the working system and its
  evaluation are what get scored

---

## 8. Team

Six members. **Workload is fully shared** — no fixed role silos.

| Member |
|--------|
| Aary Desai |
| Aryan Rupela |
| Mihir Agath |
| Naitree Mehta |
| Niyati Kamani |
| Pal Patel |

### 8.1 Working Agreements

- **Everyone commits.** Commit history is a compliance artifact under the 10–15 September
  rule; a member with no commits is invisible to judges.
- Claim a task before starting it — shared ownership is not shared editing of one file
- Feature branches off `main`; no direct pushes once development is underway
- `requirements.txt` and `package.json` committed and current
- **At least two members must be able to run the full stack from a clean clone**, because
  reproducibility is the gated axis

### 8.2 Suggested Parallel Tracks

Shared workload still needs parallelism to fit four days:

| Track | Focus |
|-------|-------|
| Model | Dataset prep, training, augmentation, macro-F1 tuning |
| Interface | `predict.py`, `evaluate.py`, FastAPI backend |
| Frontend | PWA capture → result flow |
| Content & bonus | Knowledge base, sustainability formula, weather module |
| Docs & demo | README, model report, video — started early, not on day 4 |

---

## 9. Technical Architecture

### 9.1 Flow

```
Farmer's phone (PWA)
        |  compressed JPEG over HTTPS
        v
FastAPI backend  ──>  PyTorch model (loaded once at startup)
        |                      |
        |                      v
        |              class + confidence
        v
Disease knowledge base (JSON)  ──>  actionable precaution
        |
        +──> [Bonus C] weather context
        +──> [Bonus D] sustainability score
        +──> [Bonus E] grounded plain-language explanation
        v
Result card returned to farmer
```

`predict.py` is standalone and does **not** depend on the web stack — judges must be able
to run it without starting a server.

### 9.2 Stack

**ML / computer vision**

| Tool | Purpose |
|------|---------|
| PyTorch + torchvision | Model, transfer learning, transforms |
| EfficientNet-B0 / MobileNetV3 / ResNet18 | Pretrained backbone, fine-tuned |
| Google Colab (free T4) | Training |
| scikit-learn | **Macro-F1**, confusion matrix, per-class precision/recall |
| albumentations | Domain-randomising augmentation (Section 5.4) |

**Backend**

| Tool | Purpose |
|------|---------|
| FastAPI | HTTP API, OpenAPI docs at `/docs` |
| Uvicorn | ASGI server |
| Pydantic v2 | Validation |
| python-multipart | **Required** for uploads — FastAPI cannot accept files without it |
| Pillow | Image handling |
| torch (CPU build) | Server inference |
| python-dotenv | Secrets, with committed `.env.example` |
| SQLAlchemy + SQLite | Prediction history |
| ruff | Lint + format |
| pytest + httpx | API tests |

**Frontend**

| Tool | Purpose |
|------|---------|
| React + Vite | UI and build |
| Tailwind CSS | Styling |
| React Router | Navigation |
| Axios | Multipart upload |
| react-dropzone | Upload UI |
| react-webcam | Camera capture |
| browser-image-compression | Shrink 4–8 MB phone photos |
| shadcn/ui or DaisyUI | Components |
| lucide-react | Icons |
| Recharts | Confidence bars, confusion matrix |
| TanStack Query | Async state |
| i18next | Regional language (UX axis + Module E) |
| vite-plugin-pwa | Offline mode (listed innovation opportunity) |

**Deployment:** Vercel/Netlify (frontend), Render/Railway (backend), with a rehearsed
local-only fallback.

---

## 10. User Experience

### 10.1 Reference Scenario (from the brief)

| Input | Example |
|-------|---------|
| Leaf image | Uploaded photo of affected leaf |
| Crop / stage | Tomato / Growing |
| Soil / pH / moisture | Loamy / 6.5 / 31% |
| Temperature / rain probability | 28–32 °C / High |

Target output:

- **Detection (core):** Early Blight — confidence 0.91. Precaution: remove affected
  leaves, avoid overhead watering.
- **Irrigation (B):** Delay irrigation — rainfall likely in next 24h.
- **Sustainability (D):** Estimated reduction in unnecessary water use this week.
- **Assistant (E):** Plain-language explanation, optionally regional-language.

This is the demo script. Building toward exactly this output makes the video
straightforward to record.

### 10.2 Principles

- Mobile-first; the farmer is on a phone, possibly offline, possibly not reading English
- Capture or upload reachable in one tap
- Plain language — never raw labels like `Tomato___Late_blight`
- Confidence shown visually
- Every result ends in an **action**
- Low-confidence state shows top-3 alternatives and prompts a retake — honest uncertainty
  supports the Problem Understanding axis

### 10.3 Screens

1. Home / Capture
2. Processing
3. Result — disease, confidence, severity, precaution, treatment
4. Low-confidence — top-3 with retake prompt
5. Metrics — macro-F1 and confusion matrix, evidencing the core requirement
6. History (bonus)

---

## 11. Execution Plan

Four days. Ordering is fixed; the core must be reproducible before any bonus work starts.

| Day | Target | Gate |
|-----|--------|------|
| **Day 1 — 11 Sep** | Repo restructured to the mandated layout. Kickoff data downloaded, class list confirmed. Dataset split. Baseline training run started in Colab. Frontend and backend scaffolds running. | Everyone has committed at least once |
| **Day 2 — 12 Sep** | Trained model with macro-F1 recorded. `predict.py` matching the published signature exactly. `evaluate.py` producing macro-F1 + confusion matrix. Augmentation pipeline in place. | **`python predict.py --image x.jpg` works from a clean clone** |
| **Day 3 — 13 Sep** | FastAPI `/predict` live. PWA capture→result flow working. Knowledge base populated. Core demo-able end to end. Retrain with full augmentation. | **Core task complete — the submission is now valid** |
| **Day 4 — 14 Sep** | Bonus modules D → C → E in priority order. README written in full. Model report written. Deployment. | Reproducibility tested by a member who did not build it |
| **Day 5 — 15 Sep** | Demo video recorded. Final metrics. Originality declaration. Buffer. **Submit.** | Repo public, link submitted |

**Day 3 is the point at which the submission becomes valid.** Nothing before it may be
skipped to reach bonus work faster. If Day 3 slips, bonus modules are cut, not the core.

---

## 12. Non-Functional Requirements

| Area | Target |
|------|--------|
| **Reproducibility** | **Judge runs a prediction in under 10 minutes from README — gated scoring axis** |
| Inference latency | Under 2 s end-to-end on mobile |
| Upload size | Under 500 KB after client-side compression |
| Demo availability | Local fallback works with no internet |
| Accessibility | Legible contrast, large tap targets, alt text |
| Language | English first; regional language for UX credit |
| Privacy | No personal data collected; images not retained beyond session by default |

---

## 13. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Model memorises lab images, fails on field test set** | **Critical — this is the stated challenge** | Aggressive domain augmentation; validate on field-like images; never trust lab validation accuracy |
| Optimising accuracy instead of macro-F1 | High — wrong metric, wrong model | Score macro-F1 from the first training run; weight rare classes |
| `predict.py` signature or label format mismatch | **Critical — working model scores zero** | Verify against the kickoff format-check sample immediately |
| Judge cannot reproduce from README | **Critical — caps a 20-point gated axis** | Clean-clone test by an uninvolved member on Day 4 |
| Repo structure does not match Section 7.1 | High — judged non-compliant | Restructured on Day 1 |
| Work committed outside 10–15 Sep | **Disqualification** | All commits inside the window; steady history |
| Demo video left to the last hours | High — 5 points plus UX assessment | Scheduled Day 5 with Day 4 buffer |
| Bonus modules started before core is done | High | Day 3 gate is hard |
| Model weights exceed hosting limits | Medium | Release assets or external link, as the brief permits |
| Missing `python-multipart` / CORS misconfiguration | Medium — hours lost to opaque errors | Configured on Day 1 |

---

## 14. Open Questions / Missing Data

### 14.1 Blocking — needed from kickoff materials

1. **The kickoff dataset itself** — the ~54,000-image PlantVillage training set. Not yet
   downloaded. Nothing can be trained without it.
2. **The exact final class list** — "~15–20 classes, ships with the kickoff data, used
   verbatim." Our label set must match exactly.
3. **The exact `predict` signature and label-string format** — "published with the data."
   A mismatch scores zero on a working model.
4. **The public field-condition sample** — needed for format checks and as our only
   real generalisation signal before judging.
5. **The provided baseline number** — the model report must state how we compare to it,
   and the AI/ML bands are anchored to it.

> All five arrive with the kickoff data. **Obtaining the kickoff package is the single
> most urgent action** — four of the five are otherwise unresolvable.

### 14.2 Needed from the team

6. **Bonus module commitment** — which of A–G are we actually attempting? The plan
   assumes D → C → E.
7. **Compute access** — anyone with a local GPU, or is it Colab free tier for all
   training runs?
8. **Repo visibility** — the repo must be **public** at submission. Is it currently?
9. **Collaborator access** — are all six members added to
   `aarydesaii/QuidsIn-SIH-Internal-2026`? Nobody can commit otherwise, and everyone
   needs commits in the window.
10. **Regional language choice** — Hindi, Gujarati, or both?
11. **Demo video ownership** — who records and edits, and with what tool?
12. **Submission mechanism** — where exactly is the repo link submitted, and by what time
    on 15 September?

### 14.3 Minor

13. **API keys** — Module C needs a weather source; Module E needs an LLM key. Free tier
    only, or does someone have paid access?
14. **Deployment accounts** — Vercel/Netlify/Render accounts set up?
15. **Document numbering** — the PDF is titled "Problem Statement 1" but the file is named
    `ProblemStatement-2.pdf`. Confirm we are working from the correct statement.

---

*Specification current as of 11 September 2026, derived from the official problem
statement PDF. Update as kickoff data resolves the open questions.*
