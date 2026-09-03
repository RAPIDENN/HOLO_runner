#!/usr/bin/env python3
"""Additive C2 polynomial radial-profile correction for the multi-N bundle.

The common-first boundary data and every free coordinate remain byte-identical
to v5.6.4.3.  Only the map that extends trace/jet/interior coefficients into
the finite collar is replaced.  The new polynomials preserve the prescribed
trace and first normal jet at rho=0 and vanish with two derivatives at rho=1,
which is the regularity required by the second-derivative EH action used here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"
PARENT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_3_multin_primitive_bundle.json"
)
PARENT_SHA256 = "9ebf92cd760225667137247c65034bd56eccc714be9f3bb15d5a605a51656519"
OUTPUT = ARTIFACTS / (
    "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitive_bundle.json"
)
TEST = HERE / (
    "test_one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_4_c2_radial_primitives.py"
)
SCHEMA = (
    "holo.one-omega-topological-so3-restricted-spectral-family-"
    "v5-6-4-4-c2-radial-primitive-bundle.v1"
)

RADIAL_PROFILE_TEXT = (
    "h0(rho)=1-10*rho^3+15*rho^4-6*rho^5; h1(rho)=rho*h0(rho); "
    "h0(0)=1,h0'(0)=h0''(0)=0,h1(0)=0,h1'(0)=1,h1''(0)=0; "
    "h0,h1 and derivatives through order 2 vanish at rho=1; all fields equal "
    "the fixed reference for rho>=1"
)
RADIAL_BASIS_TEXT = (
    "K(N)=N and b_j(rho)=64*rho^3*(1-rho)^3*P_j(2rho-1), "
    "j=0,...,K(N)-1 on 0<rho<1, extended by zero; b_j and derivatives "
    "through order 2 vanish at both endpoints"
)


class C2RadialPrimitiveError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _contains_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, dict):
        return any(_contains_boolean(key) or _contains_boolean(item)
                   for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_boolean(item) for item in value)
    return False


def radial_profiles(rho: np.ndarray, K: int) -> Mapping[str, np.ndarray]:
    r = np.asarray(rho, dtype=float)
    if r.ndim != 1 or np.any((r < 0.0) | (r > 1.0)):
        raise C2RadialPrimitiveError("rho must be a vector in [0,1]")
    if isinstance(K, bool) or not isinstance(K, int) or K <= 0:
        raise C2RadialPrimitiveError("K must be a positive integer")
    h0 = 1.0 - 10.0 * r**3 + 15.0 * r**4 - 6.0 * r**5
    h0_first = -30.0 * r**2 + 60.0 * r**3 - 30.0 * r**4
    h0_second = -60.0 * r + 180.0 * r**2 - 120.0 * r**3
    h1 = r * h0
    h1_first = h0 + r * h0_first
    h1_second = 2.0 * h0_first + r * h0_second

    s = r * (1.0 - r)
    s_first = 1.0 - 2.0 * r
    envelope = 64.0 * s**3
    envelope_first = 192.0 * s**2 * s_first
    envelope_second = 384.0 * s * s_first**2 - 384.0 * s**2
    z = 2.0 * r - 1.0
    bumps = np.empty((r.size, K), dtype=float)
    bumps_first = np.empty_like(bumps)
    bumps_second = np.empty_like(bumps)
    for degree in range(K):
        coefficients = np.zeros(degree + 1, dtype=float)
        coefficients[degree] = 1.0
        first_coefficients = np.polynomial.legendre.legder(coefficients, 1)
        second_coefficients = np.polynomial.legendre.legder(coefficients, 2)
        polynomial = np.polynomial.legendre.legval(z, coefficients)
        polynomial_first = 2.0 * np.polynomial.legendre.legval(
            z, first_coefficients
        )
        polynomial_second = 4.0 * np.polynomial.legendre.legval(
            z, second_coefficients
        )
        bumps[:, degree] = envelope * polynomial
        bumps_first[:, degree] = (
            envelope_first * polynomial + envelope * polynomial_first
        )
        bumps_second[:, degree] = (
            envelope_second * polynomial
            + 2.0 * envelope_first * polynomial_first
            + envelope * polynomial_second
        )
    return {
        "h0": h0,
        "h0_first": h0_first,
        "h0_second": h0_second,
        "h1": h1,
        "h1_first": h1_first,
        "h1_second": h1_second,
        "bumps": bumps,
        "bumps_first": bumps_first,
        "bumps_second": bumps_second,
    }


def endpoint_contract(K: int = 3) -> Mapping[str, Any]:
    values = radial_profiles(np.asarray((0.0, 1.0)), K)
    return {
        "rho_0": {
            "h0": float(values["h0"][0]),
            "h0_first": float(values["h0_first"][0]),
            "h0_second": float(values["h0_second"][0]),
            "h1": float(values["h1"][0]),
            "h1_first": float(values["h1_first"][0]),
            "h1_second": float(values["h1_second"][0]),
            "bumps_Linf": float(np.max(np.abs(values["bumps"][0]))),
            "bumps_first_Linf": float(np.max(np.abs(values["bumps_first"][0]))),
            "bumps_second_Linf": float(np.max(np.abs(values["bumps_second"][0]))),
        },
        "rho_1": {
            key + "_Linf": float(np.max(np.abs(array[-1])))
            for key, array in values.items()
        },
    }


def build_bundle() -> Mapping[str, Any]:
    observed = _sha256(PARENT)
    if observed != PARENT_SHA256:
        raise C2RadialPrimitiveError(f"v5.6.4.3 parent drift: {observed}")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    inherited_hash = parent.pop("payload_sha256")
    if _canonical_sha256(parent) != inherited_hash:
        raise C2RadialPrimitiveError("v5.6.4.3 embedded payload hash drift")
    parent["schema"] = SCHEMA
    parent["classification"] = (
        "primitive_pointwise_multin_family;N1_N2_N3;C2_polynomial_radial_extension;"
        "authoritative_free_curves;no_action_receipt;no_decision_booleans;"
        "no_continuous_promotion"
    )
    parent["source_pins"]["v5_6_4_3_parent_bundle"] = {
        "path": str(PARENT.relative_to(REPO)),
        "sha256": PARENT_SHA256,
        "consumed_content": "all primitive free coordinates, tangents, pointwise gluing contracts, and literal action contract",
    }
    for contract in parent["pointwise_decoder_contract_by_N"].values():
        contract["radial_profiles"] = RADIAL_PROFILE_TEXT
        contract["radial_basis"] = RADIAL_BASIS_TEXT
    parent["radial_profile_correction"] = {
        "reason": (
            "The inherited C-infinity flat exponential collar is mathematically valid "
            "but produced slow oscillatory global Gauss convergence after second metric "
            "derivatives. The additive C2 polynomial collar preserves the same boundary "
            "trace/jet and cap data while making the finite spectral action auditable."
        ),
        "regularity_scope": (
            "C2 on the closed collar after zero extension at rho=1; sufficient for the "
            "literal second-derivative EH density and the declared classical finite family"
        ),
        "h0": "1-10*rho^3+15*rho^4-6*rho^5",
        "h1": "rho*h0",
        "interior_envelope": "64*rho^3*(1-rho)^3",
        "endpoint_values": endpoint_contract(),
        "unchanged_objects": [
            "literal v5.2 action and coefficients",
            "common-first boundary decoder and gluing map",
            "all authoritative free central configurations and tangents",
            "SO3 frames, relative rotations, embeddings, and side orientations",
        ],
    }
    parent["provenance_v5_6_4_4"] = {
        "generator": {
            "path": str(Path(__file__).resolve().relative_to(REPO)),
            "sha256": _sha256(Path(__file__).resolve()),
        },
        "test": {
            "path": str(TEST.relative_to(REPO)),
            "sha256": _sha256(TEST) if TEST.exists() else "test_not_present",
        },
    }
    if _contains_boolean(parent):
        raise C2RadialPrimitiveError("corrected primitive bundle contains a boolean")
    parent["payload_sha256"] = _canonical_sha256(parent)
    return parent


def render_bundle(bundle: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(render_bundle(build_bundle()))
    print(OUTPUT)
    print(_sha256(OUTPUT))


if __name__ == "__main__":
    main()
