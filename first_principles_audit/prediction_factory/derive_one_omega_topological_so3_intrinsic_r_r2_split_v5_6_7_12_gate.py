#!/usr/bin/env python3
"""Exact component split of the audited v5.6.7.8 intrinsic-curvature lemma.

This gate has one narrow purpose.  It separates

    xi*Rcal - B4_bar*Rcal^2/(16*k_infinity^2)

into its ``R`` and ``R_squared`` components in an internal sparse Laurent
polynomial ring, differentiates each component with respect to ``Rcal``, and
applies the already audited second-jet Euler--Green normal form component by
component.  Adding the tagged blocks reconstructs the byte-pinned v5.6.7.8
ADM normal form exactly and without cancellation between block supports.
Identity/source metadata is validated separately from semantic consumption.
Typed component-local slots are decoded without consulting golden rows, traced
before normalization, and only then folded through an explicit R-plus-R^2 sum.

The v5.6.7.8 object consumed here is already post-adjoint.  This module does
not claim to recover raw action-AST Frechet rows and deliberately exports no
``FrechetRowV1`` adapter.  It also proves nothing about K, a, Robin, shape,
the full twenty-component Green identity, C1, or N1.  No artifact is written.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SCHEMA = "holo.one-omega-topological-so3-intrinsic-r-r2-split-v5-6-7-12.v1"
BLOCK_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "post-adjoint-component-row-v1"
)
SLOT_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "component-local-scalar-slot-v1"
)
CURRENT_COEFFICIENT_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "component-local-current-coefficient-v1"
)
PROVENANCE_TRACE_SCHEMA = (
    "holo.one-omega-topological-so3-intrinsic-r-r2-"
    "pre-normalized-provenance-trace-v1"
)

V5678_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_moving_interface_variational_"
    "completion_v5_6_7_8_gate.py"
)
V5678_TEST = (
    HERE
    / "test_one_omega_topological_so3_moving_interface_variational_"
    "completion_v5_6_7_8_gate.py"
)
V5678_SHA256 = {
    V5678_SOURCE.name: "18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb",
    V5678_TEST.name: "9e8fab34d1e8d877a0e2ab799bec9ea26e40a05f8c63d4a333d0ea8d2664b0a0",
}
V5678_GIT_BLOBS = {
    V5678_SOURCE.name: "ae8c029b646569a67e2e1180a59b8cbd0afbcba5",
    V5678_TEST.name: "e44017431a2496f1bd333e08bab17e3eb3dba0bb",
}
V5678_AUDITED_COMMIT = "85585849fa65411a33330ce3822e03c77b067ad7"
V5678_SCHEMA = (
    "holo.one-omega-topological-so3-moving-interface-variational-"
    "completion-v5-6-7-8.v1"
)
V5678_TRUE_DECISION = "corrected_intrinsic_Rcal_interface_variation_exact_pass"
V5678_ADM_NORMAL_FORM_SHA256 = (
    "bf2ed2b9404287fc3ef059b3644413547d8c3b71776170c671fae1caaa790940"
)
V52_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
V52_FOLIATION_LITERAL = (
    "S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*["
    "Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
    "B4_bar*Rcal^2/(16*k_infinity^2)]"
)

EXPECTED_BLOCKS_SHA256 = (
    "fd25b86f601c517ce7648581e91b2275ea28535919bad12e36b7955ac3025eb3"
)
EXPECTED_COMPOSED_ADAPTER_SHA256 = V5678_ADM_NORMAL_FORM_SHA256

VARIABLES = ("xi", "B4_bar", "k_infinity", "Rcal")
XI, B4_BAR, K_INFINITY, RCAL = range(4)
COMPONENTS = ("R", "R_squared")
COMPONENT_ORDINALS = {name: ordinal for ordinal, name in enumerate(COMPONENTS)}
SOURCE_ID = "v5.2.S_fol_lower.intrinsic_Rcal"
SOURCE_SIDE = "lower"
SOURCE_DOMAIN = "Sigma"
CORRECT_GAUSS = {
    "projected_ambient_Riemann": 1,
    "K_trace_squared": -1,
    "K_tensor_squared": 1,
}

MUTATIONS = (
    "shared_oracle_swap",
    "wrong_R2_derivative_factor",
    "wrong_Gauss_sign",
    "mix_xi_B4_across_blocks",
    "omit_R2_weighted_current",
    "double_Cartan",
    "alias_k_to_itself",
    "wrong_literal_derivative_expression",
    "wrong_Gauss_formula",
    "wrong_weighted_current_terms",
    "wrong_Cartan_term",
    "wrong_component_label",
    "wrong_component_ordinal",
    "wrong_source_span",
    "wrong_side",
    "wrong_domain",
    "extra_public_field",
    "swap_aggregate_components_after_repin",
    "combined_swap_relabel_and_unconsumed_fields_after_repin",
)

TRUE_DECISION_KEYS = frozenset(
    {
        "literal_v5_2_R_R_squared_component_split_byte_bound_pass",
        "componentwise_R_R_squared_polynomial_derivative_exact_pass",
        "componentwise_R_R_squared_post_adjoint_Euler_Green_split_exact_pass",
        "R_R_squared_sum_reconstructs_v5_6_7_8_normal_form_pass",
        "R_R_squared_no_cross_cancellation_pass",
    }
)

FALSE_DECISION_KEYS = frozenset(
    {
        "raw_action_AST_Frechet_rows_recovered_pass",
        "FrechetRowV1_adapter_export_pass",
        "raw_Frechet_to_post_adjoint_bridge_pass",
        "K_a_Robin_componentwise_variation_pass",
        "all_twenty_components_componentwise_variation_pass",
        "moving_embedding_shape_equation_pass",
        "full_off_shell_Green_theorem_selected_sector_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "publication_authorized",
    }
)


class IntrinsicRR2SplitError(ValueError):
    """A dependency, polynomial, post-adjoint row, or scope invariant failed."""


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise IntrinsicRR2SplitError(f"cannot hash {path}: {exc}") from exc


def _git_blob_sha1(path: Path) -> str:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise IntrinsicRR2SplitError(f"cannot read {path}: {exc}") from exc
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 - Git object id


def _audited_commit_bindings(paths: Mapping[str, Path]) -> dict[str, Any]:
    """Resolve the pinned files inside the exact audited Git tree."""

    try:
        commit = subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "rev-parse",
                "--verify",
                f"{V5678_AUDITED_COMMIT}^{{commit}}",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        blobs = {
            name: subprocess.run(
                [
                    "git",
                    "-C",
                    str(REPO_ROOT),
                    "rev-parse",
                    f"{V5678_AUDITED_COMMIT}:{path.relative_to(REPO_ROOT)}",
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            for name, path in paths.items()
        }
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise IntrinsicRR2SplitError(f"cannot resolve audited v5.6.7.8 tree: {exc}") from exc
    if commit != V5678_AUDITED_COMMIT or blobs != V5678_GIT_BLOBS:
        raise IntrinsicRR2SplitError(
            f"audited v5.6.7.8 commit/tree drift: commit={commit}, blobs={blobs}"
        )
    return {"commit": commit, "file_blobs": blobs}


def _load_v5678_module():
    module_name = "_holo_pinned_v5678_for_v56712"
    spec = importlib.util.spec_from_file_location(module_name, V5678_SOURCE)
    if spec is None or spec.loader is None:
        raise IntrinsicRR2SplitError("cannot construct the v5.6.7.8 import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise IntrinsicRR2SplitError(f"cannot execute pinned v5.6.7.8: {exc}") from exc
    return module


def _dependency_certificate() -> dict[str, Any]:
    paths = {V5678_SOURCE.name: V5678_SOURCE, V5678_TEST.name: V5678_TEST}
    observed_sha256 = {name: _sha256(path) for name, path in paths.items()}
    observed_blobs = {name: _git_blob_sha1(path) for name, path in paths.items()}
    if observed_sha256 != V5678_SHA256:
        raise IntrinsicRR2SplitError(f"v5.6.7.8 SHA256 drift: {observed_sha256}")
    if observed_blobs != V5678_GIT_BLOBS:
        raise IntrinsicRR2SplitError(f"v5.6.7.8 Git-blob drift: {observed_blobs}")
    audited_tree = _audited_commit_bindings(paths)

    module = _load_v5678_module()
    report = module.build_report()
    try:
        normal_form = report["corrected_intrinsic_Rcal_variation"][
            "ADM_action_normal_forms"
        ]
        normal_form_hash = module._canonical_sha256(normal_form)
        source_pins = report["source_pins"]
        passed = bool(
            report["schema"] == V5678_SCHEMA
            and report["decision"][V5678_TRUE_DECISION] is True
            and normal_form_hash == V5678_ADM_NORMAL_FORM_SHA256
            and report["corrected_intrinsic_Rcal_variation"][
                "ADM_action_normal_forms_sha256"
            ]
            == V5678_ADM_NORMAL_FORM_SHA256
            and source_pins["v5_2_canonical_exact_action_sha256"]
            == V52_ACTION_SHA256
            and source_pins["v5_2_foliation_literal"] == V52_FOLIATION_LITERAL
        )
    except (KeyError, TypeError):
        passed = False
        normal_form = {}
        normal_form_hash = ""
    if not passed:
        raise IntrinsicRR2SplitError("v5.6.7.8 semantic dependency is not certified")
    return {
        "pass": True,
        "audited_commit": V5678_AUDITED_COMMIT,
        "audited_tree": audited_tree,
        "commit_binding": (
            "provenance plus exact source/test SHA256 and Git blob ids from the audited tree"
        ),
        "files": {
            name: {
                "path": str(paths[name]),
                "sha256": observed_sha256[name],
                "git_blob_sha1": observed_blobs[name],
            }
            for name in sorted(paths)
        },
        "schema": report["schema"],
        "accepted_microlemma_decision": V5678_TRUE_DECISION,
        "v5_2_exact_action_sha256": V52_ACTION_SHA256,
        "v5_2_foliation_literal": V52_FOLIATION_LITERAL,
        "v5_6_7_8_ADM_normal_form": normal_form,
        "v5_6_7_8_ADM_normal_form_sha256": normal_form_hash,
        "input_stage": "post_adjoint_ADM_Euler_Green_normal_form",
        "raw_Frechet_rows_present": False,
    }


Monomial = tuple[int, int, int, int]


def _monomial_sort_key(monomial: Monomial) -> tuple[int, int, int, int]:
    return (-monomial[XI], monomial[RCAL], -monomial[B4_BAR], monomial[K_INFINITY])


@dataclass(frozen=True)
class LaurentPolynomial:
    """Sparse Q[xi,B4_bar,k_infinity^+-1,Rcal] element."""

    terms: tuple[tuple[Monomial, Fraction], ...]

    @staticmethod
    def from_terms(rows: Iterable[tuple[Monomial, Fraction | int]]) -> "LaurentPolynomial":
        merged: dict[Monomial, Fraction] = {}
        for monomial, coefficient in rows:
            if len(monomial) != len(VARIABLES):
                raise IntrinsicRR2SplitError("Laurent monomial arity drift")
            value = coefficient if isinstance(coefficient, Fraction) else Fraction(coefficient)
            merged[monomial] = merged.get(monomial, Fraction(0)) + value
        normalized = tuple(
            (monomial, merged[monomial])
            for monomial in sorted(merged, key=_monomial_sort_key)
            if merged[monomial] != 0
        )
        return LaurentPolynomial(normalized)

    def __add__(self, other: "LaurentPolynomial") -> "LaurentPolynomial":
        return LaurentPolynomial.from_terms((*self.terms, *other.terms))

    def scaled(self, coefficient: Fraction | int) -> "LaurentPolynomial":
        value = coefficient if isinstance(coefficient, Fraction) else Fraction(coefficient)
        return LaurentPolynomial.from_terms(
            (monomial, value * term_coefficient)
            for monomial, term_coefficient in self.terms
        )

    def derivative_Rcal(self) -> "LaurentPolynomial":
        rows: list[tuple[Monomial, Fraction]] = []
        for monomial, coefficient in self.terms:
            power = monomial[RCAL]
            if power == 0:
                continue
            derived = list(monomial)
            derived[RCAL] -= 1
            rows.append((tuple(derived), coefficient * power))
        return LaurentPolynomial.from_terms(rows)

    def evaluate(self, values: Mapping[str, Fraction]) -> Fraction:
        if set(values) != set(VARIABLES):
            raise IntrinsicRR2SplitError("Laurent evaluation variable inventory drift")
        total = Fraction(0)
        for monomial, coefficient in self.terms:
            term = coefficient
            for variable, power in zip(VARIABLES, monomial, strict=True):
                term *= values[variable] ** power
            total += term
        return total

    def support(self) -> frozenset[Monomial]:
        return frozenset(monomial for monomial, _ in self.terms)


def _derive_intrinsic_components_from_pinned_literal_bytes(
    literal: str,
) -> dict[str, dict[str, Any]]:
    """Parse and differentiate the two intrinsic monomials from pinned bytes.

    This is the independent source-binding route.  Its byte pin, tokenizer,
    owner assignment, coefficient arithmetic, canonical power ordering, and
    exponent-rule derivative are all local to this function.  In particular,
    it does not consult the producer's expected-polynomial oracle, either row
    builder, the public decoder, or a golden snapshot.
    """

    pinned = (
        b"S_fol_lower=Mb^2/2*int_Sigma sqrt(-gamma)*["
        b"Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2+xi*Rcal+eta*a_mu*a^mu-"
        b"B4_bar*Rcal^2/(16*k_infinity^2)]"
    )
    try:
        source = literal.encode("ascii")
    except (AttributeError, UnicodeEncodeError) as exc:
        raise IntrinsicRR2SplitError(
            "independent intrinsic parser requires an ASCII action literal"
        ) from exc
    if source != pinned:
        raise IntrinsicRR2SplitError(
            "independent intrinsic parser byte pin does not match v5.2"
        )

    token = re.compile(
        rb"(?P<sign>[+-])"
        rb"(?P<numerator>[A-Za-z_][A-Za-z0-9_]*)\*Rcal"
        rb"(?:\^(?P<rcal_power>[1-9][0-9]*))?"
        rb"(?:/\((?P<integer>[1-9][0-9]*)\*"
        rb"(?P<denominator>[A-Za-z_][A-Za-z0-9_]*)\^"
        rb"(?P<denominator_power>[1-9][0-9]*)\))?"
    )
    matches = list(token.finditer(source))
    if len(matches) != 2:
        raise IntrinsicRR2SplitError(
            "independent intrinsic parser did not find exactly two Rcal monomials"
        )

    power_order = ("xi", "B4_bar", "k_infinity", "Rcal")
    derived: dict[str, dict[str, Any]] = {}
    for match in matches:
        sign = 1 if match.group("sign") == b"+" else -1
        numerator_symbol = match.group("numerator").decode("ascii")
        rcal_power = int(match.group("rcal_power") or b"1")
        integer = int(match.group("integer") or b"1")
        denominator_raw = match.group("denominator")
        denominator_symbol = (
            denominator_raw.decode("ascii") if denominator_raw is not None else None
        )
        denominator_power = int(match.group("denominator_power") or b"0")
        if (denominator_symbol is None) != (denominator_power == 0):
            raise IntrinsicRR2SplitError(
                "independent intrinsic parser denominator grammar drift"
            )
        owner = "R" if rcal_power == 1 else "R_squared" if rcal_power == 2 else ""
        if not owner or owner in derived:
            raise IntrinsicRR2SplitError(
                "independent intrinsic parser owner/power inventory drift"
            )

        action_coefficient = Fraction(sign, integer)
        action_powers = {numerator_symbol: 1, "Rcal": rcal_power}
        if denominator_symbol is not None:
            action_powers[denominator_symbol] = -denominator_power
        if not set(action_powers).issubset(power_order):
            raise IntrinsicRR2SplitError(
                "independent intrinsic parser symbol inventory drift"
            )

        derivative_coefficient = action_coefficient * rcal_power
        derivative_powers = dict(action_powers)
        derivative_powers["Rcal"] -= 1
        derivative_powers = {
            symbol: power for symbol, power in derivative_powers.items() if power
        }

        def canonical_row(
            coefficient: Fraction, powers: Mapping[str, int]
        ) -> list[dict[str, Any]]:
            return [
                {
                    "coefficient": [coefficient.numerator, coefficient.denominator],
                    "powers": [
                        [symbol, powers[symbol]]
                        for symbol in power_order
                        if powers.get(symbol, 0)
                    ],
                }
            ]

        def canonical_text(coefficient: Fraction, powers: Mapping[str, int]) -> str:
            magnitude = abs(coefficient)
            numerator = [] if magnitude.numerator == 1 else [str(magnitude.numerator)]
            denominator = (
                [] if magnitude.denominator == 1 else [str(magnitude.denominator)]
            )
            for symbol in power_order:
                power = powers.get(symbol, 0)
                if power == 0:
                    continue
                factor = symbol if abs(power) == 1 else f"{symbol}^{abs(power)}"
                (numerator if power > 0 else denominator).append(factor)
            if not numerator:
                numerator.append("1")
            rendered = "*".join(numerator)
            if denominator:
                rendered += "/(" + "*".join(denominator) + ")"
            return ("-" if coefficient < 0 else "") + rendered

        source_start = match.start() + (1 if sign > 0 else 0)
        source_end = match.end()
        source_text = source[source_start:source_end].decode("ascii")
        derived[owner] = {
            "schema": "holo.v5-2-independent-intrinsic-literal-monomial-v1",
            "owner": owner,
            "sign": sign,
            "coefficient": [
                action_coefficient.numerator,
                action_coefficient.denominator,
            ],
            "numerator_symbol": numerator_symbol,
            "denominator_integer": integer,
            "denominator_symbol": denominator_symbol,
            "denominator_power": denominator_power,
            "Rcal_power": rcal_power,
            "source_span": {
                "source_id": "v5.2.S_fol_lower.intrinsic_Rcal",
                "start": source_start,
                "end": source_end,
                "text": source_text,
            },
            "literal_expression": source_text,
            "action_polynomial": canonical_row(action_coefficient, action_powers),
            "derivative_polynomial": canonical_row(
                derivative_coefficient, derivative_powers
            ),
            "literal_derivative_expression": canonical_text(
                derivative_coefficient, derivative_powers
            ),
        }

    if tuple(derived) != ("R", "R_squared"):
        raise IntrinsicRR2SplitError(
            "independent intrinsic parser component order drift"
        )
    expected_shapes = {
        "R": (1, [1, 1], "xi", 1, None, 0),
        "R_squared": (-1, [-1, 16], "B4_bar", 2, "k_infinity", 2),
    }
    for owner, shape in expected_shapes.items():
        row = derived[owner]
        observed = (
            row["sign"],
            row["coefficient"],
            row["numerator_symbol"],
            row["Rcal_power"],
            row["denominator_symbol"],
            row["denominator_power"],
        )
        if observed != shape:
            raise IntrinsicRR2SplitError(
                f"independent intrinsic parser {owner} semantic shape drift"
            )
    return derived


def _poly_row(poly: LaurentPolynomial) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": [coefficient.numerator, coefficient.denominator],
            "powers": [
                [variable, power]
                for variable, power in zip(VARIABLES, monomial, strict=True)
                if power
            ],
        }
        for monomial, coefficient in poly.terms
    ]


def _poly_from_row(rows: Sequence[Mapping[str, Any]]) -> LaurentPolynomial:
    """Decode the public canonical row without trusting an internal polynomial."""

    decoded: list[tuple[Monomial, Fraction]] = []
    for row in rows:
        if set(row) != {"coefficient", "powers"}:
            raise IntrinsicRR2SplitError("canonical polynomial-row key drift")
        coefficient = row["coefficient"]
        if (
            not isinstance(coefficient, Sequence)
            or isinstance(coefficient, (str, bytes))
            or len(coefficient) != 2
        ):
            raise IntrinsicRR2SplitError("canonical coefficient is not a rational pair")
        numerator, denominator = coefficient
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise IntrinsicRR2SplitError("canonical coefficient is not integral")
        powers = [0] * len(VARIABLES)
        seen: set[str] = set()
        for power_row in row["powers"]:
            if (
                not isinstance(power_row, Sequence)
                or isinstance(power_row, (str, bytes))
                or len(power_row) != 2
            ):
                raise IntrinsicRR2SplitError("canonical power is not a pair")
            variable, power = power_row
            if variable not in VARIABLES or variable in seen or not isinstance(power, int):
                raise IntrinsicRR2SplitError("canonical power inventory drift")
            seen.add(variable)
            powers[VARIABLES.index(variable)] = power
        decoded.append((tuple(powers), Fraction(numerator, denominator)))
    polynomial = LaurentPolynomial.from_terms(decoded)
    if _poly_row(polynomial) != list(rows):
        raise IntrinsicRR2SplitError("polynomial row is not in canonical normal form")
    return polynomial


def _render_monomial(
    monomial: Monomial,
    coefficient: Fraction,
    aliases: Mapping[str, str],
) -> tuple[str, str]:
    sign = "-" if coefficient < 0 else "+"
    magnitude = abs(coefficient)
    numerator: list[str] = []
    denominator: list[str] = []
    if magnitude.numerator != 1:
        numerator.append(str(magnitude.numerator))
    if magnitude.denominator != 1:
        denominator.append(str(magnitude.denominator))
    for index in (XI, B4_BAR, RCAL, K_INFINITY):
        power = monomial[index]
        if not power:
            continue
        rendered = aliases[VARIABLES[index]]
        factor = rendered if abs(power) == 1 else f"{rendered}^{abs(power)}"
        (numerator if power > 0 else denominator).append(factor)
    if not numerator:
        numerator.append("1")
    body = "*".join(numerator)
    if denominator:
        body += "/(" + "*".join(denominator) + ")"
    return sign, body


def _render_polynomial(poly: LaurentPolynomial, aliases: Mapping[str, str]) -> str:
    pieces: list[str] = []
    for index, (monomial, coefficient) in enumerate(poly.terms):
        sign, body = _render_monomial(monomial, coefficient, aliases)
        if index == 0:
            pieces.append(body if sign == "+" else "-" + body)
        else:
            pieces.append(sign + body)
    return "".join(pieces) if pieces else "0"


def _literal_aliases() -> dict[str, str]:
    return {variable: variable for variable in VARIABLES}


def _v5678_aliases(mutation: str | None) -> dict[str, str]:
    return {
        "xi": "xi",
        "B4_bar": "B4",
        "k_infinity": "k_infinity" if mutation == "alias_k_to_itself" else "k",
        "Rcal": "Rcal",
    }


def _expected_component_polynomials() -> tuple[LaurentPolynomial, LaurentPolynomial]:
    r = LaurentPolynomial.from_terms([((1, 0, 0, 1), 1)])
    r2 = LaurentPolynomial.from_terms([((0, 1, -2, 2), Fraction(-1, 16))])
    return r, r2


def _parse_literal_split(literal: str) -> dict[str, str]:
    match = re.fullmatch(
        r"S_fol_lower=Mb\^2/2\*int_Sigma sqrt\(-gamma\)\*\["
        r"Kcal_mu_nu\*Kcal\^mu_nu-lambda_K\*Kcal\^2\+"
        r"(?P<R>xi\*Rcal)\+eta\*a_mu\*a\^mu"
        r"(?P<R2>-B4_bar\*Rcal\^2/\(16\*k_infinity\^2\))\]",
        literal,
    )
    if match is None:
        raise IntrinsicRR2SplitError("v5.2 foliation literal is outside the exact grammar")
    return {"R": match.group("R"), "R_squared": match.group("R2")}


def _literal_component_spans(literal: str) -> dict[str, dict[str, Any]]:
    """Bind each public component to its unique byte-exact literal occurrence."""

    parsed = _parse_literal_split(literal)
    spans: dict[str, dict[str, Any]] = {}
    for name in COMPONENTS:
        text = parsed[name]
        start = literal.find(text)
        if start < 0 or literal.find(text, start + 1) >= 0:
            raise IntrinsicRR2SplitError(
                f"{name} literal is absent or non-unique in the pinned action"
            )
        end = start + len(text)
        if literal[start:end] != text:
            raise IntrinsicRR2SplitError(f"{name} literal source-span drift")
        spans[name] = {
            "source_id": SOURCE_ID,
            "start": start,
            "end": end,
            "text": text,
        }
    return spans


def _gauss_formula(weights: Mapping[str, int]) -> str:
    if dict(weights) == CORRECT_GAUSS:
        return "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab"
    return "h^ac*h^bd*R_abcd+K^2-K_ab*K^ab"


def _component_slot_ref(kind: str, component: str) -> dict[str, str]:
    if kind not in {"component_action", "component_derivative"}:
        raise IntrinsicRR2SplitError(f"unknown component-local slot kind {kind}")
    if component not in COMPONENTS:
        raise IntrinsicRR2SplitError(f"unknown component-local slot owner {component}")
    return {"schema": SLOT_SCHEMA, "kind": kind, "component": component}


def _post_adjoint_operator_template(component: str) -> dict[str, Any]:
    """Linear operator skeleton copied from the byte-pinned .8 normal form.

    The scalar slots are supplied independently by each polynomial component.
    This is an adapter for a post-adjoint object, not a raw Frechet-row schema.
    """

    return {
        "Euler_coefficients_inside_N_sqrt_h": {
            "lapse_n": [
                {
                    "rational": [1, 1],
                    "scalar_slot": _component_slot_ref(
                        "component_action", component
                    ),
                    "tensor": "1",
                }
            ],
            "shift_v_i": [0, 0, 0],
            "spatial_metric_Q_ij": [
                {
                    "rational": [1, 2],
                    "scalar_slot": _component_slot_ref(
                        "component_action", component
                    ),
                    "tensor": "h^ij",
                },
                {
                    "rational": [-1, 1],
                    "scalar_slot": _component_slot_ref(
                        "component_derivative", component
                    ),
                    "tensor": "Rcal^ij",
                },
                {
                    "rational": [1, 1],
                    "scalar_slot": _component_slot_ref(
                        "component_derivative", component
                    ),
                    "operator": "N^-1*(D^iD^j-h^ij*D^2)(N*())",
                },
            ],
        },
        "weighted_IBP_current_terms": [
            {
                "rational": [1, 1],
                "scalar_slot": _component_slot_ref(
                    "component_derivative", component
                ),
                "operator": "N*()*D_j*Q^ij",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": _component_slot_ref(
                    "component_derivative", component
                ),
                "operator": "N*()*D^i*Q",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": _component_slot_ref(
                    "component_derivative", component
                ),
                "operator": "D_j(N*())*Q^ij",
            },
            {
                "rational": [1, 1],
                "scalar_slot": _component_slot_ref(
                    "component_derivative", component
                ),
                "operator": "D^i(N*())*Q",
            },
        ],
        "Cartan": {
            "operator": "+i_(N*tau*u)(l_())",
            "scalar_slot": _component_slot_ref("component_action", component),
        },
    }


def _density_context() -> dict[str, str]:
    return {
        "overall_constant": "Mb^2/2",
        "measure": "N*sqrt(h)",
    }


def _fixed_clock_adm_variations() -> dict[str, str]:
    return {
        "lapse": "n=delta_N/N=-H_prime_uu/2",
        "shift": "v_i=N*H_prime_ui",
        "spatial_metric": "Q_ij=H_prime_ij",
    }


def _adapter_aliases() -> dict[str, str]:
    return {
        "xi": "xi",
        "B4_bar": "B4",
        "k_infinity": "k",
        "Rcal": "Rcal",
    }


def _post_adjoint_block(
    name: str,
    action: LaurentPolynomial,
    derivative: LaurentPolynomial,
    gauss: Mapping[str, int],
    *,
    source_span: Mapping[str, Any],
    current_present: bool,
    cartan_occurrences: int,
) -> dict[str, Any]:
    template = _post_adjoint_operator_template(name)
    action_ref = _component_slot_ref("component_action", name)
    derivative_ref = _component_slot_ref("component_derivative", name)
    return {
        "schema": BLOCK_SCHEMA,
        "component": name,
        "component_ordinal": COMPONENT_ORDINALS[name],
        "side": SOURCE_SIDE,
        "domain": SOURCE_DOMAIN,
        "source_span": dict(source_span),
        "stage": "post_adjoint_component_normal_form",
        "density_context": _density_context(),
        "independent_fixed_clock_ADM_variations": _fixed_clock_adm_variations(),
        "adapter_aliases": _adapter_aliases(),
        "action_polynomial": _poly_row(action),
        "d_action_d_Rcal": _poly_row(derivative),
        "literal_expression": _render_polynomial(action, _literal_aliases()),
        "literal_derivative_expression": _render_polynomial(
            derivative, _literal_aliases()
        ),
        "scalar_slots": {
            "component_action": {
                "ref": copy.deepcopy(action_ref),
                "polynomial": _poly_row(action),
            },
            "component_derivative": {
                "ref": copy.deepcopy(derivative_ref),
                "with_respect_to": "Rcal",
                "polynomial": _poly_row(derivative),
            },
        },
        "Gauss": dict(gauss),
        "Gauss_formula": _gauss_formula(gauss),
        "Euler_coefficients_inside_N_sqrt_h": template[
            "Euler_coefficients_inside_N_sqrt_h"
        ],
        "weighted_IBP_current": {
            "present": current_present,
            "prefactor": "(Mb^2/2)*sqrt(h)",
            "coefficient": {
                "schema": CURRENT_COEFFICIENT_SCHEMA,
                "operator": "N_times",
                "scalar_slot": copy.deepcopy(derivative_ref),
            },
            "terms": (
                template["weighted_IBP_current_terms"] if current_present else []
            ),
        },
        "d4_Cartan_current": {
            "rendered_component_term": f"+i_(N*tau*u)(l_{name})",
            "operator": template["Cartan"],
            "occurrences": cartan_occurrences,
            "source_clock_gauge_vector": "chi=-N*tau*u",
            "gauge_variation_is_subtracted": True,
            "separate_material_transgression_appended": False,
        },
        "raw_Frechet_rows_exported": False,
    }


def _build_component_blocks(mutation: str | None) -> dict[str, Any]:
    r_action, r2_action = _expected_component_polynomials()
    source_spans = _literal_component_spans(V52_FOLIATION_LITERAL)
    if mutation == "shared_oracle_swap":
        r_action, r2_action = r2_action, r_action
    elif mutation == "mix_xi_B4_across_blocks":
        cancelling = LaurentPolynomial.from_terms([((0, 1, -2, 1), 1)])
        r_action = r_action + cancelling
        r2_action = r2_action + cancelling.scaled(-1)

    r_derivative = r_action.derivative_Rcal()
    r2_derivative = r2_action.derivative_Rcal()
    if mutation == "wrong_R2_derivative_factor":
        r2_derivative = LaurentPolynomial.from_terms(
            [((0, 1, -2, 1), Fraction(-1, 16))]
        )

    r_gauss = dict(CORRECT_GAUSS)
    r2_gauss = dict(CORRECT_GAUSS)
    if mutation == "wrong_Gauss_sign":
        r2_gauss.update({"K_trace_squared": 1, "K_tensor_squared": -1})

    r_block = _post_adjoint_block(
        "R",
        r_action,
        r_derivative,
        r_gauss,
        source_span=source_spans["R"],
        current_present=True,
        cartan_occurrences=1,
    )
    r2_block = _post_adjoint_block(
        "R_squared",
        r2_action,
        r2_derivative,
        r2_gauss,
        source_span=source_spans["R_squared"],
        current_present=mutation != "omit_R2_weighted_current",
        cartan_occurrences=2 if mutation == "double_Cartan" else 1,
    )
    blocks = {
        "R": {"polynomial": r_action, "derivative": r_derivative, "row": r_block},
        "R_squared": {
            "polynomial": r2_action,
            "derivative": r2_derivative,
            "row": r2_block,
        },
    }
    if mutation == "alias_k_to_itself":
        blocks["R_squared"]["row"]["adapter_aliases"]["k_infinity"] = (
            "k_infinity"
        )
    elif mutation == "wrong_literal_derivative_expression":
        blocks["R_squared"]["row"]["literal_derivative_expression"] += "+0"
    elif mutation == "wrong_Gauss_formula":
        blocks["R"]["row"]["Gauss_formula"] = (
            "h^ac*h^bd*R_abcd+K^2-K_ab*K^ab"
        )
    elif mutation == "wrong_weighted_current_terms":
        blocks["R_squared"]["row"]["weighted_IBP_current"]["terms"][0][
            "rational"
        ] = [2, 1]
    elif mutation == "wrong_Cartan_term":
        blocks["R"]["row"]["d4_Cartan_current"][
            "rendered_component_term"
        ] = (
            "+i_(N*tau*u)(l_R_squared)"
        )
    elif mutation == "wrong_component_label":
        blocks["R"]["row"]["component"] = "R_squared"
    elif mutation == "wrong_component_ordinal":
        blocks["R_squared"]["row"]["component_ordinal"] = 0
    elif mutation == "wrong_source_span":
        blocks["R"]["row"]["source_span"]["start"] += 1
    elif mutation == "wrong_side":
        blocks["R"]["row"]["side"] = "upper"
    elif mutation == "wrong_domain":
        blocks["R_squared"]["row"]["domain"] = "M4"
    elif mutation == "extra_public_field":
        blocks["R"]["row"]["untrusted"] = "ignored-before-fix"
    elif mutation == "swap_aggregate_components_after_repin":
        blocks["R"], blocks["R_squared"] = blocks["R_squared"], blocks["R"]
    elif mutation == "combined_swap_relabel_and_unconsumed_fields_after_repin":
        blocks["R"]["row"], blocks["R_squared"]["row"] = (
            blocks["R_squared"]["row"],
            blocks["R"]["row"],
        )
        for name in COMPONENTS:
            row = blocks[name]["row"]
            row["component"] = name
            row["component_ordinal"] = COMPONENT_ORDINALS[name]
            row["side"] = SOURCE_SIDE
            row["domain"] = SOURCE_DOMAIN
            row["source_span"] = dict(source_spans[name])
            row["literal_derivative_expression"] = "forged-derivative"
            row["Gauss_formula"] = "forged-Gauss"
            row["weighted_IBP_current"]["terms"] = [
                {
                    "rational": [99, 1],
                    "scalar_slot": {
                        "schema": SLOT_SCHEMA,
                        "kind": "total_derivative",
                        "component": name,
                    },
                    "operator": "forged-current",
                }
            ]
            row["d4_Cartan_current"]["rendered_component_term"] = (
                "+forged-Cartan"
            )
    elif mutation == "shared_oracle_swap":
        for name in COMPONENTS:
            blocks[name]["row"]["literal_expression"] = source_spans[name]["text"]
    return blocks


def _public_blocks(blocks: Mapping[str, Any]) -> dict[str, Any]:
    return {name: blocks[name]["row"] for name in COMPONENTS}


def _no_cross_cancellation_certificate(blocks: Mapping[str, Any]) -> dict[str, Any]:
    action_supports = {
        name: blocks[name]["polynomial"].support() for name in blocks
    }
    derivative_supports = {
        name: blocks[name]["derivative"].support() for name in blocks
    }
    action_overlap = action_supports["R"] & action_supports["R_squared"]
    derivative_overlap = derivative_supports["R"] & derivative_supports["R_squared"]
    tagged_action_count = sum(len(value) for value in action_supports.values())
    tagged_derivative_count = sum(len(value) for value in derivative_supports.values())
    total_action = blocks["R"]["polynomial"] + blocks["R_squared"]["polynomial"]
    total_derivative = blocks["R"]["derivative"] + blocks["R_squared"]["derivative"]
    passed = bool(
        not action_overlap
        and not derivative_overlap
        and len(total_action.support()) == tagged_action_count
        and len(total_derivative.support()) == tagged_derivative_count
    )
    return {
        "pass": passed,
        "criterion": "disjoint tagged monomial supports before normalization",
        "action_supports": {
            name: [_poly_row(LaurentPolynomial.from_terms([(monomial, 1)]))[0] for monomial in sorted(support, key=_monomial_sort_key)]
            for name, support in action_supports.items()
        },
        "derivative_supports": {
            name: [_poly_row(LaurentPolynomial.from_terms([(monomial, 1)]))[0] for monomial in sorted(support, key=_monomial_sort_key)]
            for name, support in derivative_supports.items()
        },
        "action_overlap": len(action_overlap),
        "derivative_overlap": len(derivative_overlap),
        "normalization_dropped_tagged_action_terms": (
            tagged_action_count - len(total_action.support())
        ),
        "normalization_dropped_tagged_derivative_terms": (
            tagged_derivative_count - len(total_derivative.support())
        ),
    }


def _independent_expected_public_blocks(
    dependency: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the expected public rows without calling the row exporter.

    This is deliberately a second construction.  In particular it never calls
    ``_post_adjoint_block`` or ``_build_component_blocks``; re-pinning an
    exported-block hash therefore cannot bless relabelled or forged rows.
    """

    literal = str(dependency["v5_2_foliation_literal"])
    parsed = _parse_literal_split(literal)
    spans = {
        "R": {
            "source_id": "v5.2.S_fol_lower.intrinsic_Rcal",
            "start": 81,
            "end": 88,
            "text": "xi*Rcal",
        },
        "R_squared": {
            "source_id": "v5.2.S_fol_lower.intrinsic_Rcal",
            "start": 102,
            "end": 134,
            "text": "-B4_bar*Rcal^2/(16*k_infinity^2)",
        },
    }
    if any(
        literal[row["start"] : row["end"]] != row["text"]
        or parsed[name] != row["text"]
        for name, row in spans.items()
    ):
        raise IntrinsicRR2SplitError("independent expected source-span binding drift")
    action_rows = {
        "R": [
            {
                "coefficient": [1, 1],
                "powers": [["xi", 1], ["Rcal", 1]],
            }
        ],
        "R_squared": [
            {
                "coefficient": [-1, 16],
                "powers": [
                    ["B4_bar", 1],
                    ["k_infinity", -2],
                    ["Rcal", 2],
                ],
            }
        ],
    }
    derivative_rows = {
        "R": [{"coefficient": [1, 1], "powers": [["xi", 1]]}],
        "R_squared": [
            {
                "coefficient": [-1, 8],
                "powers": [
                    ["B4_bar", 1],
                    ["k_infinity", -2],
                    ["Rcal", 1],
                ],
            }
        ],
    }
    literal_derivatives = {
        "R": "xi",
        "R_squared": "-B4_bar*Rcal/(8*k_infinity^2)",
    }
    expected: dict[str, Any] = {}
    for name in COMPONENTS:
        action_ref = {
            "schema": SLOT_SCHEMA,
            "kind": "component_action",
            "component": name,
        }
        derivative_ref = {
            "schema": SLOT_SCHEMA,
            "kind": "component_derivative",
            "component": name,
        }
        euler_template = {
            "lapse_n": [
                {
                    "rational": [1, 1],
                    "scalar_slot": copy.deepcopy(action_ref),
                    "tensor": "1",
                }
            ],
            "shift_v_i": [0, 0, 0],
            "spatial_metric_Q_ij": [
                {
                    "rational": [1, 2],
                    "scalar_slot": copy.deepcopy(action_ref),
                    "tensor": "h^ij",
                },
                {
                    "rational": [-1, 1],
                    "scalar_slot": copy.deepcopy(derivative_ref),
                    "tensor": "Rcal^ij",
                },
                {
                    "rational": [1, 1],
                    "scalar_slot": copy.deepcopy(derivative_ref),
                    "operator": "N^-1*(D^iD^j-h^ij*D^2)(N*())",
                },
            ],
        }
        current_terms = [
            {
                "rational": [1, 1],
                "scalar_slot": copy.deepcopy(derivative_ref),
                "operator": "N*()*D_j*Q^ij",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": copy.deepcopy(derivative_ref),
                "operator": "N*()*D^i*Q",
            },
            {
                "rational": [-1, 1],
                "scalar_slot": copy.deepcopy(derivative_ref),
                "operator": "D_j(N*())*Q^ij",
            },
            {
                "rational": [1, 1],
                "scalar_slot": copy.deepcopy(derivative_ref),
                "operator": "D^i(N*())*Q",
            },
        ]
        cartan_operator = {
            "operator": "+i_(N*tau*u)(l_())",
            "scalar_slot": copy.deepcopy(action_ref),
        }
        expected[name] = {
            "schema": BLOCK_SCHEMA,
            "component": name,
            "component_ordinal": COMPONENT_ORDINALS[name],
            "side": SOURCE_SIDE,
            "domain": SOURCE_DOMAIN,
            "source_span": spans[name],
            "stage": "post_adjoint_component_normal_form",
            "density_context": {
                "overall_constant": "Mb^2/2",
                "measure": "N*sqrt(h)",
            },
            "independent_fixed_clock_ADM_variations": {
                "lapse": "n=delta_N/N=-H_prime_uu/2",
                "shift": "v_i=N*H_prime_ui",
                "spatial_metric": "Q_ij=H_prime_ij",
            },
            "adapter_aliases": {
                "xi": "xi",
                "B4_bar": "B4",
                "k_infinity": "k",
                "Rcal": "Rcal",
            },
            "action_polynomial": copy.deepcopy(action_rows[name]),
            "d_action_d_Rcal": copy.deepcopy(derivative_rows[name]),
            "literal_expression": parsed[name],
            "literal_derivative_expression": literal_derivatives[name],
            "scalar_slots": {
                "component_action": {
                    "ref": copy.deepcopy(action_ref),
                    "polynomial": copy.deepcopy(action_rows[name]),
                },
                "component_derivative": {
                    "ref": copy.deepcopy(derivative_ref),
                    "with_respect_to": "Rcal",
                    "polynomial": copy.deepcopy(derivative_rows[name]),
                },
            },
            "Gauss": {
                "projected_ambient_Riemann": 1,
                "K_trace_squared": -1,
                "K_tensor_squared": 1,
            },
            "Gauss_formula": "h^ac*h^bd*R_abcd-K^2+K_ab*K^ab",
            "Euler_coefficients_inside_N_sqrt_h": copy.deepcopy(euler_template),
            "weighted_IBP_current": {
                "present": True,
                "prefactor": "(Mb^2/2)*sqrt(h)",
                "coefficient": {
                    "schema": CURRENT_COEFFICIENT_SCHEMA,
                    "operator": "N_times",
                    "scalar_slot": copy.deepcopy(derivative_ref),
                },
                "terms": current_terms,
            },
            "d4_Cartan_current": {
                "rendered_component_term": f"+i_(N*tau*u)(l_{name})",
                "operator": copy.deepcopy(cartan_operator),
                "occurrences": 1,
                "source_clock_gauge_vector": "chi=-N*tau*u",
                "gauge_variation_is_subtracted": True,
                "separate_material_transgression_appended": False,
            },
            "raw_Frechet_rows_exported": False,
        }
    return expected


def _strict_equal(observed: Any, expected: Any) -> bool:
    """JSON-shaped equality which does not identify booleans with integers."""

    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return (
            list(observed) == list(expected)
            and all(
                key in observed and _strict_equal(observed[key], expected[key])
                for key in expected
            )
        )
    if isinstance(expected, list):
        return len(observed) == len(expected) and all(
            _strict_equal(left, right)
            for left, right in zip(observed, expected, strict=True)
        )
    return bool(observed == expected)


def _public_block_schema_certificate(
    public_blocks: Mapping[str, Any],
    dependency: Mapping[str, Any],
) -> dict[str, Any]:
    expected = _independent_expected_public_blocks(dependency)
    top_level_exact = type(public_blocks) is dict and tuple(public_blocks) == COMPONENTS
    checks: dict[str, bool] = {"top_level_component_inventory_and_order_exact": top_level_exact}
    groups = {
        "identity": (
            "schema",
            "component",
            "component_ordinal",
            "side",
            "domain",
            "stage",
        ),
        "source": ("source_span", "literal_expression"),
        "polynomial": (
            "action_polynomial",
            "d_action_d_Rcal",
            "literal_derivative_expression",
            "scalar_slots",
        ),
        "adapter_context": (
            "density_context",
            "independent_fixed_clock_ADM_variations",
            "adapter_aliases",
        ),
        "Gauss": ("Gauss", "Gauss_formula"),
        "Euler": ("Euler_coefficients_inside_N_sqrt_h",),
        "weighted_current": ("weighted_IBP_current",),
        "Cartan": ("d4_Cartan_current",),
        "scope": ("raw_Frechet_rows_exported",),
    }
    for name in COMPONENTS:
        row = public_blocks.get(name) if isinstance(public_blocks, Mapping) else None
        wanted = expected[name]
        checks[f"{name}_strict_key_inventory"] = bool(
            type(row) is dict and list(row) == list(wanted)
        )
        for group, keys in groups.items():
            checks[f"{name}_{group}_exact"] = bool(
                isinstance(row, Mapping)
                and all(
                    key in row and _strict_equal(row[key], wanted[key])
                    for key in keys
                )
            )
        checks[f"{name}_whole_row_exact"] = bool(
            isinstance(row, dict) and _strict_equal(row, wanted)
        )
    checks["all"] = all(checks.values())
    return {
        "schema": BLOCK_SCHEMA,
        "component_order": list(COMPONENTS),
        "checks": checks,
        "pass": checks["all"],
        "expected_rows_sha256": _canonical_sha256(expected),
        "observed_rows_sha256": _canonical_sha256(public_blocks),
    }


def _public_leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    paths: list[tuple[Any, ...]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            paths.extend(_public_leaf_paths(item, (*prefix, key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(_public_leaf_paths(item, (*prefix, index)))
    else:
        paths.append(prefix)
    return paths


def _path_label(path: Sequence[Any]) -> str:
    return ".".join(str(part) for part in path)


def _require_exact_keys(value: Any, keys: Sequence[str], label: str) -> None:
    if type(value) is not dict or tuple(value) != tuple(keys):
        raise IntrinsicRR2SplitError(f"{label} key inventory drift")


def _decode_rational(value: Any, label: str) -> tuple[int, int]:
    if (
        type(value) is not list
        or len(value) != 2
        or type(value[0]) is not int
        or type(value[1]) is not int
        or value[1] == 0
    ):
        raise IntrinsicRR2SplitError(f"{label} is not an exact rational pair")
    return value[0], value[1]


def _validate_component_slot_ref(
    value: Any,
    component: str,
    expected_kind: str,
    label: str,
) -> dict[str, str]:
    _require_exact_keys(value, ("schema", "kind", "component"), label)
    if (
        value["schema"] != SLOT_SCHEMA
        or value["kind"] != expected_kind
        or value["component"] != component
    ):
        raise IntrinsicRR2SplitError(
            f"{label} is not a {component}-local {expected_kind} slot"
        )
    return copy.deepcopy(value)


def _decode_operator_term(
    value: Any,
    component: str,
    expected_kind: str,
    label: str,
) -> dict[str, Any]:
    if type(value) is not dict or tuple(value) not in {
        ("rational", "scalar_slot", "tensor"),
        ("rational", "scalar_slot", "operator"),
    }:
        raise IntrinsicRR2SplitError(f"{label} operator-term grammar drift")
    _decode_rational(value["rational"], f"{label}.rational")
    _validate_component_slot_ref(
        value["scalar_slot"], component, expected_kind, f"{label}.scalar_slot"
    )
    payload_key = "tensor" if "tensor" in value else "operator"
    if type(value[payload_key]) is not str or not value[payload_key]:
        raise IntrinsicRR2SplitError(f"{label}.{payload_key} is not a string")
    return copy.deepcopy(value)


def _strict_decode_public_blocks(
    public_blocks: Mapping[str, Any],
    dependency: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Decode only the closed component-local grammar, never expected rows.

    Exact snapshot equality is a separate certificate.  This decoder checks
    identities and source binding directly, then accepts structurally valid
    semantic alternatives so causal tests can observe the fold rather than
    counting a golden-row rejection as consumption.
    """

    if type(public_blocks) is not dict or tuple(public_blocks) != COMPONENTS:
        raise IntrinsicRR2SplitError("public component inventory/order drift")
    literal = str(dependency["v5_2_foliation_literal"])
    parsed = _parse_literal_split(literal)
    spans = _literal_component_spans(literal)
    expected_actions = dict(zip(COMPONENTS, _expected_component_polynomials(), strict=True))
    row_keys = (
        "schema",
        "component",
        "component_ordinal",
        "side",
        "domain",
        "source_span",
        "stage",
        "density_context",
        "independent_fixed_clock_ADM_variations",
        "adapter_aliases",
        "action_polynomial",
        "d_action_d_Rcal",
        "literal_expression",
        "literal_derivative_expression",
        "scalar_slots",
        "Gauss",
        "Gauss_formula",
        "Euler_coefficients_inside_N_sqrt_h",
        "weighted_IBP_current",
        "d4_Cartan_current",
        "raw_Frechet_rows_exported",
    )
    decoded: dict[str, Any] = {}
    grammar_paths: list[str] = []
    for name in COMPONENTS:
        row = public_blocks[name]
        _require_exact_keys(row, row_keys, f"{name} public row")
        if (
            row["schema"] != BLOCK_SCHEMA
            or row["component"] != name
            or row["component_ordinal"] != COMPONENT_ORDINALS[name]
            or row["side"] != SOURCE_SIDE
            or row["domain"] != SOURCE_DOMAIN
            or row["stage"] != "post_adjoint_component_normal_form"
            or not _strict_equal(row["source_span"], spans[name])
            or row["literal_expression"] != parsed[name]
            or row["raw_Frechet_rows_exported"] is not False
        ):
            raise IntrinsicRR2SplitError(f"{name} identity/source metadata drift")
        action_metadata = _poly_from_row(row["action_polynomial"])
        derivative_metadata = _poly_from_row(row["d_action_d_Rcal"])
        if (
            action_metadata != expected_actions[name]
            or derivative_metadata != action_metadata.derivative_Rcal()
            or row["literal_derivative_expression"]
            != _render_polynomial(derivative_metadata, _literal_aliases())
            or row["Gauss_formula"] != _gauss_formula(row["Gauss"])
        ):
            raise IntrinsicRR2SplitError(f"{name} literal/Gauss metadata drift")

        _require_exact_keys(
            row["density_context"], ("overall_constant", "measure"), f"{name}.density"
        )
        if not all(type(value) is str and value for value in row["density_context"].values()):
            raise IntrinsicRR2SplitError(f"{name} density context grammar drift")
        adm = row["independent_fixed_clock_ADM_variations"]
        _require_exact_keys(adm, ("lapse", "shift", "spatial_metric"), f"{name}.ADM")
        if not all(type(value) is str and value for value in adm.values()):
            raise IntrinsicRR2SplitError(f"{name} ADM grammar drift")
        aliases = row["adapter_aliases"]
        _require_exact_keys(aliases, VARIABLES, f"{name}.aliases")
        if not all(type(value) is str and value for value in aliases.values()):
            raise IntrinsicRR2SplitError(f"{name} alias grammar drift")

        slots = row["scalar_slots"]
        _require_exact_keys(
            slots,
            ("component_action", "component_derivative"),
            f"{name}.scalar_slots",
        )
        action_slot = slots["component_action"]
        derivative_slot = slots["component_derivative"]
        _require_exact_keys(action_slot, ("ref", "polynomial"), f"{name}.action_slot")
        _require_exact_keys(
            derivative_slot,
            ("ref", "with_respect_to", "polynomial"),
            f"{name}.derivative_slot",
        )
        _validate_component_slot_ref(
            action_slot["ref"], name, "component_action", f"{name}.action_slot.ref"
        )
        _validate_component_slot_ref(
            derivative_slot["ref"],
            name,
            "component_derivative",
            f"{name}.derivative_slot.ref",
        )
        if derivative_slot["with_respect_to"] != "Rcal":
            raise IntrinsicRR2SplitError(f"{name} derivative variable drift")
        slot_action = _poly_from_row(action_slot["polynomial"])
        slot_derivative = _poly_from_row(derivative_slot["polynomial"])

        gauss = row["Gauss"]
        _require_exact_keys(gauss, tuple(CORRECT_GAUSS), f"{name}.Gauss")
        if not all(type(value) is int for value in gauss.values()):
            raise IntrinsicRR2SplitError(f"{name} Gauss weights are not integers")

        euler = row["Euler_coefficients_inside_N_sqrt_h"]
        _require_exact_keys(
            euler, ("lapse_n", "shift_v_i", "spatial_metric_Q_ij"), f"{name}.Euler"
        )
        if type(euler["lapse_n"]) is not list or len(euler["lapse_n"]) != 1:
            raise IntrinsicRR2SplitError(f"{name} lapse-term inventory drift")
        if (
            type(euler["shift_v_i"]) is not list
            or len(euler["shift_v_i"]) != 3
            or not all(type(value) is int for value in euler["shift_v_i"])
        ):
            raise IntrinsicRR2SplitError(f"{name} shift inventory drift")
        if (
            type(euler["spatial_metric_Q_ij"]) is not list
            or len(euler["spatial_metric_Q_ij"]) != 3
        ):
            raise IntrinsicRR2SplitError(f"{name} spatial-term inventory drift")
        lapse = [
            _decode_operator_term(
                euler["lapse_n"][0], name, "component_action", f"{name}.Euler.lapse.0"
            )
        ]
        spatial = [
            _decode_operator_term(
                term,
                name,
                "component_action" if index == 0 else "component_derivative",
                f"{name}.Euler.spatial.{index}",
            )
            for index, term in enumerate(euler["spatial_metric_Q_ij"])
        ]

        current = row["weighted_IBP_current"]
        _require_exact_keys(
            current, ("present", "prefactor", "coefficient", "terms"), f"{name}.current"
        )
        if type(current["present"]) is not bool or type(current["prefactor"]) is not str:
            raise IntrinsicRR2SplitError(f"{name} current header grammar drift")
        coefficient = current["coefficient"]
        _require_exact_keys(
            coefficient,
            ("schema", "operator", "scalar_slot"),
            f"{name}.current.coefficient",
        )
        if (
            coefficient["schema"] != CURRENT_COEFFICIENT_SCHEMA
            or coefficient["operator"] not in {"N_times", "N_squared_times"}
        ):
            raise IntrinsicRR2SplitError(f"{name} current coefficient grammar drift")
        _validate_component_slot_ref(
            coefficient["scalar_slot"],
            name,
            "component_derivative",
            f"{name}.current.coefficient.scalar_slot",
        )
        if type(current["terms"]) is not list or len(current["terms"]) != 4:
            raise IntrinsicRR2SplitError(f"{name} current term inventory drift")
        current_terms = [
            _decode_operator_term(
                term,
                name,
                "component_derivative",
                f"{name}.current.terms.{index}",
            )
            for index, term in enumerate(current["terms"])
        ]

        cartan = row["d4_Cartan_current"]
        _require_exact_keys(
            cartan,
            (
                "rendered_component_term",
                "operator",
                "occurrences",
                "source_clock_gauge_vector",
                "gauge_variation_is_subtracted",
                "separate_material_transgression_appended",
            ),
            f"{name}.Cartan",
        )
        operator = cartan["operator"]
        _require_exact_keys(operator, ("operator", "scalar_slot"), f"{name}.Cartan.operator")
        _validate_component_slot_ref(
            operator["scalar_slot"], name, "component_action", f"{name}.Cartan.slot"
        )
        if (
            type(operator["operator"]) is not str
            or operator["operator"].count("()") != 1
            or cartan["rendered_component_term"]
            != operator["operator"].replace("()", name)
            or type(cartan["occurrences"]) is not int
            or cartan["occurrences"] < 0
            or type(cartan["source_clock_gauge_vector"]) is not str
            or type(cartan["gauge_variation_is_subtracted"]) is not bool
            or type(cartan["separate_material_transgression_appended"]) is not bool
        ):
            raise IntrinsicRR2SplitError(f"{name} Cartan grammar drift")

        decoded[name] = {
            "row": row,
            "slot_action": slot_action,
            "slot_derivative": slot_derivative,
            "lapse_terms": lapse,
            "spatial_terms": spatial,
            "current_terms": current_terms,
        }
        grammar_paths.extend(
            [
                f"{name}.scalar_slots.component_action",
                f"{name}.scalar_slots.component_derivative",
                f"{name}.Euler_coefficients_inside_N_sqrt_h.lapse_n.0",
                *(f"{name}.Euler_coefficients_inside_N_sqrt_h.spatial_metric_Q_ij.{i}" for i in range(3)),
                f"{name}.weighted_IBP_current.coefficient",
                *(f"{name}.weighted_IBP_current.terms.{i}" for i in range(4)),
                f"{name}.d4_Cartan_current.operator",
            ]
        )
    return decoded, sorted(grammar_paths)


def _build_pre_normalized_provenance_trace(
    decoded: Mapping[str, Any],
) -> dict[str, Any]:
    components: dict[str, Any] = {}
    reachability: list[dict[str, str]] = []
    for name in COMPONENTS:
        row = decoded[name]["row"]
        for field in ("overall_constant", "measure"):
            reachability.append(
                {
                    "component": name,
                    "role": "density_context_field",
                    "source_path": f"{name}.density_context.{field}",
                    "pre_normalized_path": f"components.{name}.density_context.{field}",
                }
            )
        for field in ("lapse", "shift", "spatial_metric"):
            reachability.append(
                {
                    "component": name,
                    "role": "ADM_variation_field",
                    "source_path": f"{name}.independent_fixed_clock_ADM_variations.{field}",
                    "pre_normalized_path": f"components.{name}.ADM_variations.{field}",
                }
            )
        for field in VARIABLES:
            reachability.append(
                {
                    "component": name,
                    "role": "adapter_alias_field",
                    "source_path": f"{name}.adapter_aliases.{field}",
                    "pre_normalized_path": f"components.{name}.adapter_aliases.{field}",
                }
            )
        for field in CORRECT_GAUSS:
            reachability.append(
                {
                    "component": name,
                    "role": "Gauss_weight",
                    "source_path": f"{name}.Gauss.{field}",
                    "pre_normalized_path": f"components.{name}.Gauss.{field}",
                }
            )
        slots = {
            "component_action": {
                "source_path": f"{name}.scalar_slots.component_action",
                "ref": copy.deepcopy(row["scalar_slots"]["component_action"]["ref"]),
                "polynomial": _poly_row(decoded[name]["slot_action"]),
            },
            "component_derivative": {
                "source_path": f"{name}.scalar_slots.component_derivative",
                "ref": copy.deepcopy(row["scalar_slots"]["component_derivative"]["ref"]),
                "polynomial": _poly_row(decoded[name]["slot_derivative"]),
            },
        }
        for kind, slot in slots.items():
            for field in ("coefficient", "powers"):
                reachability.append(
                    {
                        "component": name,
                        "role": f"{kind}_polynomial_{field}",
                        "source_path": f"{slot['source_path']}.polynomial.0.{field}",
                        "pre_normalized_path": f"components.{name}.slots.{kind}.polynomial.0.{field}",
                    }
                )
        euler = {
            "lapse_n": copy.deepcopy(decoded[name]["lapse_terms"]),
            "shift_v_i": copy.deepcopy(
                row["Euler_coefficients_inside_N_sqrt_h"]["shift_v_i"]
            ),
            "spatial_metric_Q_ij": copy.deepcopy(decoded[name]["spatial_terms"]),
        }
        for family, terms in (
            ("lapse_n", euler["lapse_n"]),
            ("spatial_metric_Q_ij", euler["spatial_metric_Q_ij"]),
        ):
            for index, term in enumerate(terms):
                base = f"{name}.Euler_coefficients_inside_N_sqrt_h.{family}.{index}"
                for field in ("rational", "tensor" if "tensor" in term else "operator"):
                    reachability.append(
                        {
                            "component": name,
                            "role": "Euler_operator_term_field",
                            "source_path": f"{base}.{field}",
                            "pre_normalized_path": f"components.{name}.Euler.{family}.{index}.{field}",
                        }
                    )
        for index, _ in enumerate(euler["shift_v_i"]):
            reachability.append(
                {
                    "component": name,
                    "role": "Euler_shift_entry",
                    "source_path": f"{name}.Euler_coefficients_inside_N_sqrt_h.shift_v_i.{index}",
                    "pre_normalized_path": f"components.{name}.Euler.shift_v_i.{index}",
                }
            )
        current = copy.deepcopy(row["weighted_IBP_current"])
        for field in ("present", "prefactor"):
            reachability.append(
                {
                    "component": name,
                    "role": "weighted_current_header",
                    "source_path": f"{name}.weighted_IBP_current.{field}",
                    "pre_normalized_path": f"components.{name}.weighted_current.{field}",
                }
            )
        reachability.append(
            {
                "component": name,
                "role": "weighted_current_coefficient",
                "source_path": f"{name}.weighted_IBP_current.coefficient.operator",
                "pre_normalized_path": f"components.{name}.weighted_current.coefficient.operator",
            }
        )
        for field in (
            "occurrences",
            "source_clock_gauge_vector",
            "gauge_variation_is_subtracted",
            "separate_material_transgression_appended",
        ):
            reachability.append(
                {
                    "component": name,
                    "role": "Cartan_fold_field",
                    "source_path": f"{name}.d4_Cartan_current.{field}",
                    "pre_normalized_path": f"components.{name}.Cartan.{field}",
                }
            )
        for index, _ in enumerate(current["terms"]):
            base = f"{name}.weighted_IBP_current.terms.{index}"
            for field in ("rational", "operator"):
                reachability.append(
                    {
                        "component": name,
                        "role": "weighted_current_operator_term_field",
                        "source_path": f"{base}.{field}",
                        "pre_normalized_path": f"components.{name}.weighted_current.terms.{index}.{field}",
                    }
                )
        cartan = copy.deepcopy(row["d4_Cartan_current"])
        reachability.append(
            {
                "component": name,
                "role": "Cartan_operator_term",
                "source_path": f"{name}.d4_Cartan_current.operator.operator",
                "pre_normalized_path": f"components.{name}.Cartan.operator.operator",
            }
        )
        components[name] = {
            "density_context": copy.deepcopy(row["density_context"]),
            "ADM_variations": copy.deepcopy(
                row["independent_fixed_clock_ADM_variations"]
            ),
            "adapter_aliases": copy.deepcopy(row["adapter_aliases"]),
            "slots": slots,
            "Gauss": copy.deepcopy(row["Gauss"]),
            "Euler": euler,
            "weighted_current": current,
            "Cartan": cartan,
        }
    action_operands = [components[name]["slots"]["component_action"]["polynomial"] for name in COMPONENTS]
    derivative_operands = [components[name]["slots"]["component_derivative"]["polynomial"] for name in COMPONENTS]
    total_action = _poly_from_row(action_operands[0]) + _poly_from_row(action_operands[1])
    total_derivative = _poly_from_row(derivative_operands[0]) + _poly_from_row(derivative_operands[1])
    return {
        "schema": PROVENANCE_TRACE_SCHEMA,
        "component_order": list(COMPONENTS),
        "components": components,
        "explicit_component_sums": {
            "f": {
                "operation": "ordered_sum_R_then_R_squared",
                "operands": copy.deepcopy(action_operands),
                "result": _poly_row(total_action),
            },
            "f_R": {
                "operation": "ordered_sum_R_then_R_squared",
                "operands": copy.deepcopy(derivative_operands),
                "result": _poly_row(total_derivative),
            },
        },
        "reachability": reachability,
    }


def _same_trace_value(trace: Mapping[str, Any], field: str) -> Any:
    values = [trace["components"][name][field] for name in COMPONENTS]
    if not all(_strict_equal(value, values[0]) for value in values[1:]):
        raise IntrinsicRR2SplitError(f"component {field} values do not fold uniquely")
    return copy.deepcopy(values[0])


def _total_slot_from_ref(value: Mapping[str, Any]) -> str:
    kind = value["kind"]
    if kind == "component_action":
        return "f"
    if kind == "component_derivative":
        return "f_R"
    raise IntrinsicRR2SplitError(f"non-component slot reached fold: {kind}")


def _translate_euler_term(term: Mapping[str, Any]) -> tuple[int, int, str]:
    numerator, denominator = _decode_rational(term["rational"], "Euler rational")
    body = _total_slot_from_ref(term["scalar_slot"])
    if "tensor" in term:
        tensor = str(term["tensor"])
        if tensor != "1":
            body += "*" + tensor
    elif "operator" in term:
        body = str(term["operator"]).replace("()", body)
    else:
        raise IntrinsicRR2SplitError("Euler term has neither tensor nor operator")
    return numerator, denominator, body


def _normalize_current_terms(terms: Sequence[Mapping[str, Any]]) -> list[list[Any]]:
    templates = {
        "N*()*D_j*Q^ij": ("N*{}", "D_j*Q^ij"),
        "N*()*D^i*Q": ("N*{}", "D^i*Q"),
        "D_j(N*())*Q^ij": ("D_j(N*{})", "Q^ij"),
        "D^i(N*())*Q": ("D^i(N*{})", "Q"),
    }
    normalized: list[list[Any]] = []
    for index, term in enumerate(terms):
        numerator, denominator = _decode_rational(term["rational"], f"current.{index}")
        if denominator != 1:
            raise IntrinsicRR2SplitError("current rational is not integral in .8 IR")
        try:
            left, right = templates[str(term["operator"])]
        except KeyError as exc:
            raise IntrinsicRR2SplitError("current operator is outside .8 grammar") from exc
        normalized.append(
            [numerator, left.format(_total_slot_from_ref(term["scalar_slot"])), right]
        )
    return normalized


def _fold_pre_normalized_provenance_trace(trace: Mapping[str, Any]) -> dict[str, Any]:
    if trace.get("schema") != PROVENANCE_TRACE_SCHEMA or trace.get("component_order") != list(COMPONENTS):
        raise IntrinsicRR2SplitError("pre-normalized provenance trace header drift")
    components = trace["components"]
    sums = trace["explicit_component_sums"]
    total_f = _poly_from_row(sums["f"]["result"])
    total_f_r = _poly_from_row(sums["f_R"]["result"])
    for key, slot_name in (("f", "component_action"), ("f_R", "component_derivative")):
        operands = sums[key]["operands"]
        recomputed = _poly_from_row(operands[0]) + _poly_from_row(operands[1])
        if sums[key]["operation"] != "ordered_sum_R_then_R_squared" or recomputed != _poly_from_row(sums[key]["result"]):
            raise IntrinsicRR2SplitError(f"explicit {key} component sum drift")
        if any(
            not _strict_equal(operands[index], components[name]["slots"][slot_name]["polynomial"])
            for index, name in enumerate(COMPONENTS)
        ):
            raise IntrinsicRR2SplitError(f"explicit {key} operands lost provenance")

    aliases = _same_trace_value(trace, "adapter_aliases")
    density_context = _same_trace_value(trace, "density_context")
    adm_variations = _same_trace_value(trace, "ADM_variations")
    gauss = _same_trace_value(trace, "Gauss")
    euler_rows = [components[name]["Euler"] for name in COMPONENTS]
    normalized_euler = []
    for euler in euler_rows:
        normalized_euler.append(
            {
                "lapse_n": [list(_translate_euler_term(term)) for term in euler["lapse_n"]],
                "shift_v_i": copy.deepcopy(euler["shift_v_i"]),
                "spatial_metric_Q_ij": [
                    list(_translate_euler_term(term)) for term in euler["spatial_metric_Q_ij"]
                ],
            }
        )
    if not _strict_equal(normalized_euler[0], normalized_euler[1]):
        raise IntrinsicRR2SplitError("component Euler operators do not fold uniquely")
    lapse_terms = normalized_euler[0]["lapse_n"]
    if any(denominator != 1 for _, denominator, _ in lapse_terms):
        raise IntrinsicRR2SplitError("lapse rational cannot use .8 compact form")

    current_rows = [components[name]["weighted_current"] for name in COMPONENTS]
    normalized_current = [_normalize_current_terms(row["terms"]) for row in current_rows]
    if not _strict_equal(normalized_current[0], normalized_current[1]):
        raise IntrinsicRR2SplitError("component current terms do not fold uniquely")
    current_present = all(row["present"] for row in current_rows)
    prefactors = [row["prefactor"] for row in current_rows]
    if prefactors[0] != prefactors[1]:
        raise IntrinsicRR2SplitError("component current prefactors do not fold uniquely")
    coefficient_ops = [row["coefficient"]["operator"] for row in current_rows]
    if coefficient_ops[0] != coefficient_ops[1]:
        raise IntrinsicRR2SplitError("component current coefficients do not fold uniquely")
    coefficient_render = {
        "N_times": "a=N*f_R",
        "N_squared_times": "a=N^2*f_R",
    }[coefficient_ops[0]]

    cartan_rows = [components[name]["Cartan"] for name in COMPONENTS]
    cartan_ops = [row["operator"]["operator"] for row in cartan_rows]
    if cartan_ops[0] != cartan_ops[1]:
        raise IntrinsicRR2SplitError("component Cartan operators do not fold uniquely")
    cartan_occurrences = [row["occurrences"] for row in cartan_rows]
    if cartan_occurrences[0] != cartan_occurrences[1]:
        raise IntrinsicRR2SplitError("component Cartan multiplicities do not fold uniquely")
    source_clocks = [row["source_clock_gauge_vector"] for row in cartan_rows]
    gauge_flags = [row["gauge_variation_is_subtracted"] for row in cartan_rows]
    if source_clocks[0] != source_clocks[1] or gauge_flags[0] is not gauge_flags[1]:
        raise IntrinsicRR2SplitError("component Cartan gauge fields do not fold uniquely")

    return {
        "density": {
            "overall_constant": density_context["overall_constant"],
            "measure": density_context["measure"],
            "f": _render_polynomial(total_f, aliases),
            "f_R": _render_polynomial(total_f_r, aliases),
            "Gauss_Rcal": _gauss_formula(gauss),
        },
        "independent_fixed_clock_ADM_variations": adm_variations,
        "Euler_coefficients_inside_N_sqrt_h": {
            "lapse_n": [[numerator, body] for numerator, _, body in lapse_terms],
            "shift_v_i": normalized_euler[0]["shift_v_i"],
            "spatial_metric_Q_ij": normalized_euler[0]["spatial_metric_Q_ij"],
        },
        "weighted_IBP_current": {
            "prefactor": prefactors[0],
            "terms": normalized_current[0] if current_present else [],
            "free_product_rule_coefficient": coefficient_render,
        },
        "d4_current": {
            "spatial_current_multiplicity": int(current_present),
            "source_clock_gauge_vector": source_clocks[0],
            "gauge_variation_is_subtracted": gauge_flags[0],
            "Cartan_term": cartan_ops[0].replace("()", "Rcal"),
            "Cartan_coefficient": cartan_occurrences[0],
            "Cartan_multiplicity": cartan_occurrences[0],
            "separate_material_transgression_appended": any(
                row["separate_material_transgression_appended"] for row in cartan_rows
            ),
        },
    }


def _compose_v5678_adapter_with_trace(
    public_blocks: Mapping[str, Any],
    dependency: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    decoded, _ = _strict_decode_public_blocks(public_blocks, dependency)
    trace = _build_pre_normalized_provenance_trace(decoded)
    return _fold_pre_normalized_provenance_trace(trace), trace


def _compose_v5678_adapter(
    public_blocks: Mapping[str, Any],
    dependency: Mapping[str, Any],
) -> dict[str, Any]:
    """Compose from typed rows through an explicit pre-normalized trace."""

    adapter, _ = _compose_v5678_adapter_with_trace(public_blocks, dependency)
    return adapter


def _component_slot_source_binding_certificate(
    public_blocks: Mapping[str, Any], dependency: Mapping[str, Any]
) -> dict[str, Any]:
    """Bind each typed slot to its own literal component outside the decoder.

    Keeping this equality separate lets the decoder accept valid alternatives
    for causal testing while still killing aggregate-preserving R/R_squared
    swaps even if a snapshot hash and expected-row table are co-mutated.
    """

    try:
        literal_semantics = _derive_intrinsic_components_from_pinned_literal_bytes(
            str(dependency["v5_2_foliation_literal"])
        )
        decoded, _ = _strict_decode_public_blocks(public_blocks, dependency)
    except IntrinsicRR2SplitError as exc:
        return {
            "pass": False,
            "rows": {},
            "error": str(exc),
            "independent_literal_derivation": {},
        }
    rows: dict[str, Any] = {}
    for name in COMPONENTS:
        semantic = literal_semantics[name]
        expected_action = _poly_from_row(semantic["action_polynomial"])
        expected_derivative = _poly_from_row(semantic["derivative_polynomial"])
        public_row = public_blocks[name]
        rows[name] = {
            "independent_owner_matches_component": semantic["owner"] == name,
            "source_span_matches_independent_literal_bytes": _strict_equal(
                public_row["source_span"], semantic["source_span"]
            ),
            "literal_expression_matches_independent_literal_bytes": (
                public_row["literal_expression"] == semantic["literal_expression"]
            ),
            "action_metadata_matches_independent_literal_polynomial": _strict_equal(
                public_row["action_polynomial"], semantic["action_polynomial"]
            ),
            "component_action_matches_literal_component": (
                decoded[name]["slot_action"] == expected_action
            ),
            "derivative_metadata_matches_independent_exponent_rule": _strict_equal(
                public_row["d_action_d_Rcal"], semantic["derivative_polynomial"]
            ),
            "literal_derivative_matches_independent_exponent_rule": (
                public_row["literal_derivative_expression"]
                == semantic["literal_derivative_expression"]
            ),
            "component_derivative_matches_own_action_derivative": (
                decoded[name]["slot_derivative"] == expected_derivative
                and decoded[name]["slot_derivative"]
                == decoded[name]["slot_action"].derivative_Rcal()
            ),
        }
    return {
        "pass": all(all(row.values()) for row in rows.values()),
        "rows": rows,
        "error": None,
        "independent_literal_derivation": literal_semantics,
        "expected_rows_source": (
            "independent byte-pinned literal tokenizer and local exponent-rule "
            "derivative; no producer/decoder/golden expected-polynomial table"
        ),
    }


def _set_path(value: Any, path: Sequence[Any], replacement: Any) -> None:
    cursor = value
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement


def _semantic_payload_alternatives(
    public_blocks: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Structurally valid alternatives for every typed slot/operator unit."""

    cases: list[dict[str, Any]] = []

    def add(name: str, source_path: str, attacked: dict[str, Any]) -> None:
        cases.append({"name": name, "source_path": source_path, "blocks": attacked})

    for component in COMPONENTS:
        prefix = (component,)
        for field in ("overall_constant", "measure"):
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["density_context"][field] += "#alternative"
            source = f"{component}.density_context.{field}"
            add(f"{component}_density_{field}", source, attacked)
        for field in ("lapse", "shift", "spatial_metric"):
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["independent_fixed_clock_ADM_variations"][
                field
            ] += "#alternative"
            source = f"{component}.independent_fixed_clock_ADM_variations.{field}"
            add(f"{component}_ADM_{field}", source, attacked)
        for field in VARIABLES:
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["adapter_aliases"][field] += "_alternative"
            source = f"{component}.adapter_aliases.{field}"
            add(f"{component}_alias_{field}", source, attacked)
        for field in CORRECT_GAUSS:
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["Gauss"][field] += 1
            attacked[component]["Gauss_formula"] = _gauss_formula(
                attacked[component]["Gauss"]
            )
            source = f"{component}.Gauss.{field}"
            add(f"{component}_Gauss_{field}", source, attacked)
        for slot_name in ("component_action", "component_derivative"):
            attacked = copy.deepcopy(public_blocks)
            path = (*prefix, "scalar_slots", slot_name, "polynomial", 0, "coefficient", 0)
            cursor: Any = attacked
            for part in path:
                cursor = cursor[part]
            _set_path(attacked, path, cursor * 3)
            base = f"{component}.scalar_slots.{slot_name}.polynomial.0"
            add(
                f"{component}_{slot_name}_polynomial_coefficient",
                f"{base}.coefficient",
                attacked,
            )
            attacked = copy.deepcopy(public_blocks)
            powers = attacked[component]["scalar_slots"][slot_name]["polynomial"][0][
                "powers"
            ]
            powers[-1][1] += 1
            add(
                f"{component}_{slot_name}_polynomial_powers",
                f"{base}.powers",
                attacked,
            )

        euler_paths = [
            ("lapse_n", 0),
            *( ("spatial_metric_Q_ij", index) for index in range(3) ),
        ]
        for family, index in euler_paths:
            attacked = copy.deepcopy(public_blocks)
            path = (
                *prefix,
                "Euler_coefficients_inside_N_sqrt_h",
                family,
                index,
                "rational",
                0,
            )
            cursor = attacked
            for part in path:
                cursor = cursor[part]
            _set_path(attacked, path, cursor * 2)
            base = f"{component}.Euler_coefficients_inside_N_sqrt_h.{family}.{index}"
            add(f"{component}_Euler_{family}_{index}_rational", f"{base}.rational", attacked)
            attacked = copy.deepcopy(public_blocks)
            term = attacked[component]["Euler_coefficients_inside_N_sqrt_h"][family][index]
            payload_key = "tensor" if "tensor" in term else "operator"
            term[payload_key] += "#alternative"
            add(
                f"{component}_Euler_{family}_{index}_{payload_key}",
                f"{base}.{payload_key}",
                attacked,
            )

        for index in range(3):
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["Euler_coefficients_inside_N_sqrt_h"][
                "shift_v_i"
            ][index] = 1
            source = f"{component}.Euler_coefficients_inside_N_sqrt_h.shift_v_i.{index}"
            add(f"{component}_Euler_shift_{index}", source, attacked)

        attacked = copy.deepcopy(public_blocks)
        attacked[component]["weighted_IBP_current"]["present"] = False
        source = f"{component}.weighted_IBP_current.present"
        add(f"{component}_current_present", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["weighted_IBP_current"]["prefactor"] += "#alternative"
        source = f"{component}.weighted_IBP_current.prefactor"
        add(f"{component}_current_prefactor", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["weighted_IBP_current"]["coefficient"]["operator"] = (
            "N_squared_times"
        )
        source = f"{component}.weighted_IBP_current.coefficient.operator"
        add(f"{component}_current_coefficient", source, attacked)
        for index in range(4):
            attacked = copy.deepcopy(public_blocks)
            path = (
                *prefix,
                "weighted_IBP_current",
                "terms",
                index,
                "rational",
                0,
            )
            cursor = attacked
            for part in path:
                cursor = cursor[part]
            _set_path(attacked, path, cursor * 2)
            base = f"{component}.weighted_IBP_current.terms.{index}"
            add(f"{component}_current_term_{index}_rational", f"{base}.rational", attacked)
            attacked = copy.deepcopy(public_blocks)
            attacked[component]["weighted_IBP_current"]["terms"][index][
                "operator"
            ] += "#alternative"
            add(
                f"{component}_current_term_{index}_operator",
                f"{base}.operator",
                attacked,
            )

        attacked = copy.deepcopy(public_blocks)
        cartan = attacked[component]["d4_Cartan_current"]
        cartan["operator"]["operator"] = "+X+i_(N*tau*u)(l_())"
        cartan["rendered_component_term"] = cartan["operator"]["operator"].replace(
            "()", component
        )
        source = f"{component}.d4_Cartan_current.operator.operator"
        add(f"{component}_Cartan_operator", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["d4_Cartan_current"]["occurrences"] += 1
        source = f"{component}.d4_Cartan_current.occurrences"
        add(f"{component}_Cartan_occurrences", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["d4_Cartan_current"][
            "source_clock_gauge_vector"
        ] += "#alternative"
        source = f"{component}.d4_Cartan_current.source_clock_gauge_vector"
        add(f"{component}_Cartan_source_clock", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["d4_Cartan_current"][
            "gauge_variation_is_subtracted"
        ] = False
        source = f"{component}.d4_Cartan_current.gauge_variation_is_subtracted"
        add(f"{component}_Cartan_gauge_subtracted", source, attacked)
        attacked = copy.deepcopy(public_blocks)
        attacked[component]["d4_Cartan_current"][
            "separate_material_transgression_appended"
        ] = True
        source = f"{component}.d4_Cartan_current.separate_material_transgression_appended"
        add(f"{component}_Cartan_transgression", source, attacked)
    return cases


def _metadata_inventory_certificate(
    public_blocks: Mapping[str, Any], snapshot_certificate: Mapping[str, Any]
) -> dict[str, Any]:
    metadata_roots = {
        "schema",
        "component",
        "component_ordinal",
        "side",
        "domain",
        "source_span",
        "stage",
        "action_polynomial",
        "d_action_d_Rcal",
        "literal_expression",
        "literal_derivative_expression",
        "Gauss_formula",
        "raw_Frechet_rows_exported",
    }
    paths = _public_leaf_paths(public_blocks)
    metadata = [path for path in paths if len(path) > 1 and path[1] in metadata_roots]
    return {
        "pass": bool(paths) and bool(metadata) and bool(snapshot_certificate["pass"]),
        "classification": "validated_not_folded",
        "validation_source": "strict independent expected-row snapshot certificate",
        "total_public_leaf_inventory": len(paths),
        "validated_not_folded_leaf_count": len(metadata),
        "validated_not_folded_paths": sorted(_path_label(path) for path in metadata),
        "claim_every_scalar_leaf_is_causally_consumed": False,
    }


def _changed_paths(
    left: Any, right: Any, prefix: tuple[Any, ...] = ()
) -> list[tuple[Any, ...]]:
    if type(left) is not type(right):
        return [prefix]
    if isinstance(left, dict):
        if tuple(left) != tuple(right):
            return [prefix]
        changed: list[tuple[Any, ...]] = []
        for key in left:
            changed.extend(_changed_paths(left[key], right[key], (*prefix, key)))
        return changed
    if isinstance(left, list):
        if len(left) != len(right):
            return [prefix]
        changed = []
        for index, (left_item, right_item) in enumerate(
            zip(left, right, strict=True)
        ):
            changed.extend(
                _changed_paths(left_item, right_item, (*prefix, index))
            )
        return changed
    return [] if _strict_equal(left, right) else [prefix]


def _path_is_at_or_below(path: str, root: str) -> bool:
    return path == root or path.startswith(root + ".")


def _semantic_payload_consumption_certificate(
    public_blocks: Mapping[str, Any],
    dependency: Mapping[str, Any],
    baseline_adapter: Mapping[str, Any],
    baseline_trace: Mapping[str, Any],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    reachability_map = {
        row["source_path"]: row["pre_normalized_path"]
        for row in baseline_trace["reachability"]
    }
    for case in _semantic_payload_alternatives(public_blocks):
        decoder_accepted = False
        trace_changed = False
        trace_target_changed = False
        fold_rejected = False
        adapter_changed = False
        changed_public_paths = sorted(
            _path_label(path)
            for path in _changed_paths(public_blocks, case["blocks"])
        )
        allowed_dependent_paths: set[str] = set()
        if ".Gauss." in case["source_path"]:
            allowed_dependent_paths.add(
                case["source_path"].split(".Gauss.", 1)[0] + ".Gauss_formula"
            )
        if case["source_path"].endswith(
            ".d4_Cartan_current.operator.operator"
        ):
            allowed_dependent_paths.add(
                case["source_path"].split(".operator.operator", 1)[0]
                + ".rendered_component_term"
            )
        mutation_scoped = bool(changed_public_paths) and any(
            _path_is_at_or_below(path, case["source_path"])
            for path in changed_public_paths
        ) and all(
            _path_is_at_or_below(path, case["source_path"])
            or path in allowed_dependent_paths
            for path in changed_public_paths
        )
        try:
            decoded, _ = _strict_decode_public_blocks(case["blocks"], dependency)
            decoder_accepted = True
            observed_trace = _build_pre_normalized_provenance_trace(decoded)
            trace_changed = not _strict_equal(observed_trace, baseline_trace)
            changed_trace_paths = [
                _path_label(path)
                for path in _changed_paths(baseline_trace, observed_trace)
            ]
            target = reachability_map.get(case["source_path"], "")
            trace_target_changed = bool(target) and any(
                _path_is_at_or_below(path, target) for path in changed_trace_paths
            )
            try:
                observed_adapter = _fold_pre_normalized_provenance_trace(observed_trace)
            except IntrinsicRR2SplitError:
                fold_rejected = True
            else:
                adapter_changed = not _strict_equal(observed_adapter, baseline_adapter)
        except IntrinsicRR2SplitError:
            pass
        rows.append(
            {
                "case": case["name"],
                "source_path": case["source_path"],
                "mutation_scoped_to_declared_source": mutation_scoped,
                "changed_public_paths": changed_public_paths,
                "decoder_accepted_structurally_valid_alternative": decoder_accepted,
                "pre_normalized_trace_changed": trace_changed,
                "declared_pre_normalized_target_changed": trace_target_changed,
                "fold_rejected_or_adapter_changed": fold_rejected or adapter_changed,
                "fold_rejected": fold_rejected,
                "adapter_changed": adapter_changed,
            }
        )
    reachable = {row["source_path"] for row in baseline_trace["reachability"]}
    exercised = {row["source_path"] for row in rows}
    passed = bool(rows) and all(
        row["mutation_scoped_to_declared_source"]
        and row["decoder_accepted_structurally_valid_alternative"]
        and row["pre_normalized_trace_changed"]
        and row["declared_pre_normalized_target_changed"]
        and row["fold_rejected_or_adapter_changed"]
        for row in rows
    ) and reachable == exercised
    return {
        "pass": passed,
        "block_hash_pin_consulted": False,
        "survives_internal_block_hash_repin": True,
        "criterion": (
            "each typed component slot/operator unit has a decoder-accepted "
            "structural alternative which changes its pre-normalized trace and "
            "is rejected by the semantic fold or changes the composed adapter"
        ),
        "decoder_rejection_counts_as_consumption": False,
        "typed_reachability_unit_count": len(reachable),
        "causal_alternative_count": len(rows),
        "reachability_units_all_exercised": reachable == exercised,
        "rows": rows,
    }


def _central_difference_oracle(
    blocks: Mapping[str, Any],
) -> dict[str, Any]:
    base = {
        "xi": Fraction(7, 5),
        "B4_bar": Fraction(11, 7),
        "k_infinity": Fraction(13, 6),
        "Rcal": Fraction(-5, 4),
    }
    step = Fraction(2, 9)
    rows: dict[str, Any] = {}
    for name in ("R", "R_squared"):
        polynomial = blocks[name]["polynomial"]
        derivative = blocks[name]["derivative"]
        plus = {**base, "Rcal": base["Rcal"] + step}
        minus = {**base, "Rcal": base["Rcal"] - step}
        central = (polynomial.evaluate(plus) - polynomial.evaluate(minus)) / (2 * step)
        derivative_value = derivative.evaluate(base)
        rows[name] = {
            "pass": central == derivative_value,
            "central_difference": [central.numerator, central.denominator],
            "formal_derivative": [
                derivative_value.numerator,
                derivative_value.denominator,
            ],
            "both_nonzero": central != 0 and derivative_value != 0,
        }
    return {
        "pass": all(row["pass"] and row["both_nonzero"] for row in rows.values()),
        "identity": "quadratic central difference equals exact Rcal derivative",
        "Rcal_step": [step.numerator, step.denominator],
        "rows": rows,
    }


def _coefficient_jets(component: str) -> tuple[Fraction, list[Fraction], list[list[Fraction]]]:
    n = 2
    lapse = Fraction(7, 5)
    d_lapse = [Fraction(2, 3), Fraction(-3, 7)]
    dd_lapse = [
        [Fraction(5, 11), Fraction(7, 13)],
        [Fraction(7, 13), Fraction(-2, 9)],
    ]
    xi = Fraction(13, 6)
    if component == "R":
        return (
            lapse * xi,
            [entry * xi for entry in d_lapse],
            [[entry * xi for entry in row] for row in dd_lapse],
        )
    curvature = Fraction(-5, 4)
    d_curvature = [Fraction(4, 9), Fraction(3, 8)]
    dd_curvature = [
        [Fraction(-7, 10), Fraction(5, 12)],
        [Fraction(5, 12), Fraction(11, 14)],
    ]
    coefficient = -Fraction(17, 9) / (8 * Fraction(5, 3) ** 2)
    value = coefficient * lapse * curvature
    derivative = [
        coefficient * (d_lapse[i] * curvature + lapse * d_curvature[i])
        for i in range(n)
    ]
    second = [
        [
            coefficient
            * (
                dd_lapse[i][j] * curvature
                + d_lapse[i] * d_curvature[j]
                + d_lapse[j] * d_curvature[i]
                + lapse * dd_curvature[i][j]
            )
            for j in range(n)
        ]
        for i in range(n)
    ]
    return value, derivative, second


def _product_rule_witness(component: str, current_present: bool) -> dict[str, Any]:
    n = 2
    a, da, dda = _coefficient_jets(component)
    h = [
        [Fraction(2, 7), Fraction(-3, 11)],
        [Fraction(-3, 11), Fraction(5, 13)],
    ]
    dh = [
        [
            [Fraction((axis + 2) * (i + 1) - (j + 2), 17) for j in range(n)]
            for i in range(n)
        ]
        for axis in range(n)
    ]
    for axis in range(n):
        for i in range(n):
            for j in range(i):
                dh[axis][i][j] = dh[axis][j][i]
    ddh = [
        [
            [
                [
                    Fraction((axis + 1) * (other + 2) + (i + 2) * (j + 1), 19)
                    for j in range(n)
                ]
                for i in range(n)
            ]
            for other in range(n)
        ]
        for axis in range(n)
    ]
    for axis in range(n):
        for other in range(n):
            for i in range(n):
                for j in range(n):
                    values = (
                        ddh[axis][other][i][j],
                        ddh[other][axis][i][j],
                        ddh[axis][other][j][i],
                        ddh[other][axis][j][i],
                    )
                    average = sum(values, Fraction(0)) / 4
                    ddh[axis][other][i][j] = average
                    ddh[other][axis][i][j] = average
                    ddh[axis][other][j][i] = average
                    ddh[other][axis][j][i] = average

    trace_h = sum(h[i][i] for i in range(n))
    raw = a * (
        sum(ddh[i][j][i][j] for i in range(n) for j in range(n))
        - sum(ddh[i][i][j][j] for i in range(n) for j in range(n))
    )
    bulk = (
        sum(dda[i][j] * h[i][j] for i in range(n) for j in range(n))
        - sum(dda[i][i] for i in range(n)) * trace_h
    )
    divergence = (
        sum(da[i] * dh[j][i][j] for i in range(n) for j in range(n))
        + a * sum(ddh[i][j][i][j] for i in range(n) for j in range(n))
        - sum(da[i] * dh[i][j][j] for i in range(n) for j in range(n))
        - a * sum(ddh[i][i][j][j] for i in range(n) for j in range(n))
        - sum(dda[i][j] * h[i][j] for i in range(n) for j in range(n))
        - sum(da[j] * dh[i][i][j] for i in range(n) for j in range(n))
        + sum(dda[i][i] for i in range(n)) * trace_h
        + sum(da[i] * dh[i][j][j] for i in range(n) for j in range(n))
    )
    residual = raw - bulk - divergence
    return {
        "pass": bool(
            current_present
            and residual == 0
            and raw != 0
            and bulk != 0
            and divergence != 0
        ),
        "current_encoded": current_present,
        "raw": [raw.numerator, raw.denominator],
        "Euler_bulk": [bulk.numerator, bulk.denominator],
        "current_divergence": [divergence.numerator, divergence.denominator],
        "residual": [residual.numerator, residual.denominator],
    }


def _component_product_rule_oracle(blocks: Mapping[str, Any]) -> dict[str, Any]:
    rows = {
        name: _product_rule_witness(
            name, blocks[name]["row"]["weighted_IBP_current"]["present"]
        )
        for name in ("R", "R_squared")
    }
    return {
        "pass": all(row["pass"] for row in rows.values()),
        "dimension": 2,
        "exact_rational_arithmetic": True,
        "rows": rows,
    }


def _gauss_oracle(blocks: Mapping[str, Any]) -> dict[str, Any]:
    ambient = Fraction(5, 7)
    principal = (Fraction(2, 3), Fraction(-3, 5), Fraction(5, 4))
    trace = sum(principal, Fraction(0))
    tensor_square = sum(value * value for value in principal)
    expected = ambient - trace * trace + tensor_square
    rows: dict[str, Any] = {}
    for name in ("R", "R_squared"):
        weights = blocks[name]["row"]["Gauss"]
        observed = (
            weights["projected_ambient_Riemann"] * ambient
            + weights["K_trace_squared"] * trace * trace
            + weights["K_tensor_squared"] * tensor_square
        )
        rows[name] = {
            "pass": observed == expected and observed != 0,
            "observed": [observed.numerator, observed.denominator],
            "expected": [expected.numerator, expected.denominator],
        }
    return {
        "pass": all(row["pass"] for row in rows.values()),
        "principal_curvature_witness": [
            [value.numerator, value.denominator] for value in principal
        ],
        "rows": rows,
    }


def _literal_split_certificate(
    dependency: Mapping[str, Any],
    blocks: Mapping[str, Any],
) -> dict[str, Any]:
    parsed = _parse_literal_split(str(dependency["v5_2_foliation_literal"]))
    independent = _derive_intrinsic_components_from_pinned_literal_bytes(
        str(dependency["v5_2_foliation_literal"])
    )
    expected_r = _poly_from_row(independent["R"]["action_polynomial"])
    expected_r2 = _poly_from_row(
        independent["R_squared"]["action_polynomial"]
    )
    observed = {
        name: blocks[name]["row"]["literal_expression"]
        for name in ("R", "R_squared")
    }
    return {
        "pass": bool(
            dependency["pass"]
            and dependency["v5_2_exact_action_sha256"] == V52_ACTION_SHA256
            and parsed == {
                "R": "xi*Rcal",
                "R_squared": "-B4_bar*Rcal^2/(16*k_infinity^2)",
            }
            and blocks["R"]["polynomial"] == expected_r
            and blocks["R_squared"]["polynomial"] == expected_r2
            and observed == parsed
        ),
        "literal_components": parsed,
        "generated_components": observed,
        "literal_order": ["R", "R_squared"],
        "independent_literal_semantic_derivation": independent,
    }


def _polynomial_certificate(blocks: Mapping[str, Any]) -> dict[str, Any]:
    independent = _derive_intrinsic_components_from_pinned_literal_bytes(
        V52_FOLIATION_LITERAL
    )
    expected_r = _poly_from_row(independent["R"]["action_polynomial"])
    expected_r2 = _poly_from_row(
        independent["R_squared"]["action_polynomial"]
    )
    expected_derivatives = {
        "R": expected_r.derivative_Rcal(),
        "R_squared": expected_r2.derivative_Rcal(),
    }
    central = _central_difference_oracle(blocks)
    rows = {
        name: {
            "formal_derivative_matches_exponent_rule": (
                blocks[name]["derivative"] == blocks[name]["polynomial"].derivative_Rcal()
            ),
            "matches_literal_component_derivative": (
                blocks[name]["derivative"] == expected_derivatives[name]
            ),
            "f": _poly_row(blocks[name]["polynomial"]),
            "f_R": _poly_row(blocks[name]["derivative"]),
        }
        for name in ("R", "R_squared")
    }
    total_derivative = blocks["R"]["derivative"] + blocks["R_squared"]["derivative"]
    aliases = _v5678_aliases(None)
    return {
        "pass": bool(
            all(
                row["formal_derivative_matches_exponent_rule"]
                and row["matches_literal_component_derivative"]
                for row in rows.values()
            )
            and central["pass"]
            and _render_polynomial(total_derivative, aliases)
            == "xi-B4*Rcal/(8*k^2)"
        ),
        "ring": "Q[xi,B4_bar,k_infinity^+-1,Rcal]",
        "variables": list(VARIABLES),
        "rows": rows,
        "combined_f_R_in_v5_6_7_8_aliases": _render_polynomial(
            total_derivative, aliases
        ),
        "independent_central_difference_oracle": central,
    }


def _build_core(
    dependency: Mapping[str, Any],
    mutation: str | None,
    *,
    repin_internal_hashes: bool = False,
) -> dict[str, Any]:
    if mutation is not None and mutation not in MUTATIONS:
        raise IntrinsicRR2SplitError(f"unknown mutation: {mutation}")
    blocks = _build_component_blocks(mutation)
    public_blocks = _public_blocks(blocks)
    blocks_hash = _canonical_sha256(public_blocks)
    schema = _public_block_schema_certificate(public_blocks, dependency)
    slot_source_binding = _component_slot_source_binding_certificate(
        public_blocks, dependency
    )
    literal = _literal_split_certificate(dependency, blocks)
    polynomial = _polynomial_certificate(blocks)
    no_cross = _no_cross_cancellation_certificate(blocks)
    product_rule = _component_product_rule_oracle(blocks)
    gauss = _gauss_oracle(blocks)
    metadata_inventory = _metadata_inventory_certificate(public_blocks, schema)
    try:
        adapter, provenance_trace = _compose_v5678_adapter_with_trace(
            public_blocks, dependency
        )
        composition_error = None
        consumption = _semantic_payload_consumption_certificate(
            public_blocks, dependency, adapter, provenance_trace
        )
    except IntrinsicRR2SplitError as exc:
        adapter = {}
        provenance_trace = {}
        composition_error = str(exc)
        consumption = {
            "pass": False,
            "block_hash_pin_consulted": False,
            "survives_internal_block_hash_repin": True,
            "criterion": "strict grammar failed before causal alternatives",
            "decoder_rejection_counts_as_consumption": False,
            "typed_reachability_unit_count": 0,
            "causal_alternative_count": 0,
            "reachability_units_all_exercised": False,
            "rows": [],
        }
    adapter_hash = _canonical_sha256(adapter)
    reference = dependency["v5_6_7_8_ADM_normal_form"]
    current_complete = all(
        blocks[name]["row"]["weighted_IBP_current"]["present"]
        for name in blocks
    )
    cartan_once = all(
        blocks[name]["row"]["d4_Cartan_current"]["occurrences"] == 1
        for name in blocks
    ) and bool(
        adapter
        and adapter["d4_current"]["Cartan_multiplicity"] == 1
    )
    blocks_pin = repin_internal_hashes or blocks_hash == EXPECTED_BLOCKS_SHA256
    checks = {
        "audited_v5_6_7_8_and_literal_v5_2_dependency_bound": bool(
            dependency["pass"]
        ),
        "literal_R_R_squared_split_exact": literal["pass"],
        "formal_Laurent_polynomial_derivatives_exact": polynomial["pass"],
        "component_Gauss_sign_exact": gauss["pass"],
        "component_weighted_Euler_Green_currents_exact": product_rule["pass"],
        "every_component_current_present": current_complete,
        "component_Cartan_currents_compose_once": cartan_once,
        "no_cross_component_monomial_cancellation": no_cross["pass"],
        "strict_public_component_row_schema_and_expected_rows_exact": schema["pass"],
        "component_local_slots_bind_literal_derivative_exact": slot_source_binding[
            "pass"
        ],
        "composer_decodes_and_folds_exported_rows": composition_error is None,
        "metadata_inventory_validated_not_folded": metadata_inventory["pass"],
        "typed_component_slots_and_operator_terms_causally_traced": consumption[
            "pass"
        ],
        "component_blocks_canonical_pin": blocks_pin,
        "sum_reconstructs_v5_6_7_8_ADM_normal_form": bool(
            adapter == reference
            and adapter_hash == EXPECTED_COMPOSED_ADAPTER_SHA256
            and adapter_hash == dependency["v5_6_7_8_ADM_normal_form_sha256"]
        ),
        "post_adjoint_scope_no_raw_rows_claimed": bool(
            dependency["input_stage"] == "post_adjoint_ADM_Euler_Green_normal_form"
            and dependency["raw_Frechet_rows_present"] is False
            and all(
                block["raw_Frechet_rows_exported"] is False
                for block in public_blocks.values()
            )
        ),
    }
    return {
        "blocks": public_blocks,
        "blocks_sha256": blocks_hash,
        "internal_hashes_repinned": repin_internal_hashes,
        "public_schema": schema,
        "slot_source_binding": slot_source_binding,
        "metadata_inventory": metadata_inventory,
        "field_consumption": consumption,
        "pre_normalized_provenance_trace": provenance_trace,
        "pre_normalized_provenance_trace_sha256": _canonical_sha256(
            provenance_trace
        ),
        "composition_error": composition_error,
        "literal": literal,
        "polynomial": polynomial,
        "no_cross": no_cross,
        "product_rule": product_rule,
        "gauss": gauss,
        "adapter": adapter,
        "adapter_sha256": adapter_hash,
        "checks": checks,
        "ready": all(checks.values()),
    }


def _mutant_campaign(dependency: Mapping[str, Any]) -> dict[str, Any]:
    required_failure = {
        "shared_oracle_swap": "component_local_slots_bind_literal_derivative_exact",
        "wrong_R2_derivative_factor": "formal_Laurent_polynomial_derivatives_exact",
        "wrong_Gauss_sign": "component_Gauss_sign_exact",
        "mix_xi_B4_across_blocks": "no_cross_component_monomial_cancellation",
        "omit_R2_weighted_current": "every_component_current_present",
        "double_Cartan": "component_Cartan_currents_compose_once",
        "alias_k_to_itself": "sum_reconstructs_v5_6_7_8_ADM_normal_form",
        "wrong_literal_derivative_expression": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_Gauss_formula": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_weighted_current_terms": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_Cartan_term": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_component_label": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_component_ordinal": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_source_span": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "wrong_side": "strict_public_component_row_schema_and_expected_rows_exact",
        "wrong_domain": "strict_public_component_row_schema_and_expected_rows_exact",
        "extra_public_field": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "swap_aggregate_components_after_repin": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
        "combined_swap_relabel_and_unconsumed_fields_after_repin": (
            "strict_public_component_row_schema_and_expected_rows_exact"
        ),
    }
    rows: dict[str, Any] = {}
    for mutation in MUTATIONS:
        core = _build_core(
            dependency, mutation, repin_internal_hashes=True
        )
        failed = sorted(key for key, value in core["checks"].items() if not value)
        required = required_failure[mutation]
        rows[mutation] = {
            "killed": not core["ready"],
            "internal_hashes_repinned": core["internal_hashes_repinned"],
            "block_pin_pass_after_repin": core["checks"][
                "component_blocks_canonical_pin"
            ],
            "required_failure_surface": required,
            "required_failure_observed": required in failed,
            "failed_checks": failed,
        }
    return {
        "pass": bool(
            set(rows) == set(MUTATIONS)
            and all(row["killed"] for row in rows.values())
            and all(row["internal_hashes_repinned"] for row in rows.values())
            and all(row["block_pin_pass_after_repin"] for row in rows.values())
            and all(row["required_failure_observed"] for row in rows.values())
        ),
        "required_inventory": list(MUTATIONS),
        "rows": rows,
    }


def _decision(all_checks: bool) -> dict[str, bool]:
    decision = {key: all_checks for key in TRUE_DECISION_KEYS}
    decision.update({key: False for key in FALSE_DECISION_KEYS})
    return decision


def build_report(
    mutation: str | None = None,
    *,
    repin_internal_hashes: bool = False,
) -> dict[str, Any]:
    dependency = _dependency_certificate()
    core = _build_core(
        dependency,
        mutation,
        repin_internal_hashes=repin_internal_hashes,
    )
    mutants = (
        _mutant_campaign(dependency)
        if mutation is None
        else {
            "pass": False,
            "required_inventory": list(MUTATIONS),
            "rows": {},
            "scope": "mutant-of-mutant recursion disabled",
        }
    )
    checks = {
        **core["checks"],
        "mandatory_mutants_rejected": mutants["pass"],
    }
    all_checks = all(checks.values())
    decision = _decision(all_checks)
    if mutation is None:
        if {key for key, value in decision.items() if value} != TRUE_DECISION_KEYS:
            raise IntrinsicRR2SplitError("positive decision allowlist drift")
        if {key for key, value in decision.items() if not value} != FALSE_DECISION_KEYS:
            raise IntrinsicRR2SplitError("fail-closed decision allowlist drift")
    return {
        "schema": SCHEMA,
        "status": "READY" if mutation is None and all_checks else "NOT_READY",
        "mutation": mutation,
        "internal_hashes_repinned": repin_internal_hashes,
        "dependency_certificate": dependency,
        "literal_component_split": core["literal"],
        "formal_polynomial_certificate": core["polynomial"],
        "componentwise_post_adjoint_Euler_Green_blocks": core["blocks"],
        "component_blocks_sha256": core["blocks_sha256"],
        "expected_component_blocks_sha256": EXPECTED_BLOCKS_SHA256,
        "strict_public_component_row_schema": core["public_schema"],
        "component_local_slot_source_binding": core["slot_source_binding"],
        "public_field_inventory_certificate": core["metadata_inventory"],
        "semantic_payload_causal_consumption_certificate": core[
            "field_consumption"
        ],
        "pre_normalized_component_provenance_trace": core[
            "pre_normalized_provenance_trace"
        ],
        "pre_normalized_component_provenance_trace_sha256": core[
            "pre_normalized_provenance_trace_sha256"
        ],
        "composition_error": core["composition_error"],
        "no_cross_component_cancellation_certificate": core["no_cross"],
        "component_product_rule_oracle": core["product_rule"],
        "Gauss_sign_oracle": core["gauss"],
        "composed_v5_6_7_8_adapter": core["adapter"],
        "composed_v5_6_7_8_adapter_sha256": core["adapter_sha256"],
        "expected_composed_v5_6_7_8_adapter_sha256": (
            EXPECTED_COMPOSED_ADAPTER_SHA256
        ),
        "raw_Frechet_export": {
            "rows": [],
            "FrechetRowV1_adapter_exported": False,
            "reason": (
                "the byte-pinned v5.6.7.8 dependency is post-adjoint; a split of its "
                "Euler-Green normal form cannot reconstruct raw action-AST Frechet rows"
            ),
        },
        "mandatory_mutant_certificate": mutants,
        "checks": {**checks, "all": all_checks},
        "decision": decision,
        "evidence_boundary": {
            "proved": (
                "exact tagged R/R_squared split, formal Rcal derivative, componentwise "
                "post-adjoint Euler-Green rows, typed component-local causal provenance, "
                "and exact recomposition to v5.6.7.8"
            ),
            "not_proved": (
                "raw Frechet rows, K/a/Robin, remaining 18 components, moving shape, "
                "full Green theorem, full variational principle, C1, or N1"
            ),
            "Route_C_used": False,
            "quotient_or_margin_argument_used": False,
            "artifact_written": False,
        },
    }


def main() -> int:
    print(
        json.dumps(
            _jsonable(build_report()),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
