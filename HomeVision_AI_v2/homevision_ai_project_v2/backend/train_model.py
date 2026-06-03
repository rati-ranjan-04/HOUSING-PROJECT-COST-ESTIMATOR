from __future__ import annotations

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "model_artifacts"
PLOT_DIR = ROOT / "plots"
MODEL_DIR.mkdir(exist_ok=True)
PLOT_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load California Housing data, falling back to synthetic data if unavailable."""
    try:
        from sklearn.datasets import fetch_california_housing
        data = fetch_california_housing(as_frame=True)
        df = data.frame.copy()
        df.rename(columns={"MedHouseVal": "target_price_100k"}, inplace=True)
        print("Loaded California Housing dataset from sklearn.")
        return df
    except Exception as exc:
        print(f"Could not fetch California Housing dataset ({exc}). Generating synthetic data...")
        return _generate_synthetic_california_data()


def _generate_synthetic_california_data(n_samples: int = 20640, random_state: int = 42) -> pd.DataFrame:
    """Generate synthetic data that mimics the California Housing dataset statistics."""
    rng = np.random.default_rng(random_state)

    latitude = rng.uniform(32.5, 42.0, n_samples)
    longitude = rng.uniform(-124.5, -114.5, n_samples)
    house_age = rng.uniform(1, 52, n_samples)
    ave_rooms = rng.lognormal(mean=1.6, sigma=0.45, size=n_samples).clip(1, 15)
    ave_bedrms = (ave_rooms / rng.uniform(3.5, 5.5, n_samples)).clip(0.5, 5)
    population = rng.lognormal(mean=7.0, sigma=0.9, size=n_samples).clip(3, 35682)
    ave_occup = rng.lognormal(mean=1.1, sigma=0.35, size=n_samples).clip(0.5, 10)

    # Median income: log-normal, clipped 0.5–15
    med_inc = rng.lognormal(mean=1.6, sigma=0.5, size=n_samples).clip(0.5, 15)

    # Target: loosely correlated with income and location
    noise = rng.normal(0, 0.3, n_samples)
    target = (
        0.42 * med_inc
        + 0.005 * house_age
        + 0.12 * ave_rooms
        - 0.05 * ave_bedrms
        - 0.00003 * population
        - 0.05 * ave_occup
        - 0.12 * np.abs(latitude - 34.0)
        - 0.08 * np.abs(longitude + 118.0)
        + noise
        + 1.2
    ).clip(0.15, 5.0)

    df = pd.DataFrame({
        "MedInc": np.round(med_inc, 4),
        "HouseAge": np.round(house_age, 1),
        "AveRooms": np.round(ave_rooms, 4),
        "AveBedrms": np.round(ave_bedrms, 4),
        "Population": np.round(population, 1),
        "AveOccup": np.round(ave_occup, 4),
        "Latitude": np.round(latitude, 4),
        "Longitude": np.round(longitude, 4),
        "target_price_100k": np.round(target, 4),
    })
    return df


def train() -> None:
    df = load_data()

    X = df.drop(columns=["target_price_100k"])
    y = df["target_price_100k"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = r2_score(y_test, preds)

    metrics = {
        "model_name": "LinearRegression",
        "dataset": "sklearn.datasets.fetch_california_housing (synthetic fallback if unavailable)",
        "target_unit": "100,000 USD",
        "rows": int(df.shape[0]),
        "features": list(X.columns),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
    }

    joblib.dump(model, MODEL_DIR / "linear_regression_house_price.joblib")
    joblib.dump(list(X.columns), MODEL_DIR / "feature_names.joblib")
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    coefficient_df = pd.DataFrame({
        "feature": X.columns,
        "coefficient": model.coef_
    }).sort_values("coefficient", key=abs, ascending=False)
    coefficient_df.to_csv(MODEL_DIR / "feature_coefficients.csv", index=False)

    # Plot 1: predicted vs actual
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, preds, alpha=0.35)
    plt.xlabel("Actual House Value in $100k")
    plt.ylabel("Predicted House Value in $100k")
    plt.title("HomeVision AI: Predicted vs Actual")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "predicted_vs_actual.png", dpi=180)
    plt.close()

    # Plot 2: residuals
    residuals = y_test - preds
    plt.figure(figsize=(8, 6))
    plt.scatter(preds, residuals, alpha=0.35)
    plt.axhline(0, linestyle="--")
    plt.xlabel("Predicted House Value in $100k")
    plt.ylabel("Residual")
    plt.title("HomeVision AI: Residual Plot")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "residuals.png", dpi=180)
    plt.close()

    # Plot 3: feature coefficients
    plt.figure(figsize=(9, 6))
    plt.barh(coefficient_df["feature"], coefficient_df["coefficient"])
    plt.xlabel("Linear Coefficient")
    plt.title("HomeVision AI: Feature Impact")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "feature_coefficients.png", dpi=180)
    plt.close()

    print(json.dumps(metrics, indent=2))
    print(f"Saved model artifacts to: {MODEL_DIR}")
    print(f"Saved plots to: {PLOT_DIR}")


if __name__ == "__main__":
    train()
