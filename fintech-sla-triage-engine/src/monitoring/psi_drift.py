import numpy as np


def compute_psi_from_quantiles(
    frozen_bin_edges: list[float], actual_live: np.ndarray, eps: float = 1e-4
) -> dict:
    """Computes Population Stability Index (PSI) against frozen training quantile edges."""
    clean_live = actual_live[~np.isnan(actual_live)]
    if len(clean_live) == 0:
        return {"psi": 0.0, "status": "NO_DATA"}

    edges = np.array(frozen_bin_edges, dtype=float)
    edges[0] = -np.inf
    edges[-1] = np.inf
    edges = np.unique(edges)

    num_bins = len(edges) - 1
    # Expected proportions are uniform across quantile bins (1 / num_bins)
    e_prop = np.full(num_bins, 1.0 / num_bins)

    a_counts, _ = np.histogram(clean_live, bins=edges)
    a_prop = np.clip(a_counts / max(len(clean_live), 1), eps, None)
    a_prop /= a_prop.sum()

    bin_psi = (a_prop - e_prop) * np.log(a_prop / e_prop)
    total_psi = float(np.sum(bin_psi))

    if total_psi < 0.10:
        status = "STABLE"
    elif total_psi < 0.25:
        status = "WARNING_MODERATE_DRIFT"
    else:
        status = "CRITICAL_DRIFT_RETRAIN"

    return {
        "psi": round(total_psi, 4),
        "status": status,
        "live_sample_size": int(len(clean_live)),
    }