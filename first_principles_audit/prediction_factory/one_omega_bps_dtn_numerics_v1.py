"""Bounded numerical BPS Dirichlet-to-Neumann evaluation; no physical gates.

For e**A = Omega, a = G/(6*M5c), and conformal radius x defined by
dr = Omega*dx, set rhat = -d_x(log H)/k.  The tensor and scalar-R pumps
are proportional to Omega**n with n=3/2 and n=5/2 respectively.  Their
Riccati equation, integrated from t=log(Omega_min) to the UV t=0, is

    d_t rhat = -exp(a*Omega**2)/Omega *
               (rhat**2 - 2*uhat*rhat - (p/k)**2),
    uhat = -n*Omega*exp(-a*Omega**2),       K = 2*k*rhat(0).

The two-sided UV normalization uses Omega(UV)=1.  The decaying IR Bessel
datum has order nu=n+1/2.  It is exact at a=0; for a>0 it is an IR
approximation at a finite cutoff.  Requiring |p/k|/Omega_min >= 10 and
a*Omega_min**2 <= 1e-3 is a documented numerical initialization criterion,
NOT a rigorous truncation-error bound.  Compare separately chosen cutoffs
and tolerances when using results.  The inherited conditioning exclusion
|p/k| < 1e-7 is numerical; it does not remove physical light-cone questions.

Radau uses two real components with the analytic complex Jacobian converted
to a real 2x2 matrix.  DOP853 is available only as a budgeted comparison.
Budgets are cooperative checks in callbacks, including before and after
native calls; they cannot interrupt a single native Bessel or linear-algebra
call.  This module launches no threads, caches no kernels, and certifies no
global existence, holomorphy, pole theorem, BF sector, or full stability.

Numerical-method antecedent, not imported and with no inherited claims:
derive_backreacted_master_schur_gate.py::wall_scalar_master_dtn, lines 267-353
in the source inspected when this independent implementation was written.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import scipy
from scipy import integrate, special


class DTNInputError(ValueError):
    """An input lies outside the declared binary64 numerical domain."""


class DTNEvaluationError(RuntimeError):
    """No kernel is returned after a failed or budget-exhausted evaluation."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None):
        super().__init__(message)
        self.diagnostics = {} if diagnostics is None else dict(diagnostics)


IR_ARGUMENT_MIN = 10.0
IR_DEFORMATION_MAX = 1.0e-3
MIN_DIMENSIONLESS_P = 1.0e-7
MAX_NFEV = 50_000
MAX_SECONDS = 30.0
_SECTORS = {"TT": (1.5, 2.0), "scalarR": (2.5, 3.0)}
_SOURCE_PATH = Path(__file__).resolve()
_LOADED_SOURCE_SHA256 = hashlib.sha256(_SOURCE_PATH.read_bytes()).hexdigest()


def _finite_real(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise DTNInputError(f"{name} must be a finite real number, not bool")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DTNInputError(f"{name} must be a finite real number") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        suffix = " and positive" if positive else ""
        raise DTNInputError(f"{name} must be finite{suffix}")
    return result


def _finite_complex(value: Any) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


def _inputs(p: Any, sector: str, k: Any) -> tuple[complex, float, float, float]:
    if not isinstance(sector, str) or sector not in _SECTORS:
        raise DTNInputError("sector must be 'TT' or 'scalarR'")
    if isinstance(p, (bool, np.bool_)):
        raise DTNInputError("p must be finite with Re(p)>0, not bool")
    try:
        frequency = complex(p)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DTNInputError("p must be finite with Re(p)>0") from exc
    if not _finite_complex(frequency) or frequency.real <= 0:
        raise DTNInputError("p must be finite with Re(p)>0")
    scale = _finite_real(k, "k", positive=True)
    n, nu = _SECTORS[sector]
    return frequency, scale, n, nu


def _scaled_bessel_ratio(nu: float, argument: complex) -> complex:
    numerator = complex(special.kve(nu - 1.0, argument))
    denominator = complex(special.kve(nu, argument))
    if not (_finite_complex(numerator) and _finite_complex(denominator)):
        raise ArithmeticError("scaled Bessel values are nonfinite")
    if abs(denominator) <= 128.0 * np.finfo(float).tiny:
        raise ArithmeticError("scaled Bessel denominator is unresolved")
    ratio = numerator / denominator
    if not _finite_complex(ratio):
        raise ArithmeticError("scaled Bessel ratio is nonfinite")
    return ratio


def bessel_reference(p: complex, *, sector: str = "TT", k: float = 1.0) -> complex:
    """Exact a=0 geometric reference K=2*p*K_(nu-1)(p/k)/K_nu(p/k).

    This is a Bessel evaluation, not a statement about the physical G=0
    scalar theory.  Inputs must obey Re(p)>0 and k>0; no result is cached.
    """
    frequency, scale, _, nu = _inputs(p, sector, k)
    argument = frequency / scale
    if not _finite_complex(argument) or argument == 0:
        raise DTNInputError("p/k must be finite and nonzero in binary64")
    try:
        kernel = 2.0 * frequency * _scaled_bessel_ratio(nu, argument)
        if not _finite_complex(kernel):
            raise ArithmeticError("Bessel reference kernel is nonfinite")
    except (ArithmeticError, ValueError) as exc:
        raise DTNEvaluationError(str(exc), {"p": frequency, "k": scale,
                                            "sector": sector, "a": 0.0}) from exc
    return kernel


def _source_identity() -> dict[str, Any]:
    current_hash = hashlib.sha256(_SOURCE_PATH.read_bytes()).hexdigest()
    if current_hash != _LOADED_SOURCE_SHA256:
        raise DTNEvaluationError("implementation changed after import; reload it")
    return {
        "schema": "one_omega.bps_dtn_numerics.v1",
        "implementation": _SOURCE_PATH.name,
        "implementation_sha256": current_hash,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "method_antecedent": "derive_backreacted_master_schur_gate.py::wall_scalar_master_dtn",
        "antecedent_imported": False,
        "background": "Omega=exp(A), dOmega/dr=-k*Omega*exp(-a*Omega**2)",
        "deformation_convention": "a=G/(6*M5c); a=0 used as geometric reference",
        "riccati_equation": "drhat/dlogOmega=-exp(a*Omega**2)/Omega*(rhat**2-2*uhat*rhat-(p/k)**2)",
        "uhat": "-n*Omega*exp(-a*Omega**2)",
        "two_sided_normalization": "K=2*k*rhat(UV), Omega(UV)=1",
        "physical_action_binding": None,
    }


def evaluate_dtn(
    p: complex,
    *,
    sector: str = "TT",
    k: float = 1.0,
    a: float = 0.2,
    omega_min: float | None = None,
    method: str = "Radau",
    rtol: float = 1.0e-9,
    atol: float = 1.0e-11,
    max_nfev: int = 6000,
    max_seconds: float = 5.0,
    max_step: float = 0.5,
) -> dict[str, Any]:
    """Return a fresh complex kernel and numerical diagnostics, or raise.

    p is the already selected momentum branch with Re(p)>0.  The caller
    owns its relation to frequency and spatial momentum.  A supplied cutoff
    is never silently clamped.  steps counts accepted intervals, not nodes.
    The default cutoff is min(1e-4, abs(p/k)/50).  Solver tolerances are local
    error controls, not certified bounds for the reported UV kernel.
    """
    frequency, scale, n, nu = _inputs(p, sector, k)
    deformation = _finite_real(a, "a")
    if deformation < 0:
        raise DTNInputError("a must be nonnegative")
    relative = _finite_real(rtol, "rtol", positive=True)
    absolute = _finite_real(atol, "atol", positive=True)
    if relative < 100.0 * np.finfo(float).eps:
        raise DTNInputError("rtol below scipy's binary64 floor is not accepted")
    seconds_limit = _finite_real(max_seconds, "max_seconds", positive=True)
    if seconds_limit > MAX_SECONDS:
        raise DTNInputError(f"max_seconds must be <= {MAX_SECONDS:g}")
    if (isinstance(max_nfev, (bool, np.bool_))
            or not isinstance(max_nfev, (int, np.integer))
            or not 1 <= max_nfev <= MAX_NFEV):
        raise DTNInputError(f"max_nfev must be an integer in [1,{MAX_NFEV}]")
    step_limit = _finite_real(max_step, "max_step", positive=True)
    if method not in ("Radau", "DOP853"):
        raise DTNInputError("method must be 'Radau' or 'DOP853'")
    dimensionless_p = frequency / scale
    magnitude = math.hypot(dimensionless_p.real, dimensionless_p.imag)
    if (not _finite_complex(dimensionless_p) or dimensionless_p.real <= 0
            or not math.isfinite(magnitude) or magnitude < MIN_DIMENSIONLESS_P):
        raise DTNInputError("finite |p/k| >= 1e-7 is required for numerical conditioning")
    cutoff = (min(1.0e-4, magnitude / 50.0) if omega_min is None
              else _finite_real(omega_min, "omega_min", positive=True))
    if not 0 < cutoff < 1:
        raise DTNInputError("omega_min must lie strictly between 0 and 1")
    argument = dimensionless_p / cutoff
    argument_magnitude = math.hypot(argument.real, argument.imag)
    if (not _finite_complex(argument) or not math.isfinite(argument_magnitude)
            or argument_magnitude < IR_ARGUMENT_MIN):
        raise DTNInputError(f"finite |p/k|/omega_min >= {IR_ARGUMENT_MIN:g} is required")
    cutoff_deformation = deformation * cutoff * cutoff
    if cutoff_deformation > IR_DEFORMATION_MAX:
        raise DTNInputError("a*omega_min**2 must be <= 1e-3; choose a smaller cutoff")

    start = time.monotonic()
    counts = {"nfev": 0, "njev": 0}
    settings = {"p": frequency, "k": scale, "a": deformation, "sector": sector,
                "method": method, "rtol": relative, "atol": absolute,
                "cutoff": cutoff, "omega_min": cutoff, "max_step": step_limit,
                "max_nfev": int(max_nfev), "max_seconds": seconds_limit}

    def diagnostics() -> dict[str, Any]:
        return {**settings, **counts, "elapsed_seconds": time.monotonic() - start}

    def check_budget(*, rhs_call: bool = False) -> None:
        if time.monotonic() - start >= seconds_limit:
            raise DTNEvaluationError("cooperative time budget exhausted", diagnostics())
        if rhs_call and counts["nfev"] >= max_nfev:
            raise DTNEvaluationError("RHS evaluation budget exhausted", diagnostics())

    def coefficients(t: float, state: np.ndarray) -> tuple[float, float, complex]:
        omega = math.exp(t)
        exponential = math.exp(deformation * omega * omega)
        coefficient = exponential / omega
        uhat = -n * omega / exponential
        rhat = complex(state[0], state[1])
        if not math.isfinite(coefficient) or not _finite_complex(rhat):
            raise ArithmeticError("nonfinite Riccati coefficient or state")
        return coefficient, uhat, rhat

    def rhs(t: float, state: np.ndarray) -> list[float]:
        check_budget(rhs_call=True)
        counts["nfev"] += 1
        coefficient, uhat, rhat = coefficients(t, state)
        # Factoring rhat**2-P**2 avoids subtracting two large squares.
        derivative = -coefficient * ((rhat - dimensionless_p) *
                                     (rhat + dimensionless_p) - 2.0 * uhat * rhat)
        if not _finite_complex(derivative):
            raise ArithmeticError("nonfinite Riccati RHS")
        return [derivative.real, derivative.imag]

    def jac(t: float, state: np.ndarray) -> list[list[float]]:
        check_budget()
        counts["njev"] += 1
        coefficient, uhat, rhat = coefficients(t, state)
        derivative = -2.0 * coefficient * (rhat - uhat)
        if not _finite_complex(derivative):
            raise ArithmeticError("nonfinite Riccati Jacobian")
        return [[derivative.real, -derivative.imag], [derivative.imag, derivative.real]]

    try:
        source = _source_identity()
        check_budget()
        initial_rhat = dimensionless_p * _scaled_bessel_ratio(nu, argument)
        if not _finite_complex(initial_rhat):
            raise ArithmeticError("nonfinite IR Riccati initial datum")
        check_budget()
        options = {"jac": jac} if method == "Radau" else {}
        solution = integrate.solve_ivp(
            rhs, (math.log(cutoff), 0.0), [initial_rhat.real, initial_rhat.imag],
            method=method, rtol=relative, atol=absolute, max_step=step_limit,
            dense_output=False, **options,
        )
        check_budget()
        if not solution.success or solution.t[-1] != 0.0:
            raise DTNEvaluationError(f"Riccati integration failed: {solution.message}",
                                     diagnostics())
        kernel = 2.0 * scale * complex(solution.y[0, -1], solution.y[1, -1])
        if not _finite_complex(kernel):
            raise ArithmeticError("nonfinite UV kernel")
        if _source_identity()["implementation_sha256"] != source["implementation_sha256"]:
            raise DTNEvaluationError("implementation changed during evaluation", diagnostics())
        check_budget()
    except DTNEvaluationError as exc:
        if not exc.diagnostics:
            exc.diagnostics = diagnostics()
        raise
    except (ArithmeticError, ValueError) as exc:
        raise DTNEvaluationError(str(exc), diagnostics()) from exc

    return {
        **settings, "kernel": kernel, "steps": int(len(solution.t) - 1),
        "nfev": int(solution.nfev), "njev": int(solution.njev),
        "nlu": int(solution.nlu), "rhs_calls": counts["nfev"],
        "jac_calls": counts["njev"], "elapsed_seconds": time.monotonic() - start,
        "solver_success": True, "solver_status": int(solution.status),
        "solver_message": str(solution.message), "pump_exponent": n,
        "bessel_order": nu, "initial_rhat": initial_rhat,
        "initial_argument": argument, "initial_argument_abs": argument_magnitude,
        "initial_deformation": cutoff_deformation,
        "cutoff_was_explicit": omega_min is not None,
        "initial_data_exact_for_a_zero": deformation == 0.0,
        "initialization_criterion": {"min_abs_argument": IR_ARGUMENT_MIN,
                                     "max_a_omega_squared": IR_DEFORMATION_MAX},
        "numerical_error_bound_certified": False,
        "physical_claims_certified": False,
        "budget_kind": "cooperative_callbacks_no_native_call_preemption",
        "source": source,
    }
