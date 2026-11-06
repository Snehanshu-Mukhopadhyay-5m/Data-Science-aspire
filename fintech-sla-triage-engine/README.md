# FinTech SLA Breach & Regulatory Escalation Triage Engine

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Microservice-009688.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytical_Warehouse-yellow.svg)
![Pandera](https://img.shields.io/badge/Pandera-Data_Contracts-orange.svg)
![LightGBM](https://img.shields.io/badge/LightGBM-Champion_Model-brightgreen.svg)
![pytest](https://img.shields.io/badge/Tests-Passing-success.svg)

A production-grade, end-to-end Machine Learning system designed to predict and triage Consumer Financial Protection Bureau (CFPB) complaints at risk of breaching regulatory Service Level Agreements (SLAs) or escalating into severe financial disputes. 

Unlike standard notebook workflows that assume clean data, this project implements robust MLOps patterns: resilient API ingestion, strict data contracts with quarantine routing, zero-leakage point-in-time feature engineering, monotonic probability calibration, asymmetric financial cost optimization, and sub-25ms real-time serving with TreeSHAP explainability and Population Stability Index (PSI) drift monitoring.

---

## 🏗️ System Architecture & Workflow

```mermaid
---
config:
  layout: elk
---
graph TD
    classDef storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef split fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    classDef api fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
    classDef drift fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;

    A[("DuckDB: matured_tickets<br>(1,828 rows)")]:::storage --> B["1. Out-of-Time Chronological Split<br>70% Train | 15% Val | 15% Test"]:::split

    B -->|"70% Train"| C["2. 3-Tier Benchmarking<br>Tier 0: Heuristic | Tier 1: L2 Logistic<br>Tier 2: Hybrid LightGBM"]:::model
    B -->|"15% Val"| D["3. Monotonic Isotonic Calibration<br>Fixes boosted-tree Brier score"]:::model
    C --> D
    D -->|"15% Test"| E["4. Asymmetric Cost Sweep<br>Minimizes (FN * $250) + (FP * $15)<br>Finds optimal cutoff t*"]:::model

    E --> F(["Frozen Artifacts Store<br>calibrated_lgbm.joblib | raw_lgbm_booster.joblib<br>training_baseline.json"]):::storage

    F --> G["5. FastAPI Lifespan Server<br>(api/main.py | Pytest Verified)"]:::api
    G --> H["POST /predict<br>Calibrated Risk + Routing + Top-3 TreeSHAP"]:::api
    G --> I["GET /drift<br>PSI KL-Divergence on 160 Right-Censored Tickets"]:::drift

```text
 fintech-sla-triage-engine/
├── api/
│   ├── __init__.py
│   └── main.py                 # FastAPI microservice (lifespan loading, /predict, /drift)
├── artifacts/                  # Serialized joblib models and frozen training baseline JSON
├── configs/                    # Pipeline and schema configuration files
├── data/
│   ├── quarantine/             # Parquet store isolating Pandera contract violations
│   └── fintech_triage.duckdb   # Embedded analytical warehouse (matured vs live queues)
├── pipelines/
│   └── run_pipeline.py         # End-to-end orchestration runner
├── src/
│   ├── features/
│   │   └── feature_engineering.py # Point-in-time velocity, Empirical Bayes, SVD compression
│   ├── ingestion/
│   │   └── ingest_and_validate.py # WAF fallback generator & Pandera DataFrameSchema gate
│   ├── models/
│   │   └── train_and_calibrate.py # Chronological splitting, 3-tier models, Isotonic regression
│   └── monitoring/
│       └── psi_drift.py        # Population Stability Index (PSI) KL-divergence calculator
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py        # pytest unit test suite (TestClient & PSI validation)
├── requirements.txt            # Project dependencies
└── README.md