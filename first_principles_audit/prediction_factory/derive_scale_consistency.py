#!/usr/bin/env python3
"""Test whether one compactification length can serve QCD and SPARC.

The stiff scalar masses obey ``m_n c^2 = hbar*c*mu_n/ell``.  This certificate
compares two conditional readings already present in the repository:

* identifying the first stiff mode with the legacy 1.600 GeV scalar proxy;
* placing ``ell`` at the upper boundary selected by the SPARC finite-disk scan.

Neither input is promoted to a measured scale.  Their conditional mismatch is
nevertheless an exact consistency test: a single ``ell`` cannot realize both
readings.  A future model must derive a UV matching relation, separate the QCD
and galactic sectors, or abandon one identification.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STIFF_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/stiff_boundary_force.json"
)
DISK_RELATIVE = Path(
    "first_principles_audit/prediction_factory/artifacts/sparc_finite_disk_yukawa.json"
)
RICCI_RELATIVE = Path(
    "first_principles_audit/artifacts/ricci_wilson_interface_audit.json"
)
OUTPUT = HERE / "artifacts" / "scale_consistency.json"

HBAR_C_EV_M = 1.9732698045930251e-7
SPEED_OF_LIGHT_M_S = 299_792_458.0
KPC_M = 3.085677581491367e19
SECONDS_PER_JULIAN_YEAR = 31_557_600.0


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def physical_mode_from_ell(mu: float, ell_m: float) -> dict[str, float]:
    if not (
        math.isfinite(mu)
        and mu > 0.0
        and math.isfinite(ell_m)
        and ell_m > 0.0
    ):
        raise ValueError("mu and ell must be positive and finite")
    energy_ev = HBAR_C_EV_M * mu / ell_m
    angular_frequency = SPEED_OF_LIGHT_M_S * mu / ell_m
    frequency_hz = angular_frequency / (2.0 * math.pi)
    return {
        "ell_m": ell_m,
        "interaction_range_m": ell_m / mu,
        "rest_energy_ev": energy_ev,
        "angular_frequency_rad_s": angular_frequency,
        "cyclic_frequency_hz": frequency_hz,
        "period_s": 1.0 / frequency_hz,
        "period_julian_year": 1.0
        / (frequency_hz * SECONDS_PER_JULIAN_YEAR),
    }


def ell_from_mode_energy(mu: float, energy_ev: float) -> float:
    if not (
        math.isfinite(mu)
        and mu > 0.0
        and math.isfinite(energy_ev)
        and energy_ev > 0.0
    ):
        raise ValueError("mu and energy must be positive and finite")
    return HBAR_C_EV_M * mu / energy_ev


def build() -> dict[str, Any]:
    stiff_path = REPO / STIFF_RELATIVE
    disk_path = REPO / DISK_RELATIVE
    ricci_path = REPO / RICCI_RELATIVE
    stiff = _read(stiff_path)
    disk = _read(disk_path)
    ricci = _read(ricci_path)
    if not (
        stiff.get("passes", {}).get("all") is True
        and disk.get("passes", {}).get("all") is True
        and ricci.get("passes", {}).get("all") is True
    ):
        raise RuntimeError("one or more scale inputs are not certified")

    mu0 = float(stiff["spectrum_and_force"]["masses_mu"][0])
    qcd_proxy_gev = float(
        ricci["wilson_scale"]["legacy_arithmetic"]["m0_recomputed_GeV"]
    )
    qcd_ell_m = ell_from_mode_energy(mu0, qcd_proxy_gev * 1.0e9)
    qcd_reading = physical_mode_from_ell(mu0, qcd_ell_m)
    galaxy_ell_kpc = float(disk["baseline_scan"]["best_ell_kpc"])
    galaxy_reading = physical_mode_from_ell(
        mu0, galaxy_ell_kpc * KPC_M
    )
    mismatch = galaxy_reading["ell_m"] / qcd_reading["ell_m"]

    passes = {
        "inputs_certified": True,
        "stiff_force_is_observation_free": stiff["observational_inputs_read"] == [],
        "sparc_scale_is_declared_boundary_not_measurement": (
            disk["baseline_scan"]["best_at_upper_boundary"]
            and not disk["adjudication"]["finite_scale_identified"]
        ),
        "qcd_scale_is_declared_external_proxy": (
            "external alpha_prime"
            in ricci["wilson_scale"]["legacy_causal_direction"]
        ),
        "single_scale_mismatch_exceeds_30_orders": mismatch > 1.0e30,
        "galaxy_reading_is_ultralight": galaxy_reading["rest_energy_ev"] < 1.0e-20,
        "qcd_reading_is_subatomic": qcd_reading["interaction_range_m"] < 1.0e-12,
    }
    passes["all"] = all(passes.values())

    return {
        "schema": "holo.scale-consistency.v1",
        "title": "Conditional one-scale QCD--galaxy consistency test",
        "classification": "conditional_scale_no_go_not_measurement",
        "inputs": {
            "stiff_force": {
                "path": STIFF_RELATIVE.as_posix(),
                "sha256": _sha256(stiff_path),
                "mu0": mu0,
            },
            "sparc_finite_disk": {
                "path": DISK_RELATIVE.as_posix(),
                "sha256": _sha256(disk_path),
                "best_grid_ell_kpc": galaxy_ell_kpc,
                "best_at_upper_boundary": True,
                "finite_scale_identified": False,
            },
            "legacy_qcd_proxy": {
                "path": RICCI_RELATIVE.as_posix(),
                "sha256": _sha256(ricci_path),
                "scalar_mass_proxy_gev": qcd_proxy_gev,
                "status": "external endpoint conversion, not a Wilson measurement",
            },
        },
        "scale_law": {
            "rest_energy": "m_n c^2=hbar*c*mu_n/ell",
            "cyclic_frequency": "f_n=c*mu_n/(2*pi*ell)",
            "interaction_range": "lambda_n=ell/mu_n",
        },
        "conditional_qcd_identification": qcd_reading,
        "conditional_galaxy_boundary_reading": {
            **galaxy_reading,
            "ell_kpc": galaxy_ell_kpc,
            "interaction_range_kpc": galaxy_reading["interaction_range_m"]
            / KPC_M,
            "status": (
                "saturated long-range scan boundary, not a measured best-fit scale"
            ),
        },
        "comparison": {
            "ell_galaxy_over_ell_qcd": mismatch,
            "orders_of_magnitude_in_ell": math.log10(mismatch),
            "single_ell_can_realize_both_identifications": False,
        },
        "adjudication": {
            "result": (
                "If the same ell sets both the 1.600 GeV proxy and the stiff "
                "galaxy force, the two conditional readings are incompatible by "
                "more than forty orders of magnitude."
            ),
            "allowed_resolutions": [
                "derive a UV relation that assigns different effective scales to the sectors",
                "introduce a genuinely separate ultralight galactic sector",
                "abandon the QCD identification of the stiff carrier",
                "abandon the galactic-force interpretation",
            ],
            "not_allowed": (
                "use the QCD proxy to claim a galactic range or use the SPARC "
                "boundary to claim a QCD mass without a new matching relation"
            ),
            "next_independent_input": (
                "a scale-setting observable predicted and measured without using "
                "the SPARC residual or the legacy endpoint conversion"
            ),
        },
        "passes": passes,
        "evidence_boundary": (
            "This is a conditional incompatibility proof, not a measurement of ell. "
            "The QCD number is an external legacy proxy and the SPARC value is a "
            "saturated grid boundary; neither is promoted to a detection."
        ),
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    comparison = result["comparison"]
    galaxy = result["conditional_galaxy_boundary_reading"]
    print(f"[scale consistency] {OUTPUT}")
    print(
        "[single-scale mismatch] {:.6g} ({:.3f} orders)".format(
            comparison["ell_galaxy_over_ell_qcd"],
            comparison["orders_of_magnitude_in_ell"],
        )
    )
    print(
        "[galaxy-boundary clock] f0={:.6g} Hz, T0={:.6g} yr".format(
            galaxy["cyclic_frequency_hz"], galaxy["period_julian_year"]
        )
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
