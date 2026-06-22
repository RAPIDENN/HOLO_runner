#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "A_single_Einstein_Dilaton geometry"


def _is_strictly_increasing(xs):
    return all(xs[i + 1] > xs[i] for i in range(len(xs) - 1))


def _is_finite(xs):
    return all(math.isfinite(float(x)) for x in xs)


if __name__ == "__main__":
    path = BUNDLE / "artifacts" / "ed_bulk_clock.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    if "series" not in obj:
        raise SystemExit("[ERR] ed_bulk_clock.json missing 'series'")
    s = obj["series"]
    for key in ["z", "A", "R5", "E", "dt_phys_dt_ref", "t_phys"]:
        if key not in s:
            raise SystemExit(f"[ERR] ed_bulk_clock.json missing series.{key}")

    z = list(map(float, s["z"]))
    dt = list(map(float, s["dt_phys_dt_ref"]))
    t = list(map(float, s["t_phys"]))

    if len(z) < 10:
        raise SystemExit("[ERR] ed_bulk_clock series too short")
    if not _is_strictly_increasing(z):
        raise SystemExit("[ERR] ed_bulk_clock series.z is not strictly increasing")
    if not (_is_finite(z) and _is_finite(dt) and _is_finite(t)):
        raise SystemExit("[ERR] ed_bulk_clock contains non-finite values")
    if any(x <= 0 for x in dt):
        raise SystemExit("[ERR] ed_bulk_clock dt_phys_dt_ref must be > 0 everywhere")

    # Sanity anchor: the export is normalized at z=1 so t_phys(z=1) should be 0 on the closest grid point.
    idx0 = min(range(len(z)), key=lambda i: abs(z[i] - 1.0))
    if abs(z[idx0] - 1.0) > 1e-6:
        raise SystemExit("[ERR] ed_bulk_clock does not contain z=1 endpoint (needed for canonical normalization)")
    if abs(t[idx0]) > 1e-6:
        raise SystemExit(f"[ERR] ed_bulk_clock t_phys(z≈1) not ~0 (got {t[idx0]})")

    print("[OK] 5D bulk Ricci clock artifact present and sane.")

