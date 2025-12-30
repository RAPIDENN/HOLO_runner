#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "A_single_Einstein_Dilaton geometry"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _pearson_r(x, y):
    n = min(len(x), len(y))
    if n < 2:
        return float("nan")
    mx = sum(x[:n]) / n
    my = sum(y[:n]) / n
    vx = sum((xi - mx) ** 2 for xi in x[:n])
    vy = sum((yi - my) ** 2 for yi in y[:n])
    denom = math.sqrt(vx * vy)
    if denom <= 0 or not math.isfinite(denom):
        return float("nan")
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return cov / denom


def _chi2(y_obs, y_pred, sigma_hat):
    if sigma_hat <= 0 or not math.isfinite(sigma_hat):
        return float("nan")
    n = min(len(y_obs), len(y_pred))
    return sum(((y_obs[i] - y_pred[i]) / sigma_hat) ** 2 for i in range(n))


if __name__ == "__main__":
    # Kernel existence (screening definition)
    kem = _load_json(BUNDLE / "artifacts" / "k_em_uv_projector.json")
    for k in ["z_grid", "k_em", "normalization_verified"]:
        if k not in kem:
            raise SystemExit(f"[ERR] k_em_uv_projector.json missing {k}")
    norm = float(kem["normalization_verified"])
    if not math.isfinite(norm):
        raise SystemExit("[ERR] k_em_uv_projector.json normalization_verified not finite")
    if abs(norm - 1.0) > 1e-6:
        raise SystemExit(f"[ERR] k_em_uv_projector.json normalization_verified != 1 (got {norm})")

    # UV-projected prediction exists
    em_uv = _load_json(BUNDLE / "artifacts" / "em_uv_projected.json")
    if "series" not in em_uv:
        raise SystemExit("[ERR] em_uv_projected.json missing series")
    for k in ["t_lab", "t_phys", "y_pred", "z_trace"]:
        if k not in em_uv["series"]:
            raise SystemExit(f"[ERR] em_uv_projected.json missing series.{k}")

    # NIST comparison reports exist (naive + UV)
    naive = _load_json(BUNDLE / "artifacts" / "nist_comparison_naive.json")
    uv = _load_json(BUNDLE / "artifacts" / "nist_comparison_uv.json")

    for label, obj in [("naive", naive), ("uv", uv)]:
        if "metrics" not in obj or "series" not in obj:
            raise SystemExit(f"[ERR] {label} comparison missing metrics/series")
        for k in ["n", "pearson_r", "sigma_hat", "chi2", "chi2_over_n"]:
            if k not in obj["metrics"]:
                raise SystemExit(f"[ERR] {label} comparison missing metrics.{k}")
        for k in ["y_obs", "y_pred"]:
            if k not in obj["series"]:
                raise SystemExit(f"[ERR] {label} comparison missing series.{k}")

        y_obs = list(map(float, obj["series"]["y_obs"]))
        y_pred = list(map(float, obj["series"]["y_pred"]))
        n = int(obj["metrics"]["n"])
        if n != min(len(y_obs), len(y_pred)):
            raise SystemExit(f"[ERR] {label} metrics.n does not match series lengths")

        sigma_hat = float(obj["metrics"]["sigma_hat"])
        chi2 = _chi2(y_obs, y_pred, sigma_hat)
        if not math.isfinite(chi2):
            raise SystemExit(f"[ERR] {label} recomputed chi2 is not finite")
        chi2_reported = float(obj["metrics"]["chi2"])
        if abs(chi2 - chi2_reported) > 1e-6 * max(abs(chi2_reported), 1.0):
            raise SystemExit(f"[ERR] {label} chi2 mismatch vs reported (recomputed={chi2}, reported={chi2_reported})")

        r = _pearson_r(y_obs, y_pred)
        r_reported = float(obj["metrics"]["pearson_r"])
        if abs(r - r_reported) > 1e-6 * max(abs(r_reported), 1.0):
            raise SystemExit(f"[ERR] {label} pearson_r mismatch vs reported (recomputed={r}, reported={r_reported})")

    naive_chi2n = float(naive["metrics"]["chi2_over_n"])
    uv_chi2n = float(uv["metrics"]["chi2_over_n"])
    if not (math.isfinite(naive_chi2n) and math.isfinite(uv_chi2n)):
        raise SystemExit("[ERR] chi2_over_n not finite")
    if uv_chi2n >= naive_chi2n:
        raise SystemExit("[ERR] expected UV screening to reduce chi2_over_n relative to naive mapping")

    print("[OK] UV-screened NIST channel artifacts present and internally consistent.")
