#!/usr/bin/env python3
"""Derive and certify the bounded-memory radial ADM seed through quartic order.

This is a theory-only algebra certificate.  It rewrites the canonical
Einstein--dilaton action in a scalar radial ADM gauge, verifies the exact
extrinsic-curvature identity, and expands the resulting local density with a
degree-four epsilon jet.  It deliberately stops before solving the shift or
finite-endpoint junction constraints, so it cannot be mistaken for a compact
physical S3/S4 coefficient.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "artifacts" / "radial_adm_quartic_seed.json"
EFFECTIVE_ACTION = (
    REPO / "first_principles_audit" / "artifacts" / "holo_effective_action.json"
)
ORDER = 4
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _constant(value: Any) -> np.ndarray:
    raw = np.asarray(value, dtype=float)
    result = np.zeros((ORDER + 1, *raw.shape), dtype=float)
    result[0] = raw
    return result


def _linear(value: Any) -> np.ndarray:
    raw = np.asarray(value, dtype=float)
    result = np.zeros((ORDER + 1, *raw.shape), dtype=float)
    result[1] = raw
    return result


def _broadcast(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    shape = np.broadcast_shapes(a.shape[1:], b.shape[1:])
    return (
        np.broadcast_to(a, (ORDER + 1, *shape)),
        np.broadcast_to(b, (ORDER + 1, *shape)),
    )


def _add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aa, bb = _broadcast(a, b)
    return aa + bb


def _scale(value: float, a: np.ndarray) -> np.ndarray:
    return value * a


def _mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aa, bb = _broadcast(a, b)
    result = np.zeros_like(aa)
    for degree in range(ORDER + 1):
        for left in range(degree + 1):
            result[degree] += aa[left] * bb[degree - left]
    return result


def _reciprocal(a: np.ndarray) -> np.ndarray:
    if a.shape[1:] != ():
        raise ValueError("reciprocal is implemented for scalar jets")
    if a[0] == 0.0:
        raise ZeroDivisionError("jet has zero constant term")
    result = np.zeros_like(a)
    result[0] = 1.0 / a[0]
    for degree in range(1, ORDER + 1):
        result[degree] = -sum(
            a[left] * result[degree - left]
            for left in range(1, degree + 1)
        ) / a[0]
    return result


def _exp(a: np.ndarray) -> np.ndarray:
    if a.shape[1:] != ():
        raise ValueError("exponential is implemented for scalar jets")
    result = np.zeros_like(a)
    result[0] = math.exp(float(a[0]))
    for degree in range(1, ORDER + 1):
        result[degree] = sum(
            left * a[left] * result[degree - left]
            for left in range(1, degree + 1)
        ) / degree
    return result


def _matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if a.ndim != 3 or b.ndim != 3:
        raise ValueError("matrix jet operands must have shape (degree,row,column)")
    result = np.zeros((ORDER + 1, a.shape[1], b.shape[2]), dtype=float)
    for degree in range(ORDER + 1):
        for left in range(degree + 1):
            result[degree] += a[left] @ b[degree - left]
    return result


def _trace(a: np.ndarray) -> np.ndarray:
    return np.trace(a, axis1=1, axis2=2)


def _scalar_times_matrix(scalar: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    result = np.zeros_like(matrix)
    for degree in range(ORDER + 1):
        for left in range(degree + 1):
            result[degree] += scalar[left] * matrix[degree - left]
    return result


def _lorentz_dot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    result = np.zeros(ORDER + 1, dtype=float)
    for degree in range(ORDER + 1):
        for left in range(degree + 1):
            result[degree] += a[left] @ ETA @ b[degree - left]
    return result


def quartic_density_jet(
    *,
    warp: float,
    warp_u: float,
    chi_u: float,
    potential: float,
    zeta: float,
    zeta_u: float,
    lapse: float,
    zeta_gradient: np.ndarray,
    zeta_box: float,
    beta_gradient: np.ndarray,
    beta_hessian: np.ndarray,
) -> np.ndarray:
    """Return coefficients of L(epsilon)=sum_n L_n epsilon**n, n<=4."""

    omega = _add(_constant(warp), _linear(zeta))
    root_gamma = _exp(_scale(4.0, omega))
    inverse_conformal = _exp(_scale(-2.0, omega))
    hubble = _add(_constant(warp_u), _linear(zeta_u))
    adm_lapse = _add(_constant(1.0), _linear(lapse))

    dzeta = _linear(np.asarray(zeta_gradient, dtype=float))
    dbeta = _linear(np.asarray(beta_gradient, dtype=float))
    ddbeta = _linear(np.asarray(beta_hessian, dtype=float))

    connection_piece = np.zeros_like(ddbeta)
    raised_dzeta = np.einsum("ij,dj->di", ETA, dzeta)
    zeta_dot_beta = np.zeros(ORDER + 1, dtype=float)
    for degree in range(ORDER + 1):
        for left in range(degree + 1):
            zeta_dot_beta[degree] += (
                raised_dzeta[left] @ dbeta[degree - left]
            )
    for mu in range(4):
        for nu in range(4):
            connection_piece[:, mu, nu] = _add(
                _mul(dzeta[:, mu], dbeta[:, nu]),
                _mul(dzeta[:, nu], dbeta[:, mu]),
            ) - ETA[mu, nu] * zeta_dot_beta
    covariant_beta_hessian = ddbeta - connection_piece
    eta_raised_hessian = np.einsum(
        "ij,djk->dik", ETA, covariant_beta_hessian
    )
    shift_matrix = _scalar_times_matrix(
        inverse_conformal, eta_raised_hessian
    )
    shift_trace = _trace(shift_matrix)
    shift_square_trace = _trace(_matmul(shift_matrix, shift_matrix))

    gradient_square = _lorentz_dot(dzeta, dzeta)
    ricci_bracket = _add(
        _scale(-6.0, _linear(zeta_box)),
        _scale(-6.0, gradient_square),
    )
    ricci_four = _mul(inverse_conformal, ricci_bracket)

    q = _add(
        _add(
            _scale(12.0, _mul(hubble, hubble)),
            _scale(-6.0, _mul(hubble, shift_trace)),
        ),
        _add(
            _mul(shift_trace, shift_trace),
            _scale(-1.0, shift_square_trace),
        ),
    )
    q = _add(q, _constant(-0.5 * chi_u * chi_u))
    density_bracket = _add(
        _add(_mul(adm_lapse, ricci_four), _mul(q, _reciprocal(adm_lapse))),
        _scale(-potential, adm_lapse),
    )
    return _mul(root_gamma, density_bracket)


def _exact_local_density(epsilon: float, sample: Mapping[str, Any]) -> float:
    warp = sample["warp"] + epsilon * sample["zeta"]
    hubble = sample["warp_u"] + epsilon * sample["zeta_u"]
    adm_lapse = 1.0 + epsilon * sample["lapse"]
    dzeta = epsilon * sample["zeta_gradient"]
    dbeta = epsilon * sample["beta_gradient"]
    ddbeta = epsilon * sample["beta_hessian"]
    raised_dzeta = ETA @ dzeta
    covariant_beta_hessian = (
        ddbeta
        - np.outer(dzeta, dbeta)
        - np.outer(dbeta, dzeta)
        + ETA * float(raised_dzeta @ dbeta)
    )
    shift_matrix = math.exp(-2.0 * warp) * ETA @ covariant_beta_hessian
    shift_trace = float(np.trace(shift_matrix))
    q = (
        12.0 * hubble * hubble
        - 6.0 * hubble * shift_trace
        + shift_trace * shift_trace
        - float(np.trace(shift_matrix @ shift_matrix))
        - 0.5 * sample["chi_u"] ** 2
    )
    gradient_square = float(dzeta @ ETA @ dzeta)
    ricci_four = math.exp(-2.0 * warp) * (
        -6.0 * epsilon * sample["zeta_box"] - 6.0 * gradient_square
    )
    return math.exp(4.0 * warp) * (
        adm_lapse * ricci_four
        + q / adm_lapse
        - adm_lapse * sample["potential"]
    )


def _local_sample(effective: Mapping[str, Any]) -> dict[str, Any]:
    middle = len(effective["u"]) // 2
    rng = np.random.default_rng(20260830)
    raw_hessian = rng.normal(scale=0.13, size=(4, 4))
    return {
        "warp": float(effective["A"][middle]),
        "warp_u": float(effective["A_u"][middle]),
        "chi_u": float(effective["canonical_chi_u"][middle]),
        "potential": float(effective["potential_V_of_phi"][middle]),
        "zeta": 0.17,
        "zeta_u": -0.11,
        "lapse": 0.09,
        "zeta_gradient": rng.normal(scale=0.08, size=4),
        "zeta_box": -0.07,
        "beta_gradient": rng.normal(scale=0.06, size=4),
        "beta_hessian": 0.5 * (raw_hessian + raw_hessian.T),
    }


def _extrinsic_identity_check() -> dict[str, float]:
    rng = np.random.default_rng(23051905)
    relative_errors: list[float] = []
    for _ in range(32):
        omega = float(rng.normal(scale=0.4))
        hubble = float(rng.normal(scale=0.8))
        adm_lapse = float(rng.uniform(0.55, 1.7))
        dzeta = rng.normal(scale=0.2, size=4)
        dbeta = rng.normal(scale=0.2, size=4)
        raw_hessian = rng.normal(scale=0.25, size=(4, 4))
        ddbeta = 0.5 * (raw_hessian + raw_hessian.T)
        covariant_beta_hessian = (
            ddbeta
            - np.outer(dzeta, dbeta)
            - np.outer(dbeta, dzeta)
            + ETA * float((ETA @ dzeta) @ dbeta)
        )
        gamma = math.exp(2.0 * omega) * ETA
        gamma_inverse = math.exp(-2.0 * omega) * ETA
        extrinsic_lower = (
            hubble * gamma - covariant_beta_hessian
        ) / adm_lapse
        extrinsic_mixed = gamma_inverse @ extrinsic_lower
        direct = float(
            np.trace(extrinsic_mixed) ** 2
            - np.trace(extrinsic_mixed @ extrinsic_mixed)
        )
        shift_matrix = gamma_inverse @ covariant_beta_hessian
        shift_trace = float(np.trace(shift_matrix))
        reduced = (
            12.0 * hubble * hubble
            - 6.0 * hubble * shift_trace
            + shift_trace * shift_trace
            - float(np.trace(shift_matrix @ shift_matrix))
        ) / adm_lapse**2
        relative_errors.append(
            abs(direct - reduced) / max(abs(direct), abs(reduced), 1.0)
        )
    return {
        "random_trials": len(relative_errors),
        "maximum_relative_error": max(relative_errors),
    }


def _lapse_variation_check(sample: Mapping[str, Any]) -> dict[str, float]:
    epsilon = 0.37
    warp = sample["warp"] + epsilon * sample["zeta"]
    hubble = sample["warp_u"] + epsilon * sample["zeta_u"]
    dzeta = epsilon * sample["zeta_gradient"]
    dbeta = epsilon * sample["beta_gradient"]
    ddbeta = epsilon * sample["beta_hessian"]
    covariant_beta_hessian = (
        ddbeta
        - np.outer(dzeta, dbeta)
        - np.outer(dbeta, dzeta)
        + ETA * float((ETA @ dzeta) @ dbeta)
    )
    shift_matrix = math.exp(-2.0 * warp) * ETA @ covariant_beta_hessian
    shift_trace = float(np.trace(shift_matrix))
    q = (
        12.0 * hubble * hubble
        - 6.0 * hubble * shift_trace
        + shift_trace**2
        - float(np.trace(shift_matrix @ shift_matrix))
        - 0.5 * sample["chi_u"] ** 2
    )
    ricci_four = math.exp(-2.0 * warp) * (
        -6.0 * epsilon * sample["zeta_box"]
        - 6.0 * float(dzeta @ ETA @ dzeta)
    )
    root_gamma = math.exp(4.0 * warp)
    adm_lapse = 1.0 + epsilon * sample["lapse"]

    def density_for_lapse(value: float) -> float:
        return root_gamma * (
            value * ricci_four + q / value - value * sample["potential"]
        )

    step = 1.0e-5
    numeric = (
        density_for_lapse(adm_lapse + step)
        - density_for_lapse(adm_lapse - step)
    ) / (2.0 * step)
    analytic = root_gamma * (
        ricci_four - q / adm_lapse**2 - sample["potential"]
    )
    return {
        "numeric": numeric,
        "analytic": analytic,
        "relative_error": abs(numeric - analytic)
        / max(abs(numeric), abs(analytic), 1.0),
    }


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective Einstein--dilaton input is not certified")

    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    potential = np.asarray(effective["potential_V_of_phi"], dtype=float)
    background_constraint = 12.0 * warp_u**2 - 0.5 * chi_u**2 + potential
    background_scale = np.maximum(
        np.maximum(12.0 * warp_u**2, 0.5 * chi_u**2), np.abs(potential)
    )
    background_relative = np.abs(background_constraint) / np.maximum(
        background_scale, 1.0
    )

    sample = _local_sample(effective)
    coefficients = quartic_density_jet(**sample)
    remainders: list[float] = []
    for epsilon in (0.02, 0.01, 0.005):
        exact = _exact_local_density(epsilon, sample)
        truncated = float(
            sum(coefficients[n] * epsilon**n for n in range(ORDER + 1))
        )
        remainders.append(abs(exact - truncated))
    ratios = [
        remainders[index] / remainders[index + 1]
        for index in range(len(remainders) - 1)
    ]
    extrinsic = _extrinsic_identity_check()
    lapse_variation = _lapse_variation_check(sample)

    checks = {
        "certified_effective_action_input": True,
        "no_observational_tables_read": True,
        "background_hamiltonian_constraint": bool(
            np.max(np.abs(background_constraint)) < 1.0e-12
            and np.max(background_relative) < 1.0e-13
        ),
        "extrinsic_curvature_identity": (
            extrinsic["maximum_relative_error"] < 1.0e-13
        ),
        "lapse_variation_identity": lapse_variation["relative_error"] < 1.0e-9,
        "quartic_jet_has_nonzero_S2_S3_S4": bool(
            all(abs(float(coefficients[n])) > 1.0e-12 for n in (2, 3, 4))
        ),
        "quartic_truncation_has_fifth_order_remainder": bool(
            min(ratios) > 27.0 and max(ratios) < 37.0
        ),
    }
    checks["all"] = all(checks.values())

    physical_gates = {
        "exact_bulk_ADM_scalar_density_identified": True,
        "quartic_local_jet_generator_implemented": True,
        "lapse_algebraic_solution_through_second_order_identified": True,
        "same_variables_recover_certified_S2_master_action": False,
        "shift_constraint_solved_through_second_order": False,
        "lapse_solution_substituted_through_second_order": False,
        "second_gauge_reduction_agrees": False,
        "finite_endpoint_GHY_brane_bending_combined": False,
        "compact_physical_S3_coefficients_projected": False,
        "direct_physical_S4_contact_projected": False,
    }
    physical_gates["physical_compact_S4_complete"] = all(
        physical_gates.values()
    )

    return {
        "schema": "holo.radial-adm-quartic-seed.v1",
        "title": "Exact radial ADM scalar seed with a bounded quartic jet",
        "classification": (
            "exact_bulk_ADM_vehicle_derived;physical_compact_S3_S4_not_yet_derived"
        ),
        "action_convention": {
            "five_dimensional_action": (
                "S=(2*kappa5^2)^(-1)*integral sqrt(-G)*"
                "[R-(partial chi)^2/2-V(chi)]"
            ),
            "radial_metric": (
                "ds^2=N^2 du^2+gamma_mn(dx^m+N^m du)(dx^n+N^n du)"
            ),
            "scalar_gauge": (
                "chi=chi_bar(u), gamma_mn=exp(2(A+zeta))*eta_mn, "
                "N_m=partial_m beta"
            ),
            "extrinsic_curvature": (
                "K_mn=(gamma'_mn-D_m N_n-D_n N_m)/(2N)"
            ),
            "boundary_bookkeeping": (
                "The displayed slab density assumes the conventional EH+GHY "
                "cancellation of radial total derivatives. Finite brane potentials, "
                "orientations, orbifold factors, bending and junction terms remain "
                "an explicit separate gate."
            ),
        },
        "exact_density": {
            "Omega": "A+zeta",
            "H": "A'+zeta'",
            "C_mn": (
                "partial_m partial_n beta-zeta_m beta_n-zeta_n beta_m+"
                "eta_mn*(partial zeta dot partial beta)"
            ),
            "B^m_n": "exp(-2*Omega)*eta^(mk)*C_kn",
            "R4": "exp(-2*Omega)*[-6 box(zeta)-6(partial zeta)^2]",
            "Q": (
                "12*H^2-6*H*tr(B)+tr(B)^2-tr(B^2)-chi_bar'^2/2"
            ),
            "bulk_lagrangian_after_GHY": (
                "L=sqrt(-gamma)*[N*R4+Q/N-N*V]"
            ),
            "hamiltonian_constraint": "R4-Q/N^2-V=0",
            "positive_lapse_branch": (
                "N^2=Q/(R4-V), only where the ratio is positive; do not choose "
                "a square-root sign independently across a zero"
            ),
            "lapse_eliminated_density": (
                "L_onN=2*sqrt(-gamma)*(R4-V)*sqrt(Q/(R4-V)) on the "
                "continuous N>0 branch; writing +2*sqrt[Q*(R4-V)] also "
                "requires Q and R4-V to be positive"
            ),
            "momentum_constraint": (
                "D_n{N^-1*[3H*delta^n_m+B^n_m-delta^n_m*tr(B)]}=0 "
                "in unitary gauge; it remains to be solved for beta before "
                "any physical vertex projection"
            ),
        },
        "constraint_solution_contract": {
            "linear_solution": {
                "alpha1": "zeta'/A'",
                "box_beta1": (
                    "box(zeta)/A'+exp(2A)*epsilon_ED*zeta'"
                ),
                "epsilon_ED": "-A''/A'^2=chi_bar'^2/(6*A'^2)",
            },
            "generic_lapse_series": {
                "definitions": "Q/Q0=1+f1+f2+...; (R4-V)/(R4-V)0=1+d1+d2+...",
                "alpha1": "(f1-d1)/2",
                "alpha2": (
                    "(f2-d2)/2+3*d1^2/8-d1*f1/4-f1^2/8"
                ),
            },
            "orders_needed": {
                "S2": "alpha1,beta1",
                "S3": "alpha1,beta1",
                "S4": "alpha1,alpha2,beta1,beta2; never alpha3,beta3",
            },
            "second_order_closure_falsifier": (
                "Before restricting the shift, project the second-order momentum "
                "constraint transversely. If P_T C^(2) is nonzero, add N_m^T. "
                "Likewise retain the induced TT metric as an exchange channel, "
                "not as a direct scalar contact."
            ),
        },
        "verification": {
            "background_samples": int(warp_u.size),
            "background_constraint_max_abs": float(
                np.max(np.abs(background_constraint))
            ),
            "background_constraint_max_relative": float(
                np.max(background_relative)
            ),
            "extrinsic_curvature": extrinsic,
            "lapse_variation": lapse_variation,
            "quartic_jet": {
                "coefficient_convention": "L(epsilon)=sum_n L_n epsilon^n",
                "local_coefficients_L0_to_L4": coefficients.tolist(),
                "absolute_remainders_at_epsilon_0p02_0p01_0p005": remainders,
                "halving_remainder_ratios": ratios,
                "expected_ratio_for_fifth_order_remainder": 32.0,
            },
        },
        "bounded_execution_contract": {
            "representation": (
                "degree-four coefficient jets with DAG common-subexpression "
                "elimination; stream radial quadrature"
            ),
            "forbidden_dense_object": "N_mode^4 quartic tensor",
            "required_projection": (
                "only h0^4 and h0^2*ha exchange channels on nested 3/5/7 modes"
            ),
            "cas_peak_rss_mib_max": 512,
            "numeric_peak_rss_mib_max": 128,
            "this_local_jet_bytes": int(coefficients.nbytes),
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "inputs": {
            "observational_tables_read": [],
            "effective_action": {
                "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                "sha256": _sha256(EFFECTIVE_ACTION),
            },
        },
        "next_decisive_test": (
            "Solve lapse and shift consistently, recover the certified S2 operator "
            "and normalization in these variables, then compare c000 with the BMP "
            "bulk oracle before adding finite-endpoint terms."
        ),
        "evidence_boundary": (
            "This certificate derives and checks the exact local bulk ADM vehicle "
            "that can generate quartic vertices. It does not yet solve constraints, "
            "include the physical finite boundaries, project a compact S3/S4, or "
            "support a new-force claim."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        raise SystemExit("ADM quartic seed certificate failed")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        "[background constraint max abs] "
        f"{result['verification']['background_constraint_max_abs']:.3e}"
    )
    print(
        "[extrinsic identity max relative] "
        f"{result['verification']['extrinsic_curvature']['maximum_relative_error']:.3e}"
    )
    print(
        "[physical compact S4 complete] "
        f"{result['physical_gates']['physical_compact_S4_complete']}"
    )
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
