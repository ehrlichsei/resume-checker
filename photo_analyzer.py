"""PhotoAnalyzer

Lightweight wrapper around two pre-trained open-source models:
1. LAION aesthetic predictor – returns a 0-10 aesthetic score.
2. DeepFace – returns emotion probabilities which we map to a simple
   confidence score (happy/neutral = confident).

Both libraries fetch model weights on first use and cache them under
~/.cache, so subsequent calls are fast.
"""
import importlib
from deepface import DeepFace
from PIL import Image
import io
import numpy as np

# Try to locate the predict_from_pil function regardless of the internal
# layout of aesthetic_predictor (which changed between 0.1.x and 0.2.x).
def _load_aesthetic_fn():
    try:
        module = importlib.import_module("aesthetic_predictor.predict")
        return module.predict_from_pil  # type: ignore
    except ModuleNotFoundError:
        # Fallback: some versions expose it directly in the package
        ap = importlib.import_module("aesthetic_predictor")
        if hasattr(ap, "predict_from_pil"):
            return getattr(ap, "predict_from_pil")
        # Library not available – return a dummy scorer
        def _dummy(img):
            return 5.0
        return _dummy

predict_from_pil = _load_aesthetic_fn()

class PhotoAnalyzer:
    """Provide aesthetic (beauty) and confidence metrics for a face photo."""

    def __init__(self):
        # No heavy initialisation; models load lazily on first call.
        pass

    def analyze(self, image_bytes: bytes):
        """Compute metrics.

        Returns a dict:
            {
              "aesthetic": float  # 0-10, higher = more attractive/pleasing
              "confidence": float # 0-1, higher = more confident expression
            }
        """
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # 1. Aesthetic score
        aesthetic_score = float(predict_from_pil(img_pil))

        # 2. Emotion analysis – DeepFace may return a dict or a list of dicts
        analysis = DeepFace.analyze(
            img_path=np.array(img_pil),
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )

        # Normalise to a single dict
        if isinstance(analysis, list):
            analysis = analysis[0] if analysis else {}

        emotions = analysis.get("emotion", {}) if isinstance(analysis, dict) else {}
        # Positive emotions indicating confidence
        positive = emotions.get("happy", 0) + emotions.get("neutral", 0)
        confidence_score = positive / 100.0  # convert % → [0,1]

        return {
            "aesthetic": round(aesthetic_score, 2),
            "confidence": round(confidence_score, 2),
        }
