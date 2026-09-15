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
# Thresholds sit inside those gaps, biased towards the in-distribution floor so a
# genuine leaf photo is never rejected.
MIN_VIEW_MEAN_CONFIDENCE = 0.85
MAX_NORMALISED_ENTROPY = 0.25
MIN_VIEW_AGREEMENT = 0.80
MIN_WEAKEST_VIEW_CONFIDENCE = 0.60

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


def screen(model, image_path: str) -> dict:
    """
    Run augmentation-averaged inference and decide whether the result is
    trustworthy enough to show as a diagnosis.

    Returns a dict with the predicted label, the averaged confidence, an
    `accepted` flag and the list of checks that failed.
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

    failed = []
    if view_mean_confidence < MIN_VIEW_MEAN_CONFIDENCE:
        failed.append("confidence")
    if normalised_entropy > MAX_NORMALISED_ENTROPY:
        failed.append("ambiguous_distribution")
    if agreement < MIN_VIEW_AGREEMENT:
        failed.append("unstable_under_augmentation")
    if weakest_view < MIN_WEAKEST_VIEW_CONFIDENCE:
        failed.append("weak_view")

    return {
        "accepted": not failed,
        "class_name": class_name,
        "confidence": view_mean_confidence,
        "failed_checks": failed,
        "diagnostics": {
            "view_mean_confidence": round(view_mean_confidence, 4),
            "normalised_entropy": round(normalised_entropy, 4),
            "view_agreement": round(agreement, 3),
            "weakest_view_confidence": round(weakest_view, 4),
            "views_evaluated": len(views),
        },
    }


# Wording is farmer-facing: say what to do next, not which statistic tripped.
_REJECTION_GUIDANCE = {
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
