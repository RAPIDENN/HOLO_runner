#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run verification checks")
    ap.add_argument("--sparc-dir", help="Path to SPARC sparc_175 folder")
    ap.add_argument(
        "--mode",
        choices=["current", "preprint"],
        default="current",
        help="Which SPARC artefact to verify against (default: current)",
    )
    args = ap.parse_args()

    sparc_artefact = {
        "current": ROOT / "data" / "internal" / "sparc_p5_current.json",
        "preprint": ROOT / "data" / "internal" / "sparc_p5_preprint_frozen.json",
    }[args.mode]

    print("Reproducibility (verification only)")
    if args.sparc_dir:
        subprocess.check_call([
            sys.executable,
            "tools/verify_sparc_metrics.py",
            "--sparc-dir", args.sparc_dir,
            "--artefact", str(sparc_artefact),
        ])
    subprocess.check_call([sys.executable, "tools/verify_lock5_ricci.py"])
    subprocess.check_call([sys.executable, "tools/verify_cosmo_summary.py"])
    subprocess.check_call([sys.executable, "tools/verify_bullet_cluster.py"])
    print("All checks passed")
