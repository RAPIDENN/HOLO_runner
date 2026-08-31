#!/usr/bin/env python3
"""Adjudicate C2 for the frozen compact spectrum, and only that spectrum.

The input is the existing ``holo.collective-spectral-bridge.v1`` certificate.
It records a finite seven-pole compact spectrum, a 0.210 dex crossing near
logarithmic slope 3/2, and no reduction of momentum spectral exchange to a
local nonlinear amplitude operator.  Those three facts kill C2 for the
frozen model.

This is deliberately not a no-go theorem for every critical continuum.  A
decompactified gapless spectrum, a critical boundary limit, or a genuinely
non-Gaussian collective constraint is outside the adjudicated model.  The
builder reads no observational input and fails closed if its sole source is
uncertified or malformed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPECTRAL_CERTIFICATE = HERE / "artifacts" / "collective_spectral_bridge.json"
OUTPUT = HERE / "artifacts" / "c2_critical_continuum_gate.json"

SOURCE_SCHEMA = "holo.collective-spectral-bridge.v1"
OUTPUT_SCHEMA = "holo.c2-critical-continuum-gate.v1"
FROZEN_MODEL_STATEMENT = (
    "seven fixed gapped poles; linear superposition; source exponent one"
)
MIMIC_WIDTH_LIMIT_DEX = 0.25
FROZEN_POLE_COUNT = 7


class SpectralCertificateError(ValueError):
    """The spectral certificate cannot support a fail-closed adjudication."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpectralCertificateError(
            f"cannot read spectral certificate: {exc}"
        ) from exc
    if type(value) is not dict:
        raise SpectralCertificateError("spectral certificate must be an object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise SpectralCertificateError(f"{path} must be an object")
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        raise SpectralCertificateError(f"{path} must be boolean")
    return value


def _finite_number(value: Any, path: str) -> float:
    if type(value) not in {int, float} or not math.isfinite(float(value)):
        raise SpectralCertificateError(f"{path} must be finite numeric")
    return float(value)


def _nonempty_string(value: Any, path: str) -> str:
    if type(value) is not str or not value.strip():
        raise SpectralCertificateError(f"{path} must be a non-empty string")
    return value


def _validated_view(certificate: Mapping[str, Any]) -> dict[str, Any]:
    root = _mapping(certificate, "certificate")
    if root.get("schema") != SOURCE_SCHEMA:
        raise SpectralCertificateError(f"certificate.schema must be {SOURCE_SCHEMA!r}")

    checks = _mapping(root.get("checks"), "certificate.checks")
    if (
        _boolean(checks.get("certified_inputs"), "certificate.checks.certified_inputs")
        is not True
    ):
        raise SpectralCertificateError("spectral inputs are not certified")
    if _boolean(checks.get("all"), "certificate.checks.all") is not True:
        raise SpectralCertificateError("spectral certificate checks do not pass")
    narrow_check = _boolean(
        checks.get("finite_tower_three_halves_is_only_a_narrow_crossover"),
        "certificate.checks.finite_tower_three_halves_is_only_a_narrow_crossover",
    )

    sources = _mapping(root.get("sources"), "certificate.sources")
    observational = sources.get("observational_inputs_read")
    if type(observational) is not list or observational:
        raise SpectralCertificateError(
            "certificate.sources.observational_inputs_read must be an empty array"
        )

    current = _mapping(
        root.get("current_seven_mode_test"),
        "certificate.current_seven_mode_test",
    )
    width = _finite_number(
        current.get("within_0p05_log10_width_dex"),
        "certificate.current_seven_mode_test.within_0p05_log10_width_dex",
    )
    if width <= 0.0:
        raise SpectralCertificateError("crossover width must be positive")
    densities = current.get("inferred_weight_over_mass_spacing")
    if type(densities) is not list or not densities:
        raise SpectralCertificateError("frozen pole-density list must be non-empty")
    for index, density in enumerate(densities):
        if _finite_number(density, f"pole_density[{index}]") <= 0.0:
            raise SpectralCertificateError("frozen pole densities must be positive")

    physical = _mapping(root.get("physical_gates"), "certificate.physical_gates")
    gapless_present = _boolean(
        physical.get("gapless_continuum_present_in_current_compact_spectrum"),
        "certificate.physical_gates.gapless_continuum_present_in_current_compact_spectrum",
    )
    constant_density_derived = _boolean(
        physical.get("constant_positive_density_per_mass_derived"),
        "certificate.physical_gates.constant_positive_density_per_mass_derived",
    )
    local_reduction = _boolean(
        physical.get("momentum_spectral_continuum_reduced_to_local_amplitude_operator"),
        "certificate.physical_gates.momentum_spectral_continuum_reduced_to_local_amplitude_operator",
    )

    comparison = _mapping(root.get("old_vs_new"), "certificate.old_vs_new")
    old_model = _nonempty_string(comparison.get("old"), "certificate.old_vs_new.old")
    new_requirement = _nonempty_string(
        comparison.get("new_requirement"),
        "certificate.old_vs_new.new_requirement",
    )
    locality = _mapping(
        root.get("generation_sign_and_locality"),
        "certificate.generation_sign_and_locality",
    )
    locality_warning = _nonempty_string(
        locality.get("locality_warning"),
        "certificate.generation_sign_and_locality.locality_warning",
    )
    return {
        "narrow_check": narrow_check,
        "width_dex": width,
        "pole_count": len(densities),
        "gapless_present": gapless_present,
        "constant_density_derived": constant_density_derived,
        "local_reduction": local_reduction,
        "old_model": old_model,
        "new_requirement": new_requirement,
        "locality_warning": locality_warning,
    }


def adjudicate(
    certificate: Mapping[str, Any],
    *,
    source_path: str,
    source_sha256: str,
) -> dict[str, Any]:
    """Return the scoped C2 verdict supported by one certified snapshot."""

    view = _validated_view(certificate)
    finite_discrete_gapped = bool(
        view["pole_count"] == FROZEN_POLE_COUNT
        and view["old_model"] == FROZEN_MODEL_STATEMENT
        and not view["gapless_present"]
    )
    narrow_mimic = bool(
        view["narrow_check"] and view["width_dex"] < MIMIC_WIDTH_LIMIT_DEX
    )
    no_local_reduction = not view["local_reduction"]
    kill_current = finite_discrete_gapped and narrow_mimic and no_local_reduction

    return {
        "schema": OUTPUT_SCHEMA,
        "title": "C2 critical-continuum gate for the frozen compact spectrum",
        "sources": {
            "spectral_certificate": {
                "path": source_path,
                "sha256": source_sha256,
                "schema": SOURCE_SCHEMA,
            },
            "observational_inputs_read": [],
        },
        "declared_scope": {
            "adjudicated_model": "frozen_current_compact_seven_mode_spectrum",
            "mimic_width_limit_dex": MIMIC_WIDTH_LIMIT_DEX,
            "target_blind": False,
            "parameter_fitting": False,
            "universal_no_go_claimed": False,
        },
        "evidence": {
            "frozen_pole_count": view["pole_count"],
            "gapless_continuum_present": view["gapless_present"],
            "constant_positive_density_per_mass_derived": view[
                "constant_density_derived"
            ],
            "three_halves_mimic_width_dex": view["width_dex"],
            "local_amplitude_reduction_derived": view["local_reduction"],
            "source_old_model_statement": view["old_model"],
            "source_new_requirement": view["new_requirement"],
            "source_locality_warning": view["locality_warning"],
        },
        "kill_conditions": {
            "finite_discrete_gapped_current_spectrum": finite_discrete_gapped,
            "three_halves_is_only_a_narrow_mimic": narrow_mimic,
            "local_nonlinear_amplitude_reduction_absent": no_local_reduction,
            "all": kill_current,
        },
        "decision": {
            "verdict": "KILL_C2" if kill_current else "C2_NOT_KILLED_BY_THIS_GATE",
            "kill_current_frozen_compact_spectrum": kill_current,
            "kill_all_critical_continuum_models": False,
            "physical_completion": False,
            "meaning": (
                "The frozen compact seven-mode model cannot realize C2: it is "
                "gapped and discrete, only crosses the target slope in a narrow "
                "window, and supplies no local nonlinear amplitude reduction."
                if kill_current
                else "This gate lacks the full three-part certificate required to "
                "kill the supplied model."
            ),
        },
        "outside_scope_live_classes": [
            "decompactified_gapless_continuum",
            "critical_boundary_limit",
            "non_gaussian_collective_constraint",
        ],
        "campaign_transition": "UNLOCK_C3" if kill_current else "HOLD_C2",
    }


def build(certificate_path: Path = SPECTRAL_CERTIFICATE) -> dict[str, Any]:
    certificate_path = Path(certificate_path)
    return adjudicate(
        _read(certificate_path),
        source_path=str(certificate_path.relative_to(REPO)),
        source_sha256=_sha256(certificate_path),
    )


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(f"[C2 verdict] {result['decision']['verdict']}")
    print("[scope] current frozen compact spectrum; universal no-go=False")
    return 0 if result["decision"]["verdict"] == "KILL_C2" else 1


if __name__ == "__main__":
    raise SystemExit(main())
