"""Slim IBM attrition FastAPI for Render Free (512 MB)."""

import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

DATA_PATH = Path(__file__).parent / "model" / "data" / "ibm_hr_attrition.csv"
MODEL_PATH = Path(
    os.environ.get(
        "MODEL_PATH",
        str(Path(__file__).parent / "model" / "ibm_attrition_model.joblib"),
    )
)

DESCRIPTION = """
Human Resources API for teaching deploys on Render.

## Preview
* `/preview` returns a few rows
* `/unique-values` lists unique values for a column

## Predict
* `/predict-attrition` predicts whether an employee is likely to leave
"""

app = FastAPI(
    title="HR Attrition API",
    description=DESCRIPTION,
    version="0.2",
    contact={"name": "HR API - by Jedha", "url": "https://jedha.co"},
)

df: pd.DataFrame | None = None
classifier = None
feature_names: list[str] = []


class AttritionInput(BaseModel):
    features: dict[str, Any] = Field(
        description="Feature name to value mapping expected by the trained model"
    )


@app.on_event("startup")
async def startup() -> None:
    global df, classifier, feature_names
    df = pd.read_csv(DATA_PATH)
    artifact = joblib.load(MODEL_PATH)
    classifier = artifact["model"]
    feature_names = list(artifact["feature_names"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "rows": 0 if df is None else len(df),
        "model_loaded": classifier is not None,
        "model_path": str(MODEL_PATH),
        "app_env": os.environ.get("APP_ENV", "unset"),
    }


@app.get("/preview")
async def preview(rows: int = 10):
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    sample = df.sample(min(rows, len(df)))
    return sample.to_dict(orient="records")


@app.get("/unique-values")
async def unique_values(column: str):
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Unknown column: {column}")
    return {"column": column, "values": df[column].dropna().unique().tolist()}


@app.post("/predict-attrition")
async def predict_attrition(payload: AttritionInput):
    if classifier is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")

    input_df = pd.DataFrame([payload.features])
    missing = [col for col in feature_names if col not in input_df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    ordered = input_df[feature_names]
    prediction = classifier.predict(ordered)[0]
    probability = float(classifier.predict_proba(ordered)[0][1])
    return {
        "Attrition": "Yes" if int(prediction) == 1 else "No",
        "Probability": round(probability, 3),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
