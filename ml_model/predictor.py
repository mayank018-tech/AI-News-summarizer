"""
ml_model/predictor.py
─────────────────────
Loads the trained TF-IDF + LinearSVC pipeline and exposes a single
`predict_category(text)` function that returns a structured dict
compatible with the existing /analyze response format.
"""

import os
import re
import joblib
import numpy as np

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, "ml_model", "category_classifier.pkl")

LABEL_MAP = {
    0: "AI Technology & Systems",
    1: "Research & Science",
    2: "Policy, Law & Ethics",
}

# Load model once at import time (cached for all requests)
_pipeline = None

def _load_pipeline():
    global _pipeline
    if _pipeline is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model not found at {_MODEL_PATH}. "
                "Please run: python ml_model/train_model.py"
            )
        _pipeline = joblib.load(_MODEL_PATH)
    return _pipeline


def _clean(text: str) -> str:
    """Minimal text cleaning matching the training pipeline."""
    text = str(text).lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_category(text: str) -> dict:
    """
    Predict the news category for a given article text.

    Returns a dict with keys:
        primary  (str)  — winning category label
        scores   (dict) — percentage confidence per category
    """
    try:
        pipe = _load_pipeline()
        cleaned = _clean(text)

        # Get decision function scores (distance from hyperplane) for LinearSVC
        # For other models we fall back to predict_proba if available
        label_idx = None
        scores_pct = {}

        if hasattr(pipe["clf"], "decision_function"):
            raw_scores = pipe.decision_function([cleaned])[0]
            # Convert to positive values then normalise to percentages
            shifted = raw_scores - raw_scores.min()
            total   = shifted.sum() if shifted.sum() > 0 else 1.0
            probs   = (shifted / total * 100).tolist()
            label_idx = int(np.argmax(raw_scores))
        elif hasattr(pipe["clf"], "predict_proba"):
            probs_raw = pipe.predict_proba([cleaned])[0]
            probs     = (np.array(probs_raw) * 100).tolist()
            label_idx = int(np.argmax(probs_raw))
        else:
            label_idx = int(pipe.predict([cleaned])[0])
            probs = [0.0, 0.0, 0.0]
            probs[label_idx] = 100.0

        # Build named score dict — round to 1 decimal
        n_classes = len(LABEL_MAP)
        for i in range(n_classes):
            key = ["tech", "research", "policy"][i]
            scores_pct[key] = round(probs[i] if i < len(probs) else 0.0, 1)

        # Normalise so scores always sum to 100
        total_pct = sum(scores_pct.values())
        if total_pct > 0:
            scores_pct = {k: round(v / total_pct * 100, 1) for k, v in scores_pct.items()}

        return {
            "primary": LABEL_MAP[label_idx],
            "scores":  scores_pct,
        }

    except Exception as e:
        # Graceful fallback — return neutral prediction instead of crashing
        return {
            "primary": "Research & Science",
            "scores":  {"tech": 33.3, "research": 33.4, "policy": 33.3},
            "error":   str(e),
        }
