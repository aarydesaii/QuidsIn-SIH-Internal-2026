"""
Out-of-distribution screening for the diagnostic scanner.

The classifier is trained on PlantVillage, which covers 38 classes across 14 crops.
Anything outside that set - a different crop, a non-leaf photo, a blurred or badly
lit frame - still produces a confident-looking softmax, because a saturated
38-way head has no way to express "none of the above". Screening the prediction
before it reaches the farmer keeps the platform from issuing a spray
recommendation for a crop it was never trained on.

Every threshold below was calibrated by measuring the trained weights against the
sample set in data/dataset (45 in-distribution images) and three synthetic
out-of-distribution probes. Re-run scripts/calibrate_guard.py after retraining.
"""

import math

import numpy as np
from PIL import Image

# Measured separation on the current weights:
#
#                        in-distribution (n=45)      out-of-distribution (n=3)
#   view-mean confidence      min 0.934                   max 0.575
#   normalised entropy        max 0.055                   min 0.584
#   view agreement            min 1.000                   min 0.600
#   weakest single view       5th pct 0.876               max 0.575
#
# Thresholds for the CONFIRMED tier. A photo clearing all four is reported as a
# straight diagnosis.
MIN_VIEW_MEAN_CONFIDENCE = 0.85
MAX_NORMALISED_ENTROPY = 0.25
MIN_VIEW_AGREEMENT = 0.80
MIN_WEAKEST_VIEW_CONFIDENCE = 0.60

# Those four thresholds were calibrated against clean laboratory photographs, whose
# view-mean confidence never drops below 0.934. Field photographs are not that
# clean: measured over the sample set degraded with blur, low light, background
# clutter and sensor noise, genuine leaves fall as low as 0.298, and 38% of them
# failed the CONFIRMED bar. Rejecting those outright tells a farmer holding a real
# diseased leaf that the crop is unrecognisable.
#
# Confidence alone cannot fix this, because the two populations overlap: a blank
# white frame scores 0.848 while a genuinely blurred leaf scores 0.578. So the
# bounds below are structural rather than probabilistic, and being properties of
# the image they hold regardless of which weights are loaded.
#
# Measured mean-absolute-gradient over 105 real leaf photographs (clean and
# degraded with blur, low light, clutter and noise) against 8 junk inputs:
#
#   real leaves    1.63 - 48.81   (5th percentile 3.20, median 19.68)
#   flat junk      0.00 - 1.66    (white, black, solid colours, a gradient, a drawing)
#   random noise   97.52
#
# Below the floor the frame is too flat to be a photograph of a plant; above the
# ceiling it carries more high-frequency energy than any real leaf, which means
# sensor noise or static rather than foliage. Together these bounds reject all 8
# junk inputs at the cost of a single heavily-darkened real frame.
MIN_EDGE_DENSITY = 2.0
MAX_EDGE_DENSITY = 60.0

# Floor for showing anything at all. Between this floor and the CONFIRMED bar the
# prediction is returned as PROVISIONAL: shown, but flagged for verification.
MIN_USABLE_CONFIDENCE = 0.45
MAX_USABLE_ENTROPY = 0.60

# Averaging the softmax over flips and a centre crop costs one batched forward
# pass (~160 ms on CPU against ~50 ms for a single view). A single view is easy
# for an unfamiliar crop to saturate by chance; agreeing across five is not.
def _build_views(image: Image.Image):
    width, height = image.size
    side = min(width, height)
    left, top = (width - side) // 2, (height - side) // 2
    centre = image.crop((left, top, left + side, top + side)).resize((width, height))
    return [
        image,
        image.transpose(Image.FLIP_LEFT_RIGHT),
        image.transpose(Image.FLIP_TOP_BOTTOM),
        centre,
        centre.transpose(Image.FLIP_LEFT_RIGHT),
    ]


def _edge_density(image: Image.Image) -> float:
    """Mean absolute gradient. Near zero for a flat frame, high for real foliage."""
    grey = np.asarray(image.resize((224, 224)), dtype=np.float64).mean(axis=2)
    return float(np.abs(np.diff(grey, axis=0)).mean() + np.abs(np.diff(grey, axis=1)).mean())


def screen(model, image_path: str) -> dict:
    """
    Run augmentation-averaged inference and grade the result into one of three
    tiers: "confirmed", "provisional" or "reject".

    Returns a dict with the predicted label, the averaged confidence, `accepted`
    (true for confirmed and provisional), `provisional`, and the failed checks.
    """
    image = Image.open(image_path).convert("RGB")
    views = _build_views(image)

    results = model(views, verbose=False)
    class_names = results[0].names
    probabilities = np.stack([r.probs.data.cpu().numpy().astype(np.float64) for r in results])

    # Average the distributions, then read the winner off the consensus rather
    # than off whichever single view happened to score highest.
    mean_probabilities = probabilities.mean(axis=0)
    top_index = int(mean_probabilities.argmax())
    class_name = str(class_names[top_index])

    per_view_winners = probabilities.argmax(axis=1)
    per_view_confidence = probabilities.max(axis=1)

    view_mean_confidence = float(mean_probabilities[top_index])
    agreement = float((per_view_winners == top_index).mean())
    weakest_view = float(per_view_confidence.min())
    entropy = float(-np.sum(mean_probabilities * np.log(mean_probabilities + 1e-12)))
    normalised_entropy = entropy / math.log(len(mean_probabilities))

    edge = _edge_density(image)

    failed = []
    if edge < MIN_EDGE_DENSITY:
        failed.append("not_a_photograph")
    if edge > MAX_EDGE_DENSITY:
        failed.append("too_noisy")
    if view_mean_confidence < MIN_USABLE_CONFIDENCE:
        failed.append("confidence")
    if normalised_entropy > MAX_USABLE_ENTROPY:
        failed.append("ambiguous_distribution")

    if failed:
        tier = "reject"
    elif (view_mean_confidence >= MIN_VIEW_MEAN_CONFIDENCE
            and normalised_entropy <= MAX_NORMALISED_ENTROPY
            and agreement >= MIN_VIEW_AGREEMENT
            and weakest_view >= MIN_WEAKEST_VIEW_CONFIDENCE):
        tier = "confirmed"
    else:
        tier = "provisional"

    return {
        "accepted": tier != "reject",
        "provisional": tier == "provisional",
        "tier": tier,
        "class_name": class_name,
        "confidence": view_mean_confidence,
        "failed_checks": failed,
        "diagnostics": {
            "view_mean_confidence": round(view_mean_confidence, 4),
            "normalised_entropy": round(normalised_entropy, 4),
            "view_agreement": round(agreement, 3),
            "weakest_view_confidence": round(weakest_view, 4),
            "edge_density": round(edge, 2),
            "views_evaluated": len(views),
        },
    }


# Wording is farmer-facing: say what to do next, not which statistic tripped.
_REJECTION_GUIDANCE = {
    "not_a_photograph": "This frame is almost flat, so it does not look like a photograph of a leaf - point the camera at the plant",
    "too_noisy": "This frame is too grainy to read - clean the lens, add light, and hold the camera steady",
    "confidence": "Photograph a single leaf filling most of the frame, against a plain background",
    "ambiguous_distribution": "This may be a crop the model was not trained on - it currently covers 14 crops including tomato, potato, corn, apple and grape",
    "unstable_under_augmentation": "Hold the camera steady and re-take the photo in even daylight",
    "weak_view": "Move closer so the affected area is sharp, and avoid glare or heavy shadow",
}


def rejection_guidance(failed_checks) -> list:
    """Turn the failed checks into advice, keeping a stable order and no repeats."""
    tips = [_REJECTION_GUIDANCE[c] for c in failed_checks if c in _REJECTION_GUIDANCE]
    if not tips:
        tips.append(_REJECTION_GUIDANCE["confidence"])
    tips.append("If this is a crop outside the supported list, the reading will not be reliable")
    return tips
