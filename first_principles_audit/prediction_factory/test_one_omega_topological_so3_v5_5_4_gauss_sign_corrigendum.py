from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
ARTIFACT = HERE / "artifacts/one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("gauss_sign_corrigendum", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_corrigendum_is_deterministic_and_matches_artifact() -> None:
    module = _load_module()
    first = module.render_payload(module.build_payload())
    second = module.render_payload(module.build_payload())
    assert first == second
    assert first == ARTIFACT.read_bytes()


def test_exact_manufactured_geometries_fix_the_gauss_sign() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    flrw = payload["manufactured_witnesses"]["flat_FLRW"]
    sphere = payload["manufactured_witnesses"]["static_round_S3"]
    assert flrw["correct_intrinsic_R_leaf"] == {
        "decimal": 0.0,
        "denominator": 1,
        "numerator": 0,
    }
    assert flrw["v5_5_4_inherited_combination"]["numerator"] != 0
    assert sphere["correct_intrinsic_R_leaf"] == sphere["expected_round_S3_scalar"]
    assert all(flrw["checks"].values())
    assert all(sphere["checks"].values())


def test_old_receipts_are_quarantined_only_for_intrinsic_Rcal_role() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["decision"]["Gauss_sign_mismatch_reproduced"] is True
    assert payload["decision"]["v5_5_4_Ward_result_retracted"] is False
    assert payload["decision"]["v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"] is False
    assert payload["checks"]["v5_5_4_intrinsic_Rcal_binding_pass"] is False
    assert payload["checks"]["v5_5_4_eligible_as_intrinsic_Rcal_dependency_for_C1_N1"] is False


def test_promotion_keys_remain_fail_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for key in ("C1_ACTION_pass", "N1_ACTION_pass", "B4_pass", "B5_pass"):
        assert payload["checks"][key] is False
    assert payload["decision"]["C1_N1_promotion_authorized"] is False


def test_payload_self_hash_and_frozen_input_pins() -> None:
    module = _load_module()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    embedded = payload.pop("payload_sha256")
    assert hashlib.sha256(module._canonical_bytes(payload)).hexdigest() == embedded
    assert payload["checks"]["all_frozen_input_pins_verified"] is True
    assert all(
        len(record["sha256"]) == 64 for record in payload["source_pins"].values()
    )
