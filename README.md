# Render IBM Attrition API (Jedha Launch)

Slim FastAPI + scikit-learn attrition demo for Render Free (512 MB).

## Files

- `app.py` — `/health`, `/preview`, `/unique-values`, `/predict-attrition`
- `model/ibm_attrition_model.joblib` — trained pipeline (sklearn 1.7.2)
- `model/data/ibm_hr_attrition.csv` — local data (CSV, not xlsx)
- `Dockerfile` sets `MODEL_PATH` and `APP_ENV`

Keep `scikit-learn==1.7.2` in `requirements.txt` so the joblib artifact loads cleanly.

## Push + deploy

See:

`AIFS/.changelogs/M08-ML_Engineering/D06-Launch/MANUAL_DEPLOY_RUNBOOK.md`

On Render Environment (optional but good for Exercise 2 practice):

- `MODEL_PATH=/app/model/ibm_attrition_model.joblib`
- `APP_ENV=production`

## Local (no Docker)

```bash
pip install -r requirements.txt
PORT=10000 uvicorn app:app --host 0.0.0.0 --port 10000
```

Open `/health` and `/docs`.

## Predict in `/docs`

In Swagger, **POST `/predict-attrition` → Try it out** may show a placeholder like:

```json
{
  "features": {
    "additionalProp1": {}
  }
}
```

That placeholder is not valid input. Replace it with real employee fields:

1. Call **GET `/preview?rows=1`**.
2. Copy the returned employee object.
3. Remove `"Attrition"` (the model predicts this).
4. Wrap the remaining fields in `"features": { ... }`.
5. Click **Execute**.

Or pick **Ready-to-run employee example** from the example dropdown on that endpoint.

Use **GET `/unique-values?column=Department`** (or another column) to see valid
categorical values before editing fields like `OverTime` or `JobRole`.
