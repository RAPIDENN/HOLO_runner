#!/usr/bin/env python3
"""Lightweight axisymmetric controls for the nonlinear collector equation.

The nonlinear action target obeys

    div[mu(|grad Phi|/a0) grad Phi] = 4*pi*G*rho_b.

This module does three deliberately separate things:

1. evaluate that operator with a finite-volume cylindrical stencil on an
   analytic spherical Plummer control embedded in (R,z);
2. show that the tempting algebraic field ``g=nu(g_N/a0) g_N`` is curl-free
   for the spherical control but not for a flattened Miyamoto--Nagai source;
3. audit the local SPARC tables and fail closed because their mid-plane force
   contributions do not identify a unique rho_b(R,z), disk thickness, or
   vertical/outer boundary condition for the nonlinear PDE.

The final SPARC score is retained only as an *effective mid-plane algebraic
closure*.  Vobs is passed to a separate scoring function after prediction and
is never an input to the collector operator.  There are no per-galaxy fits.
All numerical grids are two-dimensional and smaller than 2e4 cells for the
finite-volume control (the curl diagnostic uses about 2.6e4 points).
"""

from __future__ import annotations

import csv
import hashlib
import inspect
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
COLLECTOR_PATH = HERE / "artifacts" / "universal_residual_collector.json"
SPLIT_PATH = HERE / "sparc_split_v1.json"
SPARC_DIR = (
    HERE.parents[2]
    / "HOLO_TRANSDUCTOR_V2"
    / "data"
    / "external"
    / "SPARC"
    / "sparc_175"
)
OUTPUT = HERE / "artifacts" / "derive_axisymmetric_collector_certificate.json"

KPC_METRES = 3.085677581491367e19
DISK_MASS_TO_LIGHT = 0.5
BULGE_MASS_TO_LIGHT = 0.7


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collector_nu(y: np.ndarray | float) -> np.ndarray:
    """Return nu(y)=[1-exp(-sqrt(y))]^-1 for strictly positive y."""

    values = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("y must be finite and strictly positive")
    return 1.0 / (-np.expm1(-np.sqrt(values)))


def collector_mu(x: np.ndarray | float) -> np.ndarray:
    """Invert x=t^2/(1-exp(-t)) and return mu(x)=1-exp(-t).

    The constitutive map is monotone.  A vectorised Newton solve avoids a
    dense lookup table and reaches double-precision closure in a fixed number
    of iterations.  The continuous deep-limit value mu(0)=0 is included.
    """

    values = np.asarray(x, dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("x must be finite and non-negative")
    result = np.zeros_like(values)
    positive = values > 0.0
    xp = values[positive]
    if xp.size:
        t = np.where(xp < 1.0, xp, np.sqrt(xp))
        for _ in range(24):
            denominator = -np.expm1(-t)
            exponential = np.exp(-t)
            residual = np.square(t) / denominator - xp
            derivative = (
                2.0 * t / denominator
                - np.square(t) * exponential / np.square(denominator)
            )
            t = np.maximum(t - residual / derivative, np.finfo(float).tiny)
        result[positive] = -np.expm1(-t)
    return result


def algebraic_collector_field(
    g_r_newton: np.ndarray,
    g_z_newton: np.ndarray,
    a0: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the algebraic collector field without any observational input."""

    if not math.isfinite(a0) or a0 <= 0.0:
        raise ValueError("a0 must be finite and positive")
    g_r = np.asarray(g_r_newton, dtype=float)
    g_z = np.asarray(g_z_newton, dtype=float)
    if g_r.shape != g_z.shape:
        raise ValueError("Newtonian field components must have equal shapes")
    if np.any(~np.isfinite(g_r)) or np.any(~np.isfinite(g_z)):
        raise ValueError("Newtonian field components must be finite")
    magnitude = np.hypot(g_r, g_z)
    boost = np.ones_like(magnitude)
    positive = magnitude > 0.0
    boost[positive] = collector_nu(magnitude[positive] / a0)
    return boost * g_r, boost * g_z


def constitutive_flux(
    g_r: np.ndarray, g_z: np.ndarray, a0: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return mu(|g|/a0) g, the flux entering the AQUAL operator."""

    magnitude = np.hypot(g_r, g_z)
    mu = collector_mu(magnitude / a0)
    return mu * g_r, mu * g_z


def _plummer_newtonian_field(
    radius: np.ndarray, height: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    denominator = np.power(np.square(radius) + np.square(height) + 1.0, 1.5)
    return radius / denominator, height / denominator


def _plummer_source(radius: np.ndarray, height: np.ndarray) -> np.ndarray:
    # Dimensionless G=M=b=1, so the PDE source is 4*pi*rho.
    return 3.0 * np.power(
        np.square(radius) + np.square(height) + 1.0, -2.5
    )


def spherical_finite_volume_control(radial_cells: int) -> dict[str, float | int]:
    """Evaluate the cylindrical nonlinear PDE on a Plummer control.

    Face-centred constitutive fluxes are differenced with the conservative
    axisymmetric formula.  The source is sampled at cell centres.  Refining
    the grid therefore provides an independent convergence check rather than
    an identity evaluated at the same points.
    """

    if radial_cells < 16:
        raise ValueError("the control needs at least 16 radial cells")
    vertical_cells = 2 * radial_cells
    r_edge = np.linspace(0.0, 8.0, radial_cells + 1)
    z_edge = np.linspace(-8.0, 8.0, vertical_cells + 1)
    r_center = 0.5 * (r_edge[:-1] + r_edge[1:])
    z_center = 0.5 * (z_edge[:-1] + z_edge[1:])
    a0 = 0.1

    r_face, z_on_r_face = np.meshgrid(r_edge, z_center, indexing="ij")
    gnr, gnz = _plummer_newtonian_field(r_face, z_on_r_face)
    gr, gz = algebraic_collector_field(gnr, gnz, a0)
    flux_r, _ = constitutive_flux(gr, gz, a0)

    r_on_z_face, z_face = np.meshgrid(r_center, z_edge, indexing="ij")
    gnr, gnz = _plummer_newtonian_field(r_on_z_face, z_face)
    gr, gz = algebraic_collector_field(gnr, gnz, a0)
    _, flux_z = constitutive_flux(gr, gz, a0)

    radial_divergence = 2.0 * (
        r_edge[1:, None] * flux_r[1:, :]
        - r_edge[:-1, None] * flux_r[:-1, :]
    ) / (np.square(r_edge[1:, None]) - np.square(r_edge[:-1, None]))
    vertical_divergence = (flux_z[:, 1:] - flux_z[:, :-1]) / np.diff(
        z_edge
    )[None, :]
    divergence = radial_divergence + vertical_divergence

    radius, height = np.meshgrid(r_center, z_center, indexing="ij")
    source = _plummer_source(radius, height)
    weights = radius * np.diff(r_edge)[:, None] * np.diff(z_edge)[None, :]
    relative_l2 = math.sqrt(
        float(np.sum(weights * np.square(divergence - source)))
        / float(np.sum(weights * np.square(source)))
    )
    maximum_relative_to_source_peak = float(
        np.max(np.abs(divergence - source)) / np.max(source)
    )
    return {
        "radial_cells": radial_cells,
        "vertical_cells": vertical_cells,
        "total_cells": radial_cells * vertical_cells,
        "weighted_relative_l2_residual": relative_l2,
        "maximum_error_over_source_peak": maximum_relative_to_source_peak,
    }


def razor_thin_sheet_control() -> dict[str, float]:
    """Check the local jump condition mu(g/a0)g=2*pi*G*Sigma."""

    y = np.geomspace(1.0e-10, 1.0e10, 4096)
    g_newton = y  # units a0=1; g_N=2*pi*G*Sigma
    g = collector_nu(y) * g_newton
    recovered = collector_mu(g) * g
    return {
        "sampled_y_min": float(y[0]),
        "sampled_y_max": float(y[-1]),
        "maximum_relative_jump_error": float(
            np.max(np.abs(recovered - g_newton) / g_newton)
        ),
    }


def _nu_derivative(y: np.ndarray) -> np.ndarray:
    t = np.sqrt(y)
    denominator = -np.expm1(-t)
    return -np.exp(-t) / (2.0 * t * np.square(denominator))


def miyamoto_nagai_curl_obstruction(
    flattening_a: float, radial_points: int = 160
) -> dict[str, float | int]:
    """Measure curl[nu(|g_N|/a0) g_N] for an analytic axisymmetric source.

    ``flattening_a=0`` is the spherical Plummer control.  A positive ``a`` is
    a flattened Miyamoto--Nagai density.  Derivatives of |g_N| are analytic,
    so the non-zero curl is physical rather than a finite-difference artefact.
    """

    if flattening_a < 0.0 or not math.isfinite(flattening_a):
        raise ValueError("flattening_a must be finite and non-negative")
    if radial_points < 32:
        raise ValueError("curl control needs at least 32 radial points")
    r = np.linspace(0.1, 10.0, radial_points)
    z = np.linspace(-5.0, 5.0, radial_points + 1)
    radius, height = np.meshgrid(r, z, indexing="ij")
    b = 0.5
    a0 = 0.03
    d = np.sqrt(np.square(height) + b * b)
    big_b = flattening_a + d
    u = np.square(radius) + np.square(big_b)
    q = big_b * height / d
    h2 = np.square(radius) + np.square(q)
    inverse_u_3_2 = np.power(u, -1.5)
    gnr = radius * inverse_u_3_2
    gnz = q * inverse_u_3_2
    magnitude = np.sqrt(h2) * inverse_u_3_2

    q_z = np.square(height) / np.square(d) + big_b * b * b / np.power(d, 3)
    magnitude_r = magnitude * (radius / h2 - 3.0 * radius / u)
    magnitude_z = magnitude * (
        q * q_z / h2 - 3.0 * big_b * height / (d * u)
    )
    y = magnitude / a0
    curl_phi = (_nu_derivative(y) / a0) * (
        magnitude_z * gnr - magnitude_r * gnz
    )
    collector_magnitude = collector_nu(y) * magnitude
    weights = radius
    normalized_rms = math.sqrt(
        float(np.sum(weights * np.square(curl_phi)))
        / float(np.sum(weights * np.square(collector_magnitude / b)))
    )
    return {
        "flattening_a_over_b": flattening_a / b,
        "radial_points": radial_points,
        "vertical_points": radial_points + 1,
        "grid_points": radial_points * (radial_points + 1),
        "normalized_weighted_rms_curl": normalized_rms,
        "maximum_absolute_curl_dimensionless": float(np.max(np.abs(curl_phi))),
    }


def audit_sparc_source_contract(data_dir: Path = SPARC_DIR) -> dict[str, Any]:
    files = sorted(data_dir.glob("*_rotmod.csv"))
    if not files:
        raise FileNotFoundError(f"no SPARC tables under {data_dir}")
    header_sets: set[tuple[str, ...]] = set()
    for path in files:
        with path.open("r", encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle), None)
        if not header:
            raise ValueError(f"empty SPARC table: {path}")
        header_sets.add(tuple(header))
    headers = sorted({field for header in header_sets for field in header})
    scoring_only = [field for field in ("Vobs_kms", "eVobs_kms") if field in headers]
    required_missing = [
        "Sigma_gas(R)",
        "rho_stars(R,z) or component scale heights",
        "rho_gas(R,z) or gas scale height",
        "vertical and outer boundary conditions",
    ]
    return {
        "tables": len(files),
        "uniform_header": len(header_sets) == 1,
        "available_columns": headers,
        "scoring_only_columns": scoring_only,
        "available_source_proxies": [
            field
            for field in (
                "R_kpc",
                "Vgas_kms",
                "Vdisk_kms",
                "Vbul_kms",
                "Vbar_kms",
                "SBdisk",
                "SBbul",
            )
            if field in headers
        ],
        "required_but_not_identified": required_missing,
        "physical_axisymmetric_pde_identifiable": False,
        "status": "FAIL_CLOSED_MISSING_UNIQUE_3D_BARYON_SOURCE",
        "reason": (
            "Mid-plane component rotation curves and stellar surface brightness "
            "do not uniquely determine rho_b(R,z), the gas surface-density "
            "profile, component thicknesses, or PDE boundary conditions. Many "
            "3D sources share the same sampled mid-plane radial force."
        ),
    }


def predict_effective_midplane(
    radius_kpc: float,
    v_gas_kms: float,
    v_disk_kms: float,
    v_bulge_kms: float,
    a0_m_s2: float,
) -> float:
    """Predict velocity from source proxies only; this is not the 2D PDE."""

    values = (radius_kpc, v_gas_kms, v_disk_kms, v_bulge_kms, a0_m_s2)
    if any(not math.isfinite(value) for value in values):
        raise ValueError("mid-plane inputs must be finite")
    if radius_kpc <= 0.0 or a0_m_s2 <= 0.0:
        raise ValueError("radius and a0 must be positive")
    vbar_squared_kms2 = (
        v_gas_kms * abs(v_gas_kms)
        + DISK_MASS_TO_LIGHT * v_disk_kms**2
        + BULGE_MASS_TO_LIGHT * v_bulge_kms**2
    )
    if vbar_squared_kms2 <= 0.0:
        return 0.0
    radius_metres = radius_kpc * KPC_METRES
    gbar = vbar_squared_kms2 * 1.0e6 / radius_metres
    g_collector = float(collector_nu(gbar / a0_m_s2)) * gbar
    return math.sqrt(g_collector * radius_metres) / 1000.0


def score_prediction(
    prediction_kms: float, observed_kms: float, uncertainty_kms: float
) -> tuple[float, float]:
    """Use observations only after a prediction has been produced."""

    if uncertainty_kms <= 0.0:
        raise ValueError("observational uncertainty must be positive")
    chi2 = ((prediction_kms - observed_kms) / uncertainty_kms) ** 2
    fractional = abs(prediction_kms - observed_kms) / observed_kms
    return chi2, fractional


def score_frozen_test_midplane_closure(a0_m_s2: float) -> dict[str, Any]:
    split = _read_json(SPLIT_PATH)["groups"]
    test_names: Sequence[str] = split["test"]
    chi2 = 0.0
    fractional_errors: list[float] = []
    points = 0
    for name in test_names:
        path = SPARC_DIR / f"{name}_rotmod.csv"
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                prediction = predict_effective_midplane(
                    float(row["R_kpc"]),
                    float(row["Vgas_kms"]),
                    float(row["Vdisk_kms"]),
                    float(row["Vbul_kms"]),
                    a0_m_s2,
                )
                # Vobs and eVobs cross the boundary only here, after prediction.
                point_chi2, fractional = score_prediction(
                    prediction,
                    float(row["Vobs_kms"]),
                    float(row["eVobs_kms"]),
                )
                chi2 += point_chi2
                fractional_errors.append(fractional)
                points += 1
    return {
        "galaxies": len(test_names),
        "velocity_points": points,
        "chi2_per_point": chi2 / points,
        "median_absolute_fractional_velocity_error": float(
            np.median(fractional_errors)
        ),
        "classification": (
            "effective_midplane_algebraic_closure_not_axisymmetric_pde_solution"
        ),
    }


def build() -> dict[str, Any]:
    collector = _read_json(COLLECTOR_PATH)
    if collector.get("passes", {}).get("all") is not True:
        raise RuntimeError("frozen collector certificate must pass")
    a0 = float(collector["train_fit"]["g_dagger_m_s2"])

    source_audit = audit_sparc_source_contract()
    coarse = spherical_finite_volume_control(48)
    fine = spherical_finite_volume_control(96)
    convergence = (
        coarse["weighted_relative_l2_residual"]
        / fine["weighted_relative_l2_residual"]
    )
    sheet = razor_thin_sheet_control()
    spherical_curl = miyamoto_nagai_curl_obstruction(0.0)
    flattened_curl = miyamoto_nagai_curl_obstruction(3.0)
    curl_ratio = (
        flattened_curl["normalized_weighted_rms_curl"]
        / max(spherical_curl["normalized_weighted_rms_curl"], 1.0e-300)
    )
    score = score_frozen_test_midplane_closure(a0)

    operator_parameters = list(inspect.signature(predict_effective_midplane).parameters)
    scoring_names_absent = not any(
        token in name.lower()
        for name in operator_parameters
        for token in ("vobs", "observed", "uncertainty", "sigma")
    )
    largest_grid_points = max(
        int(fine["total_cells"]), int(flattened_curl["grid_points"])
    )
    # Conservative accounting for 32 simultaneous float64 arrays, well above
    # the live count in either control routine.
    conservative_bytes = largest_grid_points * 32 * 8

    passes = {
        "frozen_global_acceleration_scale_loaded_without_refit": a0 > 0.0,
        "no_per_galaxy_parameters": collector["train_fit"]["per_galaxy_parameters"]
        == 0,
        "vobs_absent_from_operator_signature": scoring_names_absent,
        "sparc_source_contract_fails_closed": not source_audit[
            "physical_axisymmetric_pde_identifiable"
        ],
        "spherical_axisymmetric_operator_converges": (
            fine["weighted_relative_l2_residual"] < 3.0e-3
            and convergence > 3.5
        ),
        "razor_thin_jump_condition_closes": sheet[
            "maximum_relative_jump_error"
        ]
        < 2.0e-14,
        "spherical_algebraic_field_is_curl_free": spherical_curl[
            "normalized_weighted_rms_curl"
        ]
        < 1.0e-14,
        "flattened_algebraic_field_has_curl_obstruction": (
            flattened_curl["normalized_weighted_rms_curl"] > 1.0e-3
            and curl_ratio > 1.0e12
        ),
        "memory_budget_below_16_mib": conservative_bytes < 16 * 1024**2,
        "frozen_test_scoring_is_finite": math.isfinite(score["chi2_per_point"]),
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.axisymmetric-collector-prototype.v1",
        "title": "Axisymmetric nonlinear collector controls and SPARC source gate",
        "classification": (
            "analytic_controls_plus_fail_closed_source_audit_not_holo_derivation"
        ),
        "claim_boundary": (
            "The nonlinear constitutive law passes spherical and razor-thin "
            "analytic controls in cylindrical coordinates. The local algebraic "
            "collector is not a valid flattened-disk field because it develops "
            "curl. Public local SPARC tables do not identify the unique 3D source "
            "and boundary data needed to solve the nonlinear axisymmetric PDE; "
            "therefore no physical SPARC PDE solution or HOLO-force confirmation "
            "is claimed."
        ),
        "equation": {
            "axisymmetric_form": (
                "(1/R)d_R[R mu(|grad Phi|/a0) d_R Phi] + "
                "d_z[mu(|grad Phi|/a0) d_z Phi] = 4*pi*G*rho_b(R,z)"
            ),
            "constitutive_parametric_form": (
                "t=sqrt(gN/a0), mu=1-exp(-t), "
                "|grad Phi|/a0=t^2/[1-exp(-t)]"
            ),
        },
        "frozen_input": {
            "collector_path": str(COLLECTOR_PATH.relative_to(HERE.parents[1])),
            "collector_sha256": _sha256(COLLECTOR_PATH),
            "a0_m_s2": a0,
            "fit_origin": "existing frozen SPARC training split",
            "refit_performed_here": False,
            "per_galaxy_parameters": 0,
        },
        "sparc_source_identifiability": source_audit,
        "analytic_and_numerical_controls": {
            "spherical_plummer_cylindrical_finite_volume": {
                "coarse": coarse,
                "fine": fine,
                "coarse_to_fine_l2_ratio": convergence,
            },
            "razor_thin_sheet_jump": sheet,
            "algebraic_field_integrability": {
                "spherical_plummer": spherical_curl,
                "flattened_miyamoto_nagai": flattened_curl,
                "flattened_to_spherical_rms_curl_ratio": curl_ratio,
                "meaning": (
                    "A non-zero curl means nu(|gN|/a0)gN cannot be grad Phi. "
                    "The flattened problem requires a genuine nonlinear PDE solve."
                ),
            },
        },
        "effective_midplane_diagnostic": {
            "operator_parameters": operator_parameters,
            "observational_parameters": list(
                inspect.signature(score_prediction).parameters
            ),
            "frozen_test_score": score,
            "warning": (
                "This score reproduces only the train-frozen algebraic mid-plane "
                "closure. It is not promoted to an axisymmetric PDE prediction."
            ),
        },
        "resource_bound": {
            "largest_grid_points": largest_grid_points,
            "conservative_simultaneous_float64_arrays": 32,
            "conservative_peak_array_bytes": conservative_bytes,
            "conservative_peak_array_mib": conservative_bytes / 1024**2,
            "three_dimensional_mesh_allocated": False,
        },
        "next_required_inputs": [
            "gas surface-density profiles with sign-safe provenance",
            "stellar and gas vertical scale-height prescriptions",
            "mass-to-light assumptions frozen before scoring",
            "outer and vertical boundary conditions",
            "an independent galaxy holdout after the PDE pipeline is frozen",
        ],
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "passes": passes,
    }


def main() -> None:
    result = build()
    _write_json(OUTPUT, result)
    control = result["analytic_and_numerical_controls"]
    score = result["effective_midplane_diagnostic"]["frozen_test_score"]
    print(f"[artifact] {OUTPUT}")
    print(
        "[axisymmetric finite-volume residual] "
        f"{control['spherical_plummer_cylindrical_finite_volume']['fine']['weighted_relative_l2_residual']:.6g}"
    )
    print(
        "[flattened curl obstruction] "
        f"{control['algebraic_field_integrability']['flattened_miyamoto_nagai']['normalized_weighted_rms_curl']:.6g}"
    )
    print(f"[effective test chi2/point] {score['chi2_per_point']:.9g}")
    print(
        "[physical SPARC PDE] "
        f"{result['sparc_source_identifiability']['status']}"
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    if not result["passes"]["all"]:
        raise SystemExit("axisymmetric collector prototype certificate failed")


if __name__ == "__main__":
    main()
