from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from PIL import Image, ImageFilter
import numpy as np


@dataclass
class ImageScore:
    filename: str
    width: int
    height: int
    brightness: float
    contrast: float
    sharpness: float
    greenery_ratio: float
    warm_light_ratio: float
    visual_quality_score: float
    predicted_view_type: str


def _safe_open_image(file_obj) -> Image.Image:
    image = Image.open(file_obj)
    return image.convert("RGB")


def _estimate_view_type(arr: np.ndarray) -> str:
    """Simple heuristic classifier for demo purposes.

    Exterior images usually have more green/blue pixels.
    Interior images often have warmer light and lower greenery.
    """
    r = arr[:, :, 0].astype(float)
    g = arr[:, :, 1].astype(float)
    b = arr[:, :, 2].astype(float)

    greenery = ((g > r * 1.08) & (g > b * 1.08) & (g > 70)).mean()
    sky_like = ((b > r * 1.1) & (b > g * 1.03) & (b > 100)).mean()
    warm_light = ((r > g * 1.03) & (g > b * 1.02) & (r > 120)).mean()

    if greenery + sky_like > 0.16:
        return "Exterior"
    if warm_light > 0.22:
        return "Interior"
    return "Mixed/Unknown"


def analyze_single_image(file_obj, filename: str = "uploaded_image") -> ImageScore:
    image = _safe_open_image(file_obj)
    image.thumbnail((900, 900))

    arr = np.asarray(image).astype(np.float32)
    gray = np.asarray(image.convert("L")).astype(np.float32)

    brightness = float(gray.mean() / 255.0)
    contrast = float(gray.std() / 128.0)

    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    sharpness = float(np.asarray(edges).std() / 80.0)

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    greenery_ratio = float(((g > r * 1.08) & (g > b * 1.08) & (g > 70)).mean())
    warm_light_ratio = float(((r > g * 1.03) & (g > b * 1.02) & (r > 120)).mean())

    # Portfolio-friendly visual condition score.
    # Clipped so that poor/overexposed photos cannot dominate model output.
    visual_quality_score = (
        0.35 * min(brightness / 0.65, 1.0)
        + 0.25 * min(contrast / 0.80, 1.0)
        + 0.25 * min(sharpness / 0.75, 1.0)
        + 0.10 * min(warm_light_ratio / 0.30, 1.0)
        + 0.05 * min(greenery_ratio / 0.20, 1.0)
    )
    visual_quality_score = float(np.clip(visual_quality_score, 0.15, 1.0))

    return ImageScore(
        filename=filename,
        width=image.width,
        height=image.height,
        brightness=round(brightness, 4),
        contrast=round(contrast, 4),
        sharpness=round(sharpness, 4),
        greenery_ratio=round(greenery_ratio, 4),
        warm_light_ratio=round(warm_light_ratio, 4),
        visual_quality_score=round(visual_quality_score, 4),
        predicted_view_type=_estimate_view_type(arr),
    )


def analyze_house_images(files: List[Any]) -> Dict[str, Any]:
    scores: List[ImageScore] = []

    for uploaded in files:
        try:
            # Reset file pointer before reading so this works whether or not
            # the stream was previously consumed (e.g. in a multi-step pipeline).
            uploaded.file.seek(0)
            scores.append(analyze_single_image(uploaded.file, uploaded.filename))
            # Reset again so downstream consumers (e.g. Groq vision) can re-read.
            uploaded.file.seek(0)
        except Exception as exc:
            # Keep API robust even if one image fails.
            scores.append(
                ImageScore(
                    filename=getattr(uploaded, "filename", "unknown"),
                    width=0,
                    height=0,
                    brightness=0.0,
                    contrast=0.0,
                    sharpness=0.0,
                    greenery_ratio=0.0,
                    warm_light_ratio=0.0,
                    visual_quality_score=0.15,
                    predicted_view_type=f"Invalid image: {exc}",
                )
            )

    if not scores:
        return {
            "image_count": 0,
            "average_visual_score": 0.50,
            "condition_label": "No images supplied",
            "price_adjustment_factor": 1.00,
            "images": [],
        }

    avg_score = float(np.mean([s.visual_quality_score for s in scores]))

    if avg_score >= 0.78:
        condition = "Premium / well-maintained"
        factor = 1.10
    elif avg_score >= 0.62:
        condition = "Good"
        factor = 1.04
    elif avg_score >= 0.45:
        condition = "Average"
        factor = 1.00
    else:
        condition = "Needs improvement"
        factor = 0.92

    return {
        "image_count": len(scores),
        "average_visual_score": round(avg_score, 4),
        "condition_label": condition,
        "price_adjustment_factor": factor,
        "images": [asdict(s) for s in scores],
    }
