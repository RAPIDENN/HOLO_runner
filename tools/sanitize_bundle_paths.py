#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _basename(path: str) -> str:
    p = Path(path)
    return p.name if p.name else str(path)


def _sanitize_nist_comparison(obj: Dict[str, Any]) -> Dict[str, Any]:
    inputs = obj.get("inputs", {})
    if not isinstance(inputs, dict):
        return obj

    # Replace absolute machine paths with dataset-identifying relative names only.
    if isinstance(inputs.get("channel_path"), str):
        inputs["channel_path"] = _basename(inputs["channel_path"])
    if isinstance(inputs.get("tau_json"), str):
        inputs["tau_json"] = _basename(inputs["tau_json"])

    inv = inputs.get("nist_inventory_guess")
    if isinstance(inv, dict):
        if isinstance(inv.get("root"), str):
            # Keep dataset name only (no local absolute prefix).
            dataset = inputs.get("dataset")
            if isinstance(dataset, str) and dataset:
                inv["root"] = f"NIST/{dataset}"
            else:
                inv["root"] = "NIST"
        csv = inv.get("csv")
        if isinstance(csv, list):
            for row in csv:
                if isinstance(row, dict) and isinstance(row.get("path"), str):
                    row["path"] = _basename(row["path"])

    inputs["sanitized_paths"] = True
    obj["inputs"] = inputs
    return obj


def main() -> int:
    ap = argparse.ArgumentParser(description="Sanitize absolute local filesystem paths in HOLO_runner bundle JSON artifacts (no physics changes).")
    ap.add_argument(
        "--bundle",
        type=Path,
        default=Path("A_single_Einstein_Dilaton geometry"),
        help="Path to the verification bundle folder inside HOLO_runner.",
    )
    ap.add_argument(
        "--inplace",
        action="store_true",
        help="Rewrite the JSON files in-place (default).",
    )
    args = ap.parse_args()

    bundle = args.bundle
    targets = [
        bundle / "artifacts" / "nist_comparison_naive.json",
        bundle / "artifacts" / "nist_comparison_uv.json",
    ]
    for path in targets:
        if not path.exists():
            raise SystemExit(f"[ERR] Missing target JSON: {path}")
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise SystemExit(f"[ERR] Unexpected JSON type in {path}")
        obj2 = _sanitize_nist_comparison(obj)
        path.write_text(json.dumps(obj2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[OK] Sanitized: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

