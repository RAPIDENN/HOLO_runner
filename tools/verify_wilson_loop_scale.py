#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_finite(x: float) -> bool:
    return math.isfinite(float(x))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Verify Wilson-loop absolute scale artifact (bundle-local, no private ED kernel required)."
    )
    ap.add_argument(
        "--path",
        default="instrument_closure/2026-01-04/wilson_loop_sigma_from_ed_trace.json",
        help="Path to wilson_loop_sigma_from_ed_trace.json",
    )
    ap.add_argument("--rel-tol", type=float, default=1e-12, help="Relative tolerance for consistency checks")
    args = ap.parse_args()

    path = Path(args.path)
    obj = _load_json(path)

    required = [
        "e2A_ir",
        "alpha_prime_GeV-2",
        "sigma_eff_GeV2",
        "c_scalar",
        "m0_GeV",
    ]
    for k in required:
        if k not in obj:
            raise SystemExit(f"[ERR] {path} missing {k}")

    e2A = float(obj["e2A_ir"])
    alpha_p = float(obj["alpha_prime_GeV-2"])
    sigma = float(obj["sigma_eff_GeV2"])
    c = float(obj["c_scalar"])
    m0 = float(obj["m0_GeV"])

    if not (_is_finite(e2A) and _is_finite(alpha_p) and _is_finite(sigma) and _is_finite(c) and _is_finite(m0)):
        raise SystemExit("[ERR] non-finite values in Wilson-loop scale artifact")
    if e2A <= 0 or alpha_p <= 0 or sigma <= 0 or c <= 0 or m0 <= 0:
        raise SystemExit("[ERR] expected positive values in Wilson-loop scale artifact")

    sigma_expected = e2A / (2.0 * math.pi * alpha_p)
    if not _is_finite(sigma_expected) or sigma_expected <= 0:
        raise SystemExit("[ERR] computed sigma_eff is not finite/positive")

    rel_err_sigma = abs(sigma - sigma_expected) / max(abs(sigma_expected), 1.0)
    if rel_err_sigma > args.rel_tol:
        raise SystemExit(
            f"[ERR] sigma_eff mismatch: reported={sigma} expected={sigma_expected} rel_err={rel_err_sigma} tol={args.rel_tol}"
        )

    m0_expected = c * math.sqrt(sigma)
    rel_err_m0 = abs(m0 - m0_expected) / max(abs(m0_expected), 1.0)
    if rel_err_m0 > args.rel_tol:
        raise SystemExit(
            f"[ERR] m0 mismatch: reported={m0} expected={m0_expected} rel_err={rel_err_m0} tol={args.rel_tol}"
        )

    print("[OK] Wilson-loop scale artifact internally consistent.")

