#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "Instrumental Eigenmode Spectroscopy of a Holographic Einstein--Dilaton Bulk Using Optical Clocks"
ROWS_PATH = PACK / "TEST_1" / "out" / "mode_response_matrix" / "mode_response_rows.json"

LOCAL_DATASETS = [
    "TEST_1/data/nist/Yb_Clock_phase_vs_time.csv",
    "TEST_1/data/nist/10GHz_phase_vs_time.csv",
]
EPS_CONTROL = 0.0
EPS_SIGNAL = 0.02
TOP_K = 3


def _load_rows():
    return json.loads(ROWS_PATH.read_text(encoding="utf-8"))["rows"]


def _finite_number(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def _select(rows, *, data=None, group=None, epsilon=None):
    out = []
    for row in rows:
        if data is not None and row.get("data") != data:
            continue
        if group is not None and row.get("group") != group:
            continue
        if epsilon is not None and abs(float(row.get("epsilon")) - epsilon) > 1e-12:
            continue
        out.append(row)
    return out


def _sorted_by_mode(rows):
    return sorted(rows, key=lambda row: int(row["mode"]))


def _phase_ranking(rows):
    scored = [row for row in rows if _finite_number(row.get("phase_R"))]
    return sorted(scored, key=lambda row: (float(row["phase_R"]), float(row["max_snr_db"])), reverse=True)


def _top_modes(rows, k=TOP_K):
    return [int(row["mode"]) for row in _phase_ranking(rows)[:k]]


def _spearman_rank(a_rows, b_rows):
    a_rows = _sorted_by_mode(a_rows)
    b_rows = _sorted_by_mode(b_rows)
    if len(a_rows) != len(b_rows):
        raise SystemExit("[ERR] rank comparison requires equal mode counts")

    a_vals = [float(row["phase_R"]) for row in a_rows]
    b_vals = [float(row["phase_R"]) for row in b_rows]

    def ranks(values):
        order = sorted(range(len(values)), key=lambda idx: values[idx])
        out = [0] * len(values)
        for rank, idx in enumerate(order, start=1):
            out[idx] = rank
        return out

    ra = ranks(a_vals)
    rb = ranks(b_vals)
    n = len(ra)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def _control_is_flat(rows):
    phase = [float(row["phase_R"]) for row in rows if _finite_number(row.get("phase_R"))]
    snr = [float(row["max_snr_db"]) for row in rows if _finite_number(row.get("max_snr_db"))]
    if not phase or not snr:
        return False
    return len(set(round(value, 12) for value in phase)) == 1 and len(set(round(value, 12) for value in snr)) == 1


def _remote_negative_summary(rows):
    remote_rows = _select(rows, group="rocit", epsilon=EPS_SIGNAL)
    per_dataset = {}
    for row in remote_rows:
        per_dataset.setdefault(row["data"], []).append(row)

    usable = 0
    phase_zero = 0
    below_threshold = 0
    for dataset, dataset_rows in per_dataset.items():
        phase = [float(row["phase_R"]) for row in dataset_rows if _finite_number(row.get("phase_R"))]
        snr = [float(row["max_snr_db"]) for row in dataset_rows if _finite_number(row.get("max_snr_db"))]
        if not phase or not snr:
            continue
        usable += 1
        if max(phase) == 0.0 and min(phase) == 0.0:
            phase_zero += 1
        if max(snr) < 10.0:
            below_threshold += 1

    return {
        "datasets_total": len(per_dataset),
        "datasets_usable": usable,
        "datasets_all_phase_zero": phase_zero,
        "datasets_max_snr_below_10db": below_threshold,
    }


if __name__ == "__main__":
    rows = _load_rows()

    control_flat = {}
    signal_rows = {}
    for dataset in LOCAL_DATASETS:
        control_rows = _select(rows, data=dataset, epsilon=EPS_CONTROL)
        signal_rows[dataset] = _select(rows, data=dataset, epsilon=EPS_SIGNAL)
        if len(control_rows) != 10 or len(signal_rows[dataset]) != 10:
            raise SystemExit(f"[ERR] expected 10 modes for local dataset {dataset}")
        control_flat[dataset] = _control_is_flat(control_rows)
        if not control_flat[dataset]:
            raise SystemExit(f"[ERR] control epsilon does not stay flat for {dataset}")

    a, b = LOCAL_DATASETS
    top_a = _top_modes(signal_rows[a])
    top_b = _top_modes(signal_rows[b])
    rho = _spearman_rank(signal_rows[a], signal_rows[b])
    remote = _remote_negative_summary(rows)

    if top_a != top_b:
        raise SystemExit(f"[ERR] local holdout top-{TOP_K} mismatch: {top_a} vs {top_b}")
    if rho < 0.99:
        raise SystemExit(f"[ERR] local holdout rank correlation too low: {rho}")
    if remote["datasets_usable"] == 0:
        raise SystemExit("[ERR] no usable remote datasets found in frozen bundle")
    if remote["datasets_all_phase_zero"] != remote["datasets_usable"]:
        raise SystemExit("[ERR] expected all usable remote datasets to have phase_R=0 across modes")

    print("[OK] Eigenmode holdout passed.")
    print(f"     local control flat at eps={EPS_CONTROL}: yes")
    print(f"     local top-{TOP_K} modes at eps={EPS_SIGNAL}: {top_a}")
    print(f"     local rank correlation across independent NIST channels: {rho:.6f}")
    print(
        "     remote negative summary: "
        f"{remote['datasets_all_phase_zero']}/{remote['datasets_usable']} usable datasets "
        "with phase_R=0 across modes"
    )
