#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    path = ROOT / "data" / "internal" / "lock5_ricci_results.json"
    data = json.loads(path.read_text())
    if not data.get("passed"):
        raise SystemExit("[ERR] lock5_ricci_results passed flag is false")
    print("[OK] LOCK5 Ricci summary present and marked as passed.")
