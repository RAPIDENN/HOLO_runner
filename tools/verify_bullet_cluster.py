#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    path = ROOT / "data" / "internal" / "bullet_cluster_ed.json"
    data = json.loads(path.read_text())
    if "summary" not in data:
        raise SystemExit("[ERR] bullet cluster summary missing")
    fig = ROOT / "figures" / "bullet_cluster_ed.png"
    if not fig.exists():
        raise SystemExit("[ERR] bullet cluster figure missing")
    print("[OK] Bullet Cluster artefact/figure present.")
