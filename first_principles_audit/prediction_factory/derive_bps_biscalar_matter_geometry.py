#!/usr/bin/env python3
"""Derive the two-modulus matter-selector geometry on the real ED background.

The functional-BPS interval starts with two candidate zero-mode solutions.
This certificate proves that their endpoint map is invertible and their
Einstein-frame kinetic metric is positive, resolving two physical moduli.  It
keeps both endpoint positions, ``y=(u_-,u_+)``, and computes for
each endpoint inverse induced conformal factor (the normalized Jordan
curvature selector)

    C_i(y) = [F(y)/F_0] exp[-2(A_i(y)-A_i(y_0))],
    F(y)   = integral_{u_-}^{u_+} exp(2A) du.

It derives the covectors C_{i,a}, coordinate Hessians C_{i,ab}, the physical
Einstein-frame endpoint moduli metric (up to one positive constant) and its
Levi-Civita connection.  This permits the invariant
question: does a unit tangent v with v^a C_{i,a}=0 exist, and is
v^a v^b nabla_a nabla_b C_i nonzero?

An algebraic tangent is not a dynamically selected field.  The output fails
closed unless the brane theory selects a unique physical tangent, fixes the
matter localization and supplies the absolute kappa_5/ell normalization.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import cumulative_trapezoid, simpson


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EFFECTIVE_ACTION = (
    REPO / "first_principles_audit/artifacts/holo_effective_action.json"
)
BPS_CERTIFICATE = HERE / "artifacts/adm_bmp_tricritical_necessity.json"
OUTPUT = HERE / "artifacts/bps_biscalar_matter_geometry.json"

CRITERIA = {
    "background_samples": 1979,
    "stored_gram_relative_max": 2.0e-7,
    "endpoint_metric_transform_relative_max": 1.0e-6,
    "local_selector_jet_relative_max": 1.0e-4,
    "local_metric_derivative_relative_max": 1.0e-4,
    "endpoint_map_determinant_abs_min": 1.0e-6,
    "metric_min_eigenvalue": 1.0e-6,
    "silent_tangent_residual_max": 1.0e-12,
    "projected_covariant_curvature_negative_max": -1.0e-8,
    "common_covector_gram_determinant_min": 1.0e-6,
    "palma_davis_weyl_reconstruction_relative_max": 1.0e-12,
    "palma_davis_corrected_relative_max": 1.0e-12,
    "palma_davis_literal_max_eigenvalue_negative": -1.0e-6,
}


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


def _relative(left: np.ndarray, right: np.ndarray) -> float:
    return float(
        np.linalg.norm(np.asarray(left) - np.asarray(right))
        / max(np.linalg.norm(np.asarray(right)), 1.0e-300)
    )


def _endpoint_metric_from_basis(
    gram: np.ndarray, endpoint_map: np.ndarray
) -> np.ndarray:
    gram = np.asarray(gram, dtype=float)
    endpoint_map = np.asarray(endpoint_map, dtype=float)
    if gram.shape != (2, 2) or endpoint_map.shape != (2, 2):
        raise ValueError("two-by-two Gram and endpoint map required")
    if abs(float(np.linalg.det(endpoint_map))) <= 1.0e-14:
        raise ValueError("endpoint-to-zero-mode map is singular")
    inverse = np.linalg.inv(endpoint_map)
    return inverse.T @ gram @ inverse


def _closed_endpoint_gram_I(
    E_minus: float,
    E_plus: float,
    H_minus: float,
    H_plus: float,
    F: float,
) -> np.ndarray:
    """Dimensionless endpoint Gram metric before the factor 6/kappa_5^2."""

    return np.asarray(
        [
            [
                E_minus * (E_minus + 2.0 * F * H_minus) / (4.0 * F),
                -E_minus * E_plus / (4.0 * F),
            ],
            [
                -E_minus * E_plus / (4.0 * F),
                E_plus * (E_plus - 2.0 * F * H_plus) / (4.0 * F),
            ],
        ],
        dtype=float,
    )


def _endpoint_gram_derivatives_I(
    E_minus: float,
    E_plus: float,
    H_minus: float,
    H_plus: float,
    H_u_minus: float,
    H_u_plus: float,
    F: float,
) -> np.ndarray:
    """Return partial_c I_ab in endpoint coordinates (c,a,b)."""

    Em, Ep, Hm, Hp, Bm, Bp = (
        E_minus,
        E_plus,
        H_minus,
        H_plus,
        H_u_minus,
        H_u_plus,
    )
    derivatives = np.empty((2, 2, 2), dtype=float)
    derivatives[0] = np.asarray(
        [
            [
                Em
                * (
                    2.0 * Bm * F**2
                    + Em**2
                    + 4.0 * Em * F * Hm
                    + 4.0 * F**2 * Hm**2
                )
                / (4.0 * F**2),
                -Em * Ep * (Em + 2.0 * F * Hm) / (4.0 * F**2),
            ],
            [
                -Em * Ep * (Em + 2.0 * F * Hm) / (4.0 * F**2),
                Em * Ep**2 / (4.0 * F**2),
            ],
        ]
    )
    derivatives[1] = np.asarray(
        [
            [
                -Em**2 * Ep / (4.0 * F**2),
                Em * Ep * (Ep - 2.0 * F * Hp) / (4.0 * F**2),
            ],
            [
                Em * Ep * (Ep - 2.0 * F * Hp) / (4.0 * F**2),
                -Ep
                * (
                    2.0 * Bp * F**2
                    + Ep**2
                    - 4.0 * Ep * F * Hp
                    + 4.0 * F**2 * Hp**2
                )
                / (4.0 * F**2),
            ],
        ]
    )
    return derivatives


def _christoffel(metric: np.ndarray, derivative: np.ndarray) -> np.ndarray:
    metric = np.asarray(metric, dtype=float)
    derivative = np.asarray(derivative, dtype=float)
    if metric.shape != (2, 2) or derivative.shape != (2, 2, 2):
        raise ValueError("unexpected metric or derivative shape")
    inverse = np.linalg.inv(metric)
    connection = np.zeros((2, 2, 2), dtype=float)
    for upper in range(2):
        for left in range(2):
            for right in range(2):
                connection[upper, left, right] = 0.5 * sum(
                    inverse[upper, contracted]
                    * (
                        derivative[left, contracted, right]
                        + derivative[right, contracted, left]
                        - derivative[contracted, left, right]
                    )
                    for contracted in range(2)
                )
    return connection


def _selector_jets(
    E_minus: float,
    E_plus: float,
    H_minus: float,
    H_plus: float,
    H_u_minus: float,
    H_u_plus: float,
    F: float,
) -> dict[str, dict[str, np.ndarray | float]]:
    ratios = np.asarray([E_minus / F, E_plus / F], dtype=float)
    H = np.asarray([H_minus, H_plus], dtype=float)
    H_u = np.asarray([H_u_minus, H_u_plus], dtype=float)
    log_F_hessian = np.asarray(
        [
            [
                -2.0 * H_minus * ratios[0] - ratios[0] ** 2,
                ratios[0] * ratios[1],
            ],
            [
                ratios[0] * ratios[1],
                2.0 * H_plus * ratios[1] - ratios[1] ** 2,
            ],
        ]
    )
    result: dict[str, dict[str, np.ndarray | float]] = {}
    for label, endpoint in (("lower", 0), ("upper", 1)):
        gradient = np.asarray([-ratios[0], ratios[1]], dtype=float)
        gradient[endpoint] -= 2.0 * H[endpoint]
        log_hessian = log_F_hessian.copy()
        log_hessian[endpoint, endpoint] -= 2.0 * H_u[endpoint]
        hessian = log_hessian + np.outer(gradient, gradient)
        result[label] = {
            "value": 1.0,
            "gradient": gradient,
            "coordinate_hessian": hessian,
            "log_hessian": log_hessian,
        }
    return result


def _selector_invariants(
    metric: np.ndarray,
    gradient: np.ndarray,
    covariant_hessian: np.ndarray,
    coordinate_hessian: np.ndarray | None = None,
) -> dict[str, Any]:
    metric = np.asarray(metric, dtype=float)
    gradient = np.asarray(gradient, dtype=float)
    covariant_hessian = np.asarray(covariant_hessian, dtype=float)
    inverse = np.linalg.inv(metric)
    raw_tangent = np.asarray([gradient[1], -gradient[0]], dtype=float)
    norm = float(np.sqrt(raw_tangent @ metric @ raw_tangent))
    if norm <= 0.0:
        raise ValueError("silent tangent has nonpositive norm")
    tangent = raw_tangent / norm
    result = {
        "gradient_norm_squared": float(gradient @ inverse @ gradient),
        "unit_silent_tangent": tangent.tolist(),
        "linear_silence_residual": float(abs(gradient @ tangent)),
        "metric_unit_residual": float(abs(tangent @ metric @ tangent - 1.0)),
        "covariant_projected_curvature": float(
            tangent @ covariant_hessian @ tangent
        ),
    }
    result["covariant_quadratic_Taylor_coefficient"] = (
        0.5 * result["covariant_projected_curvature"]
    )
    if coordinate_hessian is not None:
        result["coordinate_projected_curvature_noninvariant"] = float(
            tangent @ np.asarray(coordinate_hessian) @ tangent
        )
    result["one_minus_C_quadratic_coefficient"] = float(
        -0.5 * result["covariant_projected_curvature"]
    )
    return result


def _common_silence(metric: np.ndarray, gradients: np.ndarray) -> dict[str, Any]:
    inverse = np.linalg.inv(np.asarray(metric, dtype=float))
    gradients = np.asarray(gradients, dtype=float)
    covector_gram = gradients @ inverse @ gradients.T
    singular = np.linalg.svd(gradients, compute_uv=False)
    determinant = float(np.linalg.det(covector_gram))
    correlation = float(
        covector_gram[0, 1]
        / np.sqrt(covector_gram[0, 0] * covector_gram[1, 1])
    )
    return {
        "covector_gram": covector_gram.tolist(),
        "covector_gram_determinant": determinant,
        "metric_correlation": correlation,
        "ordinary_gradient_matrix_determinant": float(
            np.linalg.det(gradients)
        ),
        "ordinary_gradient_singular_values": singular.tolist(),
        "common_nonzero_silent_tangent_exists": bool(
            singular[-1] <= 1.0e-12 * singular[0]
        ),
    }


def _local_real_geometry_fit(
    u: np.ndarray,
    warp: np.ndarray,
    warp_u: np.ndarray,
    cumulative_F: np.ndarray,
    points: int = 10,
) -> dict[str, Any]:
    """One-sided two-dimensional fit using only nearby real ED samples."""

    monomials = [
        (left, degree - left)
        for degree in range(6)
        for left in range(degree + 1)
    ]
    offsets: list[tuple[float, float]] = []
    selectors: dict[str, list[float]] = {"lower": [], "upper": []}
    metrics: list[np.ndarray] = []
    F0 = float(cumulative_F[-1])
    for lower_offset in range(points):
        lower = lower_offset
        for upper_offset in range(points):
            upper = u.size - 1 - upper_offset
            delta_minus = float(u[lower] - u[0])
            delta_plus = float(u[upper] - u[-1])
            F = float(cumulative_F[upper] - cumulative_F[lower])
            Em = float(np.exp(2.0 * warp[lower]))
            Ep = float(np.exp(2.0 * warp[upper]))
            offsets.append((delta_minus, delta_plus))
            selectors["lower"].append(
                F
                / F0
                * float(np.exp(-2.0 * (warp[lower] - warp[0])))
            )
            selectors["upper"].append(
                F
                / F0
                * float(np.exp(-2.0 * (warp[upper] - warp[-1])))
            )
            # The Einstein-frame kinetic metric per M_Pl^2 is 6 I/F.  Store
            # I/F here so that this one-sided fit validates both the endpoint
            # Gram derivatives and the field-dependent Weyl factor.
            metrics.append(
                _closed_endpoint_gram_I(
                    Em,
                    Ep,
                    float(warp_u[lower]),
                    float(warp_u[upper]),
                    F,
                )
                / F
            )

    scale = max(abs(value) for pair in offsets for value in pair)
    design = np.asarray(
        [
            [
                (delta_minus / scale) ** left
                * (delta_plus / scale) ** right
                for left, right in monomials
            ]
            for delta_minus, delta_plus in offsets
        ]
    )

    def fit(values: np.ndarray) -> dict[str, np.ndarray | float]:
        coefficients = np.linalg.lstsq(design, values, rcond=None)[0]
        mapped = {
            power: coefficients[index] / scale ** sum(power)
            for index, power in enumerate(monomials)
        }
        return {
            "value": mapped[(0, 0)],
            "gradient": np.asarray([mapped[(1, 0)], mapped[(0, 1)]]),
            "hessian": np.asarray(
                [
                    [2.0 * mapped[(2, 0)], mapped[(1, 1)]],
                    [mapped[(1, 1)], 2.0 * mapped[(0, 2)]],
                ]
            ),
        }

    selector_fits = {
        label: fit(np.asarray(values)) for label, values in selectors.items()
    }
    metric_values = np.asarray(metrics)
    metric_coefficients = np.linalg.lstsq(
        design, metric_values.reshape(metric_values.shape[0], 4), rcond=None
    )[0]
    metric_mapped = {
        power: metric_coefficients[index].reshape(2, 2)
        / scale ** sum(power)
        for index, power in enumerate(monomials)
    }
    return {
        "points_per_endpoint": points,
        "fit_degree": 5,
        "samples": len(offsets),
        "selector_fits": selector_fits,
        "metric_value": metric_mapped[(0, 0)],
        "metric_derivatives": np.asarray(
            [metric_mapped[(1, 0)], metric_mapped[(0, 1)]]
        ),
    }


def _palma_davis_oracle(
    E_minus: float,
    E_plus: float,
    H_minus: float,
    H_plus: float,
    chi_u_minus: float,
    chi_u_plus: float,
    F: float,
    einstein_metric_hat: np.ndarray,
) -> dict[str, Any]:
    """Rebuild Palma--Davis Eqs. (26--28) from Eqs. (21--23) and Weyl."""

    k = E_minus / F
    psi_u = np.sqrt(2.0 / 3.0) * np.asarray(
        [chi_u_minus, chi_u_plus]
    )
    U_B = -4.0 * np.asarray([H_minus, H_plus])
    alpha = psi_u / U_B
    A1_squared = 1.0
    A2_squared = E_plus / E_minus
    omega_2_squared = E_plus / E_minus

    # Jordan-frame Eqs. (21)--(23), evaluated at Omega^2=1.
    jordan = np.asarray(
        [
            [
                alpha[0] ** -2 * (k / U_B[0] - 0.5),
                -alpha[0] ** -1
                * alpha[1] ** -1
                * omega_2_squared
                * k
                / U_B[1],
            ],
            [
                -alpha[0] ** -1
                * alpha[1] ** -1
                * omega_2_squared
                * k
                / U_B[1],
                alpha[1] ** -2 * omega_2_squared * k / U_B[1],
            ],
        ]
    )
    # Omega^2=kF/E_- globally. Convert endpoint derivatives of ln Omega to
    # the paper's boundary-scalar coordinates psi^a.
    d_ln_Omega_d_endpoint = 0.5 * np.asarray(
        [-E_minus / F - 2.0 * H_minus, E_plus / F]
    )
    d_ln_Omega_d_psi = d_ln_Omega_d_endpoint / psi_u
    weyl_reconstructed = jordan + 8.0 * np.outer(
        d_ln_Omega_d_psi, d_ln_Omega_d_psi
    )

    # Closed Einstein-frame Eqs. (26)--(28), with the cross term obtained
    # from the Weyl reconstruction rather than the printed alpha_1 alpha_2.
    gamma_11 = (
        2.0
        * alpha[0] ** -2
        * k**2
        * A1_squared**2
        / U_B[0] ** 2
        * (1.0 - U_B[0] / (2.0 * k * A1_squared))
    )
    gamma_22 = (
        2.0
        * alpha[1] ** -2
        * k**2
        * A2_squared**2
        / U_B[1] ** 2
        * (1.0 + U_B[1] / (2.0 * k * A2_squared))
    )
    common = -2.0 * k**2 * A1_squared * A2_squared / (U_B[0] * U_B[1])
    corrected = np.asarray(
        [
            [gamma_11, common / (alpha[0] * alpha[1])],
            [common / (alpha[0] * alpha[1]), gamma_22],
        ]
    )
    literal = np.asarray(
        [
            [gamma_11, common * alpha[0] * alpha[1]],
            [common * alpha[0] * alpha[1], gamma_22],
        ]
    )
    jacobian = np.diag(psi_u)

    def to_endpoint(gamma: np.ndarray) -> np.ndarray:
        return (3.0 / (2.0 * k)) * jacobian @ gamma @ jacobian

    corrected_endpoint = to_endpoint(weyl_reconstructed)
    literal_endpoint = to_endpoint(literal)
    # In endpoint coordinates Palma--Davis gives
    # G_abs=(2/kappa5^2*k) Khat with Khat=6I/F.  The positive overall factor
    # 2/k is conventional here and does not affect the connection.
    expected_positive_scale = 2.0 / k
    expected = expected_positive_scale * einstein_metric_hat
    return {
        "reference": {
            "authors": "Gonzalo A. Palma and Anne-Christine Davis",
            "title": "Moduli-Space Approximation for BPS Brane-Worlds",
            "arxiv": "hep-th/0407036",
            "url": "https://arxiv.org/abs/hep-th/0407036",
        },
        "convention_map": {
            "psi": "sqrt(2/3)*chi",
            "U_B": "2W/3=-4A'",
            "k": "exp(2A_-)/F0",
            "Omega_at_reference": 1.0,
        },
        "corrected_cross_term": (
            "gamma_12=-2*alpha_1^-1*alpha_2^-1*k^2*A_1^2*A_2^2/"
            "(U_B1*U_B2), obtained by transforming Eqs. (21)-(23)"
        ),
        "printed_equation_28_mutation": (
            "replace alpha_1^-1*alpha_2^-1 by alpha_1*alpha_2"
        ),
        "Jordan_gamma_from_equations_21_to_23": jordan.tolist(),
        "d_ln_Omega_d_psi": d_ln_Omega_d_psi.tolist(),
        "Weyl_rule": (
            "gamma_E=Omega^-2*gamma_J+8*dlnOmega tensor dlnOmega"
        ),
        "Weyl_reconstructed_gamma_psi": weyl_reconstructed.tolist(),
        "closed_corrected_gamma_psi": corrected.tolist(),
        "Weyl_vs_closed_corrected_relative": _relative(
            weyl_reconstructed, corrected
        ),
        "corrected_gamma_psi": corrected.tolist(),
        "literal_gamma_psi": literal.tolist(),
        "corrected_endpoint_metric": corrected_endpoint.tolist(),
        "literal_endpoint_metric": literal_endpoint.tolist(),
        "corrected_endpoint_eigenvalues": np.linalg.eigvalsh(
            corrected_endpoint
        ).tolist(),
        "literal_endpoint_eigenvalues": np.linalg.eigvalsh(
            literal_endpoint
        ).tolist(),
        "Einstein_metric_relation": (
            "G_endpoint_without_kappa5=(2/k)*Khat, Khat=6I/F"
        ),
        "expected_positive_scale_relative_to_Khat": expected_positive_scale,
        "corrected_relative_to_expected": _relative(
            corrected_endpoint, expected
        ),
    }


def _local_diagonal_stabilizer_gate(
    gradient: np.ndarray,
    quadratic_weights: np.ndarray,
    sextic_weights: np.ndarray,
) -> dict[str, Any]:
    gradient = np.asarray(gradient, dtype=float)
    quadratic_weights = np.asarray(quadratic_weights, dtype=float)
    sextic_weights = np.asarray(sextic_weights, dtype=float)
    both_components_nonzero = bool(np.all(np.abs(gradient) > 1.0e-12))
    silent_tangent_has_same_sign_components = bool(
        gradient[0] * gradient[1] < 0.0
    )
    return {
        "localized_quadratic_Hessian_over_kappa5_inverse_squared": (
            "diag(w_-*gamma_-,w_+*gamma_+)"
        ),
        "localized_quadratic_weights": quadratic_weights.tolist(),
        "localized_sextic_coefficients_times_rho_over_kappa5_squared": (
            sextic_weights.tolist()
        ),
        "strictly_positive_diagonal_quadratic_has_massless_direction": False,
        "semidefinite_diagonal_kernel_is_coordinate_axis": True,
        "selector_gradient_has_nonzero_component_on_both_axes": (
            both_components_nonzero
        ),
        "positive_local_diagonal_quadratic_selects_silent_tangent": False,
        "positive_local_diagonal_sextic_gives_positive_q6_along_tangent": True,
        "diagonal_sextic_selects_a_unique_linear_tangent_at_origin": False,
        "silent_tangent_has_same_sign_endpoint_components": (
            silent_tangent_has_same_sign_components
        ),
        (
            "fixed_separation_minimizer_for_positive_diagonal_even_p_has_"
            "opposite_sign_components"
        ): True,
        "positive_diagonal_p2_or_p6_completion_can_select_silent_tangent": False,
        "interpretation": (
            "Local positive gamma_i terms either gap both endpoint moduli or "
            "leave a coordinate-axis kernel, which is not silent. Positive "
            "rho_i X_i^6 stabilizes every nonzero direction when both rho_i "
            "are positive, but does not select one tangent through S2. More "
            "strongly, minimizing a|dy_-|^p+b|dy_+|^p at fixed separation "
            "for p=2 or p=6 and a,b>0 gives endpoint components of opposite "
            "sign, while the silent tangent has equal signs. A correlated "
            "non-diagonal stabilizer would be additional brane physics."
        ),
    }


def build() -> dict[str, Any]:
    effective = _read(EFFECTIVE_ACTION)
    bps = _read(BPS_CERTIFICATE)
    if effective.get("summary", {}).get("passes", {}).get("all") is not True:
        raise RuntimeError("effective-action background is not certified")
    if bps.get("checks", {}).get("all") is not True:
        raise RuntimeError("real-background BPS certificate must pass first")

    u = np.asarray(effective["u"], dtype=float)
    warp = np.asarray(effective["A"], dtype=float)
    warp_u = np.asarray(effective["A_u"], dtype=float)
    chi_u = np.asarray(effective["canonical_chi_u"], dtype=float)
    if not (
        u.size == CRITERIA["background_samples"]
        and all(array.shape == u.shape for array in (warp, warp_u, chi_u))
        and all(np.all(np.isfinite(array)) for array in (u, warp, warp_u, chi_u))
        and np.all(np.diff(u) > 0.0)
        and np.all(warp_u < 0.0)
        and np.all(chi_u > 0.0)
    ):
        raise ValueError("invalid reconstructed Einstein--dilaton background")

    E = np.exp(2.0 * warp)
    cumulative_F = cumulative_trapezoid(E, u, initial=0.0)
    F = float(cumulative_F[-1])
    Em, Ep = (float(E[0]), float(E[-1]))
    Hm, Hp = (float(warp_u[0]), float(warp_u[-1]))
    Bm, Bp = (-float(chi_u[0] ** 2) / 6.0, -float(chi_u[-1] ** 2) / 6.0)
    endpoint_exp_4A = np.asarray([Em**2, Ep**2])
    endpoint_chi_u = np.asarray([chi_u[0], chi_u[-1]])
    localized_quadratic_weights = (
        0.5 * endpoint_exp_4A * np.square(endpoint_chi_u)
    )
    localized_sextic_weights = (
        endpoint_exp_4A * endpoint_chi_u**6 / 1440.0
    )

    psi_1 = warp_u / E
    psi_2 = 1.0 - 2.0 * warp_u * cumulative_F / E
    D_psi_1 = (-np.square(chi_u) / 6.0) / E
    D_psi_2 = -2.0 * (-np.square(chi_u) / 6.0) * cumulative_F / E
    profiles = (psi_1, psi_2)
    D_profiles = (D_psi_1, D_psi_2)
    recomputed_gram = np.asarray(
        [
            [
                float(
                    simpson(
                        E
                        * (
                            profiles[left] * profiles[right]
                            + 3.0
                            * D_profiles[left]
                            * D_profiles[right]
                            / np.square(chi_u)
                        ),
                        x=u,
                    )
                )
                for right in range(2)
            ]
            for left in range(2)
        ]
    )
    stored_gram = np.asarray(
        bps["massless_kernel"]["dimensionless_Gram_I"], dtype=float
    )

    # In unitary gauge beta=6 D(Psi)/chi'^2.  The source-free traceless
    # junction gives xi_i=-beta_i, hence dy_i=J_ia c^a for the two modes.
    endpoint_map = np.asarray(
        [[1.0 / Em, 0.0], [1.0 / Ep, -2.0 * F / Ep]], dtype=float
    )
    transformed_endpoint_gram = _endpoint_metric_from_basis(
        stored_gram, endpoint_map
    )
    closed_endpoint_gram = _closed_endpoint_gram_I(Em, Ep, Hm, Hp, F)
    single_interval_metric_hat = 6.0 * closed_endpoint_gram
    single_interval_metric_derivative_hat = 6.0 * _endpoint_gram_derivatives_I(
        Em, Ep, Hm, Hp, Bm, Bp, F
    )
    # The zero-mode Gram is not yet the Einstein-frame sigma-model metric.
    # Dividing by the four-dimensional Planck integral supplies the Weyl
    # factor.  Khat=6I/F equals K_ab/M_Pl^2 and is fixed up to the overall
    # positive canonical scale set by kappa_5 and the physical length ell.
    inverse_F_log_derivative = np.asarray([Em / F, -Ep / F])
    einstein_metric_hat = single_interval_metric_hat / F
    einstein_metric_derivative_hat = np.asarray(
        [
            (
                single_interval_metric_derivative_hat[index]
                + inverse_F_log_derivative[index]
                * single_interval_metric_hat
            )
            / F
            for index in range(2)
        ]
    )
    metric_eigenvalues = np.linalg.eigvalsh(einstein_metric_hat)
    connection = _christoffel(
        einstein_metric_hat, einstein_metric_derivative_hat
    )

    # Mutation: omitting 1/F uses a non-Einstein Gram connection and can even
    # reverse the projected-curvature sign.
    single_interval_connection = _christoffel(
        single_interval_metric_hat, single_interval_metric_derivative_hat
    )

    jets = _selector_jets(Em, Ep, Hm, Hp, Bm, Bp, F)
    fit = _local_real_geometry_fit(u, warp, warp_u, cumulative_F)
    selector_fit_errors: dict[str, dict[str, float]] = {}
    selector_results: dict[str, Any] = {}
    gradients = []
    for label in ("lower", "upper"):
        gradient = np.asarray(jets[label]["gradient"])
        hessian = np.asarray(jets[label]["coordinate_hessian"])
        covariant_hessian = hessian - np.einsum(
            "cab,c->ab", connection, gradient
        )
        invariants = _selector_invariants(
            einstein_metric_hat,
            gradient,
            covariant_hessian,
            coordinate_hessian=hessian,
        )
        fitted = fit["selector_fits"][label]
        selector_fit_errors[label] = {
            "value_abs": float(abs(float(fitted["value"]) - 1.0)),
            "gradient_relative": _relative(fitted["gradient"], gradient),
            "hessian_relative": _relative(fitted["hessian"], hessian),
        }
        selector_results[label] = {
            "definition": (
                "C_-=(F/F0)exp[-2(A_--A_-0)]"
                if label == "lower"
                else "C_+=(F/F0)exp[-2(A_+-A_+0)]"
            ),
            "C_at_reference": 1.0,
            "C_a": gradient.tolist(),
            "coordinate_C_ab": hessian.tolist(),
            "covariant_nabla_a_nabla_b_C": covariant_hessian.tolist(),
            "invariants_in_Khat_equals_6I_over_F_units": invariants,
            "conditional_geodesic_mixed_jets": {
                "coordinate": (
                    "qbar is a Khat-unit Riemann-normal coordinate along the "
                    "displayed silent tangent"
                ),
                "selector_identity": (
                    "C_i=A_i(reference)^2/A_i(y)^2 is the inverse normalized "
                    "induced conformal factor, not A_i(y)^2 itself"
                ),
                "qbar_Y_numerical_residual": float(
                    -gradient @ np.asarray(invariants["unit_silent_tangent"])
                ),
                "selector_expansion_on_silent_geodesic": {
                    "form": "C(qbar)=1+c2*qbar^2+O(qbar^3)",
                    "c2": invariants[
                        "covariant_quadratic_Taylor_coefficient"
                    ],
                },
                "target_auxiliary_s_equals_one_minus_C": {
                    "definition": "s(qbar)=1-C(qbar)",
                    "s_qbar_squared_coefficient": invariants[
                        "one_minus_C_quadratic_coefficient"
                    ],
                    "lagrangian": "L_aux=-s(qbar)*Y",
                    "qbar_Y_coefficient_by_construction": 0.0,
                    "qbar_squared_Y_candidate_coefficient": invariants[
                        "covariant_quadratic_Taylor_coefficient"
                    ],
                },
                "minimal_canonical_brane_scalar_in_Einstein_frame": {
                    "lagrangian": "L_minimal=-Y/C(qbar)",
                    "base_Y_coefficient": -1.0,
                    "qbar_Y_coefficient_by_construction": 0.0,
                    "qbar_squared_Y_candidate_coefficient": (
                        0.5 * invariants["covariant_projected_curvature"]
                    ),
                },
                "non_target_minus_C_times_Y_mutation": {
                    "lagrangian": "L_mutation=-C(qbar)*Y",
                    "qbar_squared_Y_coefficient": invariants[
                        "one_minus_C_quadratic_coefficient"
                    ],
                },
                "matter_Y_operator_identified_with_constitutive_Y": False,
                "physical_q2Y_vertex_derived": False,
                "reason_gate_remains_closed": (
                    "the BPS action does not select this tangent, absolute "
                    "normalization is open, and the constitutive Y has not "
                    "been identified with the minimal matter operator or trace "
                    "by a full constraint reduction"
                ),
            },
            "local_real_geometry_fit": {
                "C_a": np.asarray(fitted["gradient"]).tolist(),
                "coordinate_C_ab": np.asarray(fitted["hessian"]).tolist(),
                "errors": selector_fit_errors[label],
            },
            "local_diagonal_stabilizer": _local_diagonal_stabilizer_gate(
                gradient,
                localized_quadratic_weights,
                localized_sextic_weights,
            ),
            "omit_Einstein_Weyl_factor_mutation": _selector_invariants(
                single_interval_metric_hat,
                gradient,
                hessian
                - np.einsum("cab,c->ab", single_interval_connection, gradient),
                coordinate_hessian=hessian,
            ),
        }
        gradients.append(gradient)

    common = _common_silence(einstein_metric_hat, np.asarray(gradients))
    metric_fit_relative = _relative(
        6.0 * fit["metric_value"], einstein_metric_hat
    )
    metric_derivative_fit_relative = _relative(
        6.0 * fit["metric_derivatives"], einstein_metric_derivative_hat
    )
    palma_davis = _palma_davis_oracle(
        Em,
        Ep,
        Hm,
        Hp,
        float(chi_u[0]),
        float(chi_u[-1]),
        F,
        einstein_metric_hat,
    )

    maximum_selector_fit_error = max(
        error
        for row in selector_fit_errors.values()
        for key, error in row.items()
        if key != "value_abs"
    )
    maximum_silence_residual = max(
        selector_results[label]["invariants_in_Khat_equals_6I_over_F_units"][
            "linear_silence_residual"
        ]
        for label in selector_results
    )
    maximum_curvature = max(
        selector_results[label]["invariants_in_Khat_equals_6I_over_F_units"][
            "covariant_projected_curvature"
        ]
        for label in selector_results
    )
    literal_max_eigenvalue = max(
        palma_davis["literal_endpoint_eigenvalues"]
    )
    literal_min_eigenvalue = min(
        palma_davis["literal_endpoint_eigenvalues"]
    )

    checks = {
        "certified_real_background_used": u.size
        == CRITERIA["background_samples"],
        "two_candidate_BPS_zero_modes_retained": bps["massless_kernel"].get(
            "candidate_bulk_zero_mode_count"
        )
        == 2,
        "stored_zero_mode_Gram_recomputed": _relative(
            recomputed_gram, stored_gram
        )
        < CRITERIA["stored_gram_relative_max"],
        "endpoint_map_is_invertible": abs(float(np.linalg.det(endpoint_map)))
        > CRITERIA["endpoint_map_determinant_abs_min"],
        "closed_endpoint_metric_matches_transformed_Gram": _relative(
            transformed_endpoint_gram, closed_endpoint_gram
        )
        < CRITERIA["endpoint_metric_transform_relative_max"],
        "endpoint_moduli_metric_is_positive": bool(
            np.min(metric_eigenvalues) > CRITERIA["metric_min_eigenvalue"]
        ),
        "real_local_fit_reproduces_selector_jets": (
            maximum_selector_fit_error
            < CRITERIA["local_selector_jet_relative_max"]
        ),
        "real_local_fit_reproduces_metric_derivatives": (
            max(metric_fit_relative, metric_derivative_fit_relative)
            < CRITERIA["local_metric_derivative_relative_max"]
        ),
        "individual_metric_unit_silent_tangents_exist": (
            maximum_silence_residual
            < CRITERIA["silent_tangent_residual_max"]
        ),
        "individual_covariant_projected_curvatures_are_negative": (
            maximum_curvature
            < CRITERIA["projected_covariant_curvature_negative_max"]
        ),
        "no_common_silent_tangent_for_both_matter_metrics": (
            not common["common_nonzero_silent_tangent_exists"]
            and common["covector_gram_determinant"]
            > CRITERIA["common_covector_gram_determinant_min"]
        ),
        "Palma_Davis_Einstein_metric_reconstructed_from_Jordan_plus_Weyl": (
            palma_davis["Weyl_vs_closed_corrected_relative"]
            < CRITERIA["palma_davis_weyl_reconstruction_relative_max"]
        ),
        "corrected_Palma_Davis_metric_matches_local_derivation": (
            palma_davis["corrected_relative_to_expected"]
            < CRITERIA["palma_davis_corrected_relative_max"]
        ),
        "literal_Palma_Davis_equation_28_is_ghost_mutation": bool(
            literal_min_eigenvalue
            < CRITERIA["palma_davis_literal_max_eigenvalue_negative"]
            and literal_max_eigenvalue > 0.0
        ),
        "no_observational_tables_read": True,
    }
    physical_mode_count_resolved_here = bool(
        checks["two_candidate_BPS_zero_modes_retained"]
        and checks["endpoint_map_is_invertible"]
        and checks["endpoint_moduli_metric_is_positive"]
        and checks[
            "Palma_Davis_Einstein_metric_reconstructed_from_Jordan_plus_Weyl"
        ]
        and checks["corrected_Palma_Davis_metric_matches_local_derivation"]
    )
    checks["two_finite_endpoint_physical_moduli_resolved_here"] = (
        physical_mode_count_resolved_here
    )
    checks["all"] = all(checks.values())

    physical_gates = {
        "endpoint_moduli_metric_G_ab_derived": True,
        "Levi_Civita_connection_derived": True,
        "covariant_C_a_and_C_ab_derived": True,
        "algebraic_silent_direction_exists_for_lower_selector": True,
        "algebraic_silent_direction_exists_for_upper_selector": True,
        "negative_selector_curvature_on_each_individual_silent_direction": bool(
            all(
                selector_results[label][
                    "invariants_in_Khat_equals_6I_over_F_units"
                ]["covariant_projected_curvature"]
                < CRITERIA["projected_covariant_curvature_negative_max"]
                for label in selector_results
            )
        ),
        "positive_one_minus_C_quadratic_diagnostic_on_each_direction": bool(
            all(
                selector_results[label][
                    "invariants_in_Khat_equals_6I_over_F_units"
                ]["one_minus_C_quadratic_coefficient"]
                > 0.0
                for label in selector_results
            )
        ),
        "single_direction_is_silent_for_both_endpoint_selectors": False,
        "upstream_finite_endpoint_mode_gate_was_resolved": bps[
            "massless_kernel"
        ].get("finite_endpoint_physical_mode_count_resolved", False),
        "finite_endpoint_physical_mode_count_resolved_here": (
            physical_mode_count_resolved_here
        ),
        "physical_moduli_count": 2 if physical_mode_count_resolved_here else None,
        "unique_tangent_selected_by_BPS_geometry": False,
        "matter_localization_selected_by_bulk": False,
        "matter_Y_convention_fixed": False,
        "constitutive_Y_operator_identification_derived": False,
        "positive_local_diagonal_stabilizer_selects_silent_tangent": False,
        "existing_positive_diagonal_p2_or_p6_completion_selects_silent_tangent": False,
        "absolute_kappa5_ell_canonical_normalization_fixed": False,
        "standard_base_minus_Y_algebraically_separated": True,
        "q2Y_sign_and_normalization_fixed_after_base_subtraction": False,
        "full_lapse_shift_matter_qY_reduction_completed": False,
        "physical_q2Y_selector_derived": False,
    }

    return {
        "schema": "holo.bps-biscalar-matter-geometry.v1",
        "title": "Real-background two-modulus matter-selector geometry",
        "classification": (
            "two_physical_BPS_moduli_resolved;"
            "covariant_biscalar_selector_jets_derived;"
            "silent_tangents_exist_but_are_not_dynamically_selected"
        ),
        "coordinates": {
            "endpoint_moduli": ["u_minus", "u_plus"],
            "selector_expansion": (
                "C_i=1+C_i,a*delta_y^a+0.5*C_i,ab*delta_y^a*delta_y^b"
            ),
            "selector_meaning": (
                "C_i=A_i(reference)^2/A_i(y)^2 is the inverse normalized "
                "matter conformal selector. The auxiliary target uses "
                "s_i=1-C_i, while a canonical minimally coupled brane scalar "
                "has -Y/C_i; after separating its standard -Y term, both have "
                "the same candidate quadratic sign on a silent direction."
            ),
            "physical_metric": (
                "Khat_ab=K_ab/M_Pl^2=6I_ab/F in dimensionless endpoint "
                "coordinates. The absolute canonical scale still requires "
                "kappa5 and the physical length ell."
            ),
        },
        "actual_background": {
            "samples": int(u.size),
            "domain": [float(u[0]), float(u[-1])],
            "F0": F,
            "exp_2A_endpoints": [Em, Ep],
            "A_u_endpoints": [Hm, Hp],
            "A_uu_endpoints_from_flow": [Bm, Bp],
        },
        "zero_mode_to_endpoint_map": {
            "basis": [
                "Psi1=A'*exp(-2A)",
                "Psi2=1-2*A'*exp(-2A)*integral_from_lower(exp(2A)du)",
            ],
            "derivation": (
                "beta=6D(Psi)/chi'^2 and source-free traceless junction "
                "xi_i=-beta_i"
            ),
            "endpoint_map_delta_y_equals_J_times_c": endpoint_map.tolist(),
            "determinant": float(np.linalg.det(endpoint_map)),
            "stored_bulk_Gram_I": stored_gram.tolist(),
            "recomputed_bulk_Gram_I": recomputed_gram.tolist(),
            "recomputed_relative_error": _relative(
                recomputed_gram, stored_gram
            ),
        },
        "moduli_metric": {
            "closed_form_I": (
                "I_--=E_-(E_-+2FH_-)/(4F); "
                "I_-+=-E_-E_+/(4F); "
                "I_++=E_+(E_+-2FH_+)/(4F)"
            ),
            "transformed_stored_endpoint_Gram_I": (
                transformed_endpoint_gram.tolist()
            ),
            "closed_endpoint_Gram_I": closed_endpoint_gram.tolist(),
            "single_interval_Gram_hat_equals_6I": (
                single_interval_metric_hat.tolist()
            ),
            "Planck_normalized_action_derivation": {
                "absolute_kinetic_metric": (
                    "K_abs=[2/(k*F*kappa5^2)]*(6I)"
                ),
                "four_dimensional_Planck_mass": "M_Pl^2=2/(k*kappa5^2)",
                "ratio": "K_abs/M_Pl^2=Khat=6I/F",
                "endpoint_derivative_of_F": [-Em, Ep],
            },
            "Einstein_frame_relation": "Khat_ab=6I_ab/F",
            "Khat_equals_6I_over_F": einstein_metric_hat.tolist(),
            "Khat_eigenvalues": metric_eigenvalues.tolist(),
            "partial_c_Khat_ab": einstein_metric_derivative_hat.tolist(),
            "Christoffel_Gamma_c_ab": connection.tolist(),
            "transformed_vs_closed_relative": _relative(
                transformed_endpoint_gram, closed_endpoint_gram
            ),
            "real_local_fit_value_relative": metric_fit_relative,
            "real_local_fit_derivative_relative": (
                metric_derivative_fit_relative
            ),
        },
        "selectors": selector_results,
        "joint_selector_gate": common,
        "palma_davis_independent_oracle": palma_davis,
        "physical_compatibility": {
            "individual_result": (
                "For either endpoint inverse normalized matter conformal "
                "selector, the two-dimensional moduli space contains a Khat-unit "
                "direction with zero linear derivative and negative covariant "
                "selector curvature; therefore 1-C has positive quadratic curvature."
            ),
            "universal_result": (
                "The two selector covectors are independent, so no nonzero "
                "direction removes the linear coupling for matter on both branes."
            ),
            "selection_obstruction": (
                "The two physical BPS moduli are resolved, but their geometry "
                "does not select one tangent as q. Minimal positive diagonal "
                "localized p=2 or p=6 completions do not select either silent "
                "direction, and choosing one after seeing q2Y would be inverse design."
            ),
            "verdict": (
                "A covariant stationary direction with a nonzero even selector "
                "jet exists for each matter-brane choice. This does not yet "
                "derive a physical q2Y vertex. The auxiliary s=1-C target and "
                "the extra term in minimal brane-scalar -Y/C have the same "
                "candidate negative qbar^2*Y sign after separating standard -Y, "
                "but the constitutive Y operator, tangent and absolute "
                "normalization are not derived."
            ),
        },
        "physical_gates": physical_gates,
        "checks": checks,
        "criteria": CRITERIA,
        "inputs": {
            "observational_tables_read": [],
            "files": {
                "effective_action": {
                    "path": str(EFFECTIVE_ACTION.relative_to(REPO)),
                    "sha256": _sha256(EFFECTIVE_ACTION),
                },
                "BPS_certificate": {
                    "path": str(BPS_CERTIFICATE.relative_to(REPO)),
                    "sha256": _sha256(BPS_CERTIFICATE),
                },
            },
        },
        "next_decisive_test": (
            "Derive a microscopic stabilization or symmetry before looking at "
            "the target that selects one of the Khat-unit silent tangents, "
            "then perform the full lapse/shift/bending matter reduction and "
            "identify the constitutive Y with a physical matter operator and "
            "verify the q2Y sign and normalization in that same tangent."
        ),
        "evidence_boundary": (
            "This is a two-derivative moduli-space result on the real 1,979-point "
            "Einstein--dilaton background. It derives covariant selector jets and "
            "candidate silent directions, not a dynamically selected collective "
            "field, a full mixed ADM vertex, or an observed force."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    result = build()
    if not result["checks"]["all"]:
        failed = [key for key, value in result["checks"].items() if not value]
        raise SystemExit(f"BPS biscalar matter geometry failed: {failed}")
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    for label in ("lower", "upper"):
        invariant = result["selectors"][label][
            "invariants_in_Khat_equals_6I_over_F_units"
        ]
        print(
            "[{} selector] |grad C|^2={:.9g} silent curvature={:.9g}".format(
                label,
                invariant["gradient_norm_squared"],
                invariant["covariant_projected_curvature"],
            )
        )
    print("[common silent direction] False")
    print("[physical q2Y selector derived] False")
    print("[certificate] PASS")


if __name__ == "__main__":
    main()
