"""Independent constant-coefficient jet algebra for a local brane Hessian.

The input is a homogeneous quadratic position-space density in the eighteen
real charter fields and their derivatives. The output convention is
``S2 = integral f(-p).T * H(p) * f(p) / 2``, with formal differential symbols
``d_t=-I*w, d_z=I*q, d_x=d_y=0``. The left factor is the formal adjoint.
No plane wave, independent conjugate amplitude, generator import or I/O is used.

This algebra does not derive the input Lagrangian, solve constraints, impose
junction conditions, or certify stability. Parameter coefficients must be
constant in the four coordinates; symbolic parameter singularities retain their
usual domains. It rejects explicit non-finite values rather than asserting that
every parameter-dependent denominator is nonzero.
"""
from __future__ import annotations

from collections.abc import Mapping

import sympy as sp
from sympy.core.function import AppliedUndef


FIELD_NAMES = (
    "n", "N1", "N2", "N3", "H11", "H12", "H13", "H22", "H23", "H33",
    "tau", "pi1", "pi2", "pi3", "omega", "vphi1", "vphi2", "vphi3",
)
PARAMETER_NAMES = (
    "M5c", "k_inf", "G", "beta", "Mb2", "lambda_K", "xi", "eta",
    "B4bar", "kappa_hat", "y", "v", "rho_X", "mu_X", "lambda_X",
)
NEW_FIELD_NAMES = (
    "n", "N3", "Htrace", "H33", "tau", "pi3", "omega", "vphi3",
    "N1", "N2", "Hxz", "Hyz", "pi1", "pi2", "vphi1", "vphi2",
    "Hplus", "Hcross",
)


class HessianAlgebraError(ValueError):
    """The expression is outside the declared constant quadratic jet domain."""


def symbols_context() -> dict:
    """Return the exact charter field order and disambiguated symbol objects.

    Coordinate y is real; parameter y is positive. Their printed names agree,
    but they are distinct SymPy symbols and must not be reconstructed by a
    context-free string parser.
    """
    coords = sp.symbols("t x y z", real=True)
    parameters = {name: sp.Symbol(name, positive=True) for name in PARAMETER_NAMES}
    q, w = sp.symbols("q w", real=True)
    return {
        "coords": coords,
        "fields": tuple(sp.Function(name, real=True)(*coords) for name in FIELD_NAMES),
        "field_names": FIELD_NAMES,
        "parameters": parameters,
        "q": q,
        "w": w,
    }


def _context_parts(context: Mapping) -> tuple:
    if not isinstance(context, Mapping):
        raise HessianAlgebraError("context must be a mapping")
    try:
        coords = tuple(context["coords"])
        fields = tuple(context["fields"])
        names = tuple(context["field_names"])
        q, w = context["q"], context["w"]
    except (KeyError, TypeError) as exc:
        raise HessianAlgebraError("incomplete symbol context") from exc
    if (len(coords) != 4 or len(set(coords)) != 4
            or any(not isinstance(c, sp.Symbol) or c.is_real is not True for c in coords)):
        raise HessianAlgebraError("four distinct real coordinate symbols required")
    if names != FIELD_NAMES or len(fields) != len(FIELD_NAMES) or len(set(fields)) != len(fields):
        raise HessianAlgebraError("eighteen distinct fields in charter order required")
    for name, field in zip(names, fields):
        if (not isinstance(field, AppliedUndef) or field.args != coords
                or field.func.__name__ != name or field.is_real is not True):
            raise HessianAlgebraError("field must be the declared real function of all coordinates")
    if (not isinstance(q, sp.Symbol) or not isinstance(w, sp.Symbol)
            or q.is_real is not True or w.is_real is not True or q == w
            or q in coords or w in coords):
        raise HessianAlgebraError("distinct real momentum symbols required")
    return coords, fields, q, w


def _finite_expression(expression: sp.Expr) -> None:
    if expression.has(sp.nan, sp.oo, -sp.oo, sp.zoo) or expression.is_finite is False:
        raise HessianAlgebraError("non-finite expression or coefficient")


def _jet_factor(counts: tuple[int, ...], q: sp.Symbol, w: sp.Symbol) -> sp.Expr:
    nt, nx, ny, nz = counts
    if nx or ny:
        return sp.S.Zero
    return (-sp.I*w)**nt * (sp.I*q)**nz


def momentum_hessian(L2: sp.Expr, context: Mapping) -> sp.Matrix:
    """Build an 18x18 kernel by polarizing each quadratic jet monomial.

    Every ``c * jet_i * jet_j`` contributes
    ``c * adjoint(d_i) * d_j`` to H[field_i, field_j] and the exchanged term
    to H[field_j, field_i]. This also gives the required factor two for a
    diagonal monomial. Mixed derivatives commute through their multi-index.
    """
    coords, fields, q, w = _context_parts(context)
    if isinstance(L2, (int, float)) and not isinstance(L2, bool):
        L2 = sp.sympify(L2)
    if not isinstance(L2, sp.Expr):
        raise HessianAlgebraError("L2 must be a scalar SymPy expression, not serialized code")
    _finite_expression(L2)
    if L2.is_zero is True:
        return sp.zeros(len(fields))
    known_fields = set(fields)
    if L2.atoms(AppliedUndef) - known_fields:
        raise HessianAlgebraError("undeclared field or function in L2")
    field_index = {field: index for index, field in enumerate(fields)}
    coord_index = {coord: index for index, coord in enumerate(coords)}
    descriptors: dict[sp.Expr, tuple[int, tuple[int, ...]]] = {
        field: (index, (0, 0, 0, 0)) for index, field in enumerate(fields)
        if L2.has(field)
    }
    for derivative in L2.atoms(sp.Derivative):
        if derivative.expr not in field_index:
            raise HessianAlgebraError("derivative is not of a declared field")
        counts = [0, 0, 0, 0]
        for axis, order in derivative.variable_count:
            if axis not in coord_index or not isinstance(order, sp.Integer) or order <= 0:
                raise HessianAlgebraError("derivative axis or order outside the coordinate jet domain")
            counts[coord_index[axis]] += int(order)
        descriptors[derivative] = (field_index[derivative.expr], tuple(counts))
    # A sorted multi-index gives the same jet to differently ordered partials.
    jets = sorted(set(descriptors.values()))
    if not jets:
        raise HessianAlgebraError("nonzero L2 must be homogeneous quadratic in field jets")
    jet_symbols = tuple(sp.Dummy(f"jet_{i}", real=True) for i in range(len(jets)))
    by_descriptor = dict(zip(jets, jet_symbols))
    replacements = {node: by_descriptor[descriptor] for node, descriptor in descriptors.items()}
    jet_expression = L2.xreplace(replacements)
    if jet_expression.has(*coords):
        raise HessianAlgebraError("coefficients must be constant in coordinates")
    try:
        polynomial = sp.Poly(jet_expression, *jet_symbols, domain="EX")
    except (sp.PolynomialError, TypeError, ValueError) as exc:
        raise HessianAlgebraError("L2 must be polynomial and homogeneous quadratic in field jets") from exc
    factors = [_jet_factor(counts, q, w) for _, counts in jets]
    # For real q,w the adjoint is multiplication by (-1)^derivative_order.
    adjoints = [(-1)**sum(counts)*factor for (_, counts), factor in zip(jets, factors)]
    result = sp.zeros(len(fields))
    for powers, coefficient in polynomial.terms():
        if coefficient == 0:
            continue
        if sum(powers) != 2:
            raise HessianAlgebraError("L2 must be homogeneous quadratic with no constant or linear remainder")
        _finite_expression(coefficient)
        if coefficient.has(*coords):
            raise HessianAlgebraError("coefficients must be constant in coordinates")
        pair = [index for index, degree in enumerate(powers) for _ in range(degree)]
        left, right = pair
        i, j = jets[left][0], jets[right][0]
        result[i, j] += coefficient*adjoints[left]*factors[right]
        result[j, i] += coefficient*adjoints[right]*factors[left]
    return result.applyfunc(sp.expand)


def helicity_basis(context: Mapping) -> tuple[sp.Matrix, tuple[str, ...], dict]:
    """Return old=S*new in scalar(8), vector(8), tensor(2) order along z.

    Off-diagonal symmetric metric components have Frobenius weight two, hence
    the 1/sqrt(2) factors. No positivity or dynamical decoupling is inferred.
    """
    _coords, fields, _q, _w = _context_parts(context)
    old_index = {name: i for i, name in enumerate(FIELD_NAMES)}
    new_index = {name: i for i, name in enumerate(NEW_FIELD_NAMES)}
    S = sp.zeros(len(fields))
    inverse_sqrt_two = 1/sp.sqrt(2)
    for name in FIELD_NAMES:
        if name in NEW_FIELD_NAMES:
            S[old_index[name], new_index[name]] = 1
    S[old_index["H11"], new_index["Htrace"]] = inverse_sqrt_two
    S[old_index["H11"], new_index["Hplus"]] = inverse_sqrt_two
    S[old_index["H22"], new_index["Htrace"]] = inverse_sqrt_two
    S[old_index["H22"], new_index["Hplus"]] = -inverse_sqrt_two
    for old_name, new_name in (("H12", "Hcross"), ("H13", "Hxz"), ("H23", "Hyz")):
        S[old_index[old_name], new_index[new_name]] = inverse_sqrt_two
    groups = {"scalar": tuple(range(8)), "vector": tuple(range(8, 16)), "tensor": (16, 17)}
    return S, NEW_FIELD_NAMES, groups
