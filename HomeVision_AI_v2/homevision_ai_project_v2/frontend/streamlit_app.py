from __future__ import annotations

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="HomeVision AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Luxury dark theme ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --gold:    #c9a84c;
  --gold2:   #e8c97a;
  --dark:    #0d0e12;
  --surface: #13151c;
  --card:    #181b24;
  --border:  rgba(201,168,76,.18);
  --text:    #e8e6e0;
  --muted:   #7c7d85;
  --green:   #34c77b;
  --red:     #e05c5c;
  --orange:  #e09a3a;
  --blue:    #5c9de0;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background: var(--dark) !important;
  color: var(--text) !important;
}

/* Remove streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 3rem !important; max-width: 1400px !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }

/* ── HERO ── */
.hero {
  background: linear-gradient(135deg, #0d0e12 0%, #181422 50%, #0f1318 100%);
  border-bottom: 1px solid var(--border);
  padding: 3.5rem 3rem 2.5rem;
  margin: 0 -2rem 2.5rem;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 60% 80% at 80% 50%, rgba(201,168,76,.07) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'DM Sans', sans-serif;
  font-weight: 300;
  font-size: .72rem;
  letter-spacing: .25em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: .75rem;
}
.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.8rem, 5vw, 4.5rem);
  font-weight: 300;
  line-height: 1.08;
  color: #f5f0e8;
  margin: 0 0 .6rem;
}
.hero-title em { color: var(--gold); font-style: italic; font-weight: 300; }
.hero-sub {
  font-size: .92rem;
  color: var(--muted);
  font-weight: 300;
  max-width: 520px;
  line-height: 1.65;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  background: rgba(201,168,76,.1);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: .3rem .9rem;
  font-size: .72rem;
  font-weight: 500;
  letter-spacing: .08em;
  color: var(--gold2);
  margin-top: 1.2rem;
}

/* ── SECTION LABELS ── */
.section-label {
  font-family: 'DM Sans', sans-serif;
  font-size: .68rem;
  font-weight: 500;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: .6rem;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── CARDS ── */
.glass-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.6rem;
  margin-bottom: 1.2rem;
  position: relative;
}
.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(201,168,76,.04) 0%, transparent 60%);
  pointer-events: none;
}

/* ── METRIC TILES ── */
.metric-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.6rem; }
.metric-tile {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.4rem 1.2rem;
  position: relative;
  overflow: hidden;
}
.metric-tile::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--gold), transparent);
}
.mt-label { font-size: .68rem; font-weight: 500; letter-spacing: .15em; text-transform: uppercase; color: var(--muted); margin-bottom: .5rem; }
.mt-value { font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 400; color: var(--text); line-height: 1; }
.mt-sub   { font-size: .75rem; color: var(--muted); margin-top: .4rem; }

/* ── VERDICT BANNER ── */
.verdict-banner {
  border-radius: 14px;
  padding: 1.4rem 1.8rem;
  margin-bottom: 1.6rem;
  border-left: 4px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}
.verdict-green  { background: rgba(52,199,123,.08); border-color: var(--green);  }
.verdict-blue   { background: rgba(92,157,224,.08); border-color: var(--blue);   }
.verdict-orange { background: rgba(224,154,58,.08); border-color: var(--orange); }
.verdict-red    { background: rgba(224,92,92,.08);  border-color: var(--red);    }
.verdict-grey   { background: rgba(124,125,133,.08);border-color: var(--muted);  }
.verdict-title { font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; font-weight: 600; }
.verdict-detail { font-size: .85rem; color: var(--muted); }

/* ── VASTU SCORE ── */
.vastu-ring-wrap { text-align: center; }
.vastu-score-big { font-family: 'Cormorant Garamond', serif; font-size: 3.5rem; font-weight: 300; }
.vastu-label { font-size: .7rem; letter-spacing: .15em; text-transform: uppercase; color: var(--muted); }
.vastu-tag {
  display: inline-block;
  border-radius: 6px;
  padding: .25rem .7rem;
  font-size: .75rem;
  font-weight: 500;
  margin: .25rem .2rem;
}
.tag-positive { background: rgba(52,199,123,.12); color: var(--green); border: 1px solid rgba(52,199,123,.25); }
.tag-concern  { background: rgba(224,92,92,.10);  color: var(--red);   border: 1px solid rgba(224,92,92,.25);  }

/* ── LIST ITEMS ── */
.ai-list { list-style: none; padding: 0; margin: 0; }
.ai-list li {
  padding: .55rem 0;
  border-bottom: 1px solid rgba(255,255,255,.04);
  font-size: .875rem;
  color: #c8c6be;
  display: flex;
  gap: .6rem;
  align-items: flex-start;
}
.ai-list li:last-child { border-bottom: none; }
.ai-list li::before { content: '›'; color: var(--gold); flex-shrink: 0; font-size: 1rem; margin-top: -.02rem; }

/* ── STREAMLIT WIDGET OVERRIDES ── */
div[data-testid="stSlider"] > label,
div[data-testid="stNumberInput"] > label,
div[data-testid="stSelectbox"] > label,
div[data-testid="stFileUploader"] > label { color: var(--muted) !important; font-size: .8rem !important; }

div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: var(--gold) !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] [class*="Track"] {
  background: rgba(201,168,76,.25) !important;
}
div[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, #c9a84c, #a8863a) !important;
  border: none !important;
  color: #0d0e12 !important;
  font-weight: 600 !important;
  font-size: .9rem !important;
  letter-spacing: .05em !important;
  border-radius: 10px !important;
  padding: .75rem 2rem !important;
  transition: all .2s !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(201,168,76,.3) !important;
}
div[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--border) !important;
  border-radius: 12px !important;
  background: rgba(255,255,255,.015) !important;
  padding: 1rem !important;
}
.stNumberInput input, .stTextInput input {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}
.stExpander { border: 1px solid var(--border) !important; border-radius: 12px !important; background: var(--card) !important; }
.stExpander summary { color: var(--muted) !important; font-size: .85rem !important; }
div[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }
div[data-testid="stAlert"] { border-radius: 10px !important; }

/* image grid */
.img-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .6rem; margin-top: .8rem; }
.img-grid img { width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 4/3; border: 1px solid var(--border); }

/* divider */
.fancy-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 2rem 0; }

/* tab-like pills */
.pill-nav { display: flex; gap: .5rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.pill { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: .35rem 1rem; font-size: .8rem; color: var(--muted); }
.pill-active { background: rgba(201,168,76,.12); border-color: var(--gold); color: var(--gold2); }
</style>
""", unsafe_allow_html=True)


# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-Powered Real Estate Intelligence</div>
  <h1 class="hero-title">Home<em>Vision</em> AI</h1>
  <p class="hero-sub">
    Upload interior &amp; exterior photos, enter property details and the seller's asking price —
    get a complete valuation, construction cost breakdown, Vastu analysis, and an expert buy recommendation.
  </p>
  <div class="hero-badge">⚡ Powered by Groq &nbsp;·&nbsp; 🏛️ Vastu Analysis &nbsp;·&nbsp; 📸 Vision AI &nbsp;·&nbsp; 💰 Deal Intelligence</div>
</div>
""", unsafe_allow_html=True)


# ── INPUT COLUMNS ─────────────────────────────────────────────────────────────
col_left, col_mid, col_right = st.columns([1.1, 1.1, 1.2], gap="large")

with col_left:
    st.markdown('<div class="section-label">Property Details</div>', unsafe_allow_html=True)
    with st.container():
        MedInc    = st.slider("Median Area Income (×$10k)", 0.5, 15.0, 5.0, 0.1,
                               help="Median household income of the neighbourhood in units of $10,000.")
        HouseAge  = st.slider("House Age (years)", 1.0, 60.0, 20.0, 1.0)
        AveRooms  = st.slider("Average Rooms per Unit", 1.0, 12.0, 5.2, 0.1)
        AveBedrms = st.slider("Average Bedrooms per Unit", 0.5, 5.0, 1.1, 0.1)
        Population = st.number_input("Area Population", min_value=1.0, value=1200.0, step=50.0)
        AveOccup  = st.slider("Average Occupancy", 0.5, 10.0, 3.0, 0.1)

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Location</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    Latitude  = c1.number_input("Latitude",  value=34.05, step=0.01, format="%.4f")
    Longitude = c2.number_input("Longitude", value=-118.25, step=0.01, format="%.4f")

with col_mid:
    st.markdown('<div class="section-label">Pricing & Construction</div>', unsafe_allow_html=True)
    SellerAskingPrice = st.number_input(
        "Seller's Asking Price (USD)",
        min_value=0.0, value=0.0, step=5000.0, format="%.0f",
        help="Enter the price the seller is asking. Leave 0 if unknown."
    )
    PropertySizeSqft = st.number_input(
        "Property Size (sq ft)",
        min_value=0.0, value=0.0, step=100.0, format="%.0f",
        help="Total built-up area in square feet."
    )
    ConstructionCostPerSqft = st.number_input(
        "Construction Cost per sq ft (USD)",
        min_value=0.0, value=0.0, step=10.0, format="%.0f",
        help="Local construction cost per sq ft. Used to estimate making/build cost."
    )

    if PropertySizeSqft > 0 and ConstructionCostPerSqft > 0:
        est_make = PropertySizeSqft * ConstructionCostPerSqft
        st.markdown(f"""
        <div class="glass-card" style="padding:1rem 1.2rem; margin-top:.5rem;">
          <div class="mt-label">Estimated Construction Cost</div>
          <div class="mt-value" style="font-size:1.6rem; color:var(--gold2);">${est_make:,.0f}</div>
          <div class="mt-sub">{PropertySizeSqft:,.0f} sqft × ${ConstructionCostPerSqft:,.0f}/sqft</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Vastu Orientation Hint</div>',
                unsafe_allow_html=True)
    facing_dir = st.selectbox(
        "Main Door Facing Direction",
        ["Unknown / Let AI decide", "North", "North-East", "East", "South-East",
         "South", "South-West", "West", "North-West"],
        help="Vastu-preferred directions: North, North-East, East are auspicious."
    )

with col_right:
    st.markdown('<div class="section-label">House Photos</div>', unsafe_allow_html=True)
    uploaded_images = st.file_uploader(
        "Upload interior & exterior images (up to 8)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Photos help AI detect construction quality, room layout, lighting, Vastu cues, and condition."
    )

    if uploaded_images:
        st.markdown(f'<div class="mt-sub" style="margin-bottom:.6rem">{len(uploaded_images)} image(s) uploaded</div>',
                    unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, img in enumerate(uploaded_images[:9]):
            with cols[idx % 3]:
                st.image(img, use_container_width=True)
    else:
        st.markdown("""
        <div style="border:1.5px dashed rgba(201,168,76,.2); border-radius:12px; padding:2.5rem 1rem;
                    text-align:center; color:var(--muted); font-size:.82rem; margin-top:.5rem;">
          📸<br><br>
          No images uploaded.<br>
          <span style="color:rgba(201,168,76,.6);">Add photos for Vastu &amp; condition analysis.</span>
        </div>""", unsafe_allow_html=True)

# ── ANALYSE BUTTON ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

btn_col, _ = st.columns([1, 2])
with btn_col:
    analyse = st.button("🔍  Analyse & Value Property", type="primary", use_container_width=True)

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)


# ── RESULTS ───────────────────────────────────────────────────────────────────
if analyse:
    form_data = {
        "MedInc": MedInc,
        "HouseAge": HouseAge,
        "AveRooms": AveRooms,
        "AveBedrms": AveBedrms,
        "Population": Population,
        "AveOccup": AveOccup,
        "Latitude": Latitude,
        "Longitude": Longitude,
        "SellerAskingPrice": SellerAskingPrice,
        "ConstructionCostPerSqft": ConstructionCostPerSqft,
        "PropertySizeSqft": PropertySizeSqft,
    }

    files = []
    for img in (uploaded_images or []):
        files.append(("images", (img.name, img.getvalue(), img.type)))

    try:
        with st.spinner("Analysing property with AI..."):
            response = requests.post(
                f"{API_URL}/predict", data=form_data,
                files=files if files else [("images", ("", b"", "image/jpeg"))],
                timeout=90,
            )
            response.raise_for_status()
            result = response.json()

        # ── KEY METRICS ROW ───────────────────────────────────────────────────
        ai_val  = result["image_adjusted_prediction_usd"]
        base_v  = result["base_prediction_usd"]
        make_c  = result["making_cost_usd"]
        asking  = result["seller_asking_price_usd"]
        vis     = result["visual_analysis"]
        deal    = result["deal_analysis"]
        groq    = result.get("groq_ai_report", {})
        sec     = groq.get("sections", {})

        st.markdown('<div class="section-label">Valuation Overview</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-tile">
              <div class="mt-label">AI Estimated Value</div>
              <div class="mt-value">${ai_val:,.0f}</div>
              <div class="mt-sub">Image-adjusted prediction</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            mc_str = f"${make_c:,.0f}" if make_c > 0 else "—"
            st.markdown(f"""
            <div class="metric-tile">
              <div class="mt-label">Making / Build Cost</div>
              <div class="mt-value">{mc_str}</div>
              <div class="mt-sub">Estimated construction cost</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            ask_str = f"${asking:,.0f}" if asking > 0 else "—"
            st.markdown(f"""
            <div class="metric-tile">
              <div class="mt-label">Seller Asking Price</div>
              <div class="mt-value">{ask_str}</div>
              <div class="mt-sub">As entered by user</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            rec = sec.get("recommended_offer_usd", 0)
            rec_str = f"${rec:,.0f}" if rec and rec > 0 else "—"
            st.markdown(f"""
            <div class="metric-tile">
              <div class="mt-label">Recommended Offer</div>
              <div class="mt-value" style="color:var(--gold2);">{rec_str}</div>
              <div class="mt-sub">AI negotiation target</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

        # ── DEAL VERDICT BANNER ───────────────────────────────────────────────
        verdict = deal.get("deal_verdict", "N/A")
        color   = deal.get("deal_color", "grey")
        diff_pct = deal.get("asking_vs_ai_diff_pct")
        diff_str = f"{diff_pct:+.1f}% vs AI value" if diff_pct is not None else ""

        color_map = {
            "green": ("verdict-green", "✅", "#34c77b"),
            "blue":  ("verdict-blue",  "✔️", "#5c9de0"),
            "orange":("verdict-orange","⚠️", "#e09a3a"),
            "red":   ("verdict-red",   "🚨", "#e05c5c"),
            "grey":  ("verdict-grey",  "📋", "#7c7d85"),
        }
        cls, icon, clr = color_map.get(color, color_map["grey"])

        st.markdown(f"""
        <div class="verdict-banner {cls}">
          <div>
            <div class="verdict-title" style="color:{clr};">{icon} {verdict}</div>
            <div class="verdict-detail">{diff_str}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:.75rem; color:var(--muted);">Visual Condition</div>
            <div style="font-size:1.05rem; font-weight:500; color:var(--text);">{vis['condition_label']}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── PRICE GAUGE ───────────────────────────────────────────────────────
        low  = result["price_range_usd"]["low"]
        high = result["price_range_usd"]["high"]

        gauge_data = [ai_val]
        gauge_labels = ["AI Value"]
        if asking > 0:
            gauge_data.append(asking)
            gauge_labels.append("Asking")

        fig_gauge = go.Figure()
        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=ai_val,
            number={"prefix": "$", "valueformat": ",.0f", "font": {"color": "#c9a84c", "size": 28}},
            title={"text": "Estimated Market Value", "font": {"color": "#7c7d85", "size": 13}},
            gauge={
                "axis": {"range": [low * 0.8, high * 1.2], "tickformat": "$,.0f",
                         "tickfont": {"color": "#7c7d85", "size": 10}},
                "bar": {"color": "#c9a84c", "thickness": 0.28},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(201,168,76,.15)",
                "steps": [
                    {"range": [low * 0.8, low],  "color": "rgba(224,92,92,.15)"},
                    {"range": [low, high],         "color": "rgba(52,199,123,.10)"},
                    {"range": [high, high * 1.2],  "color": "rgba(92,157,224,.12)"},
                ],
                "threshold": {
                    "line": {"color": "#e05c5c", "width": 3},
                    "thickness": 0.82,
                    "value": asking if asking > 0 else ai_val,
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e8e6e0",
            height=260,
            margin=dict(t=30, b=10, l=30, r=30),
        )
        gcol1, gcol2 = st.columns([1.4, 1])
        with gcol1:
            st.plotly_chart(fig_gauge, use_container_width=True)
        with gcol2:
            land_val = deal.get("implied_land_value", 0)
            mc_ratio = deal.get("making_cost_ratio_pct", 0)
            st.markdown(f"""
            <div class="glass-card" style="margin-top:.3rem">
              <div class="mt-label" style="margin-bottom:1rem">Price Breakdown</div>
              <div style="display:flex; flex-direction:column; gap:.7rem;">
                <div><div class="mt-sub">AI Fair Value</div><div style="font-size:1.15rem; color:var(--gold2);">${ai_val:,.0f}</div></div>
                <div><div class="mt-sub">Base ML Prediction</div><div style="font-size:.95rem;">${base_v:,.0f}</div></div>
                {'<div><div class="mt-sub">Build / Making Cost</div><div style="font-size:.95rem;">$' + f'{make_c:,.0f}</div></div>' if make_c > 0 else ''}
                {'<div><div class="mt-sub">Implied Land Value</div><div style="font-size:.95rem; color:var(--green);">$' + f'{land_val:,.0f}</div></div>' if land_val > 0 else ''}
                {'<div><div class="mt-sub">Build Cost / AI Value</div><div style="font-size:.95rem;">' + f'{mc_ratio:.1f}%</div></div>' if mc_ratio > 0 else ''}
                <div><div class="mt-sub">Price Range (±10%)</div><div style="font-size:.85rem; color:var(--muted);">${low:,.0f} – ${high:,.0f}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

        # ── GROQ AI SECTIONS ──────────────────────────────────────────────────
        if groq.get("enabled") and sec:

            # Row 1: Valuation summary + Deal assessment
            r1a, r1b = st.columns(2, gap="large")

            with r1a:
                st.markdown('<div class="section-label">Valuation Summary</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card">
                  <p style="font-size:.88rem; color:#c8c6be; line-height:1.7; margin:0;">{sec.get('valuation_summary','—')}</p>
                </div>""", unsafe_allow_html=True)

                if sec.get("making_cost_analysis"):
                    st.markdown('<div class="section-label">Construction Cost Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="glass-card">
                      <p style="font-size:.88rem; color:#c8c6be; line-height:1.7; margin:0;">{sec['making_cost_analysis']}</p>
                    </div>""", unsafe_allow_html=True)

            with r1b:
                st.markdown('<div class="section-label">Deal Assessment</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card">
                  <p style="font-size:.88rem; color:#c8c6be; line-height:1.7; margin:0;">{sec.get('deal_assessment','—')}</p>
                </div>""", unsafe_allow_html=True)

                if sec.get("negotiation_tips"):
                    st.markdown('<div class="section-label">Negotiation Tips</div>', unsafe_allow_html=True)
                    tips_html = "".join(f"<li>{t}</li>" for t in sec["negotiation_tips"])
                    st.markdown(f'<div class="glass-card"><ul class="ai-list">{tips_html}</ul></div>',
                                unsafe_allow_html=True)

            # Row 2: Image observations
            img_obs = sec.get("image_observations", {})
            if img_obs:
                st.markdown('<div class="section-label">Image Analysis</div>', unsafe_allow_html=True)
                oa, ob, oc = st.columns(3, gap="medium")
                for col, (key, label, icon) in zip(
                    [oa, ob, oc],
                    [("interior", "Interior", "🛋️"), ("exterior", "Exterior", "🏠"), ("construction_quality", "Construction Quality", "🧱")]
                ):
                    with col:
                        st.markdown(f"""
                        <div class="glass-card" style="min-height:140px">
                          <div class="mt-label">{icon} {label}</div>
                          <p style="font-size:.83rem; color:#c8c6be; line-height:1.65; margin:.6rem 0 0;">{img_obs.get(key,'—')}</p>
                        </div>""", unsafe_allow_html=True)

            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

            # Row 3: Vastu
            vastu = sec.get("vastu_analysis", {})
            if vastu:
                st.markdown('<div class="section-label">Vastu Shastra Analysis</div>', unsafe_allow_html=True)
                v1, v2, v3 = st.columns([1, 1.6, 1.6], gap="large")

                with v1:
                    score = vastu.get("score", 0)
                    score_color = "#34c77b" if score >= 7 else "#e09a3a" if score >= 5 else "#e05c5c"
                    st.markdown(f"""
                    <div class="glass-card" style="text-align:center; padding:2rem 1rem">
                      <div class="vastu-score-big" style="color:{score_color};">{score}<span style="font-size:1.2rem; color:var(--muted)">/10</span></div>
                      <div class="vastu-label" style="margin-top:.3rem">Vastu Score</div>
                      <div style="margin-top:1rem; font-size:.8rem; color:var(--muted); line-height:1.6">{vastu.get('overall','')}</div>
                    </div>""", unsafe_allow_html=True)

                with v2:
                    st.markdown('<div style="margin-bottom:.5rem; font-size:.75rem; color:var(--gold);">✅ POSITIVE ASPECTS</div>',
                                unsafe_allow_html=True)
                    pos_html = "".join(f'<span class="vastu-tag tag-positive">{p}</span>' for p in vastu.get("positive_aspects", []))
                    if not pos_html:
                        pos_html = '<span style="color:var(--muted); font-size:.8rem">None identified</span>'
                    st.markdown(f'<div class="glass-card">{pos_html}</div>', unsafe_allow_html=True)

                    st.markdown('<div style="margin:1rem 0 .5rem; font-size:.75rem; color:var(--red);">⚠️ CONCERNS</div>',
                                unsafe_allow_html=True)
                    con_html = "".join(f'<span class="vastu-tag tag-concern">{c}</span>' for c in vastu.get("concerns", []))
                    if not con_html:
                        con_html = '<span style="color:var(--muted); font-size:.8rem">None identified</span>'
                    st.markdown(f'<div class="glass-card">{con_html}</div>', unsafe_allow_html=True)

                with v3:
                    recs = vastu.get("recommendations", [])
                    if recs:
                        recs_html = "".join(f"<li>{r}</li>" for r in recs)
                        st.markdown(f"""
                        <div class="glass-card">
                          <div class="mt-label" style="margin-bottom:.8rem">🔮 Vastu Remedies</div>
                          <ul class="ai-list">{recs_html}</ul>
                        </div>""", unsafe_allow_html=True)

            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

            # Row 4: Risk flags + Improvements
            rf_col, imp_col = st.columns(2, gap="large")
            with rf_col:
                flags = sec.get("risk_flags", [])
                if flags:
                    st.markdown('<div class="section-label">Risk Flags</div>', unsafe_allow_html=True)
                    flags_html = "".join(f"<li>{f}</li>" for f in flags)
                    st.markdown(f'<div class="glass-card"><ul class="ai-list">{flags_html}</ul></div>',
                                unsafe_allow_html=True)

            with imp_col:
                imps = sec.get("improvement_suggestions", [])
                if imps:
                    st.markdown('<div class="section-label">Value-Adding Improvements</div>', unsafe_allow_html=True)
                    imps_html = "".join(f"<li>{i}</li>" for i in imps)
                    st.markdown(f'<div class="glass-card"><ul class="ai-list">{imps_html}</ul></div>',
                                unsafe_allow_html=True)

        else:
            # Groq not enabled
            msg = groq.get("summary", "Groq AI report unavailable. Add GROQ_API_KEY to backend/.env.")
            st.warning(msg)

        # ── IMAGE ANALYSIS TABLE ──────────────────────────────────────────────
        image_rows = vis.get("images", [])
        if image_rows:
            st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Per-Image Vision Scores</div>', unsafe_allow_html=True)
            df = pd.DataFrame(image_rows)
            # Reorder / rename for clarity
            rename = {
                "filename": "File", "width": "W", "height": "H",
                "brightness": "Brightness", "contrast": "Contrast",
                "sharpness": "Sharpness", "greenery_ratio": "Greenery",
                "warm_light_ratio": "Warm Light", "visual_quality_score": "Quality Score",
                "predicted_view_type": "View Type",
            }
            df = df.rename(columns=rename)
            st.dataframe(df, use_container_width=True, hide_index=True)

        # ── RAW JSON EXPANDER ─────────────────────────────────────────────────
        with st.expander("🗂 Raw API Response"):
            st.json(result)

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend is not running. Start it with: `cd backend && uvicorn app:app --reload`")
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.exception(exc)
