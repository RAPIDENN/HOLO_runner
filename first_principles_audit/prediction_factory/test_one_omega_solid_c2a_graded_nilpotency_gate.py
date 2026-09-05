#!/usr/bin/env python3
"""Independent tests for the bounded solid C2a graded-nilpotency candidate."""

from __future__ import annotations

import ast
import copy
from contextlib import redirect_stdout
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import unittest

from . import derive_one_omega_solid_c2a_graded_nilpotency_gate as gate


# TEST-LOCAL ENGINE.  This deliberately does not call gate.Polynomial,
# gate.SparseSuperAlgebra, gate.CandidateModel, or gate.serialize_polynomial.
# Odd normal forms are integer bitmasks, unlike the producer's ordered tuples.


def _mis(dimension: int, maximum: int = 2) -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []

    def visit(prefix: tuple[int, ...], remaining_dimensions: int, budget: int) -> None:
        if remaining_dimensions == 0:
            rows.append(prefix)
            return
        for value in range(budget + 1):
            visit(prefix + (value,), remaining_dimensions - 1, budget - value)

    visit((), dimension, maximum)
    return sorted(rows, key=lambda row: (sum(row), row))


def _unit(dimension: int, axis: int) -> tuple[int, ...]:
    return tuple(1 if index == axis else 0 for index in range(dimension))


def _inc(index: tuple[int, ...], axis: int) -> tuple[int, ...]:
    result = tuple(value + (position == axis) for position, value in enumerate(index))
    if sum(result) > 2:
        raise OverflowError("test-local support exceeded order two; never truncate to zero")
    return result


def _lname(
    family: str,
    side: str = "shared",
    component: tuple[int | str, ...] = (),
    jet: tuple[int, ...] = (),
) -> str:
    component_text = ",".join(str(value) for value in component) or "_"
    return f"{family}[{side};{component_text}]@{'.'.join(str(x) for x in jet)}"


def _odd_name_universe() -> tuple[str, ...]:
    names: set[str] = set()
    for side in ("plus", "minus"):
        for component in range(5):
            for jet in _mis(5):
                names.add(_lname("c", side, (component,), jet))
                names.add(_lname("EvY_c", side, (component,), jet))
    for component in range(4):
        for jet in _mis(4):
            names.add(_lname("eta", "shared", (component,), jet))
    for order in range(3):
        names.add(_lname("kappa", "shared", (), (order,)))
        names.add(_lname("EvT_kappa", "shared", (), (order,)))
    return tuple(sorted(names))


@dataclass(frozen=True)
class _LSpec:
    name: str
    parity: int
    family: str
    side: str
    component: tuple[int | str, ...]
    jet: tuple[int, ...]


_LMonomial = tuple[tuple[tuple[str, int], ...], int]


class _BitPoly:
    __slots__ = ("alg", "terms")

    def __init__(
        self, alg: "_BitExterior", terms: dict[_LMonomial, Fraction] | None = None
    ) -> None:
        self.alg = alg
        self.terms = {key: value for key, value in (terms or {}).items() if value}

    @classmethod
    def q(cls, alg: "_BitExterior", value: int | Fraction) -> "_BitPoly":
        coefficient = Fraction(value)
        return cls(alg, {} if not coefficient else {((), 0): coefficient})

    def _p(self, other: int | Fraction | "_BitPoly") -> "_BitPoly":
        if isinstance(other, _BitPoly):
            if other.alg is not self.alg:
                raise AssertionError("foreign test-local algebra")
            return other
        return _BitPoly.q(self.alg, other)

    def __add__(self, other: int | Fraction | "_BitPoly") -> "_BitPoly":
        rhs = self._p(other)
        terms = dict(self.terms)
        for key, value in rhs.terms.items():
            terms[key] = terms.get(key, Fraction(0)) + value
            if not terms[key]:
                del terms[key]
        return _BitPoly(self.alg, terms)

    __radd__ = __add__

    def __neg__(self) -> "_BitPoly":
        return _BitPoly(self.alg, {key: -value for key, value in self.terms.items()})

    def __sub__(self, other: int | Fraction | "_BitPoly") -> "_BitPoly":
        return self + (-self._p(other))

    def __rsub__(self, other: int | Fraction | "_BitPoly") -> "_BitPoly":
        return self._p(other) - self

    def __mul__(self, other: int | Fraction | "_BitPoly") -> "_BitPoly":
        rhs = self._p(other)
        terms: dict[_LMonomial, Fraction] = {}
        for (left_even, left_mask), left_coefficient in self.terms.items():
            for (right_even, right_mask), right_coefficient in rhs.terms.items():
                if left_mask & right_mask:
                    continue
                inversions = 0
                bits = left_mask
                while bits:
                    lowest = bits & -bits
                    position = lowest.bit_length() - 1
                    inversions += (right_mask & ((1 << position) - 1)).bit_count()
                    bits ^= lowest
                even = dict(left_even)
                for name, power in right_even:
                    even[name] = even.get(name, 0) + power
                key = (tuple(sorted(even.items())), left_mask | right_mask)
                value = left_coefficient * right_coefficient
                if inversions % 2:
                    value = -value
                terms[key] = terms.get(key, Fraction(0)) + value
                if not terms[key]:
                    del terms[key]
        return _BitPoly(self.alg, terms)

    __rmul__ = __mul__

    @property
    def zero(self) -> bool:
        return not self.terms


class _BitExterior:
    def __init__(self) -> None:
        names = _odd_name_universe()
        self.odd_names = names
        self.odd_index = {name: index for index, name in enumerate(names)}
        self.specs: dict[str, _LSpec] = {}

    def gen(self, spec: _LSpec) -> _BitPoly:
        if spec.name in self.specs and self.specs[spec.name] != spec:
            raise AssertionError(f"metadata collision for {spec.name}")
        self.specs[spec.name] = spec
        if spec.parity:
            try:
                bit = 1 << self.odd_index[spec.name]
            except KeyError as exc:
                raise OverflowError(f"odd generator outside test support: {spec.name}") from exc
            return _BitPoly(self, {((), bit): Fraction(1)})
        return _BitPoly(self, {(((spec.name, 1),), 0): Fraction(1)})

    def odd_factors(self, mask: int) -> list[str]:
        return [
            name
            for index, name in enumerate(self.odd_names)
            if mask & (1 << index)
        ]

    def derive(
        self,
        polynomial: _BitPoly,
        on_generator: object,
        operator_parity: int,
    ) -> _BitPoly:
        result = _BitPoly.q(self, 0)
        for (even, mask), coefficient in polynomial.terms.items():
            factors: list[str] = []
            for name, power in even:
                factors.extend([name] * power)
            factors.extend(self.odd_factors(mask))
            for index, name in enumerate(factors):
                prefix = _BitPoly.q(self, coefficient)
                parity = 0
                for factor in factors[:index]:
                    prefix *= self.gen(self.specs[factor])
                    parity ^= self.specs[factor].parity
                varied = on_generator(self.specs[name])  # type: ignore[operator]
                suffix = _BitPoly.q(self, 1)
                for factor in factors[index + 1 :]:
                    suffix *= self.gen(self.specs[factor])
                result += (-1 if operator_parity * parity % 2 else 1) * prefix * varied * suffix
        return result


class _BitModel:
    """Independent bitmask realization of the nine pinned formula families."""

    def __init__(self) -> None:
        self.a = _BitExterior()
        self.cache: dict[str, _BitPoly] = {}

    def make(
        self,
        family: str,
        parity: int,
        side: str = "shared",
        component: tuple[int | str, ...] = (),
        jet: tuple[int, ...] = (),
    ) -> _BitPoly:
        name = _lname(family, side, component, jet)
        return self.a.gen(_LSpec(name, parity, family, side, component, jet))

    def c(self, side: str, component: int, jet: tuple[int, ...] = (0,) * 5) -> _BitPoly:
        return self.make("c", 1, side, (component,), jet)

    def scalar(
        self,
        side: str,
        species: str,
        component: int,
        jet: tuple[int, ...] = (0,) * 5,
    ) -> _BitPoly:
        return self.make("bulk_scalar", 0, side, (species, component), jet)

    def g(
        self,
        side: str,
        first: int,
        second: int,
        jet: tuple[int, ...] = (0,) * 5,
    ) -> _BitPoly:
        low, high = sorted((first, second))
        return self.make("g", 0, side, (low, high), jet)

    def eta(self, component: int, jet: tuple[int, ...] = (0,) * 4) -> _BitPoly:
        return self.make("eta", 1, "shared", (component,), jet)

    def X(self, component: int, jet: tuple[int, ...] = (0,) * 4) -> _BitPoly:
        return self.make("X", 0, "shared", (component,), jet)

    def Y(
        self, side: str, component: int, jet: tuple[int, ...] = (0,) * 4
    ) -> _BitPoly:
        return self.make("Y", 0, side, (component,), jet)

    def T(self, jet: tuple[int, ...] = (0,) * 4) -> _BitPoly:
        return self.make("T", 0, "shared", (), jet)

    def kappa(self, order: int = 0) -> _BitPoly:
        return self.make("kappa", 1, "shared", (), (order,))

    def C(
        self, side: str, component: int, jet: tuple[int, ...] = (0,) * 5
    ) -> _BitPoly:
        return self.make("EvY_c", 1, side, (component,), jet)

    def K(self, order: int = 0) -> _BitPoly:
        return self.make("EvT_kappa", 1, "shared", (), (order,))

    def D(self, polynomial: _BitPoly, axis: int) -> _BitPoly:
        def on(spec: _LSpec) -> _BitPoly:
            if spec.family not in {"c", "bulk_scalar", "g"}:
                raise AssertionError("foreign bulk derivative")
            return self.make(
                spec.family, spec.parity, spec.side, spec.component, _inc(spec.jet, axis)
            )

        return self.a.derive(polynomial, on, 0)

    def d(self, polynomial: _BitPoly, axis: int) -> _BitPoly:
        def on(spec: _LSpec) -> _BitPoly:
            if spec.family in {"eta", "X", "Y", "T"}:
                return self.make(
                    spec.family,
                    spec.parity,
                    spec.side,
                    spec.component,
                    _inc(spec.jet, axis),
                )
            if spec.family == "EvY_c":
                result = _BitPoly.q(self.a, 0)
                for ambient in range(5):
                    result += self.Y(spec.side, ambient, _unit(4, axis)) * self.C(
                        spec.side, int(spec.component[0]), _inc(spec.jet, ambient)
                    )
                return result
            if spec.family == "EvT_kappa":
                return self.T(_unit(4, axis)) * self.K(spec.jet[0] + 1)
            raise AssertionError("foreign worldvolume derivative")

        return self.a.derive(polynomial, on, 0)

    def dt(self, polynomial: _BitPoly) -> _BitPoly:
        def on(spec: _LSpec) -> _BitPoly:
            if spec.family != "kappa":
                raise AssertionError("foreign target derivative")
            return self.kappa(spec.jet[0] + 1)

        return self.a.derive(polynomial, on, 0)

    def prolong_bulk(self, polynomial: _BitPoly, jet: tuple[int, ...]) -> _BitPoly:
        result = polynomial
        for axis, count in enumerate(jet):
            for _ in range(count):
                result = self.D(result, axis)
        return result

    def prolong_sigma(self, polynomial: _BitPoly, jet: tuple[int, ...]) -> _BitPoly:
        result = polynomial
        for axis, count in enumerate(jet):
            for _ in range(count):
                result = self.d(result, axis)
        return result

    def prolong_target(self, polynomial: _BitPoly, order: int) -> _BitPoly:
        result = polynomial
        for _ in range(order):
            result = self.dt(result)
        return result

    def base_c(self, side: str, component: int) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for ambient in range(5):
            result -= self.c(side, ambient) * self.c(side, component, _unit(5, ambient))
        return result

    def base_scalar(self, side: str, species: str, component: int) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for ambient in range(5):
            result -= self.c(side, ambient) * self.scalar(
                side, species, component, _unit(5, ambient)
            )
        return result

    def base_g(self, side: str, first: int, second: int) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for ambient in range(5):
            result -= self.c(side, ambient) * self.g(
                side, first, second, _unit(5, ambient)
            )
            result -= self.c(side, ambient, _unit(5, first)) * self.g(
                side, ambient, second
            )
            result -= self.c(side, ambient, _unit(5, second)) * self.g(
                side, first, ambient
            )
        return result

    def base_eta(self, component: int) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for axis in range(4):
            result -= self.eta(axis) * self.eta(component, _unit(4, axis))
        return result

    def base_X(self, component: int) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for axis in range(4):
            result -= self.eta(axis) * self.X(component, _unit(4, axis))
        return result

    def base_Y(self, side: str, component: int) -> _BitPoly:
        result = self.C(side, component)
        for axis in range(4):
            result -= self.eta(axis) * self.Y(side, component, _unit(4, axis))
        return result

    def base_T(self) -> _BitPoly:
        result = self.K()
        for axis in range(4):
            result -= self.eta(axis) * self.T(_unit(4, axis))
        return result

    def base_kappa(self) -> _BitPoly:
        return -(self.kappa(0) * self.kappa(1))

    def substitute(self, polynomial: _BitPoly, replace: object) -> _BitPoly:
        result = _BitPoly.q(self.a, 0)
        for (even, mask), coefficient in polynomial.terms.items():
            term = _BitPoly.q(self.a, coefficient)
            for name, power in even:
                for _ in range(power):
                    term *= replace(self.a.specs[name])  # type: ignore[operator]
            for name in self.a.odd_factors(mask):
                term *= replace(self.a.specs[name])  # type: ignore[operator]
            result += term
        return result

    def sC(self, spec: _LSpec) -> _BitPoly:
        ambient = self.prolong_bulk(
            self.base_c(spec.side, int(spec.component[0])), spec.jet
        )

        def ev(item: _LSpec) -> _BitPoly:
            if item.family != "c" or item.side != spec.side:
                raise AssertionError("bad ambient evaluation")
            return self.C(item.side, int(item.component[0]), item.jet)

        result = self.substitute(ambient, ev)
        for index in range(5):
            # Independent executable check of the mandatory LEFT order.
            result += self.base_Y(spec.side, index) * self.C(
                spec.side, int(spec.component[0]), _inc(spec.jet, index)
            )
        return result

    def sK(self, spec: _LSpec) -> _BitPoly:
        target = self.prolong_target(self.base_kappa(), spec.jet[0])

        def ev(item: _LSpec) -> _BitPoly:
            if item.family != "kappa":
                raise AssertionError("bad target evaluation")
            return self.K(item.jet[0])

        return self.substitute(target, ev) + self.base_T() * self.K(spec.jet[0] + 1)

    def sgen(self, spec: _LSpec) -> _BitPoly:
        if spec.name in self.cache:
            return self.cache[spec.name]
        if spec.family == "c":
            result = self.prolong_bulk(
                self.base_c(spec.side, int(spec.component[0])), spec.jet
            )
        elif spec.family == "bulk_scalar":
            result = self.prolong_bulk(
                self.base_scalar(
                    spec.side, str(spec.component[0]), int(spec.component[1])
                ),
                spec.jet,
            )
        elif spec.family == "g":
            result = self.prolong_bulk(
                self.base_g(spec.side, int(spec.component[0]), int(spec.component[1])),
                spec.jet,
            )
        elif spec.family == "eta":
            result = self.prolong_sigma(self.base_eta(int(spec.component[0])), spec.jet)
        elif spec.family == "X":
            result = self.prolong_sigma(self.base_X(int(spec.component[0])), spec.jet)
        elif spec.family == "Y":
            result = self.prolong_sigma(
                self.base_Y(spec.side, int(spec.component[0])), spec.jet
            )
        elif spec.family == "T":
            result = self.prolong_sigma(self.base_T(), spec.jet)
        elif spec.family == "kappa":
            result = self.prolong_target(self.base_kappa(), spec.jet[0])
        elif spec.family == "EvY_c":
            result = self.sC(spec)
        elif spec.family == "EvT_kappa":
            result = self.sK(spec)
        else:
            raise AssertionError(f"unknown local family {spec.family}")
        self.cache[spec.name] = result
        return result

    def s(self, polynomial: _BitPoly) -> _BitPoly:
        return self.a.derive(polynomial, self.sgen, 1)


def _local_serialize(polynomial: _BitPoly) -> list[dict[str, object]]:
    unpacked: list[
        tuple[tuple[tuple[str, int], ...], tuple[str, ...], Fraction]
    ] = []
    for (even, mask), coefficient in polynomial.terms.items():
        unpacked.append((even, tuple(polynomial.alg.odd_factors(mask)), coefficient))
    rows: list[dict[str, object]] = []
    for even, odd, coefficient in sorted(unpacked, key=lambda row: (row[0], row[1])):
        rows.append(
            {
                "numerator": coefficient.numerator,
                "denominator": coefficient.denominator,
                "even": [[name, power] for name, power in even],
                "odd": list(odd),
            }
        )
    return rows


def _local_generators(model: _BitModel) -> list[tuple[str, _BitPoly]]:
    rows: list[tuple[str, _BitPoly]] = []
    for side in ("plus", "minus"):
        for component in range(5):
            rows.append((f"{side}.c[{component}]", model.c(side, component)))
        rows.append((f"{side}.Omega", model.scalar(side, "Omega", 0)))
        for component in range(3):
            rows.append((f"{side}.phi[{component}]", model.scalar(side, "phi", component)))
        for first in range(5):
            for second in range(first, 5):
                rows.append((f"{side}.g[{first},{second}]", model.g(side, first, second)))
    for component in range(4):
        rows.append((f"eta[{component}]", model.eta(component)))
    for component in range(3):
        rows.append((f"X[{component}]", model.X(component)))
    for side in ("plus", "minus"):
        for component in range(5):
            rows.append((f"{side}.Y[{component}]", model.Y(side, component)))
    rows.append(("T", model.T()))
    rows.append(("kappa", model.kappa()))
    for side in ("plus", "minus"):
        for component in range(5):
            rows.append((f"{side}.C[{component}]=EvY(c[{component}])", model.C(side, component)))
    rows.append(("K=EvT(kappa)", model.K()))
    return rows


class _CountingPath:
    def __init__(self, raw: object) -> None:
        self.raw = raw
        self.read_count = 0

    def read_bytes(self) -> object:
        self.read_count += 1
        return self.raw


class SolidC2AGradedNilpotencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_exact_dependency_byte_pins_and_no_inventory_execution(self) -> None:
        paths = (
            (gate.INVENTORY_SOURCE, gate.INVENTORY_SOURCE_SHA256),
            (gate.INVENTORY_TEST, gate.INVENTORY_TEST_SHA256),
            (gate.CHARTER_ARTIFACT, gate.CHARTER_ARTIFACT_SHA256),
        )
        for path, expected in paths:
            with self.subTest(path=path.name):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        self.assertFalse(
            self.report["pinned_inputs"]["inventory_source"]["imported_or_executed"]
        )
        self.assertFalse(
            self.report["pinned_inputs"]["inventory_test"]["imported_or_executed"]
        )

    def test_pinned_reader_exact_bytes_and_strict_json_types(self) -> None:
        path = _CountingPath(b"abc")
        self.assertEqual(gate._read_pinned_bytes(path, hashlib.sha256(b"abc").hexdigest(), "x"), b"abc")
        self.assertEqual(path.read_count, 1)
        wrong = _CountingPath(bytearray(b"abc"))
        with self.assertRaises(gate.SolidC2AGradedError):
            gate._read_pinned_bytes(wrong, hashlib.sha256(b"abc").hexdigest(), "x")
        self.assertEqual(wrong.read_count, 1)
        for raw in (
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'{"x":Infinity}',
            b'{"x":1e400}',
            b'[]',
        ):
            with self.subTest(raw=raw):
                with self.assertRaises(gate.SolidC2AGradedError):
                    gate._decode_strict_json(raw)

    def test_charter_semantics_reject_bool_int_alias_and_action_drift(self) -> None:
        charter = gate._decode_strict_json(gate.CHARTER_ARTIFACT.read_bytes())
        gate.validate_charter_semantics(charter)
        alias = copy.deepcopy(charter)
        alias["decision"]["C2_BRST_pass"] = 0
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_charter_semantics(alias)
        action = copy.deepcopy(charter)
        action["action_charter"]["route_id"] = "mutated"
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_charter_semantics(action)

    def test_literal_nine_formula_binding_and_digest(self) -> None:
        binding = self.report["candidate_rule_binding"]
        self.assertEqual(len(binding["inventory_formula_rows"]), 9)
        self.assertEqual(
            binding["inventory_formula_rows_sha256"],
            "93dd5a5775bde0ddf445fb88f9ba164bad05108c7302fec55c5360889241b155",
        )
        self.assertEqual(
            gate._canonical_json_digest(binding["inventory_formula_rows"]),
            binding["inventory_formula_rows_sha256"],
        )
        mutant = copy.deepcopy(self.report)
        mutant["candidate_rule_binding"]["inventory_formula_rows"][5]["candidate"] = "s X=0"
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_report(mutant)

    def test_independent_bitmask_engine_reconstructs_all_78_first_rules_and_squares(self) -> None:
        model = _BitModel()
        generators = _local_generators(model)
        self.assertEqual(len(generators), 78)
        producer = {
            row["label"]: row for row in self.report["exact_identities"]["rows"]
        }
        self.assertEqual(set(producer), {label for label, _ in generators})
        for label, generator in generators:
            with self.subTest(label=label):
                first = model.s(generator)
                self.assertEqual(_local_serialize(first), producer[label]["s_terms"])
                # This is a fresh bitmask calculation, not inspection of the
                # producer's serialized empty s2_terms.
                self.assertTrue(model.s(first).zero)

    def test_test_local_engine_has_real_exterior_degree_three(self) -> None:
        model = _BitModel()
        u = model.c("plus", 0)
        v = model.c("plus", 1)
        w = model.c("plus", 2)
        self.assertTrue((u * u).zero)
        self.assertTrue((u * v + v * u).zero)
        self.assertFalse((u * v * w).zero)
        monomial = next(iter((u * v * w).terms))
        self.assertEqual(monomial[1].bit_count(), 3)

    def test_evaluation_chains_are_raw_not_local_ghost_shortcuts(self) -> None:
        model = _BitModel()
        for side in ("plus", "minus"):
            for component in range(5):
                C = model.C(side, component)
                transport = model.s(C)
                for axis in range(4):
                    transport += model.eta(axis) * model.d(C, axis)
                self.assertTrue(transport.zero)
        K = model.K()
        transport_K = model.s(K)
        for axis in range(4):
            transport_K += model.eta(axis) * model.d(K, axis)
        self.assertTrue(transport_K.zero)
        serialized = json.dumps(self.report["exact_identities"], sort_keys=True)
        self.assertNotIn("local_C", serialized)
        self.assertNotIn("local_kappa", serialized)
        self.assertTrue(
            self.report["derived_evaluation_chain_identities"]
            ["raw_BRST_comes_only_from_evaluation_chain"]
        )

    def test_kappa_first_jet_is_exact_prolongation_not_a_primitive_zero(self) -> None:
        model = _BitModel()
        commutator = model.s(model.dt(model.kappa())) - model.dt(model.s(model.kappa()))
        self.assertTrue(commutator.zero)
        self.assertFalse(model.s(model.kappa(1)).zero)
        self.assertTrue(
            self.report["prolongation_commutators"]
            ["kappa_first_jet_is_derived_not_primitive"]
        )
        bad = {
            row["id"]: row for row in self.report["mutant_campaign"]["rows"]
        }["bad_target_prolongation"]
        self.assertEqual(bad["probe"], "[s,d_t]kappa")
        self.assertGreater(bad["term_count"], 0)

    def test_required_mutants_have_specific_nonzero_residues(self) -> None:
        rows = {row["id"]: row for row in self.report["mutant_campaign"]["rows"]}
        required = {
            "sc_zero",
            "sc_sign",
            "seta_zero",
            "seta_sign",
            "omit_c_evaluation",
            "evaluation_odd_order",
            "wrong_Y_sign",
            "skappa_sign",
            "skappa_zero",
            "omit_kappa_evaluation",
            "target_evaluation_odd_order",
            "local_kappa",
            "commuting_odd_algebra",
            "bad_target_prolongation",
        }
        self.assertTrue(required.issubset(rows))
        for identifier in required:
            with self.subTest(identifier=identifier):
                self.assertTrue(rows[identifier]["nonzero"])
                self.assertEqual(rows[identifier]["term_count"], len(rows[identifier]["residue_terms"]))
                self.assertGreater(rows[identifier]["term_count"], 0)

        def contains(identifier: str, numerator: int, odd: list[str]) -> bool:
            return any(
                term["numerator"] == numerator
                and term["denominator"] == 1
                and term["odd"] == odd
                for term in rows[identifier]["residue_terms"]
            )

        K0 = _lname("EvT_kappa", "shared", (), (0,))
        K1 = _lname("EvT_kappa", "shared", (), (1,))
        self.assertTrue(contains("skappa_sign", 2, [K0, K1]))
        self.assertTrue(contains("skappa_zero", 1, [K0, K1]))
        C0 = _lname("EvY_c", "plus", (0,), (0,) * 5)
        C1 = _lname("EvY_c", "plus", (0,), (1, 0, 0, 0, 0))
        self.assertTrue(contains("wrong_Y_sign", 2, [C0, C1]))
        self.assertTrue(
            any(abs(term["numerator"]) == 2 for term in rows["commuting_odd_algebra"]["residue_terms"])
        )

    def test_nilpotent_false_positives_are_rejected_by_binding_or_provenance(self) -> None:
        controls = {
            row["id"]: row
            for row in self.report["mutant_campaign"]
            ["nilpotent_false_positive_controls"]
        }
        self.assertEqual(
            set(controls),
            {
                "all_rules_zero",
                "coherent_global_s_negation",
                "coherent_global_s_rescale_by_2",
                "independent_local_C_covariant_transport",
                "independent_local_K_covariant_transport",
            },
        )
        for identifier, row in controls.items():
            with self.subTest(identifier=identifier):
                self.assertTrue(row["nilpotency_can_survive"])
                self.assertFalse(row["accepted"])
                self.assertNotEqual(
                    row["mutant_formula_rows_sha256"],
                    gate.INVENTORY_FORMULA_ROWS_SHA256,
                )

    def test_lazy_jet_factory_never_truncates_order_three_to_zero(self) -> None:
        model = gate.CandidateModel()
        jet2 = model.c("plus", 0, (2, 0, 0, 0, 0))
        jet3 = model.D_bulk(jet2, 0)
        self.assertFalse(jet3.is_zero)
        spec = model._only_spec(jet3)
        self.assertEqual(spec.jet, (3, 0, 0, 0, 0))
        with self.assertRaises(gate.SolidC2AGradedError):
            model.assert_certified_support(jet3, "test")
        self.assertTrue(self.report["algebra"]["certificate_support_is_not_a_truncation"])

    def test_symmetric_multiindices_and_homogeneous_parity_fail_closed(self) -> None:
        model = gate.CandidateModel()
        scalar = model.scalar("plus", "Omega", 0)
        self.assertTrue(
            (
                model.D_bulk(model.D_bulk(scalar, 0), 1)
                - model.D_bulk(model.D_bulk(scalar, 1), 0)
            ).is_zero
        )
        mixed = scalar + model.c("plus", 0)
        with self.assertRaises(gate.SolidC2AGradedError):
            mixed.require_homogeneous(0, "mixed")

    def test_z2_is_only_a_disjoint_label_automorphism(self) -> None:
        z2 = self.report["z2_label_automorphism"]
        self.assertTrue(z2["sJ_equals_Js"])
        self.assertTrue(z2["J_squared_equals_identity_on_labels"])
        self.assertFalse(z2["ghosts_identified"])
        self.assertFalse(z2["quotient_selected"])
        model = gate.CandidateModel()
        self.assertFalse((model.c("plus", 0) * model.c("minus", 0)).is_zero)

    def test_scope_is_candidate_only_and_every_downstream_claim_stays_false(self) -> None:
        self.assertTrue(
            self.report["decision"]["explicit_modeled_candidate_kinematic_nilpotency_pass"]
        )
        for key, value in self.report["decision"].items():
            if key != "explicit_modeled_candidate_kinematic_nilpotency_pass":
                self.assertIs(value, False, key)
        for key, value in self.report["proof_boundary"].items():
            self.assertIs(value, False, key)

    def test_report_validator_rejects_promotions_and_formula_tampering(self) -> None:
        promoted = copy.deepcopy(self.report)
        promoted["decision"]["C2_BRST_pass"] = True
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_report(promoted)
        proof = copy.deepcopy(self.report)
        proof["proof_boundary"]["gluing_tangency_proved"] = True
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_report(proof)
        formula = copy.deepcopy(self.report)
        formula["candidate_rule_binding"]["candidate_rules"]["solid_scalar"] = "s X=0"
        with self.assertRaises(gate.SolidC2AGradedError):
            gate.validate_report(formula)

    def test_report_validator_rejects_every_reproduced_top_level_overclaim(self) -> None:
        attacks: list[tuple[str, object]] = [
            ("classification", "experimentally_verified;P3_proved"),
            ("summary", "Full C2 and P3 proved"),
            ("pinned_inputs", {"invented": True}),
            ("algebra", {"bulk_side_ghost_identification_selected": True}),
            (
                "derived_evaluation_chain_identities",
                {
                    "count": 11,
                    "raw_BRST_comes_only_from_evaluation_chain": False,
                    "rows": [],
                },
            ),
        ]
        for key, replacement in attacks:
            mutant = copy.deepcopy(self.report)
            mutant[key] = replacement
            with self.subTest(key=key):
                with self.assertRaises(gate.SolidC2AGradedError):
                    gate.validate_report(mutant)

    def test_build_and_main_must_execute_the_strict_validator(self) -> None:
        original = gate.validate_report
        calls: list[dict[str, object]] = []

        def spy(report: dict[str, object]) -> None:
            calls.append(report)
            original(report)

        gate.validate_report = spy
        try:
            built = gate.build_report()
            self.assertEqual(len(calls), 1)
            self.assertIs(calls[0], built)
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(gate.main(), 0)
            self.assertEqual(len(calls), 2)
            self.assertEqual(json.loads(stream.getvalue()), calls[1])
        finally:
            gate.validate_report = original

    def test_source_has_no_sympy_inventory_import_or_write_primitive(self) -> None:
        source_path = Path(gate.__file__).resolve()
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        attributes: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Attribute):
                attributes.add(node.attr)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
        self.assertNotIn("sympy", imports)
        self.assertFalse(
            any("brst_algebra_inventory_gate" in module for module in imports)
        )
        self.assertTrue(
            imports.issubset(
                {
                    "__future__",
                    "dataclasses",
                    "fractions",
                    "hashlib",
                    "json",
                    "math",
                    "pathlib",
                    "typing",
                }
            )
        )
        self.assertTrue(
            {"write_text", "write_bytes", "touch", "mkdir"}.isdisjoint(attributes)
        )
        self.assertNotIn("open", calls)

    def test_main_prints_only_and_does_not_write_an_artifact(self) -> None:
        would_be_artifact = (
            gate.HERE / "artifacts" / "one_omega_solid_c2a_graded_nilpotency_gate.json"
        )
        self.assertFalse(hasattr(gate, "OUTPUT"))
        self.assertFalse(would_be_artifact.exists())
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.assertEqual(gate.main(), 0)
        printed = json.loads(stream.getvalue())
        gate.validate_report(printed)
        self.assertFalse(printed["artifact_written"])
        self.assertFalse(would_be_artifact.exists())


if __name__ == "__main__":
    unittest.main()
