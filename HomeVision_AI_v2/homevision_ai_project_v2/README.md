# HomeVision AI — Multi-Image House Price Predictor

HomeVision AI is an internship-ready AI project that predicts house value using:

1. **California Housing tabular ML baseline** using `LinearRegression`
2. **Multi-image visual scoring** from interior/exterior house photos
3. **FastAPI backend**
4. **Streamlit Python frontend**
5. **EDA + evaluation plots + saved model**

> Important: the California Housing dataset does not contain photos.  
> This project uses California Housing for the core ML workflow and adds a multi-image visual adjustment layer for portfolio demonstration. For production accuracy, train the image branch using a real dataset containing house images and sale prices.

## Folder Structure

```text
homevision_ai_project/
  backend/
    app.py
    train_model.py
    image_analyzer.py
    requirements.txt
  frontend/
    streamlit_app.py
    requirements.txt
  notebooks/
    HomeVision_AI_California_Housing.ipynb
  assets/
  README.md
```

## Setup

### 1. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
python train_model.py
uvicorn app:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

### 3. Run frontend

Open another terminal:

```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Model Inputs

The app accepts:

- Median income
- House age
- Average rooms
- Average bedrooms
- Population
- Average occupancy
- Latitude
- Longitude
- Multiple house images: interior + exterior

## Evaluation Metrics

The training script generates:

- MAE
- RMSE
- R² score
- Predicted vs actual plot
- Residual plot
- Feature coefficient chart

## Best Portfolio Line

“Built HomeVision AI, a hybrid house-price prediction system combining classical regression on California Housing data with multi-image visual condition scoring through a FastAPI + Streamlit full-stack Python application.”



## Groq Setup

Create this file:

```text
backend/.env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.2-90b-vision-preview
```

Do **not** hardcode your API key inside Python files. Keep it inside `.env`.

The Groq layer generates a professional real-estate valuation explanation from:
- ML prediction
- property details
- interior/exterior images
- visual condition score

