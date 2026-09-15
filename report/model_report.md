# AgriSmart AI — Model Report

**Challenge:** SIH 2026 Internal Hackathon, Problem Statement 1 — AgriSmart AI
**Institute:** L. J. Institute of Engineering and Technology [C-433]
**Date:** 15 September 2026

---

## Task

Crop-disease image classification over **38 classes** spanning 14 crop species
(apple, blueberry, cherry, corn, grape, orange, peach, bell pepper, potato,
raspberry, soybean, squash, strawberry, tomato). Each class is either a named
disease or the healthy state for that crop.

The model accepts a single leaf photograph and returns one class label. It is
exposed through the mandatory predict interface described in Section 4.2 of the
project specification.

---

## Dataset & Split

| | |
|---|---|
| Source | PlantVillage Dataset (Kaggle: `abdallahalidev/plantvillage-dataset`) |
| Variant used | `color` — the RGB photographs, not the `grayscale` or `segmented` variants |
| Total images | 54,305 |
| Classes | 38 |
| Train | 43,456 images (80%) |
| Validation | 10,849 images (20%) |
| Test | None held out locally — the organizers' held-out field set is the official test |
| Split method | Stratified per class, `random.seed(42)`, reproducible |

The `color` variant was chosen deliberately. The `segmented` variant has the
background removed, which does not match the photographs the deployed
application receives from farmers, and training on it would widen rather than
narrow the lab-to-field gap discussed under Limitations.

The split is stratified per class so that every class keeps its 80/20 proportion.
No image appears in both partitions, and the fixed seed makes the partition
reproducible from a clean run.

---

## Model / Approach

| | |
|---|---|
| Architecture | YOLOv8s-cls (Ultralytics classification head) |
| Backbone | `yolov8s-cls.pt`, ImageNet-pretrained — transfer learning |
| Parameters | 5,123,878 fused for inference / 5,129,414 unfused (12.4 GFLOPs) |
| Image size | 224 × 224 |
| Epochs | 20 |
| Batch size | 64 |
| Hardware | NVIDIA Tesla T4 (Kaggle) |
| Training time | ~1.8 hours |
| Framework | Ultralytics 8.4.152, PyTorch 2.10.0+cu128 |

### Augmentation

Augmentation was selected specifically to narrow the lab-to-field generalisation
gap, since the training images are controlled laboratory photographs while the
official test set is field photography.

| Augmentation | Value | Purpose |
|---|---|---|
| `hsv_h` / `hsv_s` / `hsv_v` | 0.015 / 0.7 / 0.4 | Tolerance to outdoor lighting, shade and white balance |
| `degrees` | 15.0 | Hand-held camera angles |
| `translate` | 0.1 | Leaf not centred in frame |
| `scale` | 0.2 | Variable camera distance |
| `shear` | 5.0 | Off-axis viewpoints |
| `perspective` | 0.0005 | Non-perpendicular capture |
| `flipud` / `fliplr` | 0.5 / 0.5 | Orientation invariance |
| `erasing` | 0.4 | Partial occlusion — leaves overlapping or partly out of frame |

Ultralytics' classification pipeline exposes no blur or noise parameter, so those
two were applied to the training images on disk instead: 25% of the train split was
duplicated once blurred (Gaussian, radius 1.2–2.6) and once with additive Gaussian
sensor noise (sigma 15–32), enlarging the split from 43,456 to roughly 65,000 images.
The validation split was left untouched so the reported metrics stay honest.

This step was added after measuring the first training run, which scored 100% on
clean images but only **44.4% on blurred ones** while remaining 80% confident — the
most dangerous failure mode for a farmer-facing tool.

---

## Metric & Result

The primary competition metric is **macro-F1**, which weights every class equally
regardless of how many images it contains. Accuracy is reported alongside it for
completeness but is not the metric of record.

| Metric | Value |
|---|---|
| **Macro-F1 (primary)** | **0.9967** |
| Macro precision | 0.9970 |
| Macro recall | 0.9964 |
| Accuracy | 0.9980 |
| Weighted F1 | 0.9980 |
| Validation images | 10,849 |

Macro-F1 (0.9967) and weighted F1 (0.9980) are close together, which indicates
the model is not achieving its score by performing well on large classes while
neglecting small ones. The smallest validation class, `Potato___healthy` with 30
images, still reaches F1 0.9831.

### Weakest classes

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | 0.9703 | 0.9608 | 0.9655 | 102 |
| `Corn_(maize)___Northern_Leaf_Blight` | 0.9798 | 0.9848 | 0.9823 | 197 |
| `Potato___healthy` | 1.0000 | 0.9667 | 0.9831 | 30 |
| `Tomato___Early_blight` | 0.9850 | 0.9850 | 0.9850 | 200 |
| `Grape___healthy` | 0.9882 | 1.0000 | 0.9941 | 84 |

Twenty of the 38 classes reach F1 1.0000 on the validation split.

Against the earlier 8-epoch run, the weakest classes improved most — which is what
macro-F1 rewards. Corn Cercospora/Gray leaf spot rose from 0.9029 to 0.9655
(+6.3 points) and Northern Leaf Blight from 0.9490 to 0.9823.

The full per-class table, the confusion matrix, and the machine-readable metric
summary are reproducible with:

```bash
python model/evaluate.py --data <validation_directory>
```

which writes `metrics.json`, `classification_report.txt`, `confusion_matrix.csv`
and `confusion_matrix.png` into this directory.

---

## Baseline

The organizers' baseline number for the held-out field test set had not been
published at the time of writing, so a direct comparison is not yet possible.

As an internal reference point, the ImageNet-pretrained `yolov8s-cls` backbone
before fine-tuning scores effectively zero on this task, because its 1,000
ImageNet categories contain no crop-disease classes; it predicts unrelated
labels for every leaf image. The entirety of the 0.9967 macro-F1 is therefore
attributable to fine-tuning on PlantVillage rather than to the pretrained
weights, though the pretrained features are what make convergence in 20 epochs
possible.

This report will be updated with the official baseline comparison once that
number is available.

---

## Limitations

**The validation score is measured in-distribution and should not be read as a
field-performance estimate.** PlantVillage consists of laboratory photographs:
single detached leaves, uniform backgrounds, controlled lighting. The validation
split is drawn from that same distribution, so 0.9967 macro-F1 measures how well
the model classifies lab images resembling those it trained on. The official test
set is field photography, and a meaningful drop is expected. This gap is the
central difficulty of the problem statement, not an artifact of this run.

**The dominant failure mode is agronomically genuine, not merely statistical.**
The two weakest classes remain a single confusable pair: Corn Cercospora / Gray
leaf spot (F1 0.9655) and Corn Northern Leaf Blight (F1 0.9823), which are
mistaken for each other. Both present as elongated grey-brown lesions running
parallel to the leaf veins, and they are difficult for trained agronomists to
separate from a photograph alone. In the previous 8-epoch run this pair produced
the two largest off-diagonal cells in the confusion matrix (11 and 9 instances);
retraining roughly halved that error rate without eliminating it. It remains the
clearest target for additional training data.

A comparable pattern appears among the tomato classes, where Target Spot, Early
blight and Spider mite damage are mutually confused — all produce irregular
necrotic leaf spotting.

**One cross-crop confusion is biologically coherent.** Five `Potato___Late_blight`
images were classified as `Tomato___Late_blight`. Both diseases are caused by the
same pathogen, *Phytophthora infestans*, and produce near-identical lesions on
the two hosts. Agronomically the treatment advice is also near-identical, so the
practical cost of this particular error is low — but it is a real limitation of a
model that classifies crop and disease as one joint label.

**Single-leaf framing.** The model was trained on images containing one leaf
against a plain background. Photographs showing whole plants, multiple
overlapping leaves, soil, hands or other field clutter fall outside the training
distribution. The augmentation pipeline above mitigates this but does not
eliminate it.

**No severity estimation.** The model reports which disease is present, not how
far it has progressed. Severity shown in the application interface is drawn from
the static knowledge base entry for the predicted class, not inferred from the
image.

**Knowledge-base coverage is narrower than model coverage.** The model predicts
38 classes while the application's agronomic knowledge base holds detailed
remedies for 15. The remaining classes resolve to a generic advisory that directs
the farmer to their local Krishi Vigyan Kendra. Diagnosis is correct for all 38;
the depth of the accompanying guidance varies.

**Robustness was measured, not assumed.** The model is now accurate under blur,
sensor noise, low light, over-exposure, low contrast, 25-degree rotation and heavy
JPEG compression (mean 99.3% across nine conditions, worst case 95.6%). The
remaining soft spot is background clutter at 97.8%, since PlantVillage contains no
cluttered scenes at all; adding real field imagery such as PlantDoc is the natural
next step and would target the same weakness as the lab-to-field gap above.
