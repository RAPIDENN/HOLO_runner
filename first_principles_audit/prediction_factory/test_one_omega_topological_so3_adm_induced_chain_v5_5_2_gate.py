#!/usr/bin/env python3
"""Adversarial tests for the additive v5.5.2 induced ADM-chain gate."""

from __future__ import annotations

import inspect
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

if __package__:
    from . import derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate as gate
else:
    import derive_one_omega_topological_so3_adm_induced_chain_v5_5_2_gate as gate


def _write_mutated_v5_2(tmp_path: Path, payload: dict[str, object]) -> tuple[Path, str]:
    path = tmp_path / "mutated-v5-2.json"
    raw = (json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def test_v5_2_source_hash_is_pinned(tmp_path: Path) -> None:
    changed = tmp_path / "changed-v5-2.json"
    changed.write_bytes(gate.V5_2_PATH.read_bytes() + b" \n")
    with pytest.raises(gate.ADMChainV552Error, match="byte hash mismatch"):
        gate._load_v5_2(changed)


def test_v5_2_loaded_coefficient_mutation_is_rejected(tmp_path: Path) -> None:
    payload = json.loads(gate.V5_2_PATH.read_text(encoding="utf-8"))
    payload["exact_classical_charter"]["coefficient_policy"]["parameters"][
        "material_Z5_per_side"
    ] = 1.125
    path, digest = _write_mutated_v5_2(tmp_path, payload)
    with pytest.raises(gate.ADMChainV552Error, match="coefficient contract mismatch"):
        gate._load_v5_2(path, digest)


def test_v5_2_literal_action_mutation_is_rejected(tmp_path: Path) -> None:
    payload = json.loads(gate.V5_2_PATH.read_text(encoding="utf-8"))
    payload["exact_classical_charter"]["exact_action"]["Robin_intrinsic"] += " [MUTANT]"
    path, digest = _write_mutated_v5_2(tmp_path, payload)
    with pytest.raises(gate.ADMChainV552Error, match="literal action contract mismatch"):
        gate._load_v5_2(path, digest)


def test_selected_action_reads_loaded_v5_2_coefficients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = gate.sample_jet()
    baseline = gate.action_adm(
        data["N"], data["beta"], data["h"], data["Omega"], data["psi"], data
    )
    monkeypatch.setitem(gate.V5_2_COEFF, "brane_beta", 2.25)
    changed = gate.action_adm(
        data["N"], data["beta"], data["h"], data["Omega"], data["psi"], data
    )
    assert abs(changed - baseline) > 1.0e-3


def test_literal_coordinates_are_explicit_and_BF_b_is_not_shift_b() -> None:
    coordinates = gate.formula_ledger()["literal_variational_coordinates"]
    assert coordinates == {
        "n": "n=δN/N",
        "b_shift": "b_shift^i=δβ^i",
        "q": "q_ij=δh_ij",
        "omega": "omega=δOmegaSigma",
        "v": "v_i=δpsi_i",
        "BF_trace_not_shift": "b_BF=iota^*B; b_BF is not b_shift",
        "primary_matter_coordinate": "psi_i fixed independently of h_ij",
    }
    assert gate.SLOT_NAMES == (
        "n", "b_shift^1", "b_shift^2", "b_shift^3", "q_11",
        "q_12", "q_13", "q_22", "q_23", "q_33",
    )


def test_gamma_is_one_induced_metric_and_ADM_Jacobian_is_bidirectional_rank_ten() -> None:
    row = gate.jacobian_certificate()
    assert row["gamma_equals_Y_star_g_realized_at_reference_embedding"] is True
    assert row["induced_reference_metric_error"] < 2.0e-15
    assert row["Jacobian_shape"] == [10, 10]
    assert row["Jacobian_rank"] == 10
    assert abs(row["Jacobian_determinant"]) > 1.0e-2
    assert row["ADM_recomposition_error"] < 2.0e-14
    assert row["analytic_inverse_max_error"] < 2.0e-14
    assert row["linear_solve_inverse_max_error"] < 2.0e-13
    assert row["nonzero_beta_norm"] > 0.1
    assert row["off_diagonal_h_norm"] > 0.1


@pytest.mark.parametrize("mutant", ["lapse_sign", "omit_q_beta", "independent_metrics"])
def test_Jacobian_mutants_cannot_pass_as_induced_ADM_coordinates(mutant: str) -> None:
    row = gate.jacobian_certificate(mutant)
    assert row["linear_solve_inverse_max_error"] > 1.0e-3


def test_one_action_has_independent_ADM_and_covariant_gamma_derivative_routes() -> None:
    row = gate.action_chain_certificate()
    assert row["action_representation_error"] < 2.0e-13
    assert row["ADM_vs_gamma_chain_max_error"] < 2.0e-8
    assert row["random_direction_pairing_max_error"] < 2.0e-8
    assert row["projection_formula_max_error"] < 2.0e-8
    assert row["minimum_absolute_ADM_slot_derivative"] > 1.0e-4
    assert np.linalg.norm(row["E_shift"]) > 1.0e-3
    # Route independence is structural: the covariant implementation may
    # decompose gamma for h-dependent Robin data, but it may not call ADM action.
    assert "action_adm(" not in inspect.getsource(gate.action_gamma)
    assert "gamma_inverse" in inspect.getsource(gate.action_gamma)
    assert "p_u" in inspect.getsource(gate.action_adm)


@pytest.mark.parametrize(
    "mutant",
    ["gamma_overall_sign", "omit_shift_slot", "independent_metrics", "off_diagonal_double_count"],
)
def test_action_chain_mutants_break_the_off_shell_identity(mutant: str) -> None:
    row = gate.action_chain_certificate(mutant)
    assert max(
        row["ADM_vs_gamma_chain_max_error"], row["random_direction_pairing_max_error"]
    ) > 1.0e-3


def test_covariant_matter_momentum_is_visible_in_shift_equation() -> None:
    row = gate.matter_shift_certificate()
    assert row["p_u_norm"] > 0.1
    assert row["spatial_gradient_min_norm"] > 0.1
    assert row["T_ui_norm"] > 1.0e-3
    assert row["matter_shift_error"] < 2.0e-9
    assert np.linalg.norm(row["numerical_E_shift_matter"]) > 1.0e-3


@pytest.mark.parametrize("mutant", ["flip_momentum_sign", "omit_matter_current"])
def test_matter_shift_sign_and_omission_mutants_are_detected(mutant: str) -> None:
    assert gate.matter_shift_certificate(mutant)["matter_shift_error"] > 1.0e-3


def test_wall_and_Robin_have_no_direct_shift_but_fake_current_is_detected() -> None:
    nominal = gate.matter_shift_certificate()
    fake = gate.matter_shift_certificate("fake_Robin_shift_current")
    assert nominal["wall_Robin_direct_shift_norm"] < 2.0e-10
    assert nominal["fake_Robin_shift_current_witness"] > 1.0e-3
    assert fake["wall_Robin_direct_shift_norm"] > 1.0e-3


def test_psi_primary_coordinate_resolves_varphi_chain_and_Robin_combination() -> None:
    row = gate.psi_varphi_chain_certificate()
    assert row["primary_coordinate"] == "psi_i"
    assert row["fixed_varphi_minus_fixed_psi_metric_error"] < 2.0e-9
    assert row["coordinate_cross_term_norm"] > 1.0e-4
    assert row["Robin_surface_coefficient_match_error"] < 2.0e-9
    assert row["full_Robin_on_shell_coefficient_norm"] < 1.0e-14
    assert row["on_shell_coordinate_cross_norm"] < 1.0e-14
    assert row["off_shell_coordinate_cross_norm"] > 1.0e-4


@pytest.mark.parametrize("mutant", ["omit_coordinate_term", "flip_coordinate_term"])
def test_psi_varphi_cross_term_mutants_fail_numerically(mutant: str) -> None:
    assert gate.psi_varphi_chain_certificate(mutant)[
        "fixed_varphi_minus_fixed_psi_metric_error"
    ] > 1.0e-3


def test_one_Israel_Brown_York_tensor_is_uniquely_reconstructed() -> None:
    row = gate.israel_reconstruction_certificate()
    assert row["Brown_York_convention"] == "pi^mn=Theta^mn-Theta gamma^mn"
    assert row["junction_convention"] == "I^mn=M pi^mn-tau^mn"
    assert row["Jacobian_rank_used_for_uniqueness"] == 10
    assert row["junction_tensor_norm"] > 1.0e-3
    assert row["projection_reconstruction_error"] < 2.0e-12
    assert row["Brown_York_wrong_sign_witness"] > 1.0e-3


@pytest.mark.parametrize(
    "mutant",
    [
        "flip_tensor_sign", "omit_lapse_slot", "omit_shift_slot",
        "omit_spatial_slot", "Brown_York_sign", "independent_Jacobian",
    ],
)
def test_Israel_sign_and_missing_projection_mutants_fail(mutant: str) -> None:
    assert gate.israel_reconstruction_certificate(mutant)[
        "projection_reconstruction_error"
    ] > 1.0e-3


def test_induced_embedding_executes_all_H_terms_and_metric_normal_equation() -> None:
    row = gate.bending_certificate()
    assert row["ambient_dimension"] == 5
    assert row["H_formula"] == "H=Y^*δg+2D_(mu xi_parallel_nu)+2 f_bend Theta_mn"
    assert row["H_formula_max_error"] < 2.0e-10
    assert row["Y_star_delta_g_norm"] > 1.0e-3
    assert row["tangential_transport_norm"] > 1.0e-3
    assert row["normal_bending_norm"] > 1.0e-3
    assert row["H_to_ADM_to_H_error"] < 1.0e-10
    assert row["recovered_b_shift_norm"] > 1.0e-3
    assert row["metric_normal_residual_absolute_value"] > 1.0e-4
    assert row["metric_Green_normal_error"] < 2.0e-14
    assert row["selected_trace_augmented_Green_error"] < 2.0e-14
    assert row["complete_v5_2_all_field_normal_embedding_claimed"] is False
    assert "two-sided bulk normal momenta" in row["missing_for_complete_normal"]


@pytest.mark.parametrize(
    "mutant",
    [
        "omit_Y_star_delta_g", "omit_tangential_transport", "omit_normal_bending",
        "flip_normal_sign", "normal_equation_sign",
    ],
)
def test_bending_and_normal_equation_mutants_fail(mutant: str) -> None:
    row = gate.bending_certificate(mutant)
    assert max(row["H_formula_max_error"], row["metric_Green_normal_error"]) > 1.0e-3


def test_formula_oracle_is_digest_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    assert gate._canonical_sha256(gate.formula_ledger()) == gate.EXPECTED_FORMULA_LEDGER_SHA256
    original = gate.formula_ledger

    def changed() -> dict[str, object]:
        value = json.loads(json.dumps(original(), ensure_ascii=False))
        value["stress_and_junction"]["Brown_York"] += " [SIGN MUTANT]"
        return value

    monkeypatch.setattr(gate, "formula_ledger", changed)
    with pytest.raises(gate.ADMChainV552Error, match="formula ledger digest mismatch"):
        gate.build_payload()


def test_mutation_suite_is_active_not_zero_on_shell() -> None:
    witnesses = gate._mutation_witnesses()
    assert len(witnesses) >= 25
    assert min(witnesses.values()) > 1.0e-5
    for required in (
        "nominal_shift_activity",
        "nominal_matter_T_ui_activity",
        "nominal_coordinate_cross_activity",
        "nominal_junction_activity",
        "nominal_normal_equation_activity",
    ):
        assert witnesses[required] > 1.0e-4


def test_build_is_fail_closed_and_uses_no_frozen_gate_helper() -> None:
    payload = gate.build_payload()
    assert payload["frozen_gate_helpers_imported"] == []
    assert payload["decision"]["candidate_checks_pass"] is True
    for key in gate.FAIL_CLOSED_KEYS:
        assert payload["decision"][key] is False
    true_pass_keys = {
        key
        for key, value in payload["decision"].items()
        if key.endswith("_pass") and value is True
    }
    assert true_pass_keys == gate.ALLOWED_TRUE_PASS_KEYS
    source = Path(gate.__file__).read_text(encoding="utf-8")
    assert "import derive_one_omega_topological_so3_green_identity_v5_5" not in source
    assert "import derive_one_omega_topological_so3_restricted_c1_n1_v5_6" not in source


def test_artifact_is_canonical_deterministic_and_provenance_bound() -> None:
    stored_bytes = gate.OUTPUT.read_bytes()
    stored = json.loads(stored_bytes)
    fresh = gate.build_payload()
    expected_bytes = (
        json.dumps(
            fresh,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert stored_bytes == expected_bytes
    assert stored == fresh
    assert stored["provenance"]["generator_sha256"] == gate._sha256(Path(gate.__file__))
    assert stored["provenance"]["test_sha256"] == gate._sha256(Path(__file__))


def test_generator_cli_reproduces_the_same_artifact_bytes() -> None:
    before = gate.OUTPUT.read_bytes()
    completed = subprocess.run(
        [sys.executable, str(Path(gate.__file__))],
        cwd=gate.HERE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert gate.OUTPUT.read_bytes() == before
