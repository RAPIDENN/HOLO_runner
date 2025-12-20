#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run verification checks")
    ap.add_argument("--sparc-dir", help="Path to SPARC sparc_175 folder")
    args = ap.parse_args()

    print("Reproducibility (verification only)")
    if args.sparc_dir:
        subprocess.check_call([sys.executable, "tools/verify_sparc_metrics.py", "--sparc-dir", args.sparc_dir])
    subprocess.check_call([sys.executable, "tools/verify_lock5_ricci.py"])
    subprocess.check_call([sys.executable, "tools/verify_cosmo_summary.py"])
    subprocess.check_call([sys.executable, "tools/verify_bullet_cluster.py"])
    print("All checks passed")
