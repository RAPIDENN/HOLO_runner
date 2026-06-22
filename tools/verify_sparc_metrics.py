#!/usr/bin/env python3
import argparse
import json
import math
from csv import reader as csv_reader
from pathlib import Path
from typing import List, Tuple
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load_rotmod(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    v_obs: List[float] = []
    v_bary: List[float] = []
    with path.open() as f:
        rdr = csv_reader(f)
        next(rdr, None)
        for row in rdr:
            if len(row) < 6:
                continue
            try:
                vobs = float(row[1])
                vgas = float(row[3])
                vdisk = float(row[4])
                vbul = float(row[5])
            except ValueError:
                continue
            vb = math.sqrt(vgas * vgas + vdisk * vdisk + vbul * vbul)
            v_obs.append(vobs)
            v_bary.append(vb)
    return np.array(v_bary, float), np.array(v_obs, float)


def chi2_proxy(v_model: np.ndarray, v_obs: np.ndarray) -> float:
    denom = np.square(v_obs) + 1.0
    num = np.square(v_model - v_obs)
    num = np.nan_to_num(num, nan=1e9, posinf=1e9, neginf=1e9)
    denom = np.nan_to_num(denom, nan=1e9, posinf=1e9, neginf=1e9)
    return float(np.sum(num / denom))


def verify_sparc(artefact: Path, sparc_dir: Path, tol: float = 0.05) -> bool:
    art = json.loads(artefact.read_text())
    galaxies = art.get("galaxies", [])
    if len(galaxies) != 175:
        print("[ERR] artefact galaxies != 175")
        return False

    mismatches = []
    for g in galaxies:
        name = g["name"]
        csv_path = sparc_dir / f"{name}_rotmod.csv"
        if not csv_path.exists():
            mismatches.append((name, "missing_csv"))
            continue
        vb, vo = load_rotmod(csv_path)
        calc = chi2_proxy(vb, vo)
        if abs(calc - float(g["chi2_newton"])) > tol:
            mismatches.append((name, f"chi2 mismatch {calc:.4g} vs {g['chi2_newton']:.4g}"))

    if mismatches:
        print("[ERR] SPARC verification mismatches:")
        for m in mismatches[:20]:
            print("  -", m[0], m[1])
        return False

    print("[OK] SPARC verification passed")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sparc-dir", required=True)
    ap.add_argument(
        "--artefact",
        type=Path,
        default=ROOT / "data" / "internal" / "sparc_p5_current.json",
        help="Path to SPARC artefact JSON (default: sparc_p5_current.json)",
    )
    ap.add_argument("--tol", type=float, default=0.05)
    args = ap.parse_args()
    if not verify_sparc(args.artefact, Path(args.sparc_dir), args.tol):
        raise SystemExit(1)
