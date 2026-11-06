from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


class IsotonicCalibratedClassifier:
    """Wraps a fitted LightGBM model with monotonic Isotonic Regression calibration."""

    def __init__(self, base_estimator: lgb.LGBMClassifier, calibrator: IsotonicRegression):
        self.base_estimator = base_estimator
        self.calibrator = calibrator

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        raw_pos = self.base_estimator.predict_proba(X)[:, 1]
        cal_pos = np.clip(self.calibrator.predict(raw_pos), 0.0, 1.0)
        return np.column_stack([1.0 - cal_pos, cal_pos])


def train_calibrated_triage_model(df: pd.DataFrame, feature_pipeline):
    """Performs chronological splitting, 3-tier benchmarking, and Isotonic calibration."""
    df = df.sort_values("date_received").reset_index(drop=True)
    n = len(df)

    # Strict Out-of-Time Split: 70% Train, 15% Validation (Calibration), 15% Test
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    # Fit feature pipeline strictly on training split to prevent leakage
    X_train = feature_pipeline.fit(train_df).transform(train_df)
    y_train = train_df["target_escalated"].values

    X_val = feature_pipeline.transform(val_df)
    y_val = val_df["target_escalated"].values

    X_test = feature_pipeline.transform(test_df)
    y_test = test_df["target_escalated"].values

    # Save feature pipeline fitted strictly on train_df
    joblib.dump(feature_pipeline, Path("artifacts") / "feature_pipeline.joblib")

    # TIER 0: Domain Heuristic Baseline
    heuristic_scores = np.clip(
        (X_test["urgency_keyword_hits"] > 0).astype(float) * 0.5
        + X_test["eb_encoded_company"].values,
        0.0,
        1.0,
    )
    print(
        f"      -> [Tier 0 Heuristic] Test PR-AUC: {average_precision_score(y_test, heuristic_scores):.4f} | "
        f"ROC-AUC: {roc_auc_score(y_test, heuristic_scores):.4f}",
        flush=True,
    )

    # TIER 1: L2 Logistic Regression Baseline
    num_cols = X_train.select_dtypes(include=[np.number]).columns
    tier1_lr = LogisticRegression(max_iter=500, C=1.0, random_state=42)
    tier1_lr.fit(X_train[num_cols].fillna(0), y_train)
    lr_probs = tier1_lr.predict_proba(X_test[num_cols].fillna(0))[:, 1]
    print(
        f"      -> [Tier 1 Logistic]  Test PR-AUC: {average_precision_score(y_test, lr_probs):.4f} | "
        f"ROC-AUC: {roc_auc_score(y_test, lr_probs):.4f}",
        flush=True,
    )

    # TIER 2: Champion Hybrid LightGBM Classifier
    base_lgbm = lgb.LGBMClassifier(
        n_estimators=150,
        learning_rate=0.04,
        num_leaves=15,
        min_child_samples=20,
        class_weight="balanced",
        random_state=42,
        verbose=-1,
    )
    base_lgbm.fit(X_train, y_train)

    # Fit Isotonic Regression Calibrator on Out-of-Time Validation Fold
    val_raw_probs = base_lgbm.predict_proba(X_val)[:, 1]
    iso_calibrator = IsotonicRegression(y_min=0.001, y_max=0.999, out_of_bounds="clip")
    iso_calibrator.fit(val_raw_probs, y_val)

    calibrated_model = IsotonicCalibratedClassifier(base_lgbm, iso_calibrator)

    # Evaluate on Out-of-Time Test Fold
    raw_test_probs = base_lgbm.predict_proba(X_test)[:, 1]
    cal_test_probs = calibrated_model.predict_proba(X_test)[:, 1]

    print(
        f"      -> [Tier 2 LightGBM]  Test PR-AUC: {average_precision_score(y_test, cal_test_probs):.4f} | "
        f"ROC-AUC: {roc_auc_score(y_test, cal_test_probs):.4f}",
        flush=True,
    )
    print(
        f"      -> Calibration Check | Uncalibrated Brier: {brier_score_loss(y_test, raw_test_probs):.4f} -> "
        f"Calibrated Brier: {brier_score_loss(y_test, cal_test_probs):.4f}",
        flush=True,
    )

    return base_lgbm, calibrated_model, X_test, y_test


def find_optimal_business_threshold(
    y_true: np.ndarray, probs: np.ndarray, cost_fn: float = 250.0, cost_fp: float = 15.0
):
    """Sweeps probability thresholds to minimize expected financial SLA triage cost."""
    thresholds = np.linspace(0.02, 0.90, 89)
    best_t, min_cost = 0.50, float("inf")

    preds_50 = (probs >= 0.50).astype(int)
    cost_at_50 = (
        np.sum((y_true == 1) & (preds_50 == 0)) * cost_fn
        + np.sum((y_true == 0) & (preds_50 == 1)) * cost_fp
    )

    for t in thresholds:
        preds = (probs >= t).astype(int)
        fn = np.sum((y_true == 1) & (preds == 0))
        fp = np.sum((y_true == 0) & (preds == 1))
        total_cost = (fn * cost_fn) + (fp * cost_fp)
        if total_cost < min_cost:
            min_cost = total_cost
            best_t = t

    savings = cost_at_50 - min_cost
    print(
        f"      -> Cost at Naive 0.50 Cutoff: ${cost_at_50:,.2f} | "
        f"Optimal Cost at t*={best_t:.4f}: ${min_cost:,.2f} (Saved ${savings:,.2f})",
        flush=True,
    )
    return float(best_t), float(min_cost)