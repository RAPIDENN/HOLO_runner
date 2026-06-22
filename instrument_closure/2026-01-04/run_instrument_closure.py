#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root_from_script(script_path: Path) -> Path:
    # instrument_closure/2026-01-04/run_instrument_closure.py -> HOLO_runner root
    return script_path.resolve().parent.parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_sha256_hex(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def verify_bundle(bundle_dir: Path, *, repo_root: Path) -> None:
    manifest_path = bundle_dir / "instrument_closure_manifest.json"
    manifest = load_json(manifest_path)
    files = manifest.get("files", [])
    if not files:
        raise RuntimeError("Manifest has no 'files' entries")

    mismatches = []
    for row in files:
        rel = row.get("path")
        expected = row.get("sha256")
        if not rel or not expected:
            mismatches.append((rel, expected, None))
            continue
        p = bundle_dir / rel
        if not p.exists():
            mismatches.append((rel, expected, None))
            continue
        got = sha256_file(p)
        if got != expected:
            mismatches.append((rel, expected, got))

    ext = manifest.get("external_channels", [])
    if ext is not None and ext != []:
        if not isinstance(ext, list):
            raise RuntimeError("Manifest 'external_channels' must be a list when present")

        # Optional cross-check: if nist_comparison_uv.json declares a nist_dataset DOI/hash,
        # ensure it matches the LAB_NIST_inputs external channel entry.
        nist_decl = None
        try:
            nist_obj = load_json(bundle_dir / "nist_comparison_uv.json")
            nist_decl = nist_obj.get("inputs", {}).get("nist_dataset")
        except Exception:
            nist_decl = None

        for row in ext:
            if not isinstance(row, dict):
                raise RuntimeError("Manifest 'external_channels' entries must be objects")
            name = row.get("name")

            # File-based external channel: verify sha256 against a file in the repo.
            if "path" in row:
                rel = row.get("path")
                expected = row.get("sha256")
                if not rel or not expected:
                    mismatches.append((f"external:{name}:{rel}", expected, None))
                    continue
                p = repo_root / rel
                if not p.exists():
                    mismatches.append((f"external:{name}:{rel}", expected, None))
                    continue
                got = sha256_file(p)
                if got != expected:
                    mismatches.append((f"external:{name}:{rel}", expected, got))
                continue

            # DOI-based external input pack: validate schema and (if available) cross-check nist_dataset in the lab report.
            if "doi" in row and "zip_sha256" in row:
                doi = row.get("doi")
                zip_sha = row.get("zip_sha256")
                if not isinstance(doi, str) or not doi:
                    raise RuntimeError(f"external_channels entry {name} missing valid doi")
                if not _is_sha256_hex(zip_sha):
                    raise RuntimeError(f"external_channels entry {name} has invalid zip_sha256")
                files_list = row.get("files")
                if not isinstance(files_list, list) or not files_list:
                    raise RuntimeError(f"external_channels entry {name} missing non-empty files list")
                for frow in files_list:
                    if not isinstance(frow, dict) or not isinstance(frow.get("name"), str) or not _is_sha256_hex(frow.get("sha256", "")):
                        raise RuntimeError(f"external_channels entry {name} has invalid files schema")

                if isinstance(nist_decl, dict) and name == "LAB_NIST_inputs":
                    if nist_decl.get("doi") != doi:
                        raise RuntimeError("nist_comparison_uv.json inputs.nist_dataset.doi does not match manifest LAB_NIST_inputs doi")
                    if nist_decl.get("zip_sha256") != zip_sha:
                        raise RuntimeError("nist_comparison_uv.json inputs.nist_dataset.zip_sha256 does not match manifest LAB_NIST_inputs zip_sha256")
                continue

            raise RuntimeError(f"external_channels entry {name} must specify either (path,sha256) or (doi,zip_sha256,files)")

    if mismatches:
        msg = ["Bundle verification failed (sha256 mismatches):"]
        for rel, expected, got in mismatches:
            msg.append(f"- {rel}: expected={expected} got={got}")
        raise RuntimeError("\n".join(msg))


def run_holo_runner_verification(repo_root: Path, sparc_dir: str) -> str:
    cmd = ["python3", "run_repro.py", "--sparc-dir", sparc_dir]
    p = subprocess.run(
        cmd,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"HOLO_runner verification failed ({p.returncode}).\n{p.stdout}")
    return p.stdout


def hkcore_refine(bundle_dir: Path, hkcore_url: str, token: str) -> dict:
    cfg = load_json(bundle_dir / "hkcore_refine_beta2.0_seed777.json").get("config")
    if not isinstance(cfg, dict):
        raise RuntimeError("hkcore_refine_beta2.0_seed777.json missing 'config'")

    out = subprocess.check_output(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            hkcore_url,
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(cfg),
        ],
        text=True,
    )
    return json.loads(out)


def main() -> int:
    script_path = Path(__file__)
    bundle_dir = script_path.resolve().parent
    repo_root = repo_root_from_script(script_path)

    p = argparse.ArgumentParser()
    p.add_argument("--sparc-dir", help="Path to SPARC 'sparc_175' CSV folder (public dataset)")
    p.add_argument("--run-hkcore", action="store_true", help="Re-run HK-core /mill/refine and print verdict summary")
    p.add_argument("--hkcore-url", default="http://127.0.0.1:8080/mill/refine")
    p.add_argument("--hkcore-token", default="devtoken")
    args = p.parse_args()

    verify_bundle(bundle_dir, repo_root=repo_root)
    print("OK: instrument_closure bundle sha256 verified")

    if args.sparc_dir:
        out = run_holo_runner_verification(repo_root, args.sparc_dir)
        # Keep output compact and avoid printing local paths.
        lines = [ln for ln in out.splitlines() if ln.strip()]
        print("OK: HOLO_runner verification passed")
        print("Summary:", lines[-1] if lines else "passed")

    if args.run_hkcore:
        res = hkcore_refine(bundle_dir, args.hkcore_url, args.hkcore_token)
        fv = res.get("result", {}).get("final_verdict", {})
        status = fv.get("status")
        rule = fv.get("rule_applied")
        print("HK-core refine:", {"status": status, "rule_applied": rule})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
