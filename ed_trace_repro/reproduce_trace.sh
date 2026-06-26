#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

EXPECTED_SHA="e1c4b9d8495a563be31c36ceeeea7575b1d46afae74b45394edb77a8ffb06725"
TRACE_REL="data/internal/holo_physics_trace_ed_industrial.json"
RUNNER_REL="kernel/rust/holo_kerneld"
EXPECTED_FILE="$SCRIPT_DIR/EXPECTED_SHA256"
IC_FILE="$SCRIPT_DIR/canonical_ic.json"

if [[ ! -f "$EXPECTED_FILE" ]]; then
  echo "[ERR] Missing expected hash file: $EXPECTED_FILE" >&2
  exit 2
fi

if [[ ! -f "$IC_FILE" ]]; then
  echo "[ERR] Missing canonical IC file: $IC_FILE" >&2
  exit 2
fi

RECORDED_SHA="$(awk '{print $1}' "$EXPECTED_FILE")"
if [[ "$RECORDED_SHA" != "$EXPECTED_SHA" ]]; then
  echo "[ERR] EXPECTED_SHA256 does not match the script constant" >&2
  echo "[ERR] EXPECTED_SHA256: $RECORDED_SHA" >&2
  echo "[ERR] Script:          $EXPECTED_SHA" >&2
  exit 1
fi

python3 - "$IC_FILE" <<'PY'
import json
import math
import sys

path = sys.argv[1]
expected = {
    "phi_0": 0.001,
    "dphi_0": -0.00027,
    "A_0": -0.03,
    "dA_0": -0.9999999390187482,
}
data = json.load(open(path, "r", encoding="utf-8"))
if set(data) != set(expected):
    raise SystemExit(f"[ERR] canonical_ic.json keys mismatch: {sorted(data)}")
for key, value in expected.items():
    if not math.isclose(float(data[key]), value, rel_tol=0.0, abs_tol=1e-15):
        raise SystemExit(f"[ERR] canonical_ic.json {key} mismatch: {data[key]} != {value}")
print("[OK] Canonical IC file is present and matches the recorded values.")
PY

if [[ -z "${ED_SOLVER_REPO:-}" ]]; then
  echo "[OK] Public reproduction metadata is self-consistent."
  echo "[INFO] Expected trace SHA256: $EXPECTED_SHA"
  echo "[INFO] To run an external solver checkout, set ED_SOLVER_REPO=/path/to/solver."
  exit 0
fi

if [[ ! -d "$ED_SOLVER_REPO/.git" ]]; then
  echo "[ERR] ED_SOLVER_REPO is not a git repository: $ED_SOLVER_REPO" >&2
  exit 2
fi

SOURCE_REV="${ED_SOLVER_REV:-HEAD}"
if ! git -C "$ED_SOLVER_REPO" cat-file -e "$SOURCE_REV^{commit}" 2>/dev/null; then
  echo "[ERR] ED_SOLVER_REV not found in ED_SOLVER_REPO: $SOURCE_REV" >&2
  exit 2
fi

TMP_DIR="$(mktemp -d /tmp/holo_ed_trace_repro.XXXXXX)"
WT="$TMP_DIR/solver_wt"
cleanup() {
  git -C "$ED_SOLVER_REPO" worktree remove --force "$WT" >/dev/null 2>&1 || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "[INFO] External solver repo: $ED_SOLVER_REPO"
echo "[INFO] External solver rev:  $SOURCE_REV"

git -C "$ED_SOLVER_REPO" worktree add --detach "$WT" "$SOURCE_REV" >/dev/null

if [[ ! -d "$WT/$RUNNER_REL" ]]; then
  echo "[ERR] External solver checkout does not contain expected runner path: $RUNNER_REL" >&2
  exit 2
fi

pushd "$WT/$RUNNER_REL" >/dev/null
cargo run --bin ed_runner --quiet -- --ic-file "$IC_FILE"
popd >/dev/null

TRACE="$WT/$TRACE_REL"
if [[ ! -f "$TRACE" ]]; then
  echo "[ERR] Expected trace was not produced: $TRACE" >&2
  exit 1
fi

ACTUAL_SHA="$(sha256sum "$TRACE" | awk '{print $1}')"

echo "[INFO] Expected SHA256: $EXPECTED_SHA"
echo "[INFO] Actual SHA256:   $ACTUAL_SHA"

if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  echo "[ERR] Trace hash mismatch" >&2
  exit 1
fi

echo "[OK] ED trace reproduced exactly."
