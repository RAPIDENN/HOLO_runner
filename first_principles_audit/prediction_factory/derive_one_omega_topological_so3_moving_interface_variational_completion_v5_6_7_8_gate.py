#!/usr/bin/env python3
"""Exact moving-interface first-variation completion for classical v5.2.

This gate is deliberately analytic and local.  It does not use Route-C,
quadrature, a finite spectral family, or a uniform ``N -> infinity`` bridge.
It works on the selected smooth, trivial, null-homotopic bundle component of
the literal v5.2 action and on compactly supported variations on
``Sigma = R^(1,3)``.

The previous v5.6.7.2 ledger stopped at three precise obligations: the
intrinsic d4 current, the moving normal-embedding row, and the combination of
those rows with the two bulk Green forms.  This gate closes only the first
irreducible sub-obligation: the corrected intrinsic-curvature term.  It also
records, without accepting, the remaining candidate assembly.  The proved
microlemma uses:

* an exact second-jet Euler--Green product-rule normalizer;
* the corrected Gauss convention and the full variation of
  ``N sqrt(h) [xi Rcal - B4 Rcal^2/(16 k^2)]``;
The two outward-normal GHY rows, oriented BF ``b_plus-b_minus`` row,
tangential d4 current, and dependent normal-shape equation are shown as a
candidate ledger only.  They are not promoted because the displayed shape and
groupoid rows have not yet been derived from the literal action AST, and the
full K/a/Robin Euler coefficients have not yet been expanded.

The bulk top form is pulled back once.  Consequently ``i_xi L5`` occurs once,
as the Cartan boundary representative of that material pullback, and is never
appended a second time.  No Euler equation is imposed in any identity.

No artifact is written.  The report printed by ``main`` is a reproducible
proof ledger; its independent test keeps all expected normal forms local to
the test module.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCHEMA = (
    "holo.one-omega-topological-so3-moving-interface-variational-"
    "completion-v5-6-7-8.v1"
)

V52_SOURCE = HERE / "derive_one_omega_topological_so3_classical_v5_2_gate.py"
V52_TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"
V52_ARTIFACT = (
    HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
)
V5672_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_"
    "naturality_v5_6_7_2_gate.py"
)
V5672_TEST = (
    HERE
    / "test_one_omega_topological_so3_geometric_bulk_diffeomorphism_"
    "naturality_v5_6_7_2_gate.py"
)
GAUSS_SOURCE = (
    HERE / "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
)
GAUSS_TEST = (
    HERE / "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
)
GAUSS_ARTIFACT = (
    HERE / "artifacts" / "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"
)

PINNED_INPUTS = {
    V52_SOURCE.name: "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
    V52_TEST.name: "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    V52_ARTIFACT.name: "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    V5672_SOURCE.name: "23d04b2d8347dca513389e0b4d7c8e329405a2e2eb4989dd1238e0d6dbf2687b",
    V5672_TEST.name: "6a26693799d22dfcba338add59d72260ec61c72ffe969ed8cefbf59a920d7fe6",
    GAUSS_SOURCE.name: "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717",
    GAUSS_TEST.name: "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78",
    GAUSS_ARTIFACT.name: "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a",
}
PINNED_PATHS = {
    V52_SOURCE.name: V52_SOURCE,
    V52_TEST.name: V52_TEST,
    V52_ARTIFACT.name: V52_ARTIFACT,
    V5672_SOURCE.name: V5672_SOURCE,
    V5672_TEST.name: V5672_TEST,
    GAUSS_SOURCE.name: GAUSS_SOURCE,
    GAUSS_TEST.name: GAUSS_TEST,
    GAUSS_ARTIFACT.name: GAUSS_ARTIFACT,
}

# The exact source hash above is the state after these three independently
# audited milestones.  The labels are provenance, while the byte pin and the
# semantic decision checks below are the executable dependency binding.
MILESTONE_COMMITS = {
    "60aa1a0": "oriented BF incidence",
    "acd7787": "scoped literal Green ledger",
    "91abcc1": "compact-support differentiated interior bulk Ward",
}

EXPECTED_ACTION_COMPONENTS = (
    "EH_bulk_plus",
    "Omega_kinetic_bulk_plus",
    "Omega_potential_bulk_plus",
    "P_kinetic_bulk_plus",
    "full_V4_bulk_plus",
    "BF_bulk_plus",
    "GHY_plus",
    "EH_bulk_minus",
    "Omega_kinetic_bulk_minus",
    "Omega_potential_bulk_minus",
    "P_kinetic_bulk_minus",
    "full_V4_bulk_minus",
    "BF_bulk_minus",
    "GHY_minus",
    "wall",
    "K_foliation",
    "R",
    "R_squared",
    "a_squared",
    "Robin",
)

INDEPENDENT_VARIATION_ROLES = (
    "g_plus",
    "Omega_plus",
    "phi_plus",
    "A_plus",
    "B_plus",
    "g_minus",
    "Omega_minus",
    "phi_minus",
    "A_minus",
    "B_minus",
    "Y_plus",
    "Y_minus",
    "T",
    "iota_plus/j_plus",
    "iota_minus/j_minus",
)

TRUE_DECISION_KEYS = frozenset(
    {
        "corrected_intrinsic_Rcal_interface_variation_exact_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "uniform_N_to_infinity_bridge_pass",
        "bounded_margin_ball_weaker_jet_exact_formula_uniform_bridge_pass",
        "same_functional_symbolic_identity_pass",
        "continuum_action_representative_independence_theorem_pass",
        "global_smooth_physical_gauge_quotient_manifold_pass",
        "fixed_reference_S_rel_diffeomorphism_Ward_pass",
        "two_sided_bulk_GHY_interface_Green_pairing_exact_pass",
        "complete_v5_2_all_field_normal_embedding_pass",
        "complete_moving_embedding_Ward_pass",
        "full_off_shell_Green_theorem_selected_sector_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "unrestricted_large_gauge_sector_pass",
        "all_boundary_topologies_pass",
        "complete_BV_BFV_boundary_complex_pass",
        "global_BF_edge_mode_absence_pass",
        "C2_BRST_pass",
        "C3_DOMAIN_pass",
        "C4_HESSIAN_pass",
        "C5_JACOBIANS_pass",
        "C6_ZERO_MODES_pass",
        "C7_REGULATOR_pass",
        "C8_CONTOUR_pass",
        "C9_REDUCTION_pass",
        "C10_INDEPENDENCE_UNITARITY_pass",
        "N2_CONSTRAINTS_pass",
        "N3_CHARACTERISTICS_pass",
        "N4_JUNCTION_BENDING_pass",
        "N5_COUPLED_BVP_pass",
        "N6_GLOBAL_STABILITY_pass",
        "N7_LINEAR_REDUCTION_pass",
        "P4_full_same_action_pass",
        "nonlinear_gravitational_P4_pass",
        "full_P2_pass",
        "B4_pass",
        "B5_pass",
        "global_noncompact_action_finite_pass",
        "publication_authorized",
    }
)

MUTATIONS = (
    "wrong_Gauss_sign",
    "wrong_R2_derivative_factor",
    "wrong_Rcal_current_sign",
    "wrong_clock_Cartan_sign",
    "wrong_N_powers",
    "wrong_deltaN_sign",
    "wrong_projector",
    "wrong_chi",
    "wrong_deltaN",
    "zero_deltaN",
    "wrong_deltaU",
    "zero_deltaU",
    "wrong_deltaH",
    "zero_deltaH",
    "wrong_lapse_factor",
    "nonzero_shift_coefficient",
    "omit_clock_Cartan",
    "double_clock_Cartan",
    "zero_lift_witness",
    "omit_intrinsic_d4_current",
    "wrong_GHY_outward_sign",
    "wrong_BF_incidence",
    "omit_bulk_metric_variation",
    "omit_bulk_Omega_variation",
    "omit_bulk_phi_variation",
    "omit_bulk_A_variation",
    "omit_bulk_B_variation",
    "freeze_Y",
    "freeze_T",
    "omit_iota_j",
    "double_i_xi_L5",
    "impose_bulk_EOM",
    "impose_interface_EOM",
)


class MovingInterfaceV5678Error(ValueError):
    """A pinned dependency or exact normal form is malformed."""


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise MovingInterfaceV5678Error(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MovingInterfaceV5678Error(f"cannot read {path}: {exc}") from exc
    if type(value) is not dict:
        raise MovingInterfaceV5678Error(f"{path} is not a JSON object")
    return value


_WARD_CACHE: dict[str, dict[str, Any]] = {}


def _load_ward_report(source_hash: str) -> dict[str, Any]:
    """Execute the byte-pinned producer, cached only under its observed hash."""

    if source_hash in _WARD_CACHE:
        return _WARD_CACHE[source_hash]
    module_name = f"_v5672_dependency_{source_hash[:16]}"
    spec = importlib.util.spec_from_file_location(module_name, V5672_SOURCE)
    if spec is None or spec.loader is None:
        raise MovingInterfaceV5678Error("cannot load v5.6.7.2 dependency")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        report = module.build_report()
    finally:
        sys.modules.pop(module_name, None)
    if type(report) is not dict:
        raise MovingInterfaceV5678Error("v5.6.7.2 returned no report")
    _WARD_CACHE[source_hash] = report
    return report


def _dependency_certificate() -> dict[str, Any]:
    observed = {name: _sha256(path) for name, path in PINNED_PATHS.items()}
    matches = {name: observed[name] == expected for name, expected in PINNED_INPUTS.items()}
    if not all(matches.values()):
        bad = {name: observed[name] for name, ok in matches.items() if not ok}
        raise MovingInterfaceV5678Error(f"pinned dependency drift: {bad}")

    v52 = _read_json(V52_ARTIFACT)
    gauss = _read_json(GAUSS_ARTIFACT)
    ward = _load_ward_report(observed[V5672_SOURCE.name])

    if v52.get("schema") != "holo.one-omega-topological-so3-classical-v5-2-gate.v1":
        raise MovingInterfaceV5678Error("v5.2 schema drift")
    exact_action = v52.get("exact_classical_charter", {}).get("exact_action")
    if type(exact_action) is not dict:
        raise MovingInterfaceV5678Error("v5.2 exact action missing")
    if _canonical_sha256(exact_action) != (
        "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
    ):
        raise MovingInterfaceV5678Error("v5.2 canonical action drift")
    expected_foliation_literal = (
        "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*[Kcal_mu_nu*Kcal^mu_nu-"
        "lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        "B4_bar*Rcal^2/(16*k_infinity^2)]"
    )
    if exact_action.get("foliation_lower") != expected_foliation_literal:
        raise MovingInterfaceV5678Error("v5.2 intrinsic-curvature literal drift")
    for key in (
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "full_classical_variational_principle_selected_sector_pass",
    ):
        if v52.get("decision", {}).get(key) is not False:
            raise MovingInterfaceV5678Error(f"v5.2 prior hold changed: {key}")

    if gauss.get("schema") != (
        "holo.one-omega-topological-so3-v5-5-4-gauss-sign-corrigendum.v1"
    ):
        raise MovingInterfaceV5678Error("Gauss corrigendum schema drift")
    gauss_formula = gauss.get("conventions", {}).get("correct_Gauss_scalar")
    expected_gauss = (
        "R_leaf=h^ac h^bd R_abcd-K^2+K_ab K^ab="
        "R4+2 Ricci(u,u)-K^2+K_ab K^ab"
    )
    if gauss_formula != expected_gauss:
        raise MovingInterfaceV5678Error("corrected Gauss formula drift")
    if gauss.get("decision", {}).get("corrected_action_route_execution_authorized") is not True:
        raise MovingInterfaceV5678Error("Gauss corrected route not authorized")
    if gauss.get("decision", {}).get("v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma") is not False:
        raise MovingInterfaceV5678Error("bad v5.5.4 route became consumable")
    try:
        flat = gauss["manufactured_witnesses"]["flat_FLRW"]
        sphere = gauss["manufactured_witnesses"]["static_round_S3"]
        gauss_witnesses_exact = bool(
            all(flat["checks"].values())
            and all(sphere["checks"].values())
            and flat["correct_intrinsic_R_leaf"]["numerator"] == 0
            and flat["v5_5_4_inherited_combination"]["numerator"] != 0
            and sphere["correct_intrinsic_R_leaf"]["numerator"] == 8
            and sphere["correct_intrinsic_R_leaf"]["denominator"] == 3
        )
    except (KeyError, TypeError) as exc:
        raise MovingInterfaceV5678Error("Gauss exact witnesses missing") from exc
    if not gauss_witnesses_exact:
        raise MovingInterfaceV5678Error("Gauss exact witnesses failed")

    ward_decision = ward.get("decision", {})
    required_true = (
        "differentiated_smooth_compact_support_bulk_Ward_identity_exact_pass",
        "literal_bulk_interface_Green_ledger_pass",
        "oriented_BF_incidence_aggregation_exact_pass",
        "finite_full_affine_connection_trace_transport_exact_pass",
        "finite_associated_matter_solder_groupoid_word_covariance_exact_pass",
    )
    required_false = (
        "complete_moving_embedding_Ward_pass",
        "complete_v5_2_all_field_normal_embedding_pass",
        "full_off_shell_Green_theorem_accepted",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
    )
    if any(ward_decision.get(key) is not True for key in required_true):
        raise MovingInterfaceV5678Error("v5.6.7.2 required positive scope drift")
    if any(ward_decision.get(key) is not False for key in required_false):
        raise MovingInterfaceV5678Error("v5.6.7.2 fail-closed scope drift")
    green = ward.get("literal_bulk_interface_Green_ledger", {})
    bf = ward.get("oriented_BF_incidence_aggregation", {})
    if green.get("component_count_with_multiplicity") != 20 or green.get("pass") is not True:
        raise MovingInterfaceV5678Error("v5.6.7.2 Green inventory drift")
    if tuple(tuple(row) for row in bf.get("oriented_boundary_integrand_terms", ())) != (
        ("b_minus_wedge_Delta_A_Sigma", 1),
        ("b_plus_wedge_Delta_A_Sigma", -1),
    ):
        raise MovingInterfaceV5678Error("v5.6.7.2 BF incidence drift")

    return {
        "pass": True,
        "expected": dict(PINNED_INPUTS),
        "observed": observed,
        "matches": matches,
        "milestone_commits": dict(MILESTONE_COMMITS),
        "v5_2_canonical_exact_action_sha256": _canonical_sha256(exact_action),
        "v5_2_foliation_literal": exact_action["foliation_lower"],
        "expected_v5_2_foliation_literal": expected_foliation_literal,
        "intrinsic_f_monomials_read_from_v5_2_literal": [
            ["xi", 1, 1],
            ["-B4/(16*k^2)", 1, 2],
        ],
        "intrinsic_df_dR_monomials_from_exponent_rule": [
            ["xi", 1, 0],
            ["-B4/(16*k^2)", 2, 1],
        ],
        "intrinsic_df_dR_formula_from_v5_2_literal": "xi-B4*Rcal/(8*k^2)",
        "v5_2_prior_C1_N1_hold_consumed": True,
        "v5_6_7_2_positive_keys_consumed": list(required_true),
        "v5_6_7_2_open_keys_consumed": list(required_false),
        "Gauss_corrigendum_consumed": True,
        "correct_Gauss_formula": gauss_formula,
        "correct_Gauss_formula_normalized": (
            "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab"
        ),
        "Gauss_exact_witnesses_consumed": gauss_witnesses_exact,
        "wrong_v5_5_4_primary_or_redteam_consumed_as_lemma": False,
    }


# A normalized monomial is
#   (coefficient-atom, derivative multi-index of coefficient,
#    variation-atom, derivative multi-index of variation).
# Every coefficient is exact Fraction arithmetic.
Monomial = tuple[str, tuple[int, ...], str, tuple[int, ...]]
Polynomial = dict[Monomial, Fraction]


def _add_term(poly: Polynomial, monomial: Monomial, coefficient: Fraction) -> None:
    value = poly.get(monomial, Fraction(0)) + coefficient
    if value:
        poly[monomial] = value
    else:
        poly.pop(monomial, None)


def _add_polynomials(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            _add_term(result, monomial, coefficient)
    return result


def _scale_polynomial(value: Polynomial, factor: Fraction) -> Polynomial:
    return {monomial: factor * coefficient for monomial, coefficient in value.items() if factor * coefficient}


def _differentiate_polynomial(value: Polynomial, direction: int) -> Polynomial:
    result: Polynomial = {}
    for (coefficient_atom, coefficient_derivatives, variation, variation_derivatives), coefficient in value.items():
        _add_term(
            result,
            (
                coefficient_atom,
                tuple(sorted(coefficient_derivatives + (direction,))),
                variation,
                variation_derivatives,
            ),
            coefficient,
        )
        _add_term(
            result,
            (
                coefficient_atom,
                coefficient_derivatives,
                variation,
                tuple(sorted(variation_derivatives + (direction,))),
            ),
            coefficient,
        )
    return result


def _polynomial_rows(value: Polynomial) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": [coefficient.numerator, coefficient.denominator],
            "coefficient_atom": monomial[0],
            "coefficient_derivatives": list(monomial[1]),
            "variation": monomial[2],
            "variation_derivatives": list(monomial[3]),
        }
        for monomial, coefficient in sorted(value.items())
    ]


def _second_jet_euler_green_identity(
    field: str,
    order: int,
    *,
    dimension: int,
    mutation: str | None = None,
) -> dict[str, Any]:
    """Prove delta L = E delta q + d theta for an arbitrary order <= 2 L."""

    if order not in (0, 1, 2) or dimension <= 0:
        raise MovingInterfaceV5678Error("unsupported jet order/dimension")
    raw: Polynomial = {}
    euler_times_delta: Polynomial = {}
    theta_by_direction: list[Polynomial] = [dict() for _ in range(dimension)]

    p0: Monomial = (f"dL/d{field}", (), f"Delta_{field}", ())
    _add_term(raw, p0, Fraction(1))
    _add_term(euler_times_delta, p0, Fraction(1))

    if order >= 1:
        for mu in range(dimension):
            p1_raw = (f"dL/dD{mu}_{field}", (), f"Delta_{field}", (mu,))
            p1_euler = (f"dL/dD{mu}_{field}", (mu,), f"Delta_{field}", ())
            p1_theta = (f"dL/dD{mu}_{field}", (), f"Delta_{field}", ())
            _add_term(raw, p1_raw, Fraction(1))
            _add_term(euler_times_delta, p1_euler, Fraction(-1))
            _add_term(
                theta_by_direction[mu],
                p1_theta,
                Fraction(-1) if mutation == "flip_first_jet_current" else Fraction(1),
            )

    if order >= 2:
        for mu in range(dimension):
            for nu in range(dimension):
                # Mixed jet coordinates commute.  Canonicalising the index
                # pair is essential: it is precisely what cancels the two
                # cross-product terms in the summed Green current.
                lo, hi = sorted((mu, nu))
                atom = f"dL/dD{lo}D{hi}_{field}"
                _add_term(raw, (atom, (), f"Delta_{field}", tuple(sorted((mu, nu)))), Fraction(1))
                _add_term(euler_times_delta, (atom, tuple(sorted((mu, nu))), f"Delta_{field}", ()), Fraction(1))
                if mutation != "omit_second_jet_current_derivative":
                    _add_term(theta_by_direction[mu], (atom, (nu,), f"Delta_{field}", ()), Fraction(-1))
                _add_term(theta_by_direction[mu], (atom, (), f"Delta_{field}", (nu,)), Fraction(1))

    divergence: Polynomial = {}
    for mu, current in enumerate(theta_by_direction):
        divergence = _add_polynomials(divergence, _differentiate_polynomial(current, mu))
    reconstructed = _add_polynomials(euler_times_delta, divergence)
    residual = _add_polynomials(raw, _scale_polynomial(reconstructed, Fraction(-1)))
    return {
        "field": field,
        "jet_order": order,
        "dimension": dimension,
        "raw_first_variation": _polynomial_rows(raw),
        "Euler_times_variation": _polynomial_rows(euler_times_delta),
        "boundary_current_by_direction": [_polynomial_rows(row) for row in theta_by_direction],
        "reconstructed_first_variation": _polynomial_rows(reconstructed),
        "normalized_residual": _polynomial_rows(residual),
        "exact_pass": not residual,
        "uses_floating_point": False,
        "Euler_equation_imposed": False,
    }


def _field_jet_rows(mutation: str | None = None) -> tuple[tuple[str, str, int, int], ...]:
    """Derive the local jet orders from the literal component dependency graph."""

    rows: list[tuple[str, str, int, int]] = []
    for side in ("plus", "minus"):
        rows.extend(
            [
                (f"EH_bulk_{side}", f"g_{side}", 2, 5),
                (f"Omega_kinetic_bulk_{side}", f"g_{side}", 0, 5),
                (f"Omega_kinetic_bulk_{side}", f"Omega_{side}", 1, 5),
                (f"Omega_potential_bulk_{side}", f"g_{side}", 0, 5),
                (f"Omega_potential_bulk_{side}", f"Omega_{side}", 0, 5),
                (f"P_kinetic_bulk_{side}", f"g_{side}", 0, 5),
                (f"P_kinetic_bulk_{side}", f"Omega_{side}", 1, 5),
                (f"P_kinetic_bulk_{side}", f"phi_{side}", 1, 5),
                (f"P_kinetic_bulk_{side}", f"A_{side}", 0, 5),
                (f"full_V4_bulk_{side}", f"g_{side}", 0, 5),
                (f"full_V4_bulk_{side}", f"Omega_{side}", 0, 5),
                (f"full_V4_bulk_{side}", f"phi_{side}", 0, 5),
                (f"BF_bulk_{side}", f"A_{side}", 1, 5),
                (f"BF_bulk_{side}", f"B_{side}", 0, 5),
                (f"GHY_{side}", "gamma", 1, 4),
                (f"GHY_{side}", f"Y_{side}", 2, 4),
            ]
        )
    rows.extend(
        [
            ("wall", "gamma", 0, 4),
            ("wall", "Omega_Sigma", 0, 4),
            ("K_foliation", "gamma", 1, 4),
            ("K_foliation", "T", 2, 4),
            ("R", "gamma", 2, 4),
            ("R", "T", 2, 4),
            ("R_squared", "gamma", 2, 4),
            ("R_squared", "T", 2, 4),
            ("a_squared", "gamma", 1, 4),
            ("a_squared", "T", 2, 4),
            ("Robin", "gamma", 1, 4),
            ("Robin", "T", 2, 4),
            ("Robin", "varphi_H", 0, 4),
        ]
    )
    omitted_by_mutation = {
        "omit_bulk_metric_variation": {"g_plus", "g_minus"},
        "omit_bulk_Omega_variation": {"Omega_plus", "Omega_minus"},
        "omit_bulk_phi_variation": {"phi_plus", "phi_minus"},
        "omit_bulk_A_variation": {"A_plus", "A_minus"},
        "omit_bulk_B_variation": {"B_plus", "B_minus"},
        "freeze_T": {"T"},
        "freeze_Y": {"Y_plus", "Y_minus"},
    }.get(mutation, set())
    return tuple(row for row in rows if row[1] not in omitted_by_mutation)


def _expected_field_jet_rows() -> tuple[tuple[str, str, int, int], ...]:
    """Independent literal target, intentionally not derived by the producer."""

    plus_minus: list[tuple[str, str, int, int]] = []
    for label in ("plus", "minus"):
        plus_minus += [
            ("EH_bulk_" + label, "g_" + label, 2, 5),
            ("Omega_kinetic_bulk_" + label, "g_" + label, 0, 5),
            ("Omega_kinetic_bulk_" + label, "Omega_" + label, 1, 5),
            ("Omega_potential_bulk_" + label, "g_" + label, 0, 5),
            ("Omega_potential_bulk_" + label, "Omega_" + label, 0, 5),
            ("P_kinetic_bulk_" + label, "g_" + label, 0, 5),
            ("P_kinetic_bulk_" + label, "Omega_" + label, 1, 5),
            ("P_kinetic_bulk_" + label, "phi_" + label, 1, 5),
            ("P_kinetic_bulk_" + label, "A_" + label, 0, 5),
            ("full_V4_bulk_" + label, "g_" + label, 0, 5),
            ("full_V4_bulk_" + label, "Omega_" + label, 0, 5),
            ("full_V4_bulk_" + label, "phi_" + label, 0, 5),
            ("BF_bulk_" + label, "A_" + label, 1, 5),
            ("BF_bulk_" + label, "B_" + label, 0, 5),
            ("GHY_" + label, "gamma", 1, 4),
            ("GHY_" + label, "Y_" + label, 2, 4),
        ]
    interface = [
        ("wall", "gamma", 0, 4),
        ("wall", "Omega_Sigma", 0, 4),
        ("K_foliation", "gamma", 1, 4),
        ("K_foliation", "T", 2, 4),
        ("R", "gamma", 2, 4),
        ("R", "T", 2, 4),
        ("R_squared", "gamma", 2, 4),
        ("R_squared", "T", 2, 4),
        ("a_squared", "gamma", 1, 4),
        ("a_squared", "T", 2, 4),
        ("Robin", "gamma", 1, 4),
        ("Robin", "T", 2, 4),
        ("Robin", "varphi_H", 0, 4),
    ]
    return tuple(plus_minus + interface)


def _universal_euler_green_certificate(mutation: str | None) -> dict[str, Any]:
    rows = _field_jet_rows(mutation)
    proofs = []
    for component, field, order, dimension in rows:
        local_mutation = None
        if mutation == "omit_intrinsic_d4_current" and component == "R_squared" and field == "gamma":
            local_mutation = "omit_second_jet_current_derivative"
        proof = _second_jet_euler_green_identity(
            field,
            order,
            dimension=dimension,
            mutation=local_mutation,
        )
        proofs.append({"component": component, **proof})
    return {
        "actual_field_jet_rows": [list(row) for row in rows],
        "independent_expected_field_jet_rows": [list(row) for row in _expected_field_jet_rows()],
        "field_jet_rows_exact": rows == _expected_field_jet_rows(),
        "proof_count": len(proofs),
        "all_normalized_residuals_zero": all(row["exact_pass"] for row in proofs),
        "no_Euler_equation_imposed": all(not row["Euler_equation_imposed"] for row in proofs),
        "proofs": proofs,
    }


def _poly_derivative_terms(mutation: str | None) -> dict[str, Any]:
    """Differentiate f(R)=xi R-B4 R^2/(16 k^2) by its monomial exponents."""

    monomials = (
        ("xi", 1, 1),
        ("-B4/(16*k^2)", 1, 2),
    )
    derivative = []
    for coefficient, multiplier, power in monomials:
        derived_multiplier = multiplier * power
        if mutation == "wrong_R2_derivative_factor" and power == 2:
            derived_multiplier = multiplier
        derivative.append((coefficient, derived_multiplier, power - 1))
    return {
        "f_monomials": [list(row) for row in monomials],
        "df_dR_monomials": [list(row) for row in derivative],
        "f_formula": "xi*Rcal-B4*Rcal^2/(16*k^2)",
        "df_dR_formula": (
            "xi-B4*Rcal/(16*k^2)"
            if mutation == "wrong_R2_derivative_factor"
            else "xi-B4*Rcal/(8*k^2)"
        ),
    }


SymbolicProduct = tuple[str, ...]


def _symbolic_add(
    polynomial: dict[SymbolicProduct, int],
    coefficient: int,
    *factors: str,
) -> None:
    monomial = tuple(sorted(factors))
    value = polynomial.get(monomial, 0) + coefficient
    if value:
        polynomial[monomial] = value
    else:
        polynomial.pop(monomial, None)


def _symbolic_Rcal_product_rule(current_sign: int) -> dict[str, Any]:
    """Expand the Rcal IBP identity as a free polynomial in 3D jets.

    Dummy sums are enumerated in the actual leaf dimension.  Symmetry of
    ``H_ij``, ``D_i D_j a`` and commuting derivative indices is encoded only
    by canonical atom names; no numerical substitution is used.
    """

    dimension = 3

    def pair(i: int, j: int) -> str:
        return f"{min(i, j)}{max(i, j)}"

    def a0() -> str:
        return "a"

    def da(i: int) -> str:
        return f"Da_{i}"

    def dda(i: int, j: int) -> str:
        return f"DDa_{pair(i, j)}"

    def h(i: int, j: int) -> str:
        return f"H_{pair(i, j)}"

    def dh(k: int, i: int, j: int) -> str:
        return f"DH_{k}_{pair(i, j)}"

    def ddh(k: int, l: int, i: int, j: int) -> str:
        return f"DDH_{pair(k, l)}_{pair(i, j)}"

    raw: dict[SymbolicProduct, int] = {}
    bulk: dict[SymbolicProduct, int] = {}
    divergence: dict[SymbolicProduct, int] = {}
    for i in range(dimension):
        for j in range(dimension):
            # a (D_i D_j H_ij - D_i D_i H_jj)
            _symbolic_add(raw, 1, a0(), ddh(i, j, i, j))
            _symbolic_add(raw, -1, a0(), ddh(i, i, j, j))
            # [(D_iD_j a)H_ij-(D_iD_i a)H_jj]
            _symbolic_add(bulk, 1, dda(i, j), h(i, j))
            _symbolic_add(bulk, -1, dda(i, i), h(j, j))
            # D_i[a D_jH_ij-a D_iH_jj-(D_j a)H_ij+(D_i a)H_jj]
            _symbolic_add(divergence, current_sign, da(i), dh(j, i, j))
            _symbolic_add(divergence, current_sign, a0(), ddh(i, j, i, j))
            _symbolic_add(divergence, -current_sign, da(i), dh(i, j, j))
            _symbolic_add(divergence, -current_sign, a0(), ddh(i, i, j, j))
            _symbolic_add(divergence, -current_sign, dda(i, j), h(i, j))
            _symbolic_add(divergence, -current_sign, da(j), dh(i, i, j))
            _symbolic_add(divergence, current_sign, dda(i, i), h(j, j))
            _symbolic_add(divergence, current_sign, da(i), dh(i, j, j))

    residual = dict(raw)
    for monomial, coefficient in bulk.items():
        _symbolic_add(residual, -coefficient, *monomial)
    for monomial, coefficient in divergence.items():
        _symbolic_add(residual, -coefficient, *monomial)
    render = lambda value: [
        {"coefficient": coefficient, "factors": list(monomial)}
        for monomial, coefficient in sorted(value.items())
    ]
    return {
        "leaf_dimension": dimension,
        "raw": render(raw),
        "bulk_after_IBP": render(bulk),
        "expanded_divergence": render(divergence),
        "normalized_residual": render(residual),
        "free_polynomial_identity_exact_pass": not residual,
        "numeric_values_substituted": False,
    }


LinearMonomial = tuple[int, str]
LinearForm = dict[LinearMonomial, Fraction]


def _linear_form(*terms: tuple[Fraction | int, int, str]) -> LinearForm:
    """Return a free Laurent-linear form in the invertible symbol ``N``."""

    result: LinearForm = {}
    for coefficient, n_power, atom in terms:
        key = (int(n_power), str(atom))
        value = result.get(key, Fraction(0)) + Fraction(coefficient)
        if value:
            result[key] = value
        else:
            result.pop(key, None)
    return result


def _linear_add(*forms: LinearForm) -> LinearForm:
    terms = []
    for form in forms:
        terms.extend((coefficient, n_power, atom) for (n_power, atom), coefficient in form.items())
    return _linear_form(*terms)


def _linear_scale(form: LinearForm, coefficient: Fraction | int, n_power: int = 0) -> LinearForm:
    factor = Fraction(coefficient)
    return _linear_form(
        *((factor * value, power + n_power, atom) for (power, atom), value in form.items())
    )


def _linear_residual(actual: LinearForm, expected: LinearForm) -> LinearForm:
    return _linear_add(actual, _linear_scale(expected, -1))


def _linear_rows(form: LinearForm) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": [coefficient.numerator, coefficient.denominator],
            "N_power": n_power,
            "atom": atom,
        }
        for (n_power, atom), coefficient in sorted(
            form.items(), key=lambda item: (item[0][1], item[0][0])
        )
    ]


def _linear_evaluate(
    form: LinearForm,
    N_value: Fraction,
    atom_values: Mapping[str, Fraction],
) -> Fraction:
    return sum(
        (
            coefficient
            * (N_value ** n_power)
            * atom_values.get(atom, Fraction(0))
        )
        for (n_power, atom), coefficient in form.items()
    )


def _clock_metric_lift_certificate(mutation: str | None) -> dict[str, Any]:
    """Free exact lift of arbitrary ``(delta gamma, delta T)`` to ADM data.

    The calculation is performed in a pointwise orthonormal leaf frame, but
    ``N`` remains an invertible Laurent indeterminate.  The components
    ``H_uu``, ``H_ui``, ``H_ij``, ``u(tau)`` and ``D_i tau`` are independent
    generators; no flat, zero-shift, or ``N=1`` specialization is made.
    """

    Huu = _linear_form((1, 0, "H_uu"))
    Utau = _linear_form((1, 0, "U_tau"))
    tau = _linear_form((1, 0, "tau"))

    # X=-g^{-1}(dT,dT)=N^-2.  For H=delta g and tau=delta T,
    # delta X=N^-2 H_uu+2 N^-1 u(tau), hence
    # delta N=-(N^3/2) delta X.
    delta_X = _linear_form((1, -2, "H_uu"), (2, -1, "U_tau"))
    chain_power = 2 if mutation == "wrong_N_powers" else 3
    delta_N = _linear_scale(delta_X, Fraction(-1, 2), chain_power)
    if mutation == "wrong_deltaN_sign":
        delta_N = _linear_scale(delta_N, -1)
    elif mutation == "wrong_deltaN":
        delta_N = _linear_add(delta_N, _linear_form((1, 0, "U_tau")))
    elif mutation == "zero_deltaN":
        delta_N = {}
    expected_delta_N = _linear_form(
        (Fraction(-1, 2), 1, "H_uu"),
        (-1, 2, "U_tau"),
    )

    # delta u_mu=(delta N/N)u_mu-N D_mu tau and
    # D_mu tau=Dperp_mu tau-u_mu u(tau).
    delta_u_parallel = _linear_add(
        _linear_scale(delta_N, 1, -1),
        _linear_scale(Utau, 1, 1),
    )
    delta_u_spatial = {
        i: _linear_form((-1, 1, f"D_tau_{i}")) for i in range(3)
    }
    if mutation == "wrong_projector":
        delta_u_spatial = {
            i: _linear_form((1, 1, f"D_tau_{i}")) for i in range(3)
        }
    elif mutation == "wrong_deltaU":
        delta_u_parallel = _linear_add(
            delta_u_parallel, _linear_form((1, 1, "U_tau"))
        )
    elif mutation == "zero_deltaU":
        delta_u_parallel = {}
        delta_u_spatial = {i: {} for i in range(3)}
    expected_delta_u_parallel = _linear_form((Fraction(-1, 2), 0, "H_uu"))
    expected_delta_u_spatial = {
        i: _linear_form((-1, 1, f"D_tau_{i}")) for i in range(3)
    }

    # u.delta u is minus the coefficient of u_mu.  Projecting
    # delta h=H+u delta u+delta u u gives the complete independent rows.
    u_dot_delta_u = _linear_scale(delta_u_parallel, -1)
    delta_h_uu = _linear_add(Huu, _linear_scale(u_dot_delta_u, -2))
    delta_h_ui = {
        i: _linear_add(
            _linear_form((1, 0, f"H_ui_{i}")),
            _linear_scale(delta_u_spatial[i], -1),
        )
        for i in range(3)
    }
    delta_h_ij = {
        f"{i}{j}": _linear_form((1, 0, f"H_ij_{i}{j}"))
        for i in range(3)
        for j in range(i, 3)
    }
    if mutation == "wrong_deltaH":
        delta_h_uu = _linear_add(delta_h_uu, Huu)
        delta_h_ui[0] = _linear_scale(delta_h_ui[0], -1)
    elif mutation == "zero_deltaH":
        delta_h_uu = {}
        delta_h_ui = {i: {} for i in range(3)}
        delta_h_ij = {key: {} for key in delta_h_ij}
    expected_delta_h_uu: LinearForm = {}
    expected_delta_h_ui = {
        i: _linear_form(
            (1, 0, f"H_ui_{i}"),
            (1, 1, f"D_tau_{i}"),
        )
        for i in range(3)
    }
    expected_delta_h_ij = {
        f"{i}{j}": _linear_form((1, 0, f"H_ij_{i}{j}"))
        for i in range(3)
        for j in range(i, 3)
    }
    unit_residual = _linear_add(
        _linear_scale(Huu, -1),
        _linear_scale(u_dot_delta_u, 2),
    )

    # Gauge-fix the arbitrary clock perturbation with chi=c N^p tau u.
    # Nominally c=-1,p=1.  Since u(T)=N^-1, tau+L_chi T=0 exactly.
    chi_coefficient = 1 if mutation == "wrong_chi" else -1
    chi_N_power = 2 if mutation == "wrong_N_powers" else 1
    chi_along_u = _linear_form((chi_coefficient, chi_N_power, "tau"))
    lie_chi_T = _linear_scale(chi_along_u, 1, -1)
    delta_prime_T = _linear_add(tau, lie_chi_T)

    # With A_tau=tau*u(log N), a_tau_i=tau*D_i(log N), and
    # tau_K_ij=tau*K_ij, L_chi g has all three independent projections.
    lie_metric_uu = _linear_form(
        (-2 * chi_coefficient, chi_N_power, "U_tau"),
        (-2 * chi_coefficient * chi_N_power, chi_N_power, "A_tau"),
    )
    lie_metric_ui = {
        i: _linear_form(
            (-chi_coefficient, chi_N_power, f"D_tau_{i}"),
            (chi_coefficient * (1 - chi_N_power), chi_N_power, f"a_tau_{i}"),
        )
        for i in range(3)
    }
    lie_metric_ij = {
        f"{i}{j}": _linear_form(
            (2 * chi_coefficient, chi_N_power, f"tau_K_{i}{j}")
        )
        for i in range(3)
        for j in range(i, 3)
    }
    H_prime_uu = _linear_add(Huu, lie_metric_uu)
    H_prime_ui = {
        i: _linear_add(
            _linear_form((1, 0, f"H_ui_{i}")), lie_metric_ui[i]
        )
        for i in range(3)
    }
    H_prime_ij = {
        key: _linear_add(
            _linear_form((1, 0, f"H_ij_{key}")), lie_metric_ij[key]
        )
        for key in lie_metric_ij
    }
    expected_H_prime_uu = _linear_form(
        (1, 0, "H_uu"),
        (2, 1, "U_tau"),
        (2, 1, "A_tau"),
    )
    expected_H_prime_ui = {
        i: _linear_form((1, 0, f"H_ui_{i}"), (1, 1, f"D_tau_{i}"))
        for i in range(3)
    }
    expected_H_prime_ij = {
        f"{i}{j}": _linear_form(
            (1, 0, f"H_ij_{i}{j}"),
            (-2, 1, f"tau_K_{i}{j}"),
        )
        for i in range(3)
        for j in range(i, 3)
    }

    # Fixed-clock ADM coordinates are algebraically independent:
    # n=-H'_uu/2, v_i=N H'_ui, Q_ij=H'_ij.  In particular v_i is
    # general even though its Euler coefficient in N sqrt(h) f(R[h]) is zero.
    adm_lapse_n = _linear_scale(H_prime_uu, Fraction(-1, 2))
    adm_shift_lower = {
        i: _linear_scale(H_prime_ui[i], 1, 1) for i in range(3)
    }
    adm_metric = dict(H_prime_ij)
    lie_chi_N = _linear_form((chi_coefficient, chi_N_power + 1, "A_tau"))
    gauge_lapse_residual = _linear_residual(
        _linear_add(delta_N, lie_chi_N),
        _linear_scale(adm_lapse_n, 1, 1),
    )

    residuals: dict[str, LinearForm] = {
        "delta_N_from_normalization": _linear_residual(delta_N, expected_delta_N),
        "delta_u_parallel": _linear_residual(
            delta_u_parallel, expected_delta_u_parallel
        ),
        "delta_h_uu": _linear_residual(delta_h_uu, expected_delta_h_uu),
        "unit_constraint": unit_residual,
        "chi_sets_delta_prime_T_to_zero": delta_prime_T,
        "gauge_lapse_compatibility": gauge_lapse_residual,
        "H_prime_uu": _linear_residual(H_prime_uu, expected_H_prime_uu),
    }
    for i in range(3):
        residuals[f"delta_u_spatial_{i}"] = _linear_residual(
            delta_u_spatial[i], expected_delta_u_spatial[i]
        )
        residuals[f"delta_h_ui_{i}"] = _linear_residual(
            delta_h_ui[i], expected_delta_h_ui[i]
        )
        residuals[f"H_prime_ui_{i}"] = _linear_residual(
            H_prime_ui[i], expected_H_prime_ui[i]
        )
    for key in delta_h_ij:
        residuals[f"delta_h_ij_{key}"] = _linear_residual(
            delta_h_ij[key], expected_delta_h_ij[key]
        )
        residuals[f"H_prime_ij_{key}"] = _linear_residual(
            H_prime_ij[key], expected_H_prime_ij[key]
        )

    normal_forms = {
        "delta_X": _linear_rows(delta_X),
        "delta_N": _linear_rows(delta_N),
        "delta_u_parallel_coefficient_of_u_covector": _linear_rows(delta_u_parallel),
        "delta_u_spatial": {
            str(i): _linear_rows(delta_u_spatial[i]) for i in range(3)
        },
        "u_dot_delta_u": _linear_rows(u_dot_delta_u),
        "delta_h_uu": _linear_rows(delta_h_uu),
        "delta_h_ui": {str(i): _linear_rows(delta_h_ui[i]) for i in range(3)},
        "delta_h_ij": {key: _linear_rows(value) for key, value in delta_h_ij.items()},
        "chi_along_u": _linear_rows(chi_along_u),
        "Lie_chi_T": _linear_rows(lie_chi_T),
        "delta_prime_T": _linear_rows(delta_prime_T),
        "H_prime_uu": _linear_rows(H_prime_uu),
        "H_prime_ui": {str(i): _linear_rows(H_prime_ui[i]) for i in range(3)},
        "H_prime_ij": {key: _linear_rows(value) for key, value in H_prime_ij.items()},
        "ADM_lapse_n": _linear_rows(adm_lapse_n),
        "ADM_shift_lower": {
            str(i): _linear_rows(adm_shift_lower[i]) for i in range(3)
        },
        "ADM_spatial_metric_Q": {
            key: _linear_rows(value) for key, value in adm_metric.items()
        },
    }

    witness_N = Fraction(7, 3)
    atom_values = {
        "H_uu": Fraction(5, 7),
        "U_tau": Fraction(-3, 11),
        "A_tau": Fraction(2, 13),
        "tau": Fraction(4, 17),
        **{f"H_ui_{i}": Fraction(((-1) ** i) * (i + 2), 5 + 2 * i) for i in range(3)},
        **{f"D_tau_{i}": Fraction(((-1) ** (i + 1)) * (2 * i + 7), 13 + 2 * i) for i in range(3)},
        **{f"a_tau_{i}": Fraction(i + 3, 19 + 2 * i) for i in range(3)},
        **{
            f"H_ij_{i}{j}": Fraction(((-1) ** (i + j)) * (i + j + 2), 23 + i + 2 * j)
            for i in range(3)
            for j in range(i, 3)
        },
        **{
            f"tau_K_{i}{j}": Fraction(((-1) ** j) * (i + 2 * j + 3), 31 + i + j)
            for i in range(3)
            for j in range(i, 3)
        },
    }
    if mutation == "zero_lift_witness":
        atom_values = {name: Fraction(0) for name in atom_values}

    evaluated = {
        "delta_N": _linear_evaluate(delta_N, witness_N, atom_values),
        "delta_u_parallel": _linear_evaluate(
            delta_u_parallel, witness_N, atom_values
        ),
        **{
            f"delta_u_spatial_{i}": _linear_evaluate(
                delta_u_spatial[i], witness_N, atom_values
            )
            for i in range(3)
        },
        **{
            f"delta_h_ui_{i}": _linear_evaluate(
                delta_h_ui[i], witness_N, atom_values
            )
            for i in range(3)
        },
        **{
            f"delta_h_ij_{key}": _linear_evaluate(
                value, witness_N, atom_values
            )
            for key, value in delta_h_ij.items()
        },
        "ADM_lapse_n": _linear_evaluate(adm_lapse_n, witness_N, atom_values),
        **{
            f"ADM_shift_{i}": _linear_evaluate(
                adm_shift_lower[i], witness_N, atom_values
            )
            for i in range(3)
        },
        **{
            f"ADM_metric_{key}": _linear_evaluate(
                value, witness_N, atom_values
            )
            for key, value in adm_metric.items()
        },
        "chi_generator": _linear_evaluate(chi_along_u, witness_N, atom_values),
    }
    all_inputs_nonzero = all(value != 0 for value in atom_values.values())
    all_outputs_nonzero = all(value != 0 for value in evaluated.values())
    tau_retained = mutation != "freeze_T"
    residual_rows = {name: _linear_rows(value) for name, value in residuals.items()}
    all_residuals_zero = all(not value for value in residuals.values())
    return {
        "arbitrary_variations": {
            "metric": "H_mu_nu=delta gamma_mu_nu",
            "clock": "tau=delta T",
            "free_components": [
                "H_uu",
                "H_ui[3]",
                "H_ij[6]",
                "U_tau=u^mu*D_mu(tau)",
                "D_tau_i[3]",
            ],
            "N_is_invertible_Laurent_indeterminate": True,
            "N_numeric_value_substituted_in_proof": False,
        },
        "derived_composite_variations": {
            "delta_N_T": "-N_T*H_uu/2-N_T^2*u^mu*D_mu(tau)",
            "delta_u_mu": "-u_mu*H_uu/2-N_T*h_mu^nu*D_nu(tau)",
            "delta_h_mu_nu": "H_mu_nu+u_mu*delta_u_nu+u_nu*delta_u_mu",
        },
        "adapted_clock_gauge": {
            "vector": "chi^mu=-N_T*tau*u^mu",
            "delta_prime_T": "tau+Lie_chi(T)=0",
            "metric_variation": "H_prime=H+Lie_chi(gamma)",
            "Cartan_current_retains_original_tau": tau_retained,
        },
        "ADM_variations": {
            "lapse": "n=delta N/N=-H_prime_uu/2",
            "background_shift": (
                "N^i arbitrary; H_prime_0i-N^j*H_prime_ji=N*H_prime_ui"
            ),
            "shift": "v_i=N_T*H_prime_ui; v_i is arbitrary",
            "spatial_metric": "Q_ij=H_prime_ij; Q_ij is arbitrary symmetric",
            "f_Rcal_shift_Euler_coefficient": "0",
        },
        "normal_forms": normal_forms,
        "normal_forms_sha256": _canonical_sha256(normal_forms),
        "free_polynomial_residuals": residual_rows,
        "all_free_polynomial_residuals_zero": all_residuals_zero,
        "nonvacuous_fraction_witness": {
            "N": [witness_N.numerator, witness_N.denominator],
            "N_is_not_one": witness_N != 1,
            "inputs": {
                name: [value.numerator, value.denominator]
                for name, value in sorted(atom_values.items())
            },
            "outputs": {
                name: [value.numerator, value.denominator]
                for name, value in sorted(evaluated.items())
            },
            "all_independent_inputs_nonzero": all_inputs_nonzero,
            "all_lapse_shift_metric_and_tensor_outputs_nonzero": all_outputs_nonzero,
        },
        "exact_pass": bool(
            all_residuals_zero
            and all_inputs_nonzero
            and all_outputs_nonzero
            and tau_retained
        ),
    }


def _fraction_matrix_witness(current_sign: int) -> dict[str, Any]:
    """Exact non-vacuous product-rule witness for the Rcal boundary current."""

    n = 3
    a = Fraction(7, 5)
    da = [Fraction(2, 7), Fraction(-3, 11), Fraction(5, 13)]
    dda = [[Fraction((i + 2) * (j + 3), 17) for j in range(n)] for i in range(n)]
    dda = [[(dda[i][j] + dda[j][i]) / 2 for j in range(n)] for i in range(n)]
    h = [[Fraction((i + 1) * (j + 2), 19) for j in range(n)] for i in range(n)]
    h = [[(h[i][j] + h[j][i]) / 2 for j in range(n)] for i in range(n)]
    dh = [
        [
            [Fraction((k + 1) * (i + 2) - (j + 1), 23) for j in range(n)]
            for i in range(n)
        ]
        for k in range(n)
    ]
    for k in range(n):
        dh[k] = [[(dh[k][i][j] + dh[k][j][i]) / 2 for j in range(n)] for i in range(n)]
    ddh = [
        [
            [
                [Fraction((k + 1) * (l + 2) + (i + 1) * (j + 3), 29) for j in range(n)]
                for i in range(n)
            ]
            for l in range(n)
        ]
        for k in range(n)
    ]
    # Symmetrise derivative and tensor pairs, which is the only property used.
    for k in range(n):
        for l in range(n):
            for i in range(n):
                for j in range(n):
                    values = (
                        ddh[k][l][i][j],
                        ddh[l][k][i][j],
                        ddh[k][l][j][i],
                        ddh[l][k][j][i],
                    )
                    average = sum(values, Fraction(0)) / 4
                    ddh[k][l][i][j] = average
                    ddh[l][k][i][j] = average
                    ddh[k][l][j][i] = average
                    ddh[l][k][j][i] = average

    trace_h = sum(h[i][i] for i in range(n))
    raw_derivative = a * (
        sum(ddh[i][j][i][j] for i in range(n) for j in range(n))
        - sum(ddh[i][i][j][j] for i in range(n) for j in range(n))
    )
    bulk_after_ibp = (
        sum(dda[i][j] * h[i][j] for i in range(n) for j in range(n))
        - sum(dda[i][i] for i in range(n)) * trace_h
    )
    # Expand D_i theta^i directly.  The two cross pairs are retained rather
    # than cancelled by hand, providing a sign-sensitive exact oracle.
    divergence = current_sign * (
        sum(da[i] * dh[j][i][j] for i in range(n) for j in range(n))
        + a * sum(ddh[i][j][i][j] for i in range(n) for j in range(n))
        - sum(da[i] * dh[i][j][j] for i in range(n) for j in range(n))
        - a * sum(ddh[i][i][j][j] for i in range(n) for j in range(n))
        - sum(dda[i][j] * h[i][j] for i in range(n) for j in range(n))
        - sum(da[j] * dh[i][i][j] for i in range(n) for j in range(n))
        + sum(dda[i][i] for i in range(n)) * trace_h
        + sum(da[i] * dh[i][j][j] for i in range(n) for j in range(n))
    )
    residual = raw_derivative - bulk_after_ibp - divergence
    return {
        "dimension": n,
        "raw_second_derivative_part": [raw_derivative.numerator, raw_derivative.denominator],
        "bulk_after_IBP_part": [bulk_after_ibp.numerator, bulk_after_ibp.denominator],
        "expanded_divergence_part": [divergence.numerator, divergence.denominator],
        "residual": [residual.numerator, residual.denominator],
        "nonzero_raw_witness": raw_derivative != 0,
        "nonzero_current_witness": divergence != 0,
        "exact_pass": residual == 0,
    }


def _Rcal_ADM_action_normal_forms(
    mutation: str | None,
    *,
    current_present: bool,
    current_sign: int,
) -> dict[str, Any]:
    """Structured fixed-clock ADM Euler/current rows for ``N sqrt(h) f(R)``."""

    lapse_factor = 2 if mutation == "wrong_lapse_factor" else 1
    shift_coefficients = [0, 0, 0]
    if mutation == "nonzero_shift_coefficient":
        shift_coefficients[1] = 1
    if mutation == "omit_clock_Cartan":
        cartan_coefficient = 0
        cartan_multiplicity = 0
    elif mutation == "double_clock_Cartan":
        cartan_coefficient = 2
        cartan_multiplicity = 2
    elif mutation == "wrong_clock_Cartan_sign":
        cartan_coefficient = -1
        cartan_multiplicity = 1
    else:
        cartan_coefficient = 1
        cartan_multiplicity = 1
    weighted_current_terms = []
    if current_present:
        weighted_current_terms = [
            [current_sign, "N*f_R", "D_j*Q^ij"],
            [-current_sign, "N*f_R", "D^i*Q"],
            [-current_sign, "D_j(N*f_R)", "Q^ij"],
            [current_sign, "D^i(N*f_R)", "Q"],
        ]
    return {
        "density": {
            "overall_constant": "Mb^2/2",
            "measure": "N*sqrt(h)",
            "f": "xi*Rcal-B4*Rcal^2/(16*k^2)",
            "f_R": "xi-B4*Rcal/(8*k^2)",
            "Gauss_Rcal": "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab",
        },
        "independent_fixed_clock_ADM_variations": {
            "lapse": "n=delta_N/N=-H_prime_uu/2",
            "shift": "v_i=N*H_prime_ui",
            "spatial_metric": "Q_ij=H_prime_ij",
        },
        "Euler_coefficients_inside_N_sqrt_h": {
            "lapse_n": [[lapse_factor, "f"]],
            "shift_v_i": shift_coefficients,
            "spatial_metric_Q_ij": [
                [1, 2, "f*h^ij"],
                [-1, 1, "f_R*Rcal^ij"],
                [1, 1, "N^-1*(D^iD^j-h^ij*D^2)(N*f_R)"],
            ],
        },
        "weighted_IBP_current": {
            "prefactor": "(Mb^2/2)*sqrt(h)",
            "terms": weighted_current_terms,
            "free_product_rule_coefficient": "a=N*f_R",
        },
        "d4_current": {
            "spatial_current_multiplicity": 1 if current_present else 0,
            "source_clock_gauge_vector": "chi=-N*tau*u",
            "gauge_variation_is_subtracted": True,
            "Cartan_term": "+i_(N*tau*u)(l_Rcal)",
            "Cartan_coefficient": cartan_coefficient,
            "Cartan_multiplicity": cartan_multiplicity,
            "separate_material_transgression_appended": False,
        },
    }


def _intrinsic_Rcal_variation(mutation: str | None = None) -> dict[str, Any]:
    gauss_k2 = 1 if mutation == "wrong_Gauss_sign" else -1
    gauss_kij2 = -1 if mutation == "wrong_Gauss_sign" else 1
    current_sign = -1 if mutation == "wrong_Rcal_current_sign" else 1
    polynomial = _poly_derivative_terms(mutation)
    symbolic_product_rule = _symbolic_Rcal_product_rule(current_sign)
    witness = _fraction_matrix_witness(current_sign)
    clock_lift = _clock_metric_lift_certificate(mutation)
    current_present = mutation != "omit_intrinsic_d4_current"
    action_normal_forms = _Rcal_ADM_action_normal_forms(
        mutation,
        current_present=current_present,
        current_sign=current_sign,
    )
    clock_cartan_sign = action_normal_forms["d4_current"]["Cartan_coefficient"]
    return {
        "adapted_coordinates": "T=t; gamma=-N^2 dt^2+h_ij(dx^i+N^i dt)(dx^j+N^j dt)",
        "corrected_Gauss_normal_form": {
            "projected_ambient_Riemann": 1,
            "K_trace_squared": gauss_k2,
            "K_tensor_squared": gauss_kij2,
        },
        "Rcal_formula": (
            "h^ac*h^bd*R_abcd+K^2-K_ab*K^ab"
            if mutation == "wrong_Gauss_sign"
            else "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab"
        ),
        "polynomial": polynomial,
        "metric_variation_before_IBP": (
            "delta_Rcal=-Rcal^ij*H_ij+D^i*D^j*H_ij-D^2*(h^ij*H_ij)"
        ),
        "complete_first_variation_normal_form": (
            "delta S_R=(Mb^2/2)*int dt d3x N*sqrt(h)*{f*n+"
            "[f*h^ij/2-f_R*Rcal^ij+N^-1*(D^iD^j-h^ijD^2)(N*f_R)]*H_ij}"
            "+int dt d3x partial_i(theta_Rcal^i)+int_Sigma d4(i_{N_T*tau*u}l_Rcal); "
            "H,n are computed from H_prime=H+Lie_(-N_T*tau*u)gamma"
        ),
        "metric_Euler_coefficient": (
            "(Mb^2/2)*N*sqrt(h)*[f*h^ij/2-f_R*Rcal^ij+"
            "N^-1*(D^i*D^j-h^ij*D^2)(N*f_R)]"
        ),
        "lapse_variation_term": "(Mb^2/2)*N*sqrt(h)*f*n, where n=delta N/N",
        "lapse_Euler_coefficient_for_n": "(Mb^2/2)*N*sqrt(h)*f",
        "shift_Euler_coefficient": "0",
        "spatial_current_theta_Rcal_i": (
            None
            if not current_present
            else (
                ("-(Mb^2/2)*sqrt(h)*[" if current_sign == -1 else "(Mb^2/2)*sqrt(h)*[")
                + "N*f_R*(D_j*H^ij-D^i*H)-D_j(N*f_R)*H^ij+D^i(N*f_R)*H]"
            )
        ),
        "d4_current": (
            "Theta_Rcal^mu=(0,theta_Rcal^i)"
            + ("-" if clock_cartan_sign == -1 else "+")
            + "i_{N_T*tau*u}l_Rcal; "
            "d4 Theta_Rcal=partial_mu Theta_Rcal^mu"
            if current_present
            else None
        ),
        "compact_support_on_Sigma_removes_integrated_d4_flux": current_present,
        "exact_product_rule_witness": witness,
        "free_symbolic_product_rule": symbolic_product_rule,
        "full_gamma_T_to_ADM_lift": clock_lift,
        "ADM_action_normal_forms": action_normal_forms,
        "ADM_action_normal_forms_sha256": _canonical_sha256(action_normal_forms),
        "clock_Cartan_current_coefficient": clock_cartan_sign,
        "T_variation_is_not_frozen": mutation != "freeze_T",
        "khronon_chain_rule": (
            "delta_T u_mu=-N_T*h_mu^nu*D_nu(delta T); "
            "E_T=D_nu[N_T*h^nu_mu*E_u^mu]"
        ),
        "metric_chain_rule": (
            "delta_gamma u_mu=-(1/2)*u_mu*u^a*u^b*H_ab; "
            "delta h_mu_nu=H_mu_nu+u_mu*delta u_nu+u_nu*delta u_mu"
        ),
        "uses_v5_5_4_wrong_intrinsic_formula": False,
        "Euler_equations_imposed": False,
    }


def _expected_intrinsic_Rcal_normal_form() -> dict[str, Any]:
    return {
        "Gauss": {
            "projected_ambient_Riemann": 1,
            "K_trace_squared": -1,
            "K_tensor_squared": 1,
        },
        "f_monomials": [["xi", 1, 1], ["-B4/(16*k^2)", 1, 2]],
        "df_dR_monomials": [["xi", 1, 0], ["-B4/(16*k^2)", 2, 1]],
        "df_dR_formula": "xi-B4*Rcal/(8*k^2)",
        "current_formula": (
            "(Mb^2/2)*sqrt(h)*[N*f_R*(D_j*H^ij-D^i*H)-"
            "D_j(N*f_R)*H^ij+D^i(N*f_R)*H]"
        ),
        "clock_Cartan_current_coefficient": 1,
    }


def _green_coefficient(row: Mapping[str, Any]) -> tuple[int, int, tuple[tuple[str, int], ...], str, str]:
    coefficient = row["coefficient"]
    return (
        int(coefficient["numerator"]),
        int(coefficient["denominator"]),
        tuple((str(name), int(power)) for name, power in coefficient["powers"]),
        str(row["factor"]),
        str(row["variation"]),
    )


def _expected_bulk_green_rows() -> tuple[tuple[int, int, tuple[tuple[str, int], ...], str, str], ...]:
    return (
        (1, 1, (), "b_minus_wedge", "Delta_A_Sigma"),
        (-1, 1, (), "b_plus_wedge", "Delta_A_Sigma"),
        (-3, 2, (("Omega_Sigma", -1), ("Z", 1)), "sqrt(-gamma)*<phi_minus,n_minus.P_minus>", "Delta_Omega_Sigma"),
        (-3, 2, (("Omega_Sigma", -1), ("Z", 1)), "sqrt(-gamma)*<phi_plus,n_plus.P_plus>", "Delta_Omega_Sigma"),
        (-1, 1, (("Z", 1),), "sqrt(-gamma)*j_minus(n_minus.P_minus)", "Delta_varphi_H"),
        (-1, 1, (("Z", 1),), "sqrt(-gamma)*j_plus(n_plus.P_plus)", "Delta_varphi_H"),
        (-1, 1, (("G", 1),), "sqrt(-gamma)*n_minus.nabla_Omega_minus", "Delta_Omega_Sigma"),
        (-1, 1, (("G", 1),), "sqrt(-gamma)*n_plus.nabla_Omega_plus", "Delta_Omega_Sigma"),
        (-1, 2, (("M5", 3),), "sqrt(-gamma)*pi_minus^(mu nu)", "Delta_gamma_mu_nu"),
        (-1, 2, (("M5", 3),), "sqrt(-gamma)*pi_plus^(mu nu)", "Delta_gamma_mu_nu"),
    )


def _two_sided_green_pairing(
    ward_report: Mapping[str, Any], mutation: str | None = None
) -> dict[str, Any]:
    upstream_rows = ward_report["literal_bulk_interface_Green_ledger"][
        "derived_integrated_boundary_terms"
    ]
    actual = [_green_coefficient(row) for row in upstream_rows]
    if mutation == "wrong_BF_incidence":
        actual = [
            ((-coefficient if factor == "b_minus_wedge" else coefficient), denominator, powers, factor, variation)
            for coefficient, denominator, powers, factor, variation in actual
        ]
    outward = {"plus": -1, "minus": 1}
    if mutation == "wrong_GHY_outward_sign":
        outward["minus"] = -1
    return {
        "actual_normalized_bulk_boundary_rows": [
            [num, den, [list(power) for power in powers], factor, variation]
            for num, den, powers, factor, variation in actual
        ],
        "independent_expected_normalized_bulk_boundary_rows": [
            [num, den, [list(power) for power in powers], factor, variation]
            for num, den, powers, factor, variation in _expected_bulk_green_rows()
        ],
        "rows_exact": tuple(actual) == _expected_bulk_green_rows(),
        "GHY": {
            "first_variation": (
                "delta(S_EH+S_GHY)=int_M (M5^3/2)*sqrt(-g)*G_MN*Delta g^MN"
                "-int_Sigma (M5^3/2)*sqrt(-gamma)*(Theta^mn-Theta*gamma^mn)*H_mn"
            ),
            "outward_normal_signs": outward,
            "expected_outward_normal_signs": {"plus": -1, "minus": 1},
            "normal_derivative_of_H_remaining": False,
            "signs_exact": outward == {"plus": -1, "minus": 1},
        },
        "BF": {
            "boundary_pairing": "-<b_plus-b_minus,Delta A_Sigma>",
            "incidence": {"plus": 1, "minus": -1},
            "off_shell_flux_is_not_cancelled": True,
            "natural_equation": "b_plus-b_minus=0",
            "incidence_exact": tuple(actual[:2]) == _expected_bulk_green_rows()[:2],
        },
        "bulk_Euler_terms_retained_off_shell": mutation != "impose_bulk_EOM",
        "natural_interface_equations_imposed": mutation == "impose_interface_EOM",
    }


def _interface_euler_rows() -> tuple[tuple[str, str], ...]:
    """Independent common-trace Euler rows after intrinsic d4 integration by parts."""

    return (
        ("Delta_gamma_mu_nu", "E_gamma_total^mu_nu"),
        ("Delta_Omega_Sigma", "E_Omega_total"),
        ("Delta_varphi_H", "E_varphi_total"),
        ("Delta_A_Sigma", "E_A_total=b_minus-b_plus"),
        ("delta_T", "E_T_intrinsic"),
    )


def _shape_equation(mutation: str | None = None) -> dict[str, Any]:
    rows: dict[str, list[tuple[int, str]]] = {}
    transgression_count = 2 if mutation == "double_i_xi_L5" else 1
    for side in ("plus", "minus"):
        terms = [
            (transgression_count, f"i_n_{side}_L5_{side}"),
            (2, f"E_gamma_total^mu_nu*Theta_{side}_mu_nu"),
            (1, f"E_Omega_total*n_{side}.nabla_Omega_{side}"),
            (1, f"<E_varphi_total,j_{side}(n_{side}.D_A_phi_{side})>"),
            (1, f"<E_A_total,Trans_iota_{side}(i_n_{side}_F_{side})>"),
        ]
        rows[side] = terms
    if mutation == "freeze_Y":
        rows = {}
    expected = {
        side: [
            (1, f"i_n_{side}_L5_{side}"),
            (2, f"E_gamma_total^mu_nu*Theta_{side}_mu_nu"),
            (1, f"E_Omega_total*n_{side}.nabla_Omega_{side}"),
            (1, f"<E_varphi_total,j_{side}(n_{side}.D_A_phi_{side})>"),
            (1, f"<E_A_total,Trans_iota_{side}(i_n_{side}_F_{side})>"),
        ]
        for side in ("plus", "minus")
    }
    return {
        "proof_status": "unproved_diagnostic_do_not_consume",
        "known_missing_Legendre_boundary_structure": (
            "i_n(L)-Theta_bulk(L_n q), with orientation fixed per side"
        ),
        "one_dimensional_oracle": (
            "(ell_q-p)*Delta_q+f*(L-p_n*partial_n_q), convention dependent"
        ),
        "normal_displacements": "delta Y_eps=f_eps*n_eps+xi_parallel_eps",
        "actual_normal_shape_rows": {
            side: [[coefficient, atom] for coefficient, atom in terms]
            for side, terms in rows.items()
        },
        "independent_expected_normal_shape_rows": {
            side: [[coefficient, atom] for coefficient, atom in terms]
            for side, terms in expected.items()
        },
        "normal_shape_equations": "S_plus=0 and S_minus=0 on admissible paired-embedding tangents",
        "shape_rows_exact": rows == expected,
        "i_xi_L5_occurrences_per_side": transgression_count if rows else 0,
        "i_xi_L5_origin": "Cartan representative of the single fixed-reference material pullback",
        "separate_domain_transgression_appended": mutation == "double_i_xi_L5",
        "Y_plus_and_Y_minus_varied": bool(rows),
        "Euler_equations_imposed_to_derive_shape_row": False,
        "shape_row_is_Noether_dependent": True,
        "shape_row_proved_from_literal_action": False,
    }


def _groupoid_variation(mutation: str | None = None) -> dict[str, Any]:
    present = mutation != "omit_iota_j"
    # General SO(3) proof: delta_ab epsilon^a_cd r^b r^d vanishes because the
    # last factor is symmetric under b<->d and epsilon is antisymmetric.
    cancellation_pairs = [
        ("delta_ab*epsilon^a_cd*r^b*lambda^c*r^d", 1),
        ("delta_ad*epsilon^a_cb*r^d*lambda^c*r^b", -1),
    ] if present else []
    return {
        "admissible_variations_present": present,
        "roles": ["iota_plus/j_plus", "iota_minus/j_minus"] if present else [],
        "common_Q_automorphism": (
            "delta_lambda varphi_H=[lambda,varphi_H]; delta_lambda A_Sigma=-D_A lambda"
            if present
            else None
        ),
        "Robin_invariant_pair_cancellation": [list(row) for row in cancellation_pairs],
        "antisymmetric_structure_constant_times_symmetric_pair_is_zero": present,
        "interface_gauge_Noether_identity": (
            "D_A E_A_total+[varphi_H,E_varphi_total]=0"
            if present
            else None
        ),
        "relative_iota_j_are_groupoid_data_not_unconstrained_extra_fields": present,
        "bulk_affine_and_associated_trace_transport_consumed": present,
    }


def _moving_ward(
    intrinsic: Mapping[str, Any],
    shape: Mapping[str, Any],
    groupoid: Mapping[str, Any],
    mutation: str | None,
) -> dict[str, Any]:
    current_present = intrinsic["d4_current"] is not None
    interface_eom_retained = mutation != "impose_interface_EOM"
    return {
        "intrinsic_first_variation": (
            "delta l_Sigma=sum_q E_q*delta q+d4 Theta_Sigma(q,delta q)"
        ),
        "intrinsic_Noether_current": (
            "J_Sigma[zeta]=Theta_Sigma(q,Lie_zeta q)-i_zeta l_Sigma"
            if current_present
            else None
        ),
        "intrinsic_off_shell_Ward_identity": (
            "d4 J_Sigma[zeta]=-sum_q E_q*Lie_zeta q"
            if current_present
            else None
        ),
        "bulk_interface_current": (
            "J_total[zeta]=sum_eps trace(Theta5_eps(Lie_zeta Phi_eps)-i_zeta L5_eps)"
            "+J_Sigma[zeta]"
            if current_present
            else None
        ),
        "moving_material_variations": {
            "metric": "H_eps=Y_eps^*delta g_eps+2D_(mu xi_parallel_nu)+2f_eps Theta_eps",
            "Omega": "Delta Omega_eps=Y_eps^*(delta Omega_eps+xi_eps.Omega_eps)",
            "phi": "Delta varphi_H=j_eps[Y_eps^*(delta phi_eps+i_xi D_A phi_eps)]+delta j_eps[Y_eps^*phi_eps]",
            "connection": "Delta A_Sigma=Trans_iota_eps[Y_eps^*(delta A_eps+i_xi F_eps)]",
            "B": "Delta B_eps=Y_eps^*(delta B_eps+Lie_xi B_eps)",
        },
        "tangential_d4_identity_exact": current_present,
        "normal_shape_identity_exact": False,
        "normal_shape_template_self_consistent_only": shape["shape_rows_exact"],
        "groupoid_vertical_identity_exact": groupoid["admissible_variations_present"],
        "bulk_and_interface_Euler_terms_retained": interface_eom_retained,
        "no_EOM_imposed": interface_eom_retained and mutation != "impose_bulk_EOM",
        "no_Y_freeze": shape["Y_plus_and_Y_minus_varied"],
        "no_T_freeze": intrinsic["T_variation_is_not_frozen"],
        "no_double_transgression": shape["i_xi_L5_occurrences_per_side"] == 1,
        "support": (
            "smooth compact support on Sigma=R^(1,3), compact bulk support at infinity; "
            "no boundary-of-boundary flux"
        ),
    }


def _variation_role_coverage(
    jet_rows: Sequence[Sequence[Any]],
    shape: Mapping[str, Any],
    groupoid: Mapping[str, Any],
) -> dict[str, Any]:
    fields = {str(row[1]) for row in jet_rows}
    covered = {
        "g_plus": "g_plus" in fields,
        "Omega_plus": "Omega_plus" in fields,
        "phi_plus": "phi_plus" in fields,
        "A_plus": "A_plus" in fields,
        "B_plus": "B_plus" in fields,
        "g_minus": "g_minus" in fields,
        "Omega_minus": "Omega_minus" in fields,
        "phi_minus": "phi_minus" in fields,
        "A_minus": "A_minus" in fields,
        "B_minus": "B_minus" in fields,
        "Y_plus": shape["Y_plus_and_Y_minus_varied"],
        "Y_minus": shape["Y_plus_and_Y_minus_varied"],
        "T": "T" in fields,
        "iota_plus/j_plus": "iota_plus/j_plus" in groupoid["roles"],
        "iota_minus/j_minus": "iota_minus/j_minus" in groupoid["roles"],
    }
    return {
        "required_roles": list(INDEPENDENT_VARIATION_ROLES),
        "covered": covered,
        "covered_roles": [role for role in INDEPENDENT_VARIATION_ROLES if covered.get(role)],
        "missing_roles": [role for role in INDEPENDENT_VARIATION_ROLES if not covered.get(role)],
        "all_required_roles_covered": all(covered.get(role) for role in INDEPENDENT_VARIATION_ROLES),
    }


def _action_component_inventory(ward_report: Mapping[str, Any]) -> dict[str, Any]:
    actual = tuple(
        ward_report["literal_bulk_interface_Green_ledger"]["actual_component_keys"]
    )
    return {
        "actual": list(actual),
        "independent_expected": list(EXPECTED_ACTION_COMPONENTS),
        "component_count": len(actual),
        "exact_twenty_component_multiset_and_order": actual == EXPECTED_ACTION_COMPONENTS,
    }


def _checks_for(
    dependency: Mapping[str, Any],
    inventory: Mapping[str, Any],
    universal: Mapping[str, Any],
    intrinsic: Mapping[str, Any],
    green: Mapping[str, Any],
    shape: Mapping[str, Any],
    groupoid: Mapping[str, Any],
    ward: Mapping[str, Any],
    coverage: Mapping[str, Any],
) -> dict[str, bool]:
    target_r = _expected_intrinsic_Rcal_normal_form()
    expected_lift_residual_names = {
        "delta_N_from_normalization",
        "delta_u_parallel",
        "delta_h_uu",
        "unit_constraint",
        "chi_sets_delta_prime_T_to_zero",
        "gauge_lapse_compatibility",
        "H_prime_uu",
        *(f"delta_u_spatial_{i}" for i in range(3)),
        *(f"delta_h_ui_{i}" for i in range(3)),
        *(f"H_prime_ui_{i}" for i in range(3)),
        *(f"delta_h_ij_{i}{j}" for i in range(3) for j in range(i, 3)),
        *(f"H_prime_ij_{i}{j}" for i in range(3) for j in range(i, 3)),
    }
    expected_lift_inputs = {
        "H_uu",
        "U_tau",
        "A_tau",
        "tau",
        *(f"H_ui_{i}" for i in range(3)),
        *(f"D_tau_{i}" for i in range(3)),
        *(f"a_tau_{i}" for i in range(3)),
        *(f"H_ij_{i}{j}" for i in range(3) for j in range(i, 3)),
        *(f"tau_K_{i}{j}" for i in range(3) for j in range(i, 3)),
    }
    expected_lift_outputs = {
        "delta_N",
        "delta_u_parallel",
        "ADM_lapse_n",
        "chi_generator",
        *(f"delta_u_spatial_{i}" for i in range(3)),
        *(f"delta_h_ui_{i}" for i in range(3)),
        *(f"ADM_shift_{i}" for i in range(3)),
        *(f"delta_h_ij_{i}{j}" for i in range(3) for j in range(i, 3)),
        *(f"ADM_metric_{i}{j}" for i in range(3) for j in range(i, 3)),
    }
    lift_binding = False
    action_binding = False
    try:
        lift = intrinsic["full_gamma_T_to_ADM_lift"]
        witness = lift["nonvacuous_fraction_witness"]
        residuals = lift["free_polynomial_residuals"]
        witness_inputs = witness["inputs"]
        witness_outputs = witness["outputs"]
        witness_N = Fraction(*witness["N"])
        lift_binding = bool(
            lift["arbitrary_variations"]["N_is_invertible_Laurent_indeterminate"]
            and lift["arbitrary_variations"]["N_numeric_value_substituted_in_proof"]
            is False
            and lift["adapted_clock_gauge"]
            == {
                "vector": "chi^mu=-N_T*tau*u^mu",
                "delta_prime_T": "tau+Lie_chi(T)=0",
                "metric_variation": "H_prime=H+Lie_chi(gamma)",
                "Cartan_current_retains_original_tau": True,
            }
            and lift["ADM_variations"]
            == {
                "lapse": "n=delta N/N=-H_prime_uu/2",
                "background_shift": (
                    "N^i arbitrary; H_prime_0i-N^j*H_prime_ji=N*H_prime_ui"
                ),
                "shift": "v_i=N_T*H_prime_ui; v_i is arbitrary",
                "spatial_metric": "Q_ij=H_prime_ij; Q_ij is arbitrary symmetric",
                "f_Rcal_shift_Euler_coefficient": "0",
            }
            and _canonical_sha256(lift["normal_forms"])
            == "e7c6765defdad9cc05e2dbd5375c10b6b31b37ca8bd04aac07966a3450f59e4a"
            and lift["normal_forms_sha256"]
            == "e7c6765defdad9cc05e2dbd5375c10b6b31b37ca8bd04aac07966a3450f59e4a"
            and set(residuals) == expected_lift_residual_names
            and all(value == [] for value in residuals.values())
            and lift["all_free_polynomial_residuals_zero"] is True
            and set(witness_inputs) == expected_lift_inputs
            and set(witness_outputs) == expected_lift_outputs
            and witness_N == Fraction(7, 3)
            and witness_N != 1
            and all(Fraction(*value) != 0 for value in witness_inputs.values())
            and all(Fraction(*value) != 0 for value in witness_outputs.values())
            and witness["N_is_not_one"] is True
            and witness["all_independent_inputs_nonzero"] is True
            and witness["all_lapse_shift_metric_and_tensor_outputs_nonzero"]
            is True
            and lift["exact_pass"] is True
        )

        action = intrinsic["ADM_action_normal_forms"]
        action_binding = bool(
            _canonical_sha256(action)
            == "bf2ed2b9404287fc3ef059b3644413547d8c3b71776170c671fae1caaa790940"
            and intrinsic["ADM_action_normal_forms_sha256"]
            == "bf2ed2b9404287fc3ef059b3644413547d8c3b71776170c671fae1caaa790940"
            and action["density"]
            == {
                "overall_constant": "Mb^2/2",
                "measure": "N*sqrt(h)",
                "f": "xi*Rcal-B4*Rcal^2/(16*k^2)",
                "f_R": "xi-B4*Rcal/(8*k^2)",
                "Gauss_Rcal": "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab",
            }
            and action["Euler_coefficients_inside_N_sqrt_h"]["lapse_n"]
            == [[1, "f"]]
            and action["Euler_coefficients_inside_N_sqrt_h"]["shift_v_i"]
            == [0, 0, 0]
            and action["Euler_coefficients_inside_N_sqrt_h"]
            ["spatial_metric_Q_ij"]
            == [
                [1, 2, "f*h^ij"],
                [-1, 1, "f_R*Rcal^ij"],
                [1, 1, "N^-1*(D^iD^j-h^ij*D^2)(N*f_R)"],
            ]
            and action["weighted_IBP_current"]
            == {
                "prefactor": "(Mb^2/2)*sqrt(h)",
                "terms": [
                    [1, "N*f_R", "D_j*Q^ij"],
                    [-1, "N*f_R", "D^i*Q"],
                    [-1, "D_j(N*f_R)", "Q^ij"],
                    [1, "D^i(N*f_R)", "Q"],
                ],
                "free_product_rule_coefficient": "a=N*f_R",
            }
            and action["d4_current"]
            == {
                "spatial_current_multiplicity": 1,
                "source_clock_gauge_vector": "chi=-N*tau*u",
                "gauge_variation_is_subtracted": True,
                "Cartan_term": "+i_(N*tau*u)(l_Rcal)",
                "Cartan_coefficient": 1,
                "Cartan_multiplicity": 1,
                "separate_material_transgression_appended": False,
            }
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        lift_binding = False
        action_binding = False
    corrected_r = bool(
        dependency["pass"]
        and intrinsic["corrected_Gauss_normal_form"] == target_r["Gauss"]
        and intrinsic["Rcal_formula"] == dependency["correct_Gauss_formula_normalized"]
        and dependency["Gauss_exact_witnesses_consumed"]
        and dependency["v5_2_foliation_literal"]
        == dependency["expected_v5_2_foliation_literal"]
        and intrinsic["polynomial"]["f_monomials"] == target_r["f_monomials"]
        and intrinsic["polynomial"]["f_monomials"]
        == dependency["intrinsic_f_monomials_read_from_v5_2_literal"]
        and intrinsic["polynomial"]["df_dR_monomials"] == target_r["df_dR_monomials"]
        and intrinsic["polynomial"]["df_dR_monomials"]
        == dependency["intrinsic_df_dR_monomials_from_exponent_rule"]
        and intrinsic["polynomial"]["df_dR_formula"] == target_r["df_dR_formula"]
        and intrinsic["polynomial"]["df_dR_formula"]
        == dependency["intrinsic_df_dR_formula_from_v5_2_literal"]
        and intrinsic["spatial_current_theta_Rcal_i"] == target_r["current_formula"]
        and intrinsic["spatial_current_theta_Rcal_i"]
        == (
            "(Mb^2/2)*sqrt(h)*[N*f_R*(D_j*H^ij-D^i*H)-"
            "D_j(N*f_R)*H^ij+D^i(N*f_R)*H]"
        )
        and intrinsic["metric_Euler_coefficient"]
        == (
            "(Mb^2/2)*N*sqrt(h)*[f*h^ij/2-f_R*Rcal^ij+"
            "N^-1*(D^i*D^j-h^ij*D^2)(N*f_R)]"
        )
        and intrinsic["lapse_Euler_coefficient_for_n"]
        == "(Mb^2/2)*N*sqrt(h)*f"
        and intrinsic["d4_current"]
        == (
            "Theta_Rcal^mu=(0,theta_Rcal^i)+i_{N_T*tau*u}l_Rcal; "
            "d4 Theta_Rcal=partial_mu Theta_Rcal^mu"
        )
        and intrinsic["clock_Cartan_current_coefficient"]
        == target_r["clock_Cartan_current_coefficient"]
        and intrinsic["exact_product_rule_witness"]["exact_pass"]
        and intrinsic["exact_product_rule_witness"]["nonzero_raw_witness"]
        and intrinsic["exact_product_rule_witness"]["nonzero_current_witness"]
        and intrinsic["free_symbolic_product_rule"][
            "free_polynomial_identity_exact_pass"
        ]
        and intrinsic["free_symbolic_product_rule"]["numeric_values_substituted"]
        is False
        and lift_binding
        and action_binding
        and intrinsic["shift_Euler_coefficient"] == "0"
        and intrinsic["compact_support_on_Sigma_removes_integrated_d4_flux"]
        and intrinsic["T_variation_is_not_frozen"]
        and intrinsic["Euler_equations_imposed"] is False
        and intrinsic["uses_v5_5_4_wrong_intrinsic_formula"] is False
    )
    candidate_two_sided = bool(
        corrected_r
        and inventory["exact_twenty_component_multiset_and_order"]
        and green["rows_exact"]
        and green["GHY"]["signs_exact"]
        and green["GHY"]["normal_derivative_of_H_remaining"] is False
        and green["BF"]["incidence_exact"]
        and green["BF"]["off_shell_flux_is_not_cancelled"]
        and green["bulk_Euler_terms_retained_off_shell"]
        and green["natural_interface_equations_imposed"] is False
    )
    nominal_complete = bool(
        candidate_two_sided
        and universal["field_jet_rows_exact"]
        and universal["all_normalized_residuals_zero"]
        and universal["no_Euler_equation_imposed"]
        and coverage["all_required_roles_covered"]
        and shape["shape_rows_exact"]
        and shape["Y_plus_and_Y_minus_varied"]
        and shape["i_xi_L5_occurrences_per_side"] == 1
        and shape["separate_domain_transgression_appended"] is False
        and groupoid["admissible_variations_present"]
        and groupoid["antisymmetric_structure_constant_times_symmetric_pair_is_zero"]
    )
    nominal_moving = bool(
        nominal_complete
        and ward["tangential_d4_identity_exact"]
        and ward["normal_shape_identity_exact"]
        and ward["groupoid_vertical_identity_exact"]
        and ward["no_EOM_imposed"]
        and ward["no_Y_freeze"]
        and ward["no_T_freeze"]
        and ward["no_double_transgression"]
    )
    # The following semantic obligations are deliberately not inferred from
    # nominal role coverage or from a generic integration-by-parts theorem.
    # They require a future producer that differentiates the literal AST.
    action_AST_to_all_physical_Euler_rows_derived = False
    K_a_Robin_coefficients_expanded = False
    shape_row_derived_from_bulk_GHY_interface_action = False
    groupoid_row_derived_from_action = False
    return {
        "dependency_bytes_schemas_and_semantic_scopes_bound": bool(dependency["pass"]),
        "literal_v5_2_twenty_component_inventory_exact": bool(
            inventory["exact_twenty_component_multiset_and_order"]
        ),
        "universal_second_jet_Euler_Green_product_rule_exact": bool(
            universal["field_jet_rows_exact"]
            and universal["all_normalized_residuals_zero"]
            and universal["no_Euler_equation_imposed"]
        ),
        "corrected_intrinsic_Rcal_interface_variation_exact": corrected_r,
        "candidate_two_sided_bulk_GHY_rows_match_pinned_ledger": candidate_two_sided,
        "all_independent_variation_roles_covered": bool(
            coverage["all_required_roles_covered"]
        ),
        "action_AST_to_all_physical_Euler_rows_derived": action_AST_to_all_physical_Euler_rows_derived,
        "K_a_Robin_Euler_coefficients_expanded": K_a_Robin_coefficients_expanded,
        "shape_row_derived_from_bulk_GHY_interface_action": shape_row_derived_from_bulk_GHY_interface_action,
        "groupoid_row_derived_from_action": groupoid_row_derived_from_action,
        "nominal_role_coverage_candidate_only": nominal_complete,
        "nominal_moving_Ward_candidate_only": nominal_moving,
        "two_sided_bulk_GHY_interface_Green_pairing_exact": False,
        "complete_v5_2_all_field_normal_embedding": False,
        "complete_moving_embedding_Ward": False,
        "full_off_shell_Green_theorem_selected_sector": False,
        "full_classical_variational_principle_selected_sector": False,
    }


def _decision(checks: Mapping[str, bool]) -> dict[str, bool]:
    corrected = checks["corrected_intrinsic_Rcal_interface_variation_exact"]
    two_sided = checks["two_sided_bulk_GHY_interface_Green_pairing_exact"]
    complete = checks["complete_v5_2_all_field_normal_embedding"]
    moving = checks["complete_moving_embedding_Ward"]
    full_green = checks["full_off_shell_Green_theorem_selected_sector"]
    full_principle = checks["full_classical_variational_principle_selected_sector"]
    promoted = bool(
        corrected and two_sided and complete and moving and full_green and full_principle
    )
    result = {
        "corrected_intrinsic_Rcal_interface_variation_exact_pass": corrected,
        "two_sided_bulk_GHY_interface_Green_pairing_exact_pass": two_sided,
        "complete_v5_2_all_field_normal_embedding_pass": complete,
        "complete_moving_embedding_Ward_pass": moving,
        "full_off_shell_Green_theorem_selected_sector_pass": full_green,
        "full_classical_variational_principle_selected_sector_pass": full_principle,
        "C1_ACTION_pass": promoted,
        "N1_ACTION_pass": promoted,
        "C1_N1_promotion_authorized": promoted,
    }
    result.update({key: False for key in FALSE_DECISION_KEYS})
    return result


def build_report(
    mutation: str | None = None,
    *,
    dependency: Mapping[str, Any] | None = None,
    ward_dependency: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if mutation is not None and mutation not in MUTATIONS:
        raise MovingInterfaceV5678Error(f"unknown mutation: {mutation}")
    dependency_report = dict(dependency) if dependency is not None else _dependency_certificate()
    if ward_dependency is None:
        observed_hash = dependency_report["observed"][V5672_SOURCE.name]
        ward_report = _load_ward_report(observed_hash)
    else:
        ward_report = dict(ward_dependency)

    inventory = _action_component_inventory(ward_report)
    universal = _universal_euler_green_certificate(mutation)
    intrinsic = _intrinsic_Rcal_variation(mutation)
    green = _two_sided_green_pairing(ward_report, mutation)
    shape = _shape_equation(mutation)
    groupoid = _groupoid_variation(mutation)
    ward = _moving_ward(intrinsic, shape, groupoid, mutation)
    coverage = _variation_role_coverage(
        universal["actual_field_jet_rows"], shape, groupoid
    )
    checks = _checks_for(
        dependency_report,
        inventory,
        universal,
        intrinsic,
        green,
        shape,
        groupoid,
        ward,
        coverage,
    )
    decision = _decision(checks)

    if mutation is None:
        expected_false_checks = {
            "action_AST_to_all_physical_Euler_rows_derived",
            "K_a_Robin_Euler_coefficients_expanded",
            "shape_row_derived_from_bulk_GHY_interface_action",
            "groupoid_row_derived_from_action",
            "nominal_moving_Ward_candidate_only",
            "two_sided_bulk_GHY_interface_Green_pairing_exact",
            "complete_v5_2_all_field_normal_embedding",
            "complete_moving_embedding_Ward",
            "full_off_shell_Green_theorem_selected_sector",
            "full_classical_variational_principle_selected_sector",
        }
        observed_false_checks = {key for key, value in checks.items() if not value}
        if observed_false_checks != expected_false_checks:
            raise MovingInterfaceV5678Error(
                "microlemma check boundary drift: "
                f"{sorted(observed_false_checks)}"
            )
        if {key for key, value in decision.items() if value} != TRUE_DECISION_KEYS:
            raise MovingInterfaceV5678Error("positive decision allowlist drift")
        if {key for key, value in decision.items() if not value} != FALSE_DECISION_KEYS:
            raise MovingInterfaceV5678Error("fail-closed decision allowlist drift")

    return {
        "schema": SCHEMA,
        "claim": (
            "Exact compact-support, off-shell moving-interface first variation of the "
            "literal v5.2 action on the selected smooth trivial null-homotopic sector"
        ),
        "classification": (
            "theory_only;exact_local_variational_identity;compact_support;"
            "selected_bundle_component;C1_N1_action_items_only;"
            "C2plus_N2plus_P4_B4_B5_fail_closed"
        ),
        "mutation": mutation,
        "source_pins": dependency_report,
        "literal_action_inventory": inventory,
        "universal_second_jet_Euler_Green_identity": universal,
        "corrected_intrinsic_Rcal_variation": intrinsic,
        "two_sided_bulk_GHY_interface_Green_pairing": green,
        "common_interface_Euler_rows": [list(row) for row in _interface_euler_rows()],
        "normal_embedding_shape_equation": shape,
        "iota_j_groupoid_variation": groupoid,
        "moving_interface_Ward_identity": ward,
        "variation_role_coverage": coverage,
        "checks": checks,
        "decision": decision,
        "exact_blockers_before_any_broader_promotion": [
            "derive every K_foliation, a_squared and Robin Euler/current coefficient from the literal v5.2 AST",
            "replace the unproved shape template by the oriented Legendre boundary row i_n(L)-Theta_bulk(L_n q), checked against the one-dimensional oracle (ell_q-p) Delta_q+f(L-p_n partial_n q)",
            "derive the two normal-shape rows from the combined bulk plus EH/GHY plus interface action rather than a role template",
            "derive constrained iota/j groupoid variations from the same action and trace maps",
            "combine those derived rows with the bulk-current traces; nominal field coverage and a universal IBP theorem are insufficient",
        ],
        "evidence_boundary": (
            "This is a formal local first-variation theorem for smooth fields and compactly "
            "supported variations on Sigma=R^(1,3). It closes only the corrected intrinsic-"
            "Rcal variation microlemma; the displayed wider assembly is diagnostic and C1/N1 "
            "remain false. In particular, the inherited shape template is explicitly unproved "
            "and is not consumed by the microlemma. It proves neither convergence of Route-C "
            "nor a global gauge quotient, large-gauge/BV-BFV completion, global finiteness of "
            "the noncompact action, N2-N7 dynamics, P4, B4, B5, or a physical bulk detection."
        ),
    }


def mutant_campaign(
    *,
    dependency: Mapping[str, Any] | None = None,
    ward_dependency: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    dependency_report = dict(dependency) if dependency is not None else _dependency_certificate()
    if ward_dependency is None:
        ward_report = _load_ward_report(
            dependency_report["observed"][V5672_SOURCE.name]
        )
    else:
        ward_report = dict(ward_dependency)
    rows: dict[str, Any] = {}
    microlemma_mutations = {
        "wrong_Gauss_sign",
        "wrong_R2_derivative_factor",
        "wrong_Rcal_current_sign",
        "wrong_clock_Cartan_sign",
        "wrong_N_powers",
        "wrong_deltaN_sign",
        "wrong_projector",
        "wrong_chi",
        "wrong_deltaN",
        "zero_deltaN",
        "wrong_deltaU",
        "zero_deltaU",
        "wrong_deltaH",
        "zero_deltaH",
        "wrong_lapse_factor",
        "nonzero_shift_coefficient",
        "omit_clock_Cartan",
        "double_clock_Cartan",
        "zero_lift_witness",
        "omit_intrinsic_d4_current",
        "freeze_T",
    }
    for mutation in MUTATIONS:
        report = build_report(
            mutation,
            dependency=dependency_report,
            ward_dependency=ward_report,
        )
        attacks_accepted_microlemma = mutation in microlemma_mutations
        killed = (
            report["decision"][
                "corrected_intrinsic_Rcal_interface_variation_exact_pass"
            ]
            is False
            if attacks_accepted_microlemma
            else (
                report["decision"][
                    "full_classical_variational_principle_selected_sector_pass"
                ]
                is False
                and report["decision"]["C1_N1_promotion_authorized"] is False
            )
        )
        rows[mutation] = {
            "attacks_accepted_microlemma": attacks_accepted_microlemma,
            "attacks_excluded_broader_claim": not attacks_accepted_microlemma,
            "killed": killed,
            "accepted_microlemma_survives_when_attack_is_out_of_scope": (
                report["decision"][
                    "corrected_intrinsic_Rcal_interface_variation_exact_pass"
                ]
                if not attacks_accepted_microlemma
                else None
            ),
            "true_decision_keys": sorted(
                key for key, value in report["decision"].items() if value
            ),
            "failed_checks": sorted(
                key for key, value in report["checks"].items() if not value
            ),
        }
    return {
        "rows": rows,
        "mutant_count": len(rows),
        "all_killed": all(row["killed"] for row in rows.values()),
    }


def main() -> int:
    report = build_report()
    report["mutant_campaign"] = mutant_campaign(
        dependency=report["source_pins"],
        ward_dependency=_load_ward_report(
            report["source_pins"]["observed"][V5672_SOURCE.name]
        ),
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
