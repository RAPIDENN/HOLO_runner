#!/usr/bin/env python3
"""Turn the user's upper-envelope idea into an exact collector construction.

For the convex AQUAL target F(X), define its conjugate W(s).  Then

    F(X) = sup_{0<s<1} [s X - W(s)],
    s = F'(X) = mu(sqrt(X)).

Every fixed-s branch is affine in X and therefore has a constant linear
permittivity.  The nonlinear force appears because a local conjugate state s
selects the upper envelope.  This is a mathematical representation of the
already exposed collector target, not yet a microscopic derivation of that
selector from HOLO.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import scipy
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator

try:
    from first_principles_audit.prediction_factory import derive_nonlinear_collector_action as action
except ModuleNotFoundError:
    import derive_nonlinear_collector_action as action


HERE = Path(__file__).resolve().parent
ACTION_PATH = HERE / "artifacts" / "nonlinear_collector_action.json"
OUTPUT = HERE / "artifacts" / "collector_legendre_envelope.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upper_envelope(
    query_x: np.ndarray,
    states_s: np.ndarray,
    dual_w: np.ndarray,
    block_size: int = 128,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Evaluate max_s(s*X-W(s)) in bounded-memory blocks."""

    query = np.asarray(query_x, dtype=float)
    states = np.asarray(states_s, dtype=float)
    dual = np.asarray(dual_w, dtype=float)
    if query.ndim != 1 or states.ndim != 1 or dual.shape != states.shape:
        raise ValueError("upper-envelope inputs must be compatible 1D arrays")
    if np.any(query <= 0.0) or np.any(states <= 0.0) or np.any(states >= 1.0):
        raise ValueError("X must be positive and selector states must lie in (0,1)")
    if block_size < 1:
        raise ValueError("block_size must be positive")

    values = np.empty_like(query)
    selectors = np.empty_like(query)
    peak_matrix_bytes = 0
    for start in range(0, query.size, block_size):
        stop = min(start + block_size, query.size)
        branches = query[start:stop, None] * states[None, :] - dual[None, :]
        peak_matrix_bytes = max(peak_matrix_bytes, branches.nbytes)
        selected = np.argmax(branches, axis=1)
        values[start:stop] = branches[np.arange(stop - start), selected]
        selectors[start:stop] = states[selected]
    return values, selectors, peak_matrix_bytes


def build() -> dict[str, Any]:
    source = _read(ACTION_PATH)
    if source["passes"]["all"] is not True:
        raise RuntimeError("nonlinear collector action target must pass first")

    _, arrays = action.reconstruct_action_table(samples=8192)
    X = arrays["X"]
    F = arrays["F"]
    mu = arrays["mu"]
    t = arrays["t"]

    # W'(s)=X with s=mu=1-exp(-t), hence dW/dt=X*exp(-t).
    # Integrating this identity is numerically stable all the way to s->1;
    # the algebraically equivalent subtraction s*X-F loses precision there.
    dual_w = (mu[0] ** 3) / 3.0 + cumulative_trapezoid(
        X * np.exp(-t), t, initial=0.0
    )
    primal_from_dual = mu * X - dual_w
    primal_dual_relative_error = np.abs(primal_from_dual - F) / np.maximum(
        np.abs(F), 1.0e-300
    )

    # Tangents and queries are deliberately interlaced, so envelope recovery
    # is not the trivial evaluation of every tangent at its contact point.
    # Binary64 rounds mu=1-exp(-t) to exactly one at very large t.  The dual
    # coordinate lives on the open interval, so stop before that endpoint.
    open_domain = np.flatnonzero(mu < 1.0 - 1.0e-12)
    last = int(open_domain[-1])
    state_indices = np.arange(0, last, 4, dtype=int)
    query_indices = np.arange(2, last - 2, 4, dtype=int)
    states = mu[state_indices]
    state_dual = dual_w[state_indices]
    query_X = X[query_indices]
    true_F = F[query_indices]
    true_mu = mu[query_indices]
    envelope_F, selected_s, peak_bytes = upper_envelope(
        query_X, states, state_dual
    )

    relative_envelope_error = np.abs(envelope_F - true_F) / np.maximum(
        np.abs(true_F), 1.0e-300
    )
    selector_relative_error = np.abs(selected_s - true_mu) / true_mu

    deep = mu < 1.0e-3
    deep_slope = float(np.polyfit(np.log(mu[deep]), np.log(dual_w[deep]), 1)[0])
    deep_coefficient = float(np.median(dual_w[deep] / np.power(mu[deep], 3)))
    # Near s=1 several adjacent values collapse to the same binary64 number.
    # PCHIP needs a strictly increasing abscissa, so evaluate the dual only on
    # the numerically resolved open interval and retain one copy of each s.
    resolved = open_domain[
        np.r_[True, np.diff(mu[open_domain]) > 0.0]
    ]
    dual_interpolator = PchipInterpolator(mu[resolved], dual_w[resolved])
    derivative_indices = resolved[8:-8]
    derivative_error = np.abs(
        dual_interpolator.derivative()(mu[derivative_indices])
        - X[derivative_indices]
    )
    derivative_relative_error = float(
        np.max(
            derivative_error
            / np.maximum(X[derivative_indices], 1.0e-300)
        )
    )

    passes = {
        "source_action_target_passes": True,
        "dual_is_nonnegative": bool(np.min(dual_w) >= -1.0e-24),
        "dual_is_strictly_increasing": bool(
            np.all(np.diff(dual_w[resolved]) > 0.0)
        ),
        "dual_derivative_recovers_X": derivative_relative_error < 5.0e-4,
        "dual_reconstructs_primal_action": (
            float(np.max(primal_dual_relative_error)) < 3.0e-6
        ),
        "deep_dual_is_cubic": (
            abs(deep_slope - 3.0) < 3.0e-3
            and abs(deep_coefficient - 1.0 / 3.0) < 2.0e-3
        ),
        "interlaced_upper_envelope_recovers_F": (
            float(np.max(relative_envelope_error)) < 2.0e-4
        ),
        "selector_recovers_mu": float(np.max(selector_relative_error)) < 6.0e-3,
        "memory_below_8_mib": peak_bytes < 8 * 1024**2,
        "no_observational_table_read": True,
    }
    passes["all"] = all(passes.values())

    anchors = np.unique(np.linspace(0, query_X.size - 1, 32, dtype=int))
    return {
        "schema": "holo.collector-legendre-envelope.v1",
        "title": "Upper-envelope dual of the nonlinear collector",
        "classification": (
            "exact_mathematical_envelope_representation_of_exposed_target;"
            "microscopic_holo_selector_not_yet_derived"
        ),
        "source": {
            "path": str(ACTION_PATH.relative_to(HERE.parents[1])),
            "sha256": _sha256(ACTION_PATH),
            "raw_sparc_or_vobs_read": False,
        },
        "construction": {
            "primal": "F(X)",
            "dual": "W(s)=sup_X[s*X-F(X)]",
            "inverse": "F(X)=sup_(0<s<1)[s*X-W(s)]",
            "selector": "s=F'(X)=mu(sqrt(X))",
            "fixed_state_branch": "F_s(X)=s*X-W(s)",
            "physical_reading": (
                "Each fixed-s branch is a constant-permittivity linear response. "
                "A local conjugate state selects their upper envelope and generates "
                "the nonlinear collector."
            ),
            "deep_limit": (
                "F~(2/3)X^(3/2), s~sqrt(X), W(s)~s^3/3"
            ),
        },
        "diagnostics": {
            "states": int(states.size),
            "interlaced_queries": int(query_X.size),
            "maximum_envelope_relative_error": float(
                np.max(relative_envelope_error)
            ),
            "maximum_selector_relative_error": float(
                np.max(selector_relative_error)
            ),
            "dual_derivative_maximum_relative_error": derivative_relative_error,
            "primal_dual_maximum_relative_error": float(
                np.max(primal_dual_relative_error)
            ),
            "deep_dual_log_slope": deep_slope,
            "deep_dual_cubic_coefficient": deep_coefficient,
            "peak_branch_matrix_mib": peak_bytes / 1024**2,
        },
        "anchors": [
            {
                "X": float(query_X[index]),
                "F": float(true_F[index]),
                "envelope_F": float(envelope_F[index]),
                "mu": float(true_mu[index]),
                "selected_s": float(selected_s[index]),
            }
            for index in anchors
        ],
        "holo_bridge_hypothesis": {
            "idea": (
                "Promote s to a local boundary/order-parameter field whose potential "
                "is W(s); couple it to the physical potential through s*X."
            ),
            "minimal_saddle_action": (
                "S=-a0^2/(8*pi*G) integral [s*X-W(s)] - integral rho*Phi; "
                "variation in s imposes X=W'(s)"
            ),
            "existing_ingredients": [
                "a scalar carrier and boundary potentials",
                "a continuous positive Robin boundary family",
                "state-dependent breathing-mode transfer functions",
            ],
            "new_unproved_link": (
                "No current certificate makes a boundary phase local, couples it as "
                "s*X, or derives W(s) and a0 from the five-dimensional action."
            ),
            "decisive_test": (
                "Derive the local selector and W(s) without SPARC, then solve the "
                "axisymmetric PDE with frozen baryonic sources."
            ),
        },
        "passes": passes,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main() -> int:
    result = build()
    _write(OUTPUT, result)
    print(f"[artifact] {OUTPUT}")
    print(
        "[envelope] max relative error="
        f"{result['diagnostics']['maximum_envelope_relative_error']:.6g}"
    )
    print(
        "[deep dual] W(s)~c*s^p with "
        f"p={result['diagnostics']['deep_dual_log_slope']:.6g}, "
        f"c={result['diagnostics']['deep_dual_cubic_coefficient']:.6g}"
    )
    print(f"[certificate] {'PASS' if result['passes']['all'] else 'FAIL'}")
    return 0 if result["passes"]["all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
