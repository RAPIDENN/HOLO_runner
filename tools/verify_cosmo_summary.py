#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    path = ROOT / "data" / "internal" / "cosmo_robustness_summary.json"
    data = json.loads(path.read_text())
    if "summary" not in data:
        raise SystemExit("[ERR] cosmo summary missing 'summary'")
    print("[OK] Cosmology robustness summary present.")
