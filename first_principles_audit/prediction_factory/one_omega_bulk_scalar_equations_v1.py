"""Exact scalar bulk equations in two field coordinates, without spacetime jets.

The scalar action density is -C_AB(q) grad(q_A).grad(q_B)/2 - V(q).
The returned E_A multiply delta(q_A) in its integrated first variation, after
integrating by parts with compact support and keeping the spacetime metric
fixed. X_AB represents the symmetric, possibly indefinite spacetime contraction
of two gradients; boxq_A represents the covariant spacetime d'Alembertian.

The old metric is differentiated from the literal conformal kinetic polynomial.
The second metric and potential are specified directly in psi coordinates.
The two Euler systems are differentiated separately, then compared using both
first- and second-derivative chain rules. Omega is strictly positive throughout.
M5c denotes M5 cubed, and Z denotes the coefficient on one bulk side.

This module performs no I/O, imports no generator, and issues no certificate.
It does not vary the metric, derive junction conditions, solve constraints,
or establish a full coupled Hessian, characteristics, stability or promotion.
"""
from __future__ import annotations

from collections.abc import Mapping

import sympy as sp


class BulkScalarError(ValueError):
    """An input is outside the declared symbolic scalar domain."""


def _symmetric_products(prefix: str, size: int) -> sp.Matrix:
    entries = {(i, j): sp.Symbol(f"{prefix}_{i}{j}", real=True)
               for i in range(size) for j in range(i, size)}
    return sp.Matrix(size, size, lambda i, j: entries[min(i, j), max(i, j)])


def symbols_context() -> dict:
    """Fresh independent fields, symmetric gradient products and box symbols."""
    omega = sp.Symbol("Omega", positive=True)
    phi = sp.symbols("phi1:4", real=True)
    psi = sp.symbols("psi1:4", real=True)
    parameters = dict(zip(("G", "Z", "M", "M5c", "k"),
                         sp.symbols("G Z M M5c k", positive=True)))
    return {
        "omega": omega, "phi": phi, "psi": psi, **parameters,
        "q_old": sp.Matrix([omega, *phi]),
        "q_new": sp.Matrix([omega, *psi]),
        "X_old": _symmetric_products("X", 4),
        "X_new": _symmetric_products("Y", 4),
        "box_old": sp.Matrix(sp.symbols("box_old0:4", real=True)),
        "box_new": sp.Matrix(sp.symbols("box_new0:4", real=True)),
        "velocities": sp.Matrix(sp.symbols("velocity0:4", real=True)),
        "s": sp.Symbol("s", nonnegative=True),
    }


def sigma_euler(metric: sp.MatrixBase, fields: sp.MatrixBase,
                gradient_products: sp.MatrixBase, boxes: sp.MatrixBase,
                potential: sp.Expr) -> sp.Matrix:
    """Differentiate a constant-spacetime sigma model in arbitrary field count.

    E_A = C_AB box(q_B)
        + (partial_C C_AB - partial_A C_BC/2) X_BC - partial_A V.
    Repeated indices range over every field; X_BC is symmetric. There is no
    positivity assumption on the spacetime contraction X and no EOM substitution.
    """
    if not isinstance(fields, sp.MatrixBase) or fields.cols != 1 or not fields.rows:
        raise BulkScalarError("fields must be a nonempty column matrix")
    count = fields.rows
    if (len(set(fields)) != count
            or any(not isinstance(field, sp.Symbol) for field in fields)):
        raise BulkScalarError("fields must be distinct independent symbols")
    if (not isinstance(metric, sp.MatrixBase) or metric.shape != (count, count)
            or metric != metric.T):
        raise BulkScalarError("metric must be a symmetric field matrix")
    if (not isinstance(gradient_products, sp.MatrixBase)
            or gradient_products.shape != (count, count)
            or gradient_products != gradient_products.T):
        raise BulkScalarError("gradient products must be a symmetric field matrix")
    if not isinstance(boxes, sp.MatrixBase) or boxes.shape != (count, 1):
        raise BulkScalarError("boxes must be a field column matrix")
    if isinstance(potential, int) and not isinstance(potential, bool):
        potential = sp.Integer(potential)
    if not isinstance(potential, sp.Expr):
        raise BulkScalarError("potential must be a scalar symbolic expression")
    for expression in (*metric, *gradient_products, *boxes, potential):
        if expression.has(sp.nan, sp.oo, -sp.oo, sp.zoo):
            raise BulkScalarError("non-finite scalar input")
    result = []
    for a in range(count):
        kinetic = sum(metric[a, b] * boxes[b] for b in range(count))
        connection = sum(
            (sp.diff(metric[a, b], fields[c])
             - sp.diff(metric[b, c], fields[a]) / 2) * gradient_products[b, c]
            for b in range(count) for c in range(count))
        result.append(sp.factor_terms(kinetic + connection - sp.diff(potential, fields[a])))
    return sp.Matrix(result)


def _simplified(matrix: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(matrix).applyfunc(sp.simplify)


def _potential_residual(expression: sp.Expr, radicand: sp.Expr) -> sp.Expr:
    """Normalize an exact first-potential-derivative residual without a root GCD.

    Here radicand = 1 + s_old**2 is strictly positive. First derivatives of
    F have at most radicand**(3/2) in the denominator. Clear that nonzero
    denominator, distribute products only, cancel rational coefficients, then
    restore it. No Taylor series, approximate evaluation or root identity is
    assumed beyond this positive real branch.
    """
    denominator = radicand**sp.Rational(3, 2)
    scaled = sp.expand_mul(sp.expand_mul(expression) * denominator)
    return sp.cancel(scaled) / denominator


def derive_model(context: Mapping | None = None) -> dict:
    """Derive and compare both complete four-field scalar bulk Euler systems."""
    ctx = symbols_context() if context is None else dict(context)
    required = set(symbols_context())
    if required - ctx.keys():
        raise BulkScalarError("incomplete scalar context")
    o = ctx["omega"]
    if not isinstance(o, sp.Symbol) or o.is_positive is not True:
        raise BulkScalarError("Omega must be a strictly positive symbol")
    phi, psi = tuple(ctx["phi"]), tuple(ctx["psi"])
    old, new = ctx["q_old"], ctx["q_new"]
    if (len(phi) != 3 or len(psi) != 3 or len(set((o, *phi, *psi))) != 7
            or old != sp.Matrix([o, *phi]) or new != sp.Matrix([o, *psi])):
        raise BulkScalarError("independent scalar triplets and their declared order are required")
    G, Z, mass, M5c, k = (ctx[name] for name in ("G", "Z", "M", "M5c", "k"))
    X, Y = ctx["X_old"], ctx["X_new"]
    boxes, new_boxes = ctx["box_old"], ctx["box_new"]
    velocity, s = ctx["velocities"], ctx["s"]

    # Route one: recover C from the literal P kinetic polynomial, not its entries.
    P = sp.Matrix([velocity[a + 1] + 3 * phi[a] * velocity[0] / (2 * o)
                   for a in range(3)])
    kinetic_norm = G * velocity[0]**2 + Z * P.dot(P)
    C_old = _simplified(sp.hessian(kinetic_norm, velocity) / 2)
    # Route two: an independent diagonal sigma metric in new field coordinates.
    C_new = sp.diag(G, *(Z / o**3 for _ in range(3)))
    transform = sp.Matrix([o, *(o**sp.Rational(3, 2) * field for field in phi)])
    jacobian = transform.jacobian(old)
    field_substitutions = dict(zip(new, transform))
    metric_pullback_residual = _simplified(C_old - jacobian.T * C_new * jacobian)

    W = 3 * M5c * k * sp.exp(-G * o**2 / (6 * M5c))
    U = sp.diff(W, o)**2 / (2 * G) - 2 * W**2 / (3 * M5c)
    F = s**2 / (2 * sp.sqrt(1 + s**2))
    Fprime = sp.diff(F, s)
    phi_squared = sum(field**2 for field in phi)
    s_old = o**3 * phi_squared
    s_new = sum(field**2 for field in psi)
    V_old = U + Z * mass**2 * o**-5 * F.subs(s, s_old)
    V_new = U + Z * mass**2 * o**-5 * F.subs(s, s_new)
    # Normalize only the proven norm identity before inserting transformed fields.
    # This preserves the exact radical argument and avoids expanding its powers.
    norm_pullback_residual = sp.expand(s_new.xreplace(field_substitutions) - s_old)
    potential_substitutions = {s_new: s_old, **field_substitutions}
    potential_pullback_residual = sp.expand(V_old - V_new.xreplace(potential_substitutions))
    E_kinetic_old = sigma_euler(C_old, old, X, boxes, sp.S.Zero)
    E_kinetic_new = sigma_euler(C_new, new, Y, new_boxes, sp.S.Zero)
    gradient_old = sp.Matrix([sp.diff(V_old, field) for field in old])
    gradient_new = sp.Matrix([sp.diff(V_new, field) for field in new])
    E_old = E_kinetic_old - gradient_old
    E_new = E_kinetic_new - gradient_new

    # Both derivative orders are essential off shell. No field equations enter.
    X_new_pulled = _simplified(jacobian * X * jacobian.T)
    transform_hessians = tuple(sp.hessian(field, old) for field in transform)
    box_chain_correction = sp.Matrix([
        sum(hessian[b, c] * X[b, c] for b in range(4) for c in range(4))
        for hessian in transform_hessians])
    box_new_pulled = _simplified(jacobian * boxes + box_chain_correction)
    substitutions = dict(potential_substitutions)
    substitutions.update({Y[b, c]: X_new_pulled[b, c]
                          for b in range(4) for c in range(b, 4)})
    substitutions.update(dict(zip(new_boxes, box_new_pulled)))
    E_new_substituted = E_new.xreplace(substitutions)
    kinetic_pulled = (jacobian.T * E_kinetic_new.xreplace(substitutions)).applyfunc(sp.cancel)
    gradient_pulled = (jacobian.T * gradient_new.xreplace(potential_substitutions)).applyfunc(sp.factor_terms)
    E_new_pulled = kinetic_pulled - gradient_pulled
    # Do not run a global simplify across rational jets, exponentials and radicals.
    # The kinetic identity is rational; the exact potential chain cancels after
    # distribution, with the independently checked norm identity used above.
    kinetic_covariance_residual = (E_kinetic_old - kinetic_pulled).applyfunc(sp.cancel)
    potential_gradient_covariance_residual = (gradient_old - gradient_pulled).applyfunc(
        lambda value: _potential_residual(value, 1 + s_old**2))
    covariance_residual = kinetic_covariance_residual - potential_gradient_covariance_residual

    # Explicit formulas are written separately from both automatic routes.
    Fprime_old = Fprime.subs(s, s_old)
    expected_phi = sp.Matrix([
        Z * (boxes[a + 1] + 3 * phi[a] * boxes[0] / (2 * o)
             - 15 * phi[a] * X[0, 0] / (4 * o**2))
        - 2 * Z * mass**2 * o**-2 * phi[a] * Fprime_old
        for a in range(3)])
    expected_omega = (
        (G + 9 * Z * phi_squared / (4 * o**2)) * boxes[0]
        + 3 * Z * sum(phi[a] * boxes[a + 1] for a in range(3)) / (2 * o)
        - 9 * Z * phi_squared * X[0, 0] / (4 * o**3)
        + 9 * Z * sum(phi[a] * X[0, a + 1] for a in range(3)) / (2 * o**2)
        + 3 * Z * sum(X[a + 1, a + 1] for a in range(3)) / (2 * o)
        - sp.diff(U, o) + 5 * Z * mass**2 * o**-6 * F.subs(s, s_old)
        - 3 * Z * mass**2 * o**-3 * phi_squared * Fprime_old)
    phi_reference_residual = (E_old[1:, :] - expected_phi).applyfunc(
        lambda value: _potential_residual(value, 1 + s_old**2))
    omega_reference_residual = _potential_residual(E_old[0] - expected_omega, 1 + s_old**2)
    phi_mixed_gradient_residual = sp.Matrix(3, 3, lambda a, b:
        sp.simplify(sp.diff(E_old[a + 1], X[0, b + 1])))
    checks = {
        "literal_kinetic_metric_matches_diagonal_pullback": metric_pullback_residual == sp.zeros(4),
        "material_norm_coordinate_invariant": norm_pullback_residual == 0,
        "full_potential_coordinate_invariant": potential_pullback_residual == 0,
        "kinetic_euler_equations_covariant_off_shell": kinetic_covariance_residual == sp.zeros(4, 1),
        "potential_gradient_covariant_off_shell": potential_gradient_covariance_residual == sp.zeros(4, 1),
        "all_four_euler_equations_covariant_off_shell": covariance_residual == sp.zeros(4, 1),
        "phi_equations_match_explicit_reference": phi_reference_residual == sp.zeros(3, 1),
        "omega_equation_matches_explicit_reference": omega_reference_residual == 0,
        "phi_equations_have_no_mixed_Omega_phi_gradient": phi_mixed_gradient_residual == sp.zeros(3),
    }
    return {
        "symbols": ctx, **ctx,
        "C_old": C_old, "C_new": C_new, "P": P,
        "old_kinetic_density": -kinetic_norm / 2,
        "W": W, "U": U, "F": F, "Fprime": Fprime,
        "s_old": s_old, "s_new": s_new, "V_old": V_old, "V_new": V_new,
        "transform": transform, "jacobian": jacobian,
        "field_substitutions": field_substitutions, "substitutions": substitutions,
        "potential_substitutions": potential_substitutions,
        "transform_hessians": transform_hessians,
        "X_new_pulled": X_new_pulled,
        "box_chain_correction": box_chain_correction,
        "box_new_pulled": box_new_pulled,
        "E_old": E_old, "E_new": E_new,
        "E_kinetic_old": E_kinetic_old, "E_kinetic_new": E_kinetic_new,
        "potential_gradient_old": gradient_old, "potential_gradient_new": gradient_new,
        "kinetic_pulled": kinetic_pulled, "potential_gradient_pulled": gradient_pulled,
        "kinetic_covariance_residual": kinetic_covariance_residual,
        "potential_gradient_covariance_residual": potential_gradient_covariance_residual,
        "norm_pullback_residual": norm_pullback_residual,
        "E_new_substituted": E_new_substituted, "E_new_pulled": E_new_pulled,
        "metric_pullback_residual": metric_pullback_residual,
        "potential_pullback_residual": potential_pullback_residual,
        "covariance_residual": covariance_residual,
        "expected_phi_equations": expected_phi,
        "expected_omega_equation": expected_omega,
        "phi_reference_residual": phi_reference_residual,
        "omega_reference_residual": omega_reference_residual,
        "phi_mixed_gradient_residual": phi_mixed_gradient_residual,
        "checks": checks,
    }
