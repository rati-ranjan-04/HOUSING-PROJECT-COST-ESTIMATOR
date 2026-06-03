from __future__ import annotations

import os
import base64
import mimetypes
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")


def _file_to_data_url(upload_file) -> Optional[str]:
    try:
        upload_file.file.seek(0)
        raw = upload_file.file.read()
        upload_file.file.seek(0)
        mime = upload_file.content_type or mimetypes.guess_type(upload_file.filename)[0] or "image/jpeg"
        encoded = base64.b64encode(raw).decode("utf-8")
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return None


def generate_ai_report(
    prediction_result: Dict[str, Any],
    uploaded_images: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Uses Groq Vision/Llama to generate a rich valuation + Vastu report."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "enabled": False,
            "summary": "Groq API key not configured. Add GROQ_API_KEY in backend/.env.",
            "sections": {},
        }

    client = Groq(api_key=api_key)

    base = prediction_result.get("base_prediction_usd")
    adjusted = prediction_result.get("image_adjusted_prediction_usd")
    making_cost = prediction_result.get("making_cost_usd", 0)
    asking = prediction_result.get("seller_asking_price_usd", 0)
    visual = prediction_result.get("visual_analysis", {})
    features = prediction_result.get("input_features", {})
    deal = prediction_result.get("deal_analysis", {})
    prop = prediction_result.get("property_details", {})

    has_images = bool(uploaded_images)
    image_note = (
        f"The user has uploaded {visual.get('image_count', 0)} house images (interior/exterior). "
        "Carefully inspect each image for: construction quality, materials used, interior finish, "
        "ceiling height, natural light, ventilation, space layout, furniture placement, "
        "cleanliness/maintenance condition, visible damage, Vastu directional compliance "
        "(entrance direction, kitchen placement, master bedroom, pooja room, toilet placement, "
        "open space/courtyard)."
        if has_images
        else "No images were uploaded. Base your observations on tabular data only."
    )

    prompt = f"""
You are HomeVision AI — an expert real-estate valuation, construction cost estimation,
and Vastu Shastra advisor. You help buyers decide whether a house is worth buying.

{image_note}

=== DATA ===
ML Base Prediction: ${base:,.0f}
Image-Adjusted AI Value: ${adjusted:,.0f}
Seller Asking Price: ${asking:,.0f} {'(not provided)' if asking == 0 else ''}
Estimated Construction/Making Cost: ${making_cost:,.0f} {'(not provided)' if making_cost == 0 else ''}
Deal Verdict: {deal.get('deal_verdict', 'N/A')}
Asking vs AI Value Difference: {deal.get('asking_vs_ai_diff_pct', 'N/A')}%
Property Size: {prop.get('size_sqft', 0)} sqft
Construction Cost/sqft: ${prop.get('construction_cost_per_sqft', 0)}/sqft

Property tabular features:
- Median Income in area: {features.get('MedInc')}
- House Age: {features.get('HouseAge')} years
- Avg Rooms: {features.get('AveRooms')}
- Avg Bedrooms: {features.get('AveBedrms')}
- Area Population: {features.get('Population')}
- Avg Occupancy: {features.get('AveOccup')}
- Location (Lat/Lon): {features.get('Latitude')}, {features.get('Longitude')}
Visual condition: {visual.get('condition_label')} (score: {visual.get('average_visual_score')})

=== YOUR TASK ===
Respond ONLY as a structured JSON object with these exact keys (no markdown, no extra text):

{{
  "valuation_summary": "2-3 sentence overview of the property value and whether it is a good buy.",
  "making_cost_analysis": "Analysis of the construction/making cost — is it reasonable for the area and age? What does the land value imply?",
  "image_observations": {{
    "interior": "Detailed observations about interior condition, finishes, light, space, visible issues.",
    "exterior": "Observations about exterior structure, facade, garden, parking, maintenance.",
    "construction_quality": "Assessment of visible construction quality, materials, ceiling, walls."
  }},
  "vastu_analysis": {{
    "score": <integer 1-10>,
    "overall": "Overall Vastu compliance summary.",
    "positive_aspects": ["list", "of", "vastu", "positives"],
    "concerns": ["list", "of", "vastu", "concerns"],
    "recommendations": ["list", "of", "vastu", "remedies"]
  }},
  "deal_assessment": "Clear buy/negotiate/avoid recommendation with reasoning based on asking price vs AI value vs making cost.",
  "recommended_offer_usd": <number — the price you would recommend the buyer offer, or 0 if not enough data>,
  "risk_flags": ["list", "of", "risks"],
  "negotiation_tips": ["list", "of", "negotiation", "tactics"],
  "improvement_suggestions": ["list", "of", "improvements", "to", "increase", "value"]
}}

Be specific, practical, and direct. Do not hedge excessively. Think like an experienced real-estate advisor.
"""

    content: list = [{"type": "text", "text": prompt}]

    for img in (uploaded_images or [])[:4]:
        data_url = _file_to_data_url(img)
        if data_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": data_url},
            })

    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a seasoned Indian real-estate advisor specializing in property valuation, "
                        "construction cost analysis, and Vastu Shastra. Always respond with valid JSON only — "
                        "no markdown fences, no preamble."
                    ),
                },
                {"role": "user", "content": content},
            ],
            temperature=0.30,
            max_tokens=1800,
        )

        raw_text = completion.choices[0].message.content or "{}"

        # Strip possible markdown code fences
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```", 2)[1]
            if clean.startswith("json"):
                clean = clean[4:]
            clean = clean.rsplit("```", 1)[0].strip()

        import json as _json
        sections = _json.loads(clean)

        return {
            "enabled": True,
            "model": DEFAULT_MODEL,
            "sections": sections,
        }

    except Exception as exc:
        return {
            "enabled": False,
            "summary": f"Groq report generation failed: {exc}",
            "sections": {},
        }
