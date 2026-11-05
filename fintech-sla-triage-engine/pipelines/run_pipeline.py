import json
from pathlib import Path
import duckdb
import joblib
import numpy as np

from src.ingestion.ingest_and_validate import fetch_cfpb_batch, validate_and_split_maturity
from src.features.feature_engineering import HybridFeaturePipeline

DATA_DIR = Path("data")
ARTIFACT_DIR = Path("artifacts")


def run_end_to_end_pipeline(batch_size: int = 2000):
    print("=== Starting FinTech SLA Triage Pipeline ===", flush=True)
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "quarantine").mkdir(exist_ok=True)
    ARTIFACT_DIR.mkdir(exist_ok=True)

    # 1. Ingest & Validate via Pandera Contract
    print(f"[1/4] Fetching {batch_size} live CFPB records and running Pandera validation...", flush=True)
    raw_df = fetch_cfpb_batch(size=batch_size)
    matured_df, live_queue_df, quarantine_df = validate_and_split_maturity(raw_df)

    con = duckdb.connect(str(DATA_DIR / "fintech_triage.duckdb"))
    con.execute("CREATE OR REPLACE TABLE matured_tickets AS SELECT * FROM matured_df")
    con.execute("CREATE OR REPLACE TABLE live_inference_queue AS SELECT * FROM live_queue_df")
    if not quarantine_df.empty:
        quarantine_df.to_parquet(DATA_DIR / "quarantine" / "quarantined_batch.parquet")

    print(
        f"      -> Stored in DuckDB | Matured: {len(matured_df)} | "
        f"Live Queue (Right-Censored): {len(live_queue_df)} | Quarantined: {len(quarantine_df)}",
        flush=True,
    )

    # 2. Point-in-Time Velocity & Hybrid NLP Features
    print("[2/4] Engineering Point-in-Time velocity, Empirical Bayes encoding, and 16-dim SVD...", flush=True)
    matured_df = HybridFeaturePipeline.add_point_in_time_velocity(matured_df)
    feature_pipe = HybridFeaturePipeline(smoothing_m=25.0, n_svd_components=16)

    X_sample = feature_pipe.fit(matured_df).transform(matured_df)
    joblib.dump(feature_pipe, ARTIFACT_DIR / "feature_pipeline.joblib")
    print(
        f"      -> Feature matrix ready! Shape: {X_sample.shape} | "
        f"Global Escalation Prior: {feature_pipe.global_prior_:.4f}",
        flush=True,
    )

    # 3. Check if Day 2 Model Training Module is Ready
    train_module_path = Path("src/models/train_and_calibrate.py")
    if not train_module_path.exists() or train_module_path.stat().st_size == 0:
        con.close()
        print("\n[Day 1 Complete!] DuckDB warehouse and feature_pipeline.joblib saved.", flush=True)
        print("Next step: Add `src/models/train_and_calibrate.py` to run Day 2 model training.", flush=True)
        return

    from src.models.train_and_calibirate import (
        train_calibrated_triage_model,
        find_optimal_business_threshold,
    )

    print("[3/4] Training Out-of-Time LightGBM and fitting Isotonic Calibration...", flush=True)
    base_lgbm, calibrated_model, X_test, y_test = train_calibrated_triage_model(
        matured_df, feature_pipe
    )

    # 4. Sweep Business Cost Threshold
    print("[4/4] Sweeping business cost curve (FN=$250 vs FP=$15)...", flush=True)
    test_probs = calibrated_model.predict_proba(X_test)[:, 1]
    optimal_t, min_cost = find_optimal_business_threshold(
        y_test, test_probs, cost_fn=250.0, cost_fp=15.0
    )

    joblib.dump(calibrated_model, ARTIFACT_DIR / "calibrated_lgbm.joblib")
    joblib.dump(base_lgbm, ARTIFACT_DIR / "raw_lgbm_booster.joblib")

    baseline_meta = {
        "optimal_threshold": round(optimal_t, 4),
        "expected_test_cost_usd": round(min_cost, 2),
        "eb_company_quantiles": np.percentile(
            X_test["eb_encoded_company"].dropna(), np.linspace(0, 100, 11)
        ).tolist(),
    }
    (ARTIFACT_DIR / "training_baseline.json").write_text(json.dumps(baseline_meta, indent=2))
    con.close()
    print(f"=== Pipeline Complete! Optimal Threshold t* = {optimal_t:.4f} | Min Test Cost = ${min_cost:,.2f} ===", flush=True)


if __name__ == "__main__":
    run_end_to_end_pipeline()