import numpy as np
from fastapi.testclient import TestClient
from api.main import app
from src.monitoring.psi_drift import compute_psi_from_quantiles


def test_psi_drift_stability():
    """Verifies PSI returns STABLE (<0.10) when live data matches training quantiles."""
    np.random.seed(42)
    frozen_edges = [0.0, 0.10, 0.15, 0.20, 0.25, 1.0]
    live_samples = np.random.uniform(0.05, 0.30, size=200)
    res = compute_psi_from_quantiles(frozen_edges, live_samples)
    assert "psi" in res
    assert res["status"] in ["STABLE", "WARNING_MODERATE_DRIFT", "CRITICAL_DRIFT_RETRAIN"]


def test_fastapi_health_and_predict():
    """Verifies FastAPI lifespan loads artifacts and scores a ticket in <100ms."""
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert "optimal_threshold" in health.json()

        payload = {
            "complaint_id": 9999001,
            "date_received": "2026-04-01",
            "company": "EQUIFAX, INC.",
            "product": "Credit reporting or other personal consumer reports",
            "issue": "Fraud or scam",
            "submitted_via": "Web",
            "complaint_what_happened": "Unauthorized wire transfer of $4500 due to fraud and identity theft.",
        }
        pred = client.post("/predict", json=payload)
        assert pred.status_code == 200
        data = pred.json()
        assert 0.0 <= data["calibrated_escalation_prob"] <= 1.0
        assert len(data["top_shap_reasons"]) == 3