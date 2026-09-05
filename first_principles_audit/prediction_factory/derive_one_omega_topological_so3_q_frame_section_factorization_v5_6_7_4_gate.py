#!/usr/bin/env python3
"""Finite q=0 section and twenty-route factorization gate (v5.6.7.4).

This gate closes one deliberately narrow obligation.  For the byte-pinned
v5.6.7.1 finite full-T4 decoder/action, it chooses the coordinate-adapted
section ``Q_frame.q = 0`` in both the primal free vector and its JVP tangent
*before* either vector reaches a decoder, a free-data numerical guard, or
``so3_exp``.  It then binds that section to the actual twelve bulk, two GHY,
and six shared-interface action routes.

This is not a claim that Q_frame lies in the kernel of the full decoder.  The
exact counterexample at q=0 is

    d/dt|0 exp(t e3) e1 = e3 x e1 = e2 != 0.

The factorization instead uses three exact cancellations in the consumed
fields: the lateral associated field, the lateral affine connection, and the
shared solder contraction.  The section is an implementation-chosen chart
section, not an intrinsic physical gauge.  Finite spectral gauge parameters
also fail to form a group already at N=2 under BCH, and the infinitesimal
orbit rank is not globally constant.  Consequently no global smooth quotient,
continuum action, uniform-in-N bridge, margin, C1/N1, P4, B4, or B5 claim is
made.  No artifact is written.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
SCHEMA = (
    "holo.one-omega-topological-so3-q-frame-section-factorization-"
    "v5-6-7-4.v1"
)

V5671_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
)
V5671_TEST = (
    HERE
    / "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
)
V5671_SOURCE_SHA256 = (
    "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9"
)
V5671_TEST_SHA256 = (
    "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694"
)
V567_EXACT_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
)
V567_EXACT_SOURCE_SHA256 = (
    "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25"
)

V56616_SOURCE = (
    HERE / "derive_one_omega_topological_so3_free_data_family_gauge_kernel_v5_6_6_16.py"
)
V56616_SOURCE_SHA256 = (
    "d199139a1ae0e67c1c1b4dca6d71e6eef4c302369045462c3076b7f726250515"
)
V5668_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_restricted_class_euler_green_identity_v5_6_6_8.py"
)
V5668_SOURCE_SHA256 = (
    "a8b26f130189dacfef14faf9cb9e1d1f19208cb645e267f198fc2f21ede428e4"
)

EXPECTED_SIDES = ("plus", "minus")
EXPECTED_BULK_SECTORS = (
    "EH",
    "Omega_kinetic",
    "Omega_potential",
    "P_kinetic",
    "full_V4",
    "BF",
)
EXPECTED_INTERFACE_SECTORS = (
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)
EXPECTED_COMPONENTS = tuple(
    name
    for side in EXPECTED_SIDES
    for name in tuple(
        f"{sector}_bulk_{side}" for sector in EXPECTED_BULK_SECTORS
    )
    + (f"GHY_{side}",)
) + EXPECTED_INTERFACE_SECTORS

# These expectations are deliberately literal and independent of the two
# report producers ``exact_invariant_identity_ledger`` and
# ``_expected_real_routes``.  The validators below never call either producer.
EXPECTED_IDENTITY_NORMAL_FORMS_LITERAL = {
    "lateral_associated_field": (("1", ("R0_inv", "phi0")),),
    "lateral_affine_connection": (
        ("1", ("R0_inv", "A0", "R0")),
        ("1", ("R0_inv", "dR0")),
    ),
    "shared_solder_contraction": (("1", ("E0", "phi0")),),
}
EXPECTED_IDENTITY_STATEMENTS_LITERAL = {
    "lateral_associated_field": "(S R0)^-1 (S phi0) = R0^-1 phi0",
    "lateral_affine_connection": (
        "(S R0)^-1 (S A0 S^-1-dS S^-1)(S R0) + "
        "(S R0)^-1 d(S R0) = R0^-1 A0 R0 + R0^-1 dR0"
    ),
    "shared_solder_contraction": "(E0 S^-1)(S phi0) = E0 phi0",
}
EXPECTED_IDENTITY_LEDGER_SHA256 = (
    "f4f6f4b98a89eaf73787d2edee41a6f9c23d083811c2e016e7a1cb1e336a7a50"
)
EXPECTED_FULL_PHI_KERNEL_COUNTEREXAMPLE_SHA256 = (
    "1d91ef3e38508e2dafc0ad3a8cb5e99f7cef53ea3c833923857e62bb687391a5"
)
EXPECTED_BCH_INPUTS_LITERAL = {
    "q": {
        "coefficient": "1",
        "basis_function": {"kind": "cos", "wavevector": [1, 1, 0, 0]},
        "generator": [1, 0, 0],
    },
    "lambda": {
        "coefficient": "1",
        "basis_function": {"kind": "cos", "wavevector": [1, 1, 0, 0]},
        "generator": [0, 1, 0],
    },
}
EXPECTED_ZERO_ORBIT_PAIR_LITERAL = {"phi": [0, 0, 0], "A": [0, 0, 0]}
EXPECTED_GENERIC_ORBIT_PAIR_LITERAL = {"phi": [1, 0, 0], "A": [0, 1, 0]}
EXPECTED_FINITE_BCH_AND_RANK_NO_GO_SHA256 = (
    "d93833a37a9b9960a97a7db46d3d73c049628d382327ec6c097b6769627798ed"
)

EXPECTED_COMPONENT_TO_LEAF_LITERAL = (
    ("EH_bulk_plus", "_relative_bulk_densities_td3['EH']"),
    ("Omega_kinetic_bulk_plus", "_relative_bulk_densities_td3['Omega_kinetic']"),
    (
        "Omega_potential_bulk_plus",
        "_relative_bulk_densities_td3['Omega_potential']",
    ),
    ("P_kinetic_bulk_plus", "_relative_bulk_densities_td3['P_kinetic']"),
    ("full_V4_bulk_plus", "_relative_bulk_densities_td3['full_V4']"),
    ("BF_bulk_plus", "_relative_bulk_densities_td3['BF']"),
    ("GHY_plus", "_ghy_density_td3"),
    ("EH_bulk_minus", "_relative_bulk_densities_td3['EH']"),
    (
        "Omega_kinetic_bulk_minus",
        "_relative_bulk_densities_td3['Omega_kinetic']",
    ),
    (
        "Omega_potential_bulk_minus",
        "_relative_bulk_densities_td3['Omega_potential']",
    ),
    ("P_kinetic_bulk_minus", "_relative_bulk_densities_td3['P_kinetic']"),
    ("full_V4_bulk_minus", "_relative_bulk_densities_td3['full_V4']"),
    ("BF_bulk_minus", "_relative_bulk_densities_td3['BF']"),
    ("GHY_minus", "_ghy_density_td3"),
    ("wall", "_interface_component_densities_td3['wall']"),
    ("K_foliation", "_interface_component_densities_td3['K_foliation']"),
    ("R", "_interface_component_densities_td3['R']"),
    ("R_squared", "_interface_component_densities_td3['R_squared']"),
    ("a_squared", "_interface_component_densities_td3['a_squared']"),
    ("Robin", "_interface_component_densities_td3['Robin']"),
)
ROUTE_SIGNATURE_FIELDS = (
    "component",
    "class",
    "domain",
    "side",
    "producer",
    "target_leaf",
    "q_factor",
)
EXPECTED_ROUTE_SIGNATURES_SHA256 = (
    "2668665c6ab3959686e21e850d6cf4f0ecd401bc37f124d4b22e24966581288f"
)

TRUE_DECISION_KEYS = frozenset(
    {
        "byte_pinned_v5_6_7_1_and_exact_full_t4_source_contract_pass",
        "Q_frame_not_kernel_of_full_Phi_exact_e3_cross_e1_counterexample_pass",
        "three_consumed_q_invariant_identities_exact_pass",
        "twelve_bulk_two_GHY_six_interface_real_route_binding_pass",
        "q_zero_primal_and_tangent_canonicalized_before_decoder_and_so3_exp_pass",
        "finite_quadrature_values_and_JVP_factor_through_q_zero_section_pass",
        "r_plus_minus_preserved_and_nontrivial_witness_pass",
        "finite_N2_BCH_and_variable_rank_global_quotient_no_go_pass",
        "independent_in_memory_runtime_and_source_mutant_campaign_pass",
        "finite_Q_frame_q_zero_section_and_twenty_route_factorization_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "Q_frame_kernel_of_full_Phi_pass",
        "complete_DPhi_kernel_and_constant_rank_pass",
        "finite_spectral_Q_frame_coordinates_form_group_under_BCH_pass",
        "global_smooth_physical_gauge_quotient_manifold_pass",
        "Q_frame_q_zero_section_is_intrinsic_canonical_physical_gauge_pass",
        "r_plus_minus_quotiented_as_Q_frame_redundancy_pass",
        "all_N_action_factorization_pass",
        "continuum_action_representative_independence_theorem_pass",
        "finite_quadrature_remainder_certificate_pass",
        "quadrature_pass",
        "integrated_action_pass",
        "margins_certified_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "P4_full_same_action_pass",
        "B4_pass",
        "B5_pass",
    }
)

REQUIRED_MUTANT_IDS = frozenset(
    {
        "claim_Q_inside_kernel_DPhi_full",
        "associated_wrong_R_order",
        "affine_wrong_common_frame_sign",
        "affine_omit_dR_term",
        "solder_freeze_EQ",
        "leave_primal_q_for_decoder",
        "leave_tangent_q_for_decoder",
        "canonicalize_only_after_decode",
        "zero_only_one_q_scalar",
        "erase_r_plus_minus_with_q",
        "delete_one_real_component_route",
        "misclassify_GHY_as_bulk",
        "replace_Robin_solder_identity",
        "split_common_q_between_sides",
        "mutate_byte_pinned_upstream_source",
        "wrapper_passes_uncanonicalized_free",
        "wrapper_does_not_zero_tangent_q",
        "invariant_formulas_present_but_not_consumed",
        "rotate_only_one_of_EQ_or_varphi",
        "claim_N2_BCH_closure",
        "claim_global_constant_orbit_rank",
        "in_memory_flip_fail_closed_decision",
        "in_memory_change_identity_normal_form",
        "in_memory_remove_component_binding",
        "producer_monkeypatch_associated_wrong_both_forms_pass_true",
        "producer_monkeypatch_affine_wrong_both_forms_pass_true",
        "producer_monkeypatch_solder_wrong_both_forms_pass_true",
        "producer_monkeypatch_EH_leaf_to_P_kinetic",
        "producer_monkeypatch_Robin_leaf_to_wall",
        "producer_monkeypatch_routes_reordered_self_consistent",
        "producer_monkeypatch_kernel_nonzero_base_q_preserved_derivative",
        "producer_monkeypatch_kernel_wrong_phi_preserved_derivative",
        "producer_monkeypatch_kernel_wrong_delta_q_preserved_derivative",
        "producer_monkeypatch_BCH_zero_q_lambda_preserved_decomposition",
        "producer_monkeypatch_BCH_parallel_generators_preserved_decomposition",
        "producer_monkeypatch_BCH_wrong_wavevector_preserved_decomposition",
        "producer_monkeypatch_rank_generic_pair_zero_preserved_matrix",
        "producer_monkeypatch_rank_generic_pair_collinear_preserved_matrix",
        "producer_monkeypatch_rank_zero_pair_generic_preserved_matrix",
    }
)


class QFrameSectionGateError(RuntimeError):
    """Fail-closed gate error."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


@lru_cache(maxsize=1)
def _load_v5671() -> Any:
    """Load only the byte-pinned implementation target, never prior ledgers."""

    observed = _sha256(V5671_SOURCE)
    if observed != V5671_SOURCE_SHA256:
        raise QFrameSectionGateError(
            f"v5.6.7.1 source hash drift: expected {V5671_SOURCE_SHA256}, got {observed}"
        )
    specification = importlib.util.spec_from_file_location(
        "_holo_v5671_q_zero_target", V5671_SOURCE
    )
    if specification is None or specification.loader is None:
        raise QFrameSectionGateError("could not construct v5.6.7.1 import specification")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _numeric_vector_shape_only(
    name: str,
    values: Sequence[float],
    expected_size: int,
) -> np.ndarray:
    raw = np.asarray(values)
    if raw.ndim != 1 or raw.size != expected_size:
        raise QFrameSectionGateError(
            f"{name} must be a vector of length {expected_size}"
        )
    if raw.dtype.kind not in "iuf":
        raise QFrameSectionGateError(f"{name} must contain real numeric scalars")
    return np.asarray(raw, dtype=float).copy()


def _local_q_section_coordinates(N: int, K: int) -> tuple[int, int, int, int, int]:
    """Resolve only the pinned layout arithmetic needed to zero q.

    The exact-primitives layout has 27*N common coordinates before q, 3*N q
    coordinates, and two side blocks of N*(106+64*K) coordinates.  The result
    is checked against the byte-pinned generated contract only *after* q has
    been zeroed.
    """

    if isinstance(N, (bool, np.bool_)) or not isinstance(N, (int, np.integer)):
        raise QFrameSectionGateError("N must be an integer >= 1")
    if isinstance(K, (bool, np.bool_)) or not isinstance(K, (int, np.integer)):
        raise QFrameSectionGateError("K must be an integer >= 1")
    N_value = int(N)
    K_value = int(K)
    if N_value < 1 or K_value < 1:
        raise QFrameSectionGateError("N and K must be integers >= 1")
    q_start = 27 * N_value
    q_stop = 30 * N_value
    dimension = N_value * (242 + 128 * K_value)
    return N_value, K_value, dimension, q_start, q_stop


def canonicalize_q_zero_before_decode(
    free: Sequence[float],
    tangent: Sequence[float],
    N: int,
    K: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Copy both vectors and choose q=0 before any upstream data decoder.

    ``full_t4_decoder_contract`` supplies only the generated coordinate layout;
    it does not decode free data, invoke a free-data numerical guard, or call
    ``so3_exp``.  The returned arrays are the only arrays passed to the actual
    local or integrated action targets.
    """

    N_value, K_value, dimension, q_start, q_stop = _local_q_section_coordinates(N, K)
    canonical_free = _numeric_vector_shape_only("free", free, dimension)
    canonical_tangent = _numeric_vector_shape_only("tangent", tangent, dimension)
    free_before = canonical_free.copy()
    tangent_before = canonical_tangent.copy()
    canonical_free[q_start:q_stop] = 0.0
    canonical_tangent[q_start:q_stop] = 0.0
    # Even the finiteness checks occur after the section has been installed.
    # We still reject non-finite input coordinates (including the discarded q
    # representatives), but no invalid q value can reach an upstream guard.
    if not np.all(np.isfinite(free_before)):
        raise QFrameSectionGateError("free must contain only finite scalars")
    if not np.all(np.isfinite(tangent_before)):
        raise QFrameSectionGateError("tangent must contain only finite scalars")

    # No upstream hash guard, generated-contract guard, decoder, or SO(3)
    # operation occurs before the two assignments above.
    upstream = _load_v5671()
    contract = upstream.full_t4_decoder_contract(N_value, K_value)
    blocks = contract["free_layout"]["blocks"]
    if "Q_frame.q" not in blocks:
        raise QFrameSectionGateError("full-T4 layout has no Q_frame.q block")
    q_specification = blocks["Q_frame.q"]
    q_shape = [int(value) for value in q_specification["shape"]]
    generated_tuple = (
        int(contract["N"]),
        int(contract["K"]),
        int(contract["free_coordinate_dimension"]),
        int(q_specification["start"]),
        int(q_specification["stop"]),
    )
    if generated_tuple != (N_value, K_value, dimension, q_start, q_stop):
        raise QFrameSectionGateError("local pre-guard q coordinates disagree with pinned layout")
    if q_shape != [N_value, 3] or q_stop - q_start != 3 * N_value:
        raise QFrameSectionGateError("Q_frame.q block shape or extent drift")
    non_q_mask = np.ones(dimension, dtype=bool)
    non_q_mask[q_start:q_stop] = False
    if not np.array_equal(canonical_free[non_q_mask], free_before[non_q_mask]):
        raise QFrameSectionGateError("q section changed a non-q primal coordinate")
    if not np.array_equal(canonical_tangent[non_q_mask], tangent_before[non_q_mask]):
        raise QFrameSectionGateError("q section changed a non-q tangent coordinate")

    r_preserved = {}
    for side in EXPECTED_SIDES:
        name = f"{side}.r_E0"
        specification = blocks[name]
        start = int(specification["start"])
        stop = int(specification["stop"])
        r_preserved[side] = bool(
            np.array_equal(canonical_free[start:stop], free_before[start:stop])
            and np.array_equal(
                canonical_tangent[start:stop], tangent_before[start:stop]
            )
        )
    metadata = {
        "section": "coordinate-adapted Q_frame.q=0",
        "intrinsic_or_physical_canonical_gauge_claimed": False,
        "N": N_value,
        "K": K_value,
        "free_coordinate_dimension": dimension,
        "q_block": {
            "name": "Q_frame.q",
            "start": q_start,
            "stop": q_stop,
            "shape": q_shape,
            "primal_max_abs_before": float(
                np.max(np.abs(free_before[q_start:q_stop]), initial=0.0)
            ),
            "tangent_max_abs_before": float(
                np.max(np.abs(tangent_before[q_start:q_stop]), initial=0.0)
            ),
            "primal_exactly_zero_after": bool(
                np.array_equal(
                    canonical_free[q_start:q_stop], np.zeros(q_stop - q_start)
                )
            ),
            "tangent_exactly_zero_after": bool(
                np.array_equal(
                    canonical_tangent[q_start:q_stop], np.zeros(q_stop - q_start)
                )
            ),
        },
        "all_non_q_primal_coordinates_preserved_exactly": True,
        "all_non_q_tangent_coordinates_preserved_exactly": True,
        "r_plus_minus_preserved_exactly": r_preserved,
        "ordering": (
            "local pinned-layout arithmetic; copy/shape validation; zero primal q; "
            "zero tangent q; finiteness check; only then load/check v5.6.7.1 and "
            "call its local/integrated target"
        ),
    }
    return canonical_free, canonical_tangent, metadata


def q_zero_local_density_values_and_eta_jvps(
    free: Sequence[float],
    tangent: Sequence[float],
    N: int,
    K: int,
    x: Sequence[float],
    rho: float,
) -> dict[str, Any]:
    """Evaluate all twenty real local routes on the pre-decoder q=0 section."""

    canonical_free, canonical_tangent, section = canonicalize_q_zero_before_decode(
        free, tangent, N, K
    )
    upstream = _load_v5671()
    result = upstream.local_density_values_and_eta_jvps(
        canonical_free,
        canonical_tangent,
        N,
        K,
        x,
        rho,
    )
    return {**result, "q_zero_section": section}


def q_zero_integrated_action_values_and_eta_jvps(
    free: Sequence[float],
    tangent: Sequence[float],
    N: int,
    K: int,
    tangential_order_per_axis: int,
    radial_order: int,
) -> dict[str, Any]:
    """Evaluate the finite separated-domain rule on the pre-decoder section."""

    canonical_free, canonical_tangent, section = canonicalize_q_zero_before_decode(
        free, tangent, N, K
    )
    upstream = _load_v5671()
    result = upstream.integrated_action_values_and_eta_jvps(
        canonical_free,
        canonical_tangent,
        N,
        K,
        tangential_order_per_axis,
        radial_order,
    )
    return {**result, "q_zero_section": section}


Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


def _reduce_word(word: Word) -> Word:
    inverse_pairs = {
        ("S_inv", "S"),
        ("S", "S_inv"),
        ("R0_inv", "R0"),
        ("R0", "R0_inv"),
    }
    stack: list[str] = []
    for token in word:
        if stack and (stack[-1], token) in inverse_pairs:
            stack.pop()
        else:
            stack.append(token)
    return tuple(stack)


def _normal_form(terms: Sequence[tuple[Fraction, Word]]) -> Polynomial:
    result: Polynomial = {}
    for coefficient, word in terms:
        reduced = _reduce_word(word)
        result[reduced] = result.get(reduced, Fraction(0)) + coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _serial_polynomial(polynomial: Polynomial) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": str(coefficient),
            "word": list(word),
        }
        for word, coefficient in sorted(polynomial.items())
    ]


def exact_invariant_identity_ledger() -> dict[str, Any]:
    associated_left = _normal_form(
        [(Fraction(1), ("R0_inv", "S_inv", "S", "phi0"))]
    )
    associated_right = _normal_form(
        [(Fraction(1), ("R0_inv", "phi0"))]
    )
    affine_left = _normal_form(
        [
            (
                Fraction(1),
                ("R0_inv", "S_inv", "S", "A0", "S_inv", "S", "R0"),
            ),
            (
                Fraction(-1),
                ("R0_inv", "S_inv", "dS", "S_inv", "S", "R0"),
            ),
            (Fraction(1), ("R0_inv", "S_inv", "dS", "R0")),
            (Fraction(1), ("R0_inv", "S_inv", "S", "dR0")),
        ]
    )
    affine_right = _normal_form(
        [
            (Fraction(1), ("R0_inv", "A0", "R0")),
            (Fraction(1), ("R0_inv", "dR0")),
        ]
    )
    solder_left = _normal_form(
        [(Fraction(1), ("E0", "S_inv", "S", "phi0"))]
    )
    solder_right = _normal_form([(Fraction(1), ("E0", "phi0"))])
    identities = {
        "lateral_associated_field": {
            "statement": "(S R0)^-1 (S phi0) = R0^-1 phi0",
            "left_normal_form": _serial_polynomial(associated_left),
            "right_normal_form": _serial_polynomial(associated_right),
            "pass": associated_left == associated_right,
        },
        "lateral_affine_connection": {
            "statement": (
                "(S R0)^-1 (S A0 S^-1-dS S^-1)(S R0) + "
                "(S R0)^-1 d(S R0) = R0^-1 A0 R0 + R0^-1 dR0"
            ),
            "left_normal_form": _serial_polynomial(affine_left),
            "right_normal_form": _serial_polynomial(affine_right),
            "pass": affine_left == affine_right,
        },
        "shared_solder_contraction": {
            "statement": "(E0 S^-1)(S phi0) = E0 phi0",
            "left_normal_form": _serial_polynomial(solder_left),
            "right_normal_form": _serial_polynomial(solder_right),
            "pass": solder_left == solder_right,
        },
    }
    return {
        "algebra": "exact noncommutative free words with only inverse-pair reductions",
        "derivative_rule_used": "d(S R0)=dS R0+S dR0",
        "identities": identities,
        "pass": all(item["pass"] for item in identities.values()),
    }


def _identity_mutants() -> dict[str, bool]:
    expected_associated = _normal_form(
        [(Fraction(1), ("R0_inv", "phi0"))]
    )
    wrong_order = _normal_form(
        [(Fraction(1), ("S_inv", "R0_inv", "S", "phi0"))]
    )
    expected_affine = _normal_form(
        [
            (Fraction(1), ("R0_inv", "A0", "R0")),
            (Fraction(1), ("R0_inv", "dR0")),
        ]
    )
    wrong_sign = _normal_form(
        [
            (
                Fraction(1),
                ("R0_inv", "S_inv", "S", "A0", "S_inv", "S", "R0"),
            ),
            (Fraction(1), ("R0_inv", "S_inv", "dS", "S_inv", "S", "R0")),
            (Fraction(1), ("R0_inv", "S_inv", "dS", "R0")),
            (Fraction(1), ("R0_inv", "S_inv", "S", "dR0")),
        ]
    )
    omit_dr = _normal_form(
        [
            (
                Fraction(1),
                ("R0_inv", "S_inv", "S", "A0", "S_inv", "S", "R0"),
            ),
            (
                Fraction(-1),
                ("R0_inv", "S_inv", "dS", "S_inv", "S", "R0"),
            ),
        ]
    )
    expected_solder = _normal_form([(Fraction(1), ("E0", "phi0"))])
    frozen_solder = _normal_form([(Fraction(1), ("E0", "S", "phi0"))])
    return {
        "associated_wrong_R_order": wrong_order != expected_associated,
        "affine_wrong_common_frame_sign": wrong_sign != expected_affine,
        "affine_omit_dR_term": omit_dr != expected_affine,
        "solder_freeze_EQ": frozen_solder != expected_solder,
    }


def full_phi_kernel_counterexample() -> dict[str, Any]:
    e1 = (1, 0, 0)
    e3 = (0, 0, 1)
    cross = (
        e3[1] * e1[2] - e3[2] * e1[1],
        e3[2] * e1[0] - e3[0] * e1[2],
        e3[0] * e1[1] - e3[1] * e1[0],
    )
    return {
        "base_q": [0, 0, 0],
        "base_phi0": list(e1),
        "Q_frame_tangent_delta_q": list(e3),
        "D_varphi_at_q0_equals_delta_q_cross_phi0": list(cross),
        "expected_e2": [0, 1, 0],
        "nonzero": cross != (0, 0, 0),
        "conclusion": "Q_frame is not a subspace of ker D(Phi_full)",
        "pass": cross == (0, 1, 0),
    }


def _integer_cross(left: Sequence[int], right: Sequence[int]) -> tuple[int, int, int]:
    if len(left) != 3 or len(right) != 3:
        raise ValueError("cross product inputs must have exactly three entries")
    a = tuple(int(value) for value in left)
    b = tuple(int(value) for value in right)
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _kernel_counterexample_accepts(ledger: Mapping[str, Any]) -> bool:
    """Validate the base point and independently differentiate exp(q) phi0 at q=0."""

    try:
        base_q = tuple(int(value) for value in ledger["base_q"])
        phi0 = tuple(int(value) for value in ledger["base_phi0"])
        delta_q = tuple(int(value) for value in ledger["Q_frame_tangent_delta_q"])
        reported = tuple(
            int(value)
            for value in ledger["D_varphi_at_q0_equals_delta_q_cross_phi0"]
        )
        independently_derived = _integer_cross(delta_q, phi0)
        return bool(
            base_q == (0, 0, 0)
            and phi0 == (1, 0, 0)
            and delta_q == (0, 0, 1)
            and independently_derived == (0, 1, 0)
            and reported == independently_derived
            and ledger["expected_e2"] == [0, 1, 0]
            and ledger["nonzero"] is True
            and ledger["conclusion"]
            == "Q_frame is not a subspace of ker D(Phi_full)"
            and ledger["pass"] is True
            and _canonical_sha256(ledger)
            == EXPECTED_FULL_PHI_KERNEL_COUNTEREXAMPLE_SHA256
        )
    except (KeyError, TypeError, ValueError):
        return False


def _function_calls(tree: ast.AST, function_name: str) -> set[str]:
    node = next(
        (
            candidate
            for candidate in ast.walk(tree)
            if isinstance(candidate, (ast.FunctionDef, ast.AsyncFunctionDef))
            and candidate.name == function_name
        ),
        None,
    )
    if node is None:
        return set()
    calls = set()
    for candidate in ast.walk(node):
        if not isinstance(candidate, ast.Call):
            continue
        if isinstance(candidate.func, ast.Name):
            calls.add(candidate.func.id)
        elif isinstance(candidate.func, ast.Attribute):
            calls.add(candidate.func.attr)
    return calls


def _function_node(tree: ast.AST, function_name: str) -> ast.FunctionDef | None:
    return next(
        (
            candidate
            for candidate in ast.walk(tree)
            if isinstance(candidate, ast.FunctionDef) and candidate.name == function_name
        ),
        None,
    )


def _assignment_value(function: ast.FunctionDef | None, name: str) -> ast.AST | None:
    if function is None:
        return None
    for candidate in ast.walk(function):
        if not isinstance(candidate, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in candidate.targets):
            return candidate.value
    return None


def _expression_names(expression: ast.AST | None) -> set[str]:
    if expression is None:
        return set()
    return {
        candidate.id
        for candidate in ast.walk(expression)
        if isinstance(candidate, ast.Name)
    }


def _constant_subscript(expression: ast.AST | None) -> tuple[str, str] | None:
    if not isinstance(expression, ast.Subscript) or not isinstance(expression.value, ast.Name):
        return None
    if isinstance(expression.slice, ast.Constant) and isinstance(expression.slice.value, str):
        return expression.value.id, expression.slice.value
    return None


def _return_dictionary(function: ast.FunctionDef | None) -> dict[str, ast.AST]:
    if function is None:
        return {}
    returns = [candidate for candidate in ast.walk(function) if isinstance(candidate, ast.Return)]
    for candidate in returns:
        if not isinstance(candidate.value, ast.Dict):
            continue
        result: dict[str, ast.AST] = {}
        for key, value in zip(candidate.value.keys, candidate.value.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                result[key.value] = value
        if result:
            return result
    return {}


def _dependency_closure(
    expression: ast.AST,
    assignments: Mapping[str, ast.AST],
) -> set[str]:
    closure = set(_expression_names(expression))
    frontier = list(closure)
    while frontier:
        name = frontier.pop()
        assigned = assignments.get(name)
        if assigned is None:
            continue
        for dependency in _expression_names(assigned) - closure:
            closure.add(dependency)
            frontier.append(dependency)
    return closure


def _dictionary_assignment_value(
    function: ast.FunctionDef | None,
    container_name: str,
    key_name: str,
) -> ast.AST | None:
    if function is None:
        return None
    for candidate in ast.walk(function):
        if not isinstance(candidate, ast.Assign) or not isinstance(candidate.value, ast.Dict):
            continue
        if not any(
            isinstance(target, ast.Subscript)
            and isinstance(target.value, ast.Name)
            and target.value.id == container_name
            for target in candidate.targets
        ):
            continue
        for key, value in zip(candidate.value.keys, candidate.value.values):
            if isinstance(key, ast.Constant) and key.value == key_name:
                return value
    return None


def _upstream_dataflow_contract(tree: ast.AST) -> dict[str, bool]:
    decoder = _function_node(tree, "decode_common_first_boundary_td3")
    collar = _function_node(tree, "_collar_ambient_x64")
    primitive_decoder = _function_node(tree, "_x64_local_primitives")
    bulk_leaf = _function_node(tree, "_bulk_component_densities_td3")
    interface_leaf = _function_node(tree, "_interface_component_densities_td3")

    phi_source = _assignment_value(decoder, "phi_source")
    A_full = _assignment_value(decoder, "A_full")
    X64_trace = _assignment_value(decoder, "X64_trace")
    side_X64 = _dictionary_assignment_value(decoder, "sides", "X64_trace")
    trace = _assignment_value(collar, "trace")
    primitive_return = _return_dictionary(primitive_decoder)
    bulk_return = _return_dictionary(bulk_leaf)
    interface_return = _return_dictionary(interface_leaf)

    interface_assignments = {
        name: value
        for name in (
            "E_Q",
            "varphi_Q",
            "phi_H",
            "robin_vector",
            "robin_norm",
        )
        if (value := _assignment_value(interface_leaf, name)) is not None
    }
    phi_H = interface_assignments.get("phi_H")
    exact_solder_multiplication = False
    if phi_H is not None:
        for candidate in ast.walk(phi_H):
            if not isinstance(candidate, ast.BinOp) or not isinstance(candidate.op, ast.Mult):
                continue
            left_names = _expression_names(candidate.left)
            right_names = _expression_names(candidate.right)
            if (
                "E_Q" in left_names
                and "varphi_Q" in right_names
                or "varphi_Q" in left_names
                and "E_Q" in right_names
            ):
                exact_solder_multiplication = True
                break
    interface_q_sensitive = {
        name
        for name, expression in interface_return.items()
        if _dependency_closure(expression, interface_assignments)
        & {"E_Q", "varphi_Q", "phi_H"}
    }

    phi_names = _expression_names(phi_source)
    A_full_names = _expression_names(A_full)
    X64_names = _expression_names(X64_trace)
    return {
        "decoder_phi_source_is_reduced_R0_inverse_phi0": bool(
            {"R0_transpose", "varphi_e0"} <= phi_names
            and not ({"R_transpose", "varphi"} <= phi_names)
        ),
        "decoder_A_full_is_built_from_reduced_A_source": bool(
            "A_source_tuple" in A_full_names
            and "A_source_full_tuple" not in A_full_names
        ),
        "decoder_X64_trace_consumes_reduced_phi_and_A": bool(
            {"phi_source", "A_full"} <= X64_names
            and "phi_source_full" not in X64_names
            and "A_source_full_tuple" not in X64_names
        ),
        "side_payload_exports_that_exact_X64_trace": bool(
            isinstance(side_X64, ast.Name) and side_X64.id == "X64_trace"
        ),
        "collar_consumes_side_X64_trace": _constant_subscript(trace)
        == ("boundary_side", "X64_trace"),
        "X64_primitive_decoder_extracts_phi_channels_16_18": bool(
            "phi" in primitive_return
            and "value[16 + a]" in ast.unparse(primitive_return["phi"])
        ),
        "X64_primitive_decoder_extracts_A_channels_19_33": bool(
            "A" in primitive_return
            and "value[19 + 3 * axis + a]" in ast.unparse(primitive_return["A"])
        ),
        "six_bulk_leaves_are_actual_return_dictionary": set(bulk_return)
        == set(EXPECTED_BULK_SECTORS),
        "bulk_leaf_reads_decoded_phi": _constant_subscript(
            _assignment_value(bulk_leaf, "phi")
        )
        == ("primitives", "phi"),
        "bulk_leaf_reads_decoded_A": _constant_subscript(
            _assignment_value(bulk_leaf, "connection")
        )
        == ("primitives", "A"),
        "six_interface_leaves_are_actual_return_dictionary": set(interface_return)
        == set(EXPECTED_INTERFACE_SECTORS),
        "interface_EQ_reads_common_EQ": _constant_subscript(
            interface_assignments.get("E_Q")
        )
        == ("common", "E_Q"),
        "interface_varphi_reads_common_varphi": _constant_subscript(
            interface_assignments.get("varphi_Q")
        )
        == ("common", "varphi"),
        "interface_phi_H_multiplies_EQ_and_varphi_exactly": exact_solder_multiplication,
        "Robin_is_the_only_q_sensitive_interface_leaf": interface_q_sensitive
        == {"Robin"},
        "Robin_dependency_closure_reaches_phi_H": bool(
            "Robin" in interface_return
            and "phi_H"
            in _dependency_closure(interface_return["Robin"], interface_assignments)
        ),
    }


def _upstream_source_contract_from_text(text: str) -> dict[str, Any]:
    observed = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"observed_sha256": observed, "pass": False, "ast_parse_pass": False}
    required_fragments = {
        "q_exp": "S = so3_exp(q)",
        "associated_full": "phi_source_full = _matvec(R_transpose, varphi, zero)",
        "associated_reduced": "phi_source = _matvec(R0_transpose, varphi_e0, zero)",
        "affine_full": "A_source_full.append(",
        "affine_reduced": "A_source.append(",
        "solder_frame": "E_Q = _matmul(E0, S_transpose, zero)",
        "solder_product": "E_Q[mu][a] * varphi_Q[a]",
        "twenty_order_guard": "twenty local-density component order drift",
        "finite_total_after_integrals": "S_total_formed_only_after_twenty_domain_integrals",
    }
    fragments = {name: fragment in text for name, fragment in required_fragments.items()}
    call_contract = {
        "local_calls_decoder": "decode_common_first_boundary_td3"
        in _function_calls(tree, "_local_density_td3"),
        "local_calls_bulk": "_bulk_components_from_boundary_td3"
        in _function_calls(tree, "_local_density_td3"),
        "local_calls_boundary": "_boundary_components_from_boundary_td3"
        in _function_calls(tree, "_local_density_td3"),
        "bulk_calls_relative_leaf": "_relative_bulk_densities_td3"
        in _function_calls(tree, "_bulk_components_from_boundary_td3"),
        "boundary_calls_GHY_leaf": "_ghy_density_td3"
        in _function_calls(tree, "_boundary_components_from_boundary_td3"),
        "boundary_calls_interface_leaf": "_interface_component_densities_td3"
        in _function_calls(tree, "_boundary_components_from_boundary_td3"),
        "integrated_calls_decoder": "decode_common_first_boundary_td3"
        in _function_calls(tree, "integrated_action_values_and_eta_jvps"),
    }
    dataflow_contract = _upstream_dataflow_contract(tree)
    return {
        "observed_sha256": observed,
        "expected_sha256": V5671_SOURCE_SHA256,
        "ast_parse_pass": True,
        "required_fragments": fragments,
        "call_contract": call_contract,
        "AST_dataflow_contract": dataflow_contract,
        "pass": bool(
            observed == V5671_SOURCE_SHA256
            and all(fragments.values())
            and all(call_contract.values())
            and all(dataflow_contract.values())
        ),
    }


def source_pin_and_target_contract() -> dict[str, Any]:
    text = V5671_SOURCE.read_text(encoding="utf-8")
    contract = _upstream_source_contract_from_text(text)
    upstream = _load_v5671()
    constants_match = {
        "sides": tuple(upstream.SIDES) == EXPECTED_SIDES,
        "bulk_sectors": tuple(upstream.BULK_SECTORS) == EXPECTED_BULK_SECTORS,
        "interface_sectors": tuple(upstream.INTERFACE_SECTORS)
        == EXPECTED_INTERFACE_SECTORS,
        "components": tuple(upstream.LOCAL_DENSITY_COMPONENTS)
        == EXPECTED_COMPONENTS,
    }
    exact_hash = _sha256(V567_EXACT_SOURCE)
    test_hash = _sha256(V5671_TEST)
    return {
        "v5_6_7_1": contract,
        "v5_6_7_1_test": {
            "observed_sha256": test_hash,
            "expected_sha256": V5671_TEST_SHA256,
            "pass": test_hash == V5671_TEST_SHA256,
        },
        "v5_6_7_exact_full_t4_primitives": {
            "observed_sha256": exact_hash,
            "expected_sha256": V567_EXACT_SOURCE_SHA256,
            "pass": exact_hash == V567_EXACT_SOURCE_SHA256,
        },
        "independent_expected_constants_match_runtime_target": constants_match,
        "pass": bool(
            contract["pass"]
            and test_hash == V5671_TEST_SHA256
            and exact_hash == V567_EXACT_SOURCE_SHA256
            and all(constants_match.values())
        ),
    }


def _expected_real_routes() -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for side in EXPECTED_SIDES:
        for sector in EXPECTED_BULK_SECTORS:
            routes.append(
                {
                    "component": f"{sector}_bulk_{side}",
                    "class": "bulk",
                    "domain": "T4 x rho",
                    "side": side,
                    "producer": "_bulk_components_from_boundary_td3",
                    "target_leaf": f"_relative_bulk_densities_td3[{sector!r}]",
                    "q_factor": "lateral associated-field and affine-connection identities",
                }
            )
        routes.append(
            {
                "component": f"GHY_{side}",
                "class": "GHY",
                "domain": "T4 boundary",
                "side": side,
                "producer": "_boundary_components_from_boundary_td3",
                "target_leaf": "_ghy_density_td3",
                "q_factor": "pulled lateral trace after associated/affine cancellation",
            }
        )
    for sector in EXPECTED_INTERFACE_SECTORS:
        routes.append(
            {
                "component": sector,
                "class": "interface",
                "domain": "shared T4 boundary",
                "side": "shared",
                "producer": "_boundary_components_from_boundary_td3",
                "target_leaf": f"_interface_component_densities_td3[{sector!r}]",
                "q_factor": (
                    "shared solder contraction (E0 S^-1)(S phi0)=E0 phi0"
                    if sector == "Robin"
                    else "common gamma/T/log_Omega fields contain no q"
                ),
            }
        )
    return routes


def _routes_accept(routes: Sequence[Mapping[str, Any]]) -> bool:
    try:
        signatures = tuple(
            tuple(route[field] for field in ROUTE_SIGNATURE_FIELDS) for route in routes
        )
        component_to_leaf = tuple(
            (route["component"], route["target_leaf"]) for route in routes
        )
    except (KeyError, TypeError):
        return False
    return bool(
        component_to_leaf == EXPECTED_COMPONENT_TO_LEAF_LITERAL
        and _canonical_sha256(signatures) == EXPECTED_ROUTE_SIGNATURES_SHA256
        and tuple(signature[0] for signature in signatures) == EXPECTED_COMPONENTS
    )


def real_twenty_route_binding_ledger() -> dict[str, Any]:
    routes = _expected_real_routes()
    counts = {
        category: sum(route["class"] == category for route in routes)
        for category in ("bulk", "GHY", "interface")
    }
    upstream = _load_v5671()
    actual_names = tuple(upstream.LOCAL_DENSITY_COMPONENTS)
    return {
        "routes": routes,
        "ordered_component_names": [route["component"] for route in routes],
        "actual_runtime_component_names": list(actual_names),
        "counts": counts,
        "expected_counts": {"bulk": 12, "GHY": 2, "interface": 6},
        "all_twenty_distinct": len({route["component"] for route in routes}) == 20,
        "source_call_graph_bound": source_pin_and_target_contract()["v5_6_7_1"][
            "pass"
        ],
        "pass": bool(
            _routes_accept(routes)
            and [route["component"] for route in routes] == list(actual_names)
            and counts == {"bulk": 12, "GHY": 2, "interface": 6}
            and len(set(actual_names)) == 20
        ),
    }


def _static_wrapper_contract_from_text(text: str) -> dict[str, Any]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"ast_parse_pass": False, "pass": False}
    definitions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    canonicalizer = definitions.get("canonicalize_q_zero_before_decode")
    wrappers = {
        "local": definitions.get("q_zero_local_density_values_and_eta_jvps"),
        "integrated": definitions.get(
            "q_zero_integrated_action_values_and_eta_jvps"
        ),
    }

    zero_assignments = {"canonical_free": False, "canonical_tangent": False}
    zero_assignment_lines: list[int] = []
    finiteness_guard_lines: list[int] = []
    upstream_guard_or_contract_lines: list[int] = []
    if canonicalizer is not None:
        for node in ast.walk(canonicalizer):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "isfinite"
            ):
                finiteness_guard_lines.append(int(getattr(node, "lineno", -1)))
            if isinstance(node, ast.Call) and (
                isinstance(node.func, ast.Name)
                and node.func.id == "_load_v5671"
                or isinstance(node.func, ast.Attribute)
                and node.func.attr == "full_t4_decoder_contract"
            ):
                upstream_guard_or_contract_lines.append(
                    int(getattr(node, "lineno", -1))
                )
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name):
                continue
            if target.value.id not in zero_assignments:
                continue
            sliced = target.slice
            is_q_slice = (
                isinstance(sliced, ast.Slice)
                and isinstance(sliced.lower, ast.Name)
                and sliced.lower.id == "q_start"
                and isinstance(sliced.upper, ast.Name)
                and sliced.upper.id == "q_stop"
            )
            is_zero = isinstance(node.value, ast.Constant) and node.value.value == 0.0
            if is_q_slice and is_zero:
                zero_assignments[target.value.id] = True
                zero_assignment_lines.append(int(getattr(node, "lineno", -1)))

    wrapper_results: dict[str, Any] = {}
    target_names = {
        "local": "local_density_values_and_eta_jvps",
        "integrated": "integrated_action_values_and_eta_jvps",
    }
    for label, node in wrappers.items():
        if node is None:
            wrapper_results[label] = {"pass": False}
            continue
        statements = list(node.body)
        if statements and isinstance(statements[0], ast.Expr) and isinstance(
            statements[0].value, ast.Constant
        ) and isinstance(statements[0].value.value, str):
            statements = statements[1:]
        first = statements[0] if statements else None
        canonical_first = False
        canonical_line = -1
        if isinstance(first, ast.Assign) and isinstance(first.value, ast.Call):
            call = first.value
            canonical_first = (
                isinstance(call.func, ast.Name)
                and call.func.id == "canonicalize_q_zero_before_decode"
            )
            canonical_line = int(getattr(first, "lineno", -1))
        target_calls = [
            candidate
            for candidate in ast.walk(node)
            if isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Attribute)
            and candidate.func.attr == target_names[label]
        ]
        correct_target_args = False
        target_line = -1
        if len(target_calls) == 1:
            target = target_calls[0]
            target_line = int(getattr(target, "lineno", -1))
            correct_target_args = (
                len(target.args) >= 2
                and isinstance(target.args[0], ast.Name)
                and target.args[0].id == "canonical_free"
                and isinstance(target.args[1], ast.Name)
                and target.args[1].id == "canonical_tangent"
            )
        forbidden_direct_calls = {
            candidate.func.attr
            for candidate in ast.walk(node)
            if isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Attribute)
            and candidate.func.attr
            in {"decode_common_first_boundary_td3", "so3_exp"}
        }
        wrapper_results[label] = {
            "canonicalization_is_first_executable_statement": canonical_first,
            "exactly_one_target_call": len(target_calls) == 1,
            "target_receives_only_canonical_arrays": correct_target_args,
            "canonicalization_precedes_target": 0 < canonical_line < target_line,
            "no_direct_decoder_or_so3_call": not forbidden_direct_calls,
            "pass": bool(
                canonical_first
                and len(target_calls) == 1
                and correct_target_args
                and 0 < canonical_line < target_line
                and not forbidden_direct_calls
            ),
        }
    return {
        "ast_parse_pass": True,
        "canonicalizer_zeros_primal_q_slice": zero_assignments["canonical_free"],
        "canonicalizer_zeros_tangent_q_slice": zero_assignments[
            "canonical_tangent"
        ],
        "q_zero_assignments_precede_finiteness_guards": bool(
            len(zero_assignment_lines) == 2
            and finiteness_guard_lines
            and max(zero_assignment_lines) < min(finiteness_guard_lines)
        ),
        "q_zero_assignments_precede_upstream_hash_and_contract_guards": bool(
            len(zero_assignment_lines) == 2
            and upstream_guard_or_contract_lines
            and max(zero_assignment_lines) < min(upstream_guard_or_contract_lines)
        ),
        "wrappers": wrapper_results,
        "pass": bool(
            canonicalizer is not None
            and all(zero_assignments.values())
            and len(zero_assignment_lines) == 2
            and finiteness_guard_lines
            and max(zero_assignment_lines) < min(finiteness_guard_lines)
            and upstream_guard_or_contract_lines
            and max(zero_assignment_lines) < min(upstream_guard_or_contract_lines)
            and all(item["pass"] for item in wrapper_results.values())
        ),
    }


def wrapper_source_contract() -> dict[str, Any]:
    return _static_wrapper_contract_from_text(
        Path(__file__).read_text(encoding="utf-8")
    )


def _call_rejected(callable_object: Any) -> bool:
    try:
        callable_object()
    except Exception:
        return True
    return False


def _component_outputs_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return bool(
        tuple(left["component_names"]) == tuple(right["component_names"])
        and tuple(left["values"]) == tuple(right["values"])
        and tuple(left["eta_jvps"]) == tuple(right["eta_jvps"])
    )


def finite_runtime_factorization_witness() -> dict[str, Any]:
    upstream = _load_v5671()
    N = 1
    K = 1
    free, contract = upstream._sample_safe_free(N, K)
    tangent = np.zeros_like(free)
    phi_spec = contract["free_layout"]["blocks"]["common.varphi_E0"]
    tangent[int(phi_spec["start"]):int(phi_spec["stop"])] = (0.03, -0.02, 0.01)
    q_spec = contract["free_layout"]["blocks"]["Q_frame.q"]
    q_start = int(q_spec["start"])
    q_stop = int(q_spec["stop"])

    free_body_guard = free.copy()
    free_body_guard[q_start:q_stop] = (3.0, 0.0, 0.0)
    tangent_nonbody_guard = tangent.copy()
    tangent_nonbody_guard[q_start:q_stop] = (9.0, 0.0, 0.0)
    free_permitted = free.copy()
    free_permitted[q_start:q_stop] = (0.0, 0.0, 0.1)
    tangent_permitted = tangent.copy()
    tangent_permitted[q_start:q_stop] = (0.02, -0.01, 0.03)
    original_body_rejected = _call_rejected(
        lambda: upstream.local_density_values_and_eta_jvps(
            free_body_guard, tangent, N, K, (0.0, 0.0, 0.0, 0.0), 0.5
        )
    )
    original_tangent_rejected = _call_rejected(
        lambda: upstream.local_density_values_and_eta_jvps(
            free, tangent_nonbody_guard, N, K, (0.0, 0.0, 0.0, 0.0), 0.5
        )
    )

    raw_local_base = upstream.local_density_values_and_eta_jvps(
        free, tangent, N, K, (0.2, 0.3, 0.4, 0.5), 0.37
    )
    raw_local_permitted = upstream.local_density_values_and_eta_jvps(
        free_permitted,
        tangent_permitted,
        N,
        K,
        (0.2, 0.3, 0.4, 0.5),
        0.37,
    )
    raw_finite_base = upstream.integrated_action_values_and_eta_jvps(
        free, tangent, N, K, 1, 1
    )
    raw_finite_permitted = upstream.integrated_action_values_and_eta_jvps(
        free_permitted, tangent_permitted, N, K, 1, 1
    )
    decoded_base = upstream.decode_common_first_boundary_td3(
        free, tangent, N, K, (0.2, 0.3, 0.4, 0.5)
    )
    decoded_permitted = upstream.decode_common_first_boundary_td3(
        free_permitted,
        tangent_permitted,
        N,
        K,
        (0.2, 0.3, 0.4, 0.5),
    )

    def body_vector(value: Any) -> np.ndarray:
        array = np.asarray(value, dtype=object)
        return np.asarray([entry.body for entry in array.flat], dtype=float)

    common_full_phi_motion = {
        name: float(
            np.max(
                np.abs(
                    body_vector(decoded_permitted["common"][name])
                    - body_vector(decoded_base["common"][name])
                ),
                initial=0.0,
            )
        )
        for name in ("S_Q", "varphi", "E_Q")
    }
    lateral_reduced_motion = {
        f"{side}.{name}": float(
            np.max(
                np.abs(
                    body_vector(decoded_permitted["sides"][side][name])
                    - body_vector(decoded_base["sides"][side][name])
                ),
                initial=0.0,
            )
        )
        for side in EXPECTED_SIDES
        for name in ("phi_trace", "A_trace_full")
    }
    raw_local_equal = _component_outputs_equal(raw_local_base, raw_local_permitted)
    raw_finite_equal = _component_outputs_equal(
        raw_finite_base, raw_finite_permitted
    )
    raw_totals_equal = raw_finite_base["S_total"] == raw_finite_permitted["S_total"]

    local_base = q_zero_local_density_values_and_eta_jvps(
        free, tangent, N, K, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    local_body = q_zero_local_density_values_and_eta_jvps(
        free_body_guard, tangent, N, K, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    local_tangent = q_zero_local_density_values_and_eta_jvps(
        free, tangent_nonbody_guard, N, K, (0.0, 0.0, 0.0, 0.0), 0.5
    )
    finite_base = q_zero_integrated_action_values_and_eta_jvps(
        free, tangent, N, K, 1, 1
    )
    finite_body = q_zero_integrated_action_values_and_eta_jvps(
        free_body_guard, tangent, N, K, 1, 1
    )
    finite_tangent = q_zero_integrated_action_values_and_eta_jvps(
        free, tangent_nonbody_guard, N, K, 1, 1
    )
    local_equal = _component_outputs_equal(local_base, local_body) and _component_outputs_equal(
        local_base, local_tangent
    )
    finite_equal = _component_outputs_equal(
        finite_base, finite_body
    ) and _component_outputs_equal(finite_base, finite_tangent)
    finite_totals_equal = finite_base["S_total"] == finite_body["S_total"] == finite_tangent[
        "S_total"
    ]
    nonvacuous_jvp = any(abs(value) > 0.0 for value in finite_base["eta_jvps"])

    return {
        "scope": {
            "N": N,
            "K": K,
            "tangential_order_per_axis": 1,
            "radial_order": 1,
            "finite_only": True,
            "arbitrary_N_or_continuum_claimed": False,
        },
        "hostile_representatives": {
            "primal_q_body_norm": 3.0,
            "tangent_q_nonbody_l1": 9.0,
            "original_v5_6_7_1_primal_rejected_before_section": original_body_rejected,
            "original_v5_6_7_1_tangent_rejected_before_section": original_tangent_rejected,
        },
        "permitted_raw_v5_6_7_1_contrast": {
            "primal_q": [0.0, 0.0, 0.1],
            "tangent_q": [0.02, -0.01, 0.03],
            "common_full_Phi_body_motion_max_abs": common_full_phi_motion,
            "common_full_Phi_moves_nontrivially": max(common_full_phi_motion.values())
            > 1.0e-3,
            "lateral_reduced_trace_body_motion_max_abs": lateral_reduced_motion,
            "lateral_reduced_traces_exactly_equal": all(
                value == 0.0 for value in lateral_reduced_motion.values()
            ),
            "raw_local_all_twenty_values_and_JVP_exactly_equal": raw_local_equal,
            "raw_finite_all_twenty_values_and_JVP_exactly_equal": raw_finite_equal,
            "raw_finite_S_total_value_and_JVP_exactly_equal": raw_totals_equal,
        },
        "local_all_twenty_values_and_JVP_exactly_equal": local_equal,
        "finite_all_twenty_values_and_JVP_exactly_equal": finite_equal,
        "finite_S_total_value_and_JVP_exactly_equal": finite_totals_equal,
        "finite_JVP_witness_nonzero": nonvacuous_jvp,
        "component_names": list(local_base["component_names"]),
        "output_names": list(finite_base["output_names"]),
        "pass": bool(
            original_body_rejected
            and original_tangent_rejected
            and max(common_full_phi_motion.values()) > 1.0e-3
            and all(value == 0.0 for value in lateral_reduced_motion.values())
            and raw_local_equal
            and raw_finite_equal
            and raw_totals_equal
            and local_equal
            and finite_equal
            and finite_totals_equal
            and nonvacuous_jvp
            and tuple(local_base["component_names"]) == EXPECTED_COMPONENTS
        ),
    }


def r_plus_minus_retention_witness() -> dict[str, Any]:
    upstream = _load_v5671()
    free, contract = upstream._sample_safe_free(1, 1)
    tangent = np.zeros_like(free)
    assigned = {
        "plus": (0.30, -0.20, 0.10),
        "minus": (-0.15, 0.25, 0.20),
    }
    slices: dict[str, tuple[int, int]] = {}
    for side, values in assigned.items():
        specification = contract["free_layout"]["blocks"][f"{side}.r_E0"]
        start = int(specification["start"])
        stop = int(specification["stop"])
        slices[side] = (start, stop)
        free[start:stop] = values
        tangent[start:stop] = tuple(value / 10.0 for value in values)
    canonical_free, canonical_tangent, metadata = canonicalize_q_zero_before_decode(
        free, tangent, 1, 1
    )
    retained = {
        side: bool(
            np.array_equal(canonical_free[start:stop], free[start:stop])
            and np.array_equal(canonical_tangent[start:stop], tangent[start:stop])
        )
        for side, (start, stop) in slices.items()
    }
    decoded = upstream.decode_common_first_boundary_td3(
        canonical_free, canonical_tangent, 1, 1, (0.0, 0.0, 0.0, 0.0)
    )
    erased = canonical_free.copy()
    erased_tangent = canonical_tangent.copy()
    for start, stop in slices.values():
        erased[start:stop] = 0.0
        erased_tangent[start:stop] = 0.0
    decoded_erased = upstream.decode_common_first_boundary_td3(
        erased, erased_tangent, 1, 1, (0.0, 0.0, 0.0, 0.0)
    )
    phi_changes = {}
    for side in EXPECTED_SIDES:
        phi = np.asarray(
            [entry.body for entry in decoded["sides"][side]["phi_trace"]], dtype=float
        )
        phi_erased = np.asarray(
            [entry.body for entry in decoded_erased["sides"][side]["phi_trace"]],
            dtype=float,
        )
        phi_changes[side] = float(np.max(np.abs(phi - phi_erased)))
    return {
        "assigned_r_E0": {side: list(values) for side, values in assigned.items()},
        "primal_and_tangent_r_retained_byte_exactly": retained,
        "section_metadata_r_retained": metadata["r_plus_minus_preserved_exactly"],
        "lateral_phi_trace_change_if_r_is_wrongly_erased": phi_changes,
        "r_quotiented_or_declared_redundant": False,
        "pass": bool(
            all(retained.values())
            and all(metadata["r_plus_minus_preserved_exactly"].values())
            and all(value > 1.0e-3 for value in phi_changes.values())
        ),
    }


def _fraction_rank(matrix: Sequence[Sequence[int]]) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    column_count = len(rows[0])
    for column in range(column_count):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row_index in range(len(rows)):
            if row_index == rank:
                continue
            factor = rows[row_index][column]
            if factor:
                rows[row_index] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(rows[row_index], rows[rank])
                ]
        rank += 1
    return rank


def _reconstruct_BCH_half_bracket_from_inputs(
    bch: Mapping[str, Any],
) -> dict[str, Any]:
    q = bch["q"]
    lam = bch["lambda"]
    if not isinstance(q, Mapping) or not isinstance(lam, Mapping):
        raise ValueError("q and lambda must be structured spectral Lie-algebra inputs")
    q_coefficient = Fraction(q["coefficient"])
    lambda_coefficient = Fraction(lam["coefficient"])
    q_basis = q["basis_function"]
    lambda_basis = lam["basis_function"]
    if not isinstance(q_basis, Mapping) or not isinstance(lambda_basis, Mapping):
        raise ValueError("BCH basis functions must be structured mappings")
    q_wavevector = tuple(int(value) for value in q_basis["wavevector"])
    lambda_wavevector = tuple(int(value) for value in lambda_basis["wavevector"])
    if (
        q_basis["kind"] != "cos"
        or lambda_basis["kind"] != "cos"
        or q_wavevector != lambda_wavevector
        or len(q_wavevector) != 4
    ):
        raise ValueError("this exact BCH ledger requires the same cosine mode")
    q_generator = tuple(int(value) for value in q["generator"])
    lambda_generator = tuple(int(value) for value in lam["generator"])
    generator_cross = _integer_cross(q_generator, lambda_generator)
    half_bracket_coefficient = q_coefficient * lambda_coefficient / 2
    # cos(theta)^2=(1+cos(2 theta))/2 is reconstructed here, not trusted
    # from any reported half-bracket or decomposition field.
    decomposed_coefficient = half_bracket_coefficient / 2
    return {
        "generator_cross": list(generator_cross),
        "half_bracket_coefficient_times_cos_squared": str(
            half_bracket_coefficient
        ),
        "constant_coefficient": str(decomposed_coefficient),
        "double_cosine_coefficient": str(decomposed_coefficient),
        "double_wavevector": [2 * value for value in q_wavevector],
    }


def _orbit_matrix_from_pair(pair: Mapping[str, Any]) -> list[list[int]]:
    phi = tuple(int(value) for value in pair["phi"])
    connection = tuple(int(value) for value in pair["A"])
    if len(phi) != 3 or len(connection) != 3:
        raise ValueError("orbit witness phi and A must be three-vectors")
    columns = []
    for generator in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        columns.append(
            _integer_cross(generator, phi)
            + _integer_cross(generator, connection)
        )
    return [
        [columns[column][row] for column in range(3)] for row in range(6)
    ]


def _integer_gram(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            sum(int(row[left]) * int(row[right]) for row in matrix)
            for right in range(3)
        ]
        for left in range(3)
    ]


def _integer_det3(matrix: Sequence[Sequence[int]]) -> int:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("determinant input must be 3x3")
    return int(
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def finite_BCH_and_variable_rank_no_go() -> dict[str, Any]:
    upstream = _load_v5671()
    labels = tuple(upstream.full_t4_decoder_contract(2, 1)["basis"]["labels"])
    expected_labels = ("1", "cos(1*x0+1*x1)")
    q_input = {
        "coefficient": "1",
        "basis_function": {"kind": "cos", "wavevector": [1, 1, 0, 0]},
        "generator": [1, 0, 0],
    }
    lambda_input = {
        "coefficient": "1",
        "basis_function": {"kind": "cos", "wavevector": [1, 1, 0, 0]},
        "generator": [0, 1, 0],
    }
    reconstructed_BCH = _reconstruct_BCH_half_bracket_from_inputs(
        {"q": q_input, "lambda": lambda_input}
    )
    zero_pair = {"phi": [0, 0, 0], "A": [0, 0, 0]}
    generic_pair = {"phi": [1, 0, 0], "A": [0, 1, 0]}
    zero_orbit_matrix = _orbit_matrix_from_pair(zero_pair)
    generic_orbit_matrix = _orbit_matrix_from_pair(generic_pair)
    generic_gram = _integer_gram(generic_orbit_matrix)
    zero_rank = _fraction_rank(zero_orbit_matrix)
    generic_rank = _fraction_rank(generic_orbit_matrix)
    return {
        "N2_BCH_nonclosure": {
            "actual_N2_basis_labels": list(labels),
            "theta": "x0+x1",
            "q": q_input,
            "lambda": lambda_input,
            "reconstructed_half_bracket": reconstructed_BCH,
            "half_bracket_display": "(1/2) cos(theta)^2 e3",
            "exact_decomposition_display": "(1/4)(1+cos(2 theta)) e3",
            "outside_mode": "cos(2*x0+2*x1)",
            "outside_coefficient": str(Fraction(1, 4)),
            "outside_mode_absent_from_actual_N2_basis": "cos(2*x0+2*x1)"
            not in labels,
            "pass": bool(
                labels == expected_labels
                and "cos(2*x0+2*x1)" not in labels
                and reconstructed_BCH
                == {
                    "generator_cross": [0, 0, 1],
                    "half_bracket_coefficient_times_cos_squared": "1/2",
                    "constant_coefficient": "1/4",
                    "double_cosine_coefficient": "1/4",
                    "double_wavevector": [2, 2, 0, 0],
                }
            ),
        },
        "nonconstant_infinitesimal_orbit_rank": {
            "action": "X -> (X cross phi, X cross A)",
            "zero_pair": zero_pair,
            "zero_pair_matrix": zero_orbit_matrix,
            "zero_pair_rank": zero_rank,
            "zero_pair_stabilizer_dimension": 3 - zero_rank,
            "generic_pair": generic_pair,
            "generic_pair_matrix": generic_orbit_matrix,
            "generic_Gram_matrix": generic_gram,
            "generic_Gram_diagonal": [generic_gram[index][index] for index in range(3)],
            "generic_Gram_determinant": 2,
            "generic_pair_rank": generic_rank,
            "generic_pair_stabilizer_dimension": 3 - generic_rank,
            "margins_can_be_held_fixed_independently": True,
            "pass": zero_rank == 0 and generic_rank == 3,
        },
        "conclusion": (
            "The truncated q coordinates are not an internal BCH-closed gauge group, "
            "and orbit rank is not globally constant; no global smooth group quotient "
            "or quotient-manifold theorem follows."
        ),
        "pass": bool(
            labels == expected_labels
            and "cos(2*x0+2*x1)" not in labels
            and zero_rank == 0
            and generic_rank == 3
        ),
    }


def _source_attack_campaign() -> dict[str, bool]:
    upstream_text = V5671_SOURCE.read_text(encoding="utf-8")
    local_text = Path(__file__).read_text(encoding="utf-8")
    mutated_upstream = upstream_text.replace(
        "phi_source = _matvec(R0_transpose, varphi_e0, zero)",
        "phi_source = _matvec(R_transpose, varphi_e0, zero)",
        1,
    )
    mutated_free_argument = local_text.replace(
        "result = upstream.local_density_values_and_eta_jvps(\n"
        "        canonical_free,",
        "result = upstream.local_density_values_and_eta_jvps(\n"
        "        free,",
        1,
    )
    mutated_tangent_zero = local_text.replace(
        "canonical_tangent[q_start:q_stop] = 0.0",
        "canonical_tangent[q_start:q_stop] = 1.0",
        1,
    )
    invariant_present_but_unused = upstream_text.replace(
        "+ phi_source\n            + tuple(A_full[mu][a]",
        "+ phi_source_full\n            + tuple(A_full[mu][a]",
        1,
    )
    rotate_only_one = upstream_text.replace(
        "E_Q[mu][a] * varphi_Q[a]",
        "E_Q[mu][a] * common[\"varphi_E0\"][a]",
        1,
    )
    return {
        "mutate_byte_pinned_upstream_source": not _upstream_source_contract_from_text(
            mutated_upstream
        )["pass"],
        "wrapper_passes_uncanonicalized_free": not _static_wrapper_contract_from_text(
            mutated_free_argument
        )["pass"],
        "wrapper_does_not_zero_tangent_q": not _static_wrapper_contract_from_text(
            mutated_tangent_zero
        )["pass"],
        "invariant_formulas_present_but_not_consumed": not _upstream_source_contract_from_text(
            invariant_present_but_unused
        )["pass"],
        "rotate_only_one_of_EQ_or_varphi": not _upstream_source_contract_from_text(
            rotate_only_one
        )["pass"],
    }


def _decision_contract_accepts(decision: Mapping[str, Any]) -> bool:
    return bool(
        set(decision) == TRUE_DECISION_KEYS | FALSE_DECISION_KEYS
        and all(decision[key] is True for key in TRUE_DECISION_KEYS)
        and all(decision[key] is False for key in FALSE_DECISION_KEYS)
    )


def _identity_contract_accepts(ledger: Mapping[str, Any]) -> bool:
    try:
        identities = ledger["identities"]
        if set(identities) != set(EXPECTED_IDENTITY_NORMAL_FORMS_LITERAL):
            return False
        for name, expected_normal_form in EXPECTED_IDENTITY_NORMAL_FORMS_LITERAL.items():
            identity = identities[name]
            left = tuple(
                (row["coefficient"], tuple(row["word"]))
                for row in identity["left_normal_form"]
            )
            right = tuple(
                (row["coefficient"], tuple(row["word"]))
                for row in identity["right_normal_form"]
            )
            if (
                identity["statement"] != EXPECTED_IDENTITY_STATEMENTS_LITERAL[name]
                or identity["pass"] is not True
                or left != expected_normal_form
                or right != expected_normal_form
            ):
                return False
        return bool(
            ledger["algebra"]
            == "exact noncommutative free words with only inverse-pair reductions"
            and ledger["derivative_rule_used"] == "d(S R0)=dS R0+S dR0"
            and ledger["pass"] is True
            and _canonical_sha256(ledger) == EXPECTED_IDENTITY_LEDGER_SHA256
        )
    except (KeyError, TypeError, ValueError):
        return False


def _no_go_contract_accepts(ledger: Mapping[str, Any]) -> bool:
    try:
        bch = ledger["N2_BCH_nonclosure"]
        rank = ledger["nonconstant_infinitesimal_orbit_rank"]
        reconstructed_BCH = _reconstruct_BCH_half_bracket_from_inputs(bch)
        zero_matrix = _orbit_matrix_from_pair(rank["zero_pair"])
        generic_matrix = _orbit_matrix_from_pair(rank["generic_pair"])
        zero_rank = _fraction_rank(zero_matrix)
        generic_rank = _fraction_rank(generic_matrix)
        generic_gram = _integer_gram(generic_matrix)
        generic_determinant = _integer_det3(generic_gram)
        expected_BCH = {
            "generator_cross": [0, 0, 1],
            "half_bracket_coefficient_times_cos_squared": "1/2",
            "constant_coefficient": "1/4",
            "double_cosine_coefficient": "1/4",
            "double_wavevector": [2, 2, 0, 0],
        }
        return bool(
            bch["q"] == EXPECTED_BCH_INPUTS_LITERAL["q"]
            and bch["lambda"] == EXPECTED_BCH_INPUTS_LITERAL["lambda"]
            and reconstructed_BCH == expected_BCH
            and bch["reconstructed_half_bracket"] == reconstructed_BCH
            and bch["actual_N2_basis_labels"] == ["1", "cos(1*x0+1*x1)"]
            and bch["theta"] == "x0+x1"
            and bch["half_bracket_display"] == "(1/2) cos(theta)^2 e3"
            and bch["exact_decomposition_display"]
            == "(1/4)(1+cos(2 theta)) e3"
            and bch["outside_mode"] == "cos(2*x0+2*x1)"
            and bch["outside_coefficient"] == "1/4"
            and bch["outside_mode_absent_from_actual_N2_basis"] is True
            and bch["pass"] is True
            and rank["zero_pair"] == EXPECTED_ZERO_ORBIT_PAIR_LITERAL
            and rank["generic_pair"] == EXPECTED_GENERIC_ORBIT_PAIR_LITERAL
            and rank["zero_pair_matrix"] == zero_matrix
            and rank["generic_pair_matrix"] == generic_matrix
            and rank["zero_pair_rank"] == zero_rank == 0
            and rank["generic_pair_rank"] == generic_rank == 3
            and rank["zero_pair_stabilizer_dimension"] == 3
            and rank["generic_pair_stabilizer_dimension"] == 0
            and rank["generic_Gram_matrix"] == generic_gram
            and rank["generic_Gram_diagonal"] == [1, 1, 2]
            and rank["generic_Gram_determinant"] == generic_determinant == 2
            and rank["margins_can_be_held_fixed_independently"] is True
            and rank["pass"] is True
            and ledger["pass"] is True
            and _canonical_sha256(ledger)
            == EXPECTED_FINITE_BCH_AND_RANK_NO_GO_SHA256
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def mutant_campaign(
    *,
    runtime: Mapping[str, Any],
    r_witness: Mapping[str, Any],
    kernel: Mapping[str, Any],
    identities: Mapping[str, Any],
    routes: Mapping[str, Any],
    no_go: Mapping[str, Any],
    canonical_decision: Mapping[str, Any],
) -> dict[str, Any]:
    upstream = _load_v5671()
    free, contract = upstream._sample_safe_free(1, 1)
    tangent = np.zeros_like(free)
    q_spec = contract["free_layout"]["blocks"]["Q_frame.q"]
    q_start, q_stop = int(q_spec["start"]), int(q_spec["stop"])
    free_body = free.copy()
    free_body[q_start:q_stop] = (3.0, 0.0, 0.0)
    tangent_nonbody = tangent.copy()
    tangent_nonbody[q_start:q_stop] = (9.0, 0.0, 0.0)
    partial = free.copy()
    partial[q_start:q_stop] = (0.0, 3.0, 0.0)
    partial[q_start] = 0.0

    identity_mutants = _identity_mutants()
    source_mutants = _source_attack_campaign()
    route_rows = list(routes["routes"])
    deleted = route_rows[:-1]
    misclassified = [dict(row) for row in route_rows]
    misclassified[6]["class"] = "bulk"
    robin_replaced = [dict(row) for row in route_rows]
    robin_replaced[-1]["q_factor"] = "frozen E0 times S phi0"
    split_q = [dict(row) for row in route_rows]
    split_q[7]["q_factor"] = "independent q_minus not tied to the common frame"

    changed_identity = json.loads(json.dumps(identities))
    changed_identity["identities"]["shared_solder_contraction"][
        "right_normal_form"
    ] = []
    coherent_identity_mutants = {}
    wrong_words = {
        "lateral_associated_field": ["R0_inv", "WRONG_phi0"],
        "lateral_affine_connection": ["R0_inv", "WRONG_A0", "R0"],
        "shared_solder_contraction": ["E0", "WRONG_phi0"],
    }
    for identity_name, wrong_word in wrong_words.items():
        mutant = json.loads(json.dumps(identities))
        wrong_normal_form = [{"coefficient": "1", "word": wrong_word}]
        mutant["identities"][identity_name]["left_normal_form"] = wrong_normal_form
        mutant["identities"][identity_name]["right_normal_form"] = json.loads(
            json.dumps(wrong_normal_form)
        )
        mutant["identities"][identity_name]["pass"] = True
        mutant["pass"] = True
        coherent_identity_mutants[identity_name] = mutant

    wrong_EH_leaf = [dict(row) for row in route_rows]
    wrong_EH_leaf[0]["target_leaf"] = "_relative_bulk_densities_td3['P_kinetic']"
    wrong_robin_leaf = [dict(row) for row in route_rows]
    wrong_robin_leaf[-1]["target_leaf"] = "_interface_component_densities_td3['wall']"
    reordered_routes = [dict(row) for row in route_rows]
    reordered_routes[0], reordered_routes[1] = reordered_routes[1], reordered_routes[0]

    kernel_nonzero_q = json.loads(json.dumps(kernel))
    kernel_nonzero_q["base_q"] = [9, 9, 9]
    kernel_wrong_phi = json.loads(json.dumps(kernel))
    kernel_wrong_phi["base_phi0"] = [0, 1, 0]
    kernel_wrong_delta = json.loads(json.dumps(kernel))
    kernel_wrong_delta["Q_frame_tangent_delta_q"] = [1, 0, 0]

    bch_zero_inputs = json.loads(json.dumps(no_go))
    bch_zero_inputs["N2_BCH_nonclosure"]["q"] = "0"
    bch_zero_inputs["N2_BCH_nonclosure"]["lambda"] = "0"
    bch_parallel = json.loads(json.dumps(no_go))
    bch_parallel["N2_BCH_nonclosure"]["lambda"]["generator"] = [1, 0, 0]
    bch_wrong_wavevector = json.loads(json.dumps(no_go))
    bch_wrong_wavevector["N2_BCH_nonclosure"]["q"]["basis_function"][
        "wavevector"
    ] = [1, 0, 0, 0]
    rank_generic_zero = json.loads(json.dumps(no_go))
    rank_generic_zero["nonconstant_infinitesimal_orbit_rank"]["generic_pair"] = {
        "phi": [0, 0, 0],
        "A": [0, 0, 0],
    }
    rank_generic_collinear = json.loads(json.dumps(no_go))
    rank_generic_collinear["nonconstant_infinitesimal_orbit_rank"][
        "generic_pair"
    ] = {"phi": [1, 0, 0], "A": [1, 0, 0]}
    rank_zero_generic = json.loads(json.dumps(no_go))
    rank_zero_generic["nonconstant_infinitesimal_orbit_rank"]["zero_pair"] = {
        "phi": [1, 0, 0],
        "A": [0, 1, 0],
    }
    flipped_decision = dict(canonical_decision)
    flipped_decision["Q_frame_kernel_of_full_Phi_pass"] = True

    rows = [
        {
            "id": "claim_Q_inside_kernel_DPhi_full",
            "producer": "full_phi_kernel_counterexample",
            "independent_target": "exact integer cross-product expectation e2",
            "detected": full_phi_kernel_counterexample()["pass"],
        },
        *[
            {
                "id": mutant_id,
                "producer": "mutated exact free-word expression",
                "independent_target": "canonical reduced normal form",
                "detected": detected,
            }
            for mutant_id, detected in identity_mutants.items()
        ],
        {
            "id": "leave_primal_q_for_decoder",
            "producer": "hostile primal q=3 representative",
            "independent_target": "byte-pinned v5.6.7.1 body guard",
            "detected": runtime["hostile_representatives"][
                "original_v5_6_7_1_primal_rejected_before_section"
            ],
        },
        {
            "id": "leave_tangent_q_for_decoder",
            "producer": "hostile tangent q=9 representative",
            "independent_target": "byte-pinned v5.6.7.1 nonbody guard",
            "detected": runtime["hostile_representatives"][
                "original_v5_6_7_1_tangent_rejected_before_section"
            ],
        },
        {
            "id": "canonicalize_only_after_decode",
            "producer": "late-section call order mutant",
            "independent_target": "byte-pinned decoder must reject q=3 first",
            "detected": _call_rejected(
                lambda: upstream.decode_common_first_boundary_td3(
                    free_body, tangent, 1, 1, (0.0, 0.0, 0.0, 0.0)
                )
            ),
        },
        {
            "id": "zero_only_one_q_scalar",
            "producer": "partial q-slice zero mutant",
            "independent_target": "byte-pinned decoder body guard",
            "detected": _call_rejected(
                lambda: upstream.decode_common_first_boundary_td3(
                    partial, tangent, 1, 1, (0.0, 0.0, 0.0, 0.0)
                )
            ),
        },
        {
            "id": "erase_r_plus_minus_with_q",
            "producer": "overbroad section mutant",
            "independent_target": "decoded lateral phi trace",
            "detected": r_witness["pass"],
        },
        {
            "id": "delete_one_real_component_route",
            "producer": "in-memory route deletion",
            "independent_target": "independent twenty-route allowlist",
            "detected": not _routes_accept(deleted),
        },
        {
            "id": "misclassify_GHY_as_bulk",
            "producer": "in-memory domain mutation",
            "independent_target": "independent twenty-route allowlist",
            "detected": not _routes_accept(misclassified),
        },
        {
            "id": "replace_Robin_solder_identity",
            "producer": "in-memory Robin dependency mutation",
            "independent_target": "independent twenty-route allowlist",
            "detected": not _routes_accept(robin_replaced),
        },
        {
            "id": "split_common_q_between_sides",
            "producer": "in-memory side-frame mutation",
            "independent_target": "independent common-frame route allowlist",
            "detected": not _routes_accept(split_q),
        },
        *[
            {
                "id": mutant_id,
                "producer": "mutated source text",
                "independent_target": (
                    "byte hash plus AST target contract"
                    if mutant_id == "mutate_byte_pinned_upstream_source"
                    else "AST wrapper control-flow contract"
                ),
                "detected": detected,
            }
            for mutant_id, detected in source_mutants.items()
        ],
        {
            "id": "claim_N2_BCH_closure",
            "producer": "finite spectral group-closure claim",
            "independent_target": "exact cos^2 product and actual N2 labels",
            "detected": no_go["N2_BCH_nonclosure"]["pass"],
        },
        {
            "id": "claim_global_constant_orbit_rank",
            "producer": "constant-rank claim",
            "independent_target": "two exact rational matrix ranks",
            "detected": no_go["nonconstant_infinitesimal_orbit_rank"]["pass"],
        },
        {
            "id": "in_memory_flip_fail_closed_decision",
            "producer": "mutated decision mapping",
            "independent_target": "exact true/false allowlist validator",
            "detected": not _decision_contract_accepts(flipped_decision),
        },
        {
            "id": "in_memory_change_identity_normal_form",
            "producer": "mutated identity ledger",
            "independent_target": "fresh exact free-word normal forms",
            "detected": not _identity_contract_accepts(changed_identity),
        },
        {
            "id": "in_memory_remove_component_binding",
            "producer": "mutated route ledger",
            "independent_target": "fresh independent twenty-route allowlist",
            "detected": not _routes_accept(deleted),
        },
        {
            "id": "producer_monkeypatch_associated_wrong_both_forms_pass_true",
            "producer": "monkeypatched exact_invariant_identity_ledger before build",
            "independent_target": "literal associated normal form plus frozen ledger fingerprint",
            "detected": not _identity_contract_accepts(
                coherent_identity_mutants["lateral_associated_field"]
            ),
        },
        {
            "id": "producer_monkeypatch_affine_wrong_both_forms_pass_true",
            "producer": "monkeypatched exact_invariant_identity_ledger before build",
            "independent_target": "literal affine normal form plus frozen ledger fingerprint",
            "detected": not _identity_contract_accepts(
                coherent_identity_mutants["lateral_affine_connection"]
            ),
        },
        {
            "id": "producer_monkeypatch_solder_wrong_both_forms_pass_true",
            "producer": "monkeypatched exact_invariant_identity_ledger before build",
            "independent_target": "literal solder normal form plus frozen ledger fingerprint",
            "detected": not _identity_contract_accepts(
                coherent_identity_mutants["shared_solder_contraction"]
            ),
        },
        {
            "id": "producer_monkeypatch_EH_leaf_to_P_kinetic",
            "producer": "monkeypatched _expected_real_routes before build",
            "independent_target": "literal component-to-leaf map plus frozen route fingerprint",
            "detected": not _routes_accept(wrong_EH_leaf),
        },
        {
            "id": "producer_monkeypatch_Robin_leaf_to_wall",
            "producer": "monkeypatched _expected_real_routes before build",
            "independent_target": "literal component-to-leaf map plus frozen route fingerprint",
            "detected": not _routes_accept(wrong_robin_leaf),
        },
        {
            "id": "producer_monkeypatch_routes_reordered_self_consistent",
            "producer": "monkeypatched _expected_real_routes before build",
            "independent_target": "literal ordered component map plus frozen route fingerprint",
            "detected": not _routes_accept(reordered_routes),
        },
        {
            "id": "producer_monkeypatch_kernel_nonzero_base_q_preserved_derivative",
            "producer": "monkeypatched full_phi_kernel_counterexample before build",
            "independent_target": "literal q=0 base plus independently reconstructed derivative fingerprint",
            "detected": not _kernel_counterexample_accepts(kernel_nonzero_q),
        },
        {
            "id": "producer_monkeypatch_kernel_wrong_phi_preserved_derivative",
            "producer": "monkeypatched full_phi_kernel_counterexample before build",
            "independent_target": "literal phi0=e1 plus independent cross-product reconstruction",
            "detected": not _kernel_counterexample_accepts(kernel_wrong_phi),
        },
        {
            "id": "producer_monkeypatch_kernel_wrong_delta_q_preserved_derivative",
            "producer": "monkeypatched full_phi_kernel_counterexample before build",
            "independent_target": "literal delta_q=e3 plus independent cross-product reconstruction",
            "detected": not _kernel_counterexample_accepts(kernel_wrong_delta),
        },
        {
            "id": "producer_monkeypatch_BCH_zero_q_lambda_preserved_decomposition",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "structured q/lambda BCH reconstruction plus full fingerprint",
            "detected": not _no_go_contract_accepts(bch_zero_inputs),
        },
        {
            "id": "producer_monkeypatch_BCH_parallel_generators_preserved_decomposition",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "independent generator cross-product reconstruction",
            "detected": not _no_go_contract_accepts(bch_parallel),
        },
        {
            "id": "producer_monkeypatch_BCH_wrong_wavevector_preserved_decomposition",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "independent spectral-product reconstruction",
            "detected": not _no_go_contract_accepts(bch_wrong_wavevector),
        },
        {
            "id": "producer_monkeypatch_rank_generic_pair_zero_preserved_matrix",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "orbit matrix reconstructed from generic pair",
            "detected": not _no_go_contract_accepts(rank_generic_zero),
        },
        {
            "id": "producer_monkeypatch_rank_generic_pair_collinear_preserved_matrix",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "orbit rank reconstructed from collinear pair",
            "detected": not _no_go_contract_accepts(rank_generic_collinear),
        },
        {
            "id": "producer_monkeypatch_rank_zero_pair_generic_preserved_matrix",
            "producer": "monkeypatched finite_BCH_and_variable_rank_no_go before build",
            "independent_target": "zero-orbit matrix reconstructed from reported pair",
            "detected": not _no_go_contract_accepts(rank_zero_generic),
        },
    ]
    ids = {row["id"] for row in rows}
    return {
        "mutants": rows,
        "required_mutant_ids": sorted(REQUIRED_MUTANT_IDS),
        "observed_mutant_ids": sorted(ids),
        "producer_target_independence_declared_for_every_mutant": all(
            row["producer"] != row["independent_target"] for row in rows
        ),
        "pass": bool(
            ids == REQUIRED_MUTANT_IDS
            and all(row["detected"] is True for row in rows)
            and all(row["producer"] != row["independent_target"] for row in rows)
        ),
    }


def linked_prior_ledgers() -> dict[str, Any]:
    """Link prior exact ledgers as metadata; none is imported as a proof oracle."""

    return {
        "v5_6_6_16_finite_gauge_kernel_ledger": {
            "path": V56616_SOURCE.name,
            "expected_sha256": V56616_SOURCE_SHA256,
            "observed_sha256": _sha256(V56616_SOURCE),
            "role": "historical finite sampled evidence only",
            "imported_or_called": False,
        },
        "v5_6_6_8_restricted_green_ledger": {
            "path": V5668_SOURCE.name,
            "expected_sha256": V5668_SOURCE_SHA256,
            "observed_sha256": _sha256(V5668_SOURCE),
            "role": "historical restricted identity evidence only",
            "imported_or_called": False,
        },
        "v5_6_7_2_exact_affine_and_solder_ledgers": {
            "path": (
                "derive_one_omega_topological_so3_geometric_bulk_"
                "diffeomorphism_naturality_v5_6_7_2_gate.py"
            ),
            "committed_HEAD_blob_sha256": (
                "653f2826bc6fd6a0d197d47abd1a7f9fd9ddb0d705339b3b6bb89cd2574531b8"
            ),
            "evidence_commits": ["f600583", "5d0c5ff", "60aa1a0", "acd7787"],
            "role": "linked exact evidence only; dirty worktree copy deliberately ignored",
            "imported_or_called": False,
        },
        "this_gate_exact_identity_engine_is_independent": True,
    }


def _canonical_decision(
    *,
    pins: Mapping[str, Any],
    kernel: Mapping[str, Any],
    identities: Mapping[str, Any],
    routes: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    runtime: Mapping[str, Any],
    r_witness: Mapping[str, Any],
    no_go: Mapping[str, Any],
    mutants_pass: bool,
) -> dict[str, bool]:
    positives = {
        "byte_pinned_v5_6_7_1_and_exact_full_t4_source_contract_pass": bool(
            pins["pass"]
        ),
        "Q_frame_not_kernel_of_full_Phi_exact_e3_cross_e1_counterexample_pass": bool(
            kernel["pass"]
        ),
        "three_consumed_q_invariant_identities_exact_pass": bool(identities["pass"]),
        "twelve_bulk_two_GHY_six_interface_real_route_binding_pass": bool(
            routes["pass"]
        ),
        "q_zero_primal_and_tangent_canonicalized_before_decoder_and_so3_exp_pass": bool(
            wrapper["pass"]
            and runtime["hostile_representatives"][
                "original_v5_6_7_1_primal_rejected_before_section"
            ]
            and runtime["hostile_representatives"][
                "original_v5_6_7_1_tangent_rejected_before_section"
            ]
        ),
        "finite_quadrature_values_and_JVP_factor_through_q_zero_section_pass": bool(
            runtime["pass"]
        ),
        "r_plus_minus_preserved_and_nontrivial_witness_pass": bool(
            r_witness["pass"]
        ),
        "finite_N2_BCH_and_variable_rank_global_quotient_no_go_pass": bool(
            no_go["pass"]
        ),
        "independent_in_memory_runtime_and_source_mutant_campaign_pass": bool(
            mutants_pass
        ),
    }
    positives[
        "finite_Q_frame_q_zero_section_and_twenty_route_factorization_pass"
    ] = all(positives.values())
    return {**positives, **{key: False for key in sorted(FALSE_DECISION_KEYS)}}


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("schema") != SCHEMA:
        raise QFrameSectionGateError("report schema drift")
    decision = report.get("decision")
    if not isinstance(decision, Mapping) or not _decision_contract_accepts(decision):
        raise QFrameSectionGateError("decision true/false allowlist drift")
    kernel = report.get("full_Phi_kernel_counterexample")
    if not isinstance(kernel, Mapping) or not _kernel_counterexample_accepts(kernel):
        raise QFrameSectionGateError("full-Phi kernel counterexample drift")
    identities = report.get("three_exact_invariant_identities")
    if not isinstance(identities, Mapping) or not _identity_contract_accepts(identities):
        raise QFrameSectionGateError("exact invariant identity ledger drift")
    routes = report.get("twenty_real_action_routes")
    if not isinstance(routes, Mapping) or not _routes_accept(routes.get("routes", [])):
        raise QFrameSectionGateError("twenty real-route binding drift")
    if routes.get("counts") != {"bulk": 12, "GHY": 2, "interface": 6}:
        raise QFrameSectionGateError("twelve/two/six route count drift")
    no_go = report.get("finite_group_and_global_quotient_no_go")
    if not isinstance(no_go, Mapping) or not _no_go_contract_accepts(no_go):
        raise QFrameSectionGateError("BCH/rank no-go drift")
    runtime = report.get("finite_runtime_factorization_witness")
    if not isinstance(runtime, Mapping) or runtime.get("pass") is not True:
        raise QFrameSectionGateError("finite runtime factorization witness failed")
    if runtime.get("scope", {}).get("arbitrary_N_or_continuum_claimed") is not False:
        raise QFrameSectionGateError("finite runtime witness overclaimed its scope")
    r_witness = report.get("r_plus_minus_retention_witness")
    if not isinstance(r_witness, Mapping) or r_witness.get("pass") is not True:
        raise QFrameSectionGateError("r plus/minus retention witness failed")
    mutants = report.get("mutant_campaign")
    if not isinstance(mutants, Mapping) or mutants.get("pass") is not True:
        raise QFrameSectionGateError("mutant campaign failed")
    rows = mutants.get("mutants", [])
    if {row.get("id") for row in rows} != REQUIRED_MUTANT_IDS:
        raise QFrameSectionGateError("mutant allowlist drift")
    if not all(row.get("detected") is True for row in rows):
        raise QFrameSectionGateError("an expected mutant survived")
    if report.get("evidence_boundary", {}).get(
        "global_group_or_smooth_quotient_claimed"
    ) is not False:
        raise QFrameSectionGateError("global quotient evidence boundary drift")


def build_report() -> dict[str, Any]:
    pins = source_pin_and_target_contract()
    kernel = full_phi_kernel_counterexample()
    identities = exact_invariant_identity_ledger()
    routes = real_twenty_route_binding_ledger()
    wrapper = wrapper_source_contract()
    runtime = finite_runtime_factorization_witness()
    r_witness = r_plus_minus_retention_witness()
    no_go = finite_BCH_and_variable_rank_no_go()
    # Validate producer outputs against independent literal/reconstruction
    # contracts before any downstream report assembly or mutant setup indexes
    # into them.  A monkeypatched producer therefore fails with the gate's own
    # exception rather than leaking a shape-dependent Python exception.
    if not _kernel_counterexample_accepts(kernel):
        raise QFrameSectionGateError("kernel counterexample producer failed independent contract")
    if not _identity_contract_accepts(identities):
        raise QFrameSectionGateError("identity producer failed independent contract")
    if not _routes_accept(routes.get("routes", [])):
        raise QFrameSectionGateError("route producer failed independent contract")
    if not _no_go_contract_accepts(no_go):
        raise QFrameSectionGateError("NO-GO producer failed independent reconstruction contract")
    provisional_decision = _canonical_decision(
        pins=pins,
        kernel=kernel,
        identities=identities,
        routes=routes,
        wrapper=wrapper,
        runtime=runtime,
        r_witness=r_witness,
        no_go=no_go,
        mutants_pass=True,
    )
    mutants = mutant_campaign(
        runtime=runtime,
        r_witness=r_witness,
        kernel=kernel,
        identities=identities,
        routes=routes,
        no_go=no_go,
        canonical_decision=provisional_decision,
    )
    decision = _canonical_decision(
        pins=pins,
        kernel=kernel,
        identities=identities,
        routes=routes,
        wrapper=wrapper,
        runtime=runtime,
        r_witness=r_witness,
        no_go=no_go,
        mutants_pass=bool(mutants["pass"]),
    )
    report = {
        "schema": SCHEMA,
        "classification": (
            "finite_full_T4_coordinate_section;twenty_real_routes;exact_algebra;"
            "runtime_and_source_mutants;fail_closed_continuum_and_global_quotient"
        ),
        "scope": (
            "A coordinate-adapted q=0 section is applied to primal and tangent before "
            "the byte-pinned v5.6.7.1 decoder/action. Exact cancellations bind the "
            "twelve bulk, two GHY and six interface routes. Runtime equality is finite "
            "N=1,Q=1,G=1 evidence; the BCH N=2 and variable-rank witnesses are exact "
            "NO-GOs. Nothing here proves arbitrary-N, continuum, margins, a global "
            "smooth quotient, C1/N1, P4, B4, or B5."
        ),
        "source_pins_and_target_contract": pins,
        "linked_prior_evidence_not_used_as_oracle": linked_prior_ledgers(),
        "full_Phi_kernel_counterexample": kernel,
        "three_exact_invariant_identities": identities,
        "twenty_real_action_routes": routes,
        "predecoder_q_zero_wrapper_source_contract": wrapper,
        "finite_runtime_factorization_witness": runtime,
        "r_plus_minus_retention_witness": r_witness,
        "finite_group_and_global_quotient_no_go": no_go,
        "mutant_campaign": mutants,
        "evidence_boundary": {
            "finite_runtime_N_values": [1],
            "exact_BCH_counterexample_N_values": [2],
            "sampled_or_finite_evidence_is_arbitrary_N_theorem": False,
            "continuum_action_or_uniform_bridge_claimed": False,
            "global_group_or_smooth_quotient_claimed": False,
            "complete_kernel_or_constant_rank_claimed": False,
            "q_zero_is_only_coordinate_adapted_section": True,
            "r_plus_minus_unchanged_and_not_quotiented": True,
        },
        "decision": decision,
    }
    validate_report(report)
    return report


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
