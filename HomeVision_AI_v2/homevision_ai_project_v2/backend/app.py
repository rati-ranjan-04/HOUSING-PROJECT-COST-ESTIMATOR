from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import json
import joblib
import numpy as np

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from image_analyzer import analyze_house_images
from groq_advisor import generate_ai_report


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model_artifacts"
MODEL_PATH = MODEL_DIR / "linear_regression_house_price.joblib"
FEATURE_PATH = MODEL_DIR / "feature_names.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

app = FastAPI(
    title="HomeVision AI API",
    description="Hybrid tabular + multi-image house price prediction API with Vastu analysis.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_model():
    if not MODEL_PATH.exists():
        raise RuntimeError("Model not found. Run: python train_model.py")
    return joblib.load(MODEL_PATH), joblib.load(FEATURE_PATH)


@app.get("/")
def health_check():
    return {
        "app": "HomeVision AI",
        "status": "running",
        "message": "Use /docs for Swagger UI or /predict for prediction.",
    }


@app.get("/metrics")
def get_metrics():
    if not METRICS_PATH.exists():
        return {"error": "metrics.json not found. Run python train_model.py first."}
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


@app.post("/predict")
async def predict_house_price(
    MedInc: float = Form(...),
    HouseAge: float = Form(...),
    AveRooms: float = Form(...),
    AveBedrms: float = Form(...),
    Population: float = Form(...),
    AveOccup: float = Form(...),
    Latitude: float = Form(...),
    Longitude: float = Form(...),
    SellerAskingPrice: float = Form(default=0.0),
    ConstructionCostPerSqft: float = Form(default=0.0),
    PropertySizeSqft: float = Form(default=0.0),
    images: Optional[List[UploadFile]] = File(default=None),
):
    model, feature_names = load_model()

    user_values = {
        "MedInc": MedInc,
        "HouseAge": HouseAge,
        "AveRooms": AveRooms,
        "AveBedrms": AveBedrms,
        "Population": Population,
        "AveOccup": AveOccup,
        "Latitude": Latitude,
        "Longitude": Longitude,
    }

    X = np.array([[user_values[name] for name in feature_names]], dtype=float)

    base_prediction_100k = float(model.predict(X)[0])
    base_usd = max(base_prediction_100k, 0) * 100_000

    image_files = images or []
    visual_report = analyze_house_images(image_files)
    adjusted_usd = base_usd * visual_report["price_adjustment_factor"]

    # Estimated construction / making cost
    making_cost_usd = 0.0
    if ConstructionCostPerSqft > 0 and PropertySizeSqft > 0:
        making_cost_usd = ConstructionCostPerSqft * PropertySizeSqft

    result = {
        "ai_name": "HomeVision AI powered by Groq",
        "base_prediction_usd": round(base_usd, 2),
        "image_adjusted_prediction_usd": round(adjusted_usd, 2),
        "making_cost_usd": round(making_cost_usd, 2),
        "seller_asking_price_usd": round(SellerAskingPrice, 2),
        "price_range_usd": {
            "low": round(adjusted_usd * 0.90, 2),
            "high": round(adjusted_usd * 1.10, 2),
        },
        "deal_analysis": _analyze_deal(
            adjusted_usd, SellerAskingPrice, making_cost_usd
        ),
        "input_features": user_values,
        "property_details": {
            "size_sqft": PropertySizeSqft,
            "construction_cost_per_sqft": ConstructionCostPerSqft,
        },
        "visual_analysis": visual_report,
        "note": (
            "This is an AI estimate, not a certified appraisal. "
            "For real deployment, train the image branch with actual house photos and sale prices."
        ),
    }

    result["groq_ai_report"] = generate_ai_report(result, image_files)
    return result


def _analyze_deal(
    ai_value: float, asking: float, making_cost: float
) -> dict:
    """Compare asking price vs AI value and making cost."""
    analysis = {
        "ai_estimated_value": round(ai_value, 2),
        "seller_asking": round(asking, 2),
        "making_cost": round(making_cost, 2),
    }

    if asking > 0 and ai_value > 0:
        diff_pct = ((asking - ai_value) / ai_value) * 100
        analysis["asking_vs_ai_diff_pct"] = round(diff_pct, 2)
        if diff_pct <= -10:
            analysis["deal_verdict"] = "Excellent Buy"
            analysis["deal_color"] = "green"
        elif diff_pct <= 0:
            analysis["deal_verdict"] = "Fair Deal"
            analysis["deal_color"] = "blue"
        elif diff_pct <= 15:
            analysis["deal_verdict"] = "Slightly Overpriced"
            analysis["deal_color"] = "orange"
        else:
            analysis["deal_verdict"] = "Overpriced — Negotiate"
            analysis["deal_color"] = "red"
    else:
        analysis["deal_verdict"] = "N/A"
        analysis["deal_color"] = "grey"

    if making_cost > 0 and ai_value > 0:
        land_value = ai_value - making_cost
        analysis["implied_land_value"] = round(max(land_value, 0), 2)
        analysis["making_cost_ratio_pct"] = round((making_cost / ai_value) * 100, 2)

    return analysis
