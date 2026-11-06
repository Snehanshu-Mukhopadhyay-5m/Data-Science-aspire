from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

from contextlib import asynccontextmanager
import json
from pathlib import Path
import time
import duckdb
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import custom classes so joblib can deserialize saved objects cleanly
from src.features.feature_engineering import HybridFeaturePipeline
from src.models.train_and_calibrate import IsotonicCalibratedClassifier
from src.monitoring.psi_drift import compute_psi_from_quantiles

ARTIFACT_DIR = Path("artifacts")
DATA_DIR = Path("data")

ml_context = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Loads frozen feature pipeline, calibrated model, and baseline metadata on startup."""
    ml_context["feature_pipeline"] = joblib.load(ARTIFACT_DIR / "feature_pipeline.joblib")
    ml_context["calibrated_model"] = joblib.load(ARTIFACT_DIR / "calibrated_lgbm.joblib")
    ml_context["raw_lgbm"] = joblib.load(ARTIFACT_DIR / "raw_lgbm_booster.joblib")
    ml_context["baseline_meta"] = json.loads(
        (ARTIFACT_DIR / "training_baseline.json").read_text()
    )
    yield
    ml_context.clear()


app = FastAPI(
    title="FinTech SLA Escalation Triage API",
    version="1.0.0",
    lifespan=lifespan,
)


class TicketRequest(BaseModel):
    complaint_id: int
    date_received: str
    company: str
    product: str
    issue: str
    submitted_via: str
    complaint_what_happened: str | None = None


class TriageResponse(BaseModel):
    complaint_id: int
    calibrated_escalation_prob: float
    optimal_threshold_used: float
    routing_action: str
    latency_ms: float
    top_shap_reasons: list[str]


def compute_top_treeshap_reasons(raw_lgbm, X_row: pd.DataFrame) -> list[str]:
    """Computes exact TreeSHAP feature attributions using LightGBM native C++ pred_contrib."""
    contrib = raw_lgbm.booster_.predict(X_row, pred_contrib=True)[0]
    feature_shaps = contrib[:-1]  # Last element is base expected value phi_0
    top_indices = np.argsort(np.abs(feature_shaps))[::-1][:3]

    reasons = []
    for idx in top_indices:
        feat_name = X_row.columns[idx]
        impact = feature_shaps[idx]
        sign = "+" if impact >= 0 else ""
        reasons.append(f"{feat_name}: {sign}{impact:.3f} log-odds impact")
    return reasons


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "optimal_threshold": ml_context["baseline_meta"]["optimal_threshold"],
        "expected_test_cost_usd": ml_context["baseline_meta"]["expected_test_cost_usd"],
    }


@app.post("/predict", response_model=TriageResponse)
def predict_ticket(ticket: TicketRequest):
    t0 = time.perf_counter()
    pipe: HybridFeaturePipeline = ml_context["feature_pipeline"]
    cal_model: IsotonicCalibratedClassifier = ml_context["calibrated_model"]
    raw_lgbm = ml_context["raw_lgbm"]
    opt_t = float(ml_context["baseline_meta"]["optimal_threshold"])

    df_in = pd.DataFrame([ticket.model_dump()])
    X_row = pipe.transform(df_in)

    prob = float(cal_model.predict_proba(X_row)[0, 1])
    action = "PRIORITY_SPECIALIST_QUEUE" if prob >= opt_t else "STANDARD_QUEUE"
    reasons = compute_top_treeshap_reasons(raw_lgbm, X_row)
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    return TriageResponse(
        complaint_id=ticket.complaint_id,
        calibrated_escalation_prob=round(prob, 4),
        optimal_threshold_used=opt_t,
        routing_action=action,
        latency_ms=latency_ms,
        top_shap_reasons=reasons,
    )


@app.get("/drift")
def check_live_queue_drift():
    db_path = DATA_DIR / "fintech_triage.duckdb"
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="DuckDB warehouse not found.")

    con = duckdb.connect(str(db_path), read_only=True)
    live_df = con.execute("SELECT * FROM live_inference_queue").df()
    con.close()

    pipe: HybridFeaturePipeline = ml_context["feature_pipeline"]
    X_live = pipe.transform(live_df)

    quantiles = ml_context["baseline_meta"]["eb_company_quantiles"]
    drift_report = compute_psi_from_quantiles(
        frozen_bin_edges=quantiles,
        actual_live=X_live["eb_encoded_company"].values,
    )
    return {"feature": "eb_encoded_company", **drift_report}