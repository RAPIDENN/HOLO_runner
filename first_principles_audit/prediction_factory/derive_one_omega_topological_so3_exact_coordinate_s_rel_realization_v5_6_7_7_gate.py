#!/usr/bin/env python3
"""Fail-closed semantic-audit ledger for the finite ``S_rel`` formula map.

This gate records a strong *structural* result and an equally important
negative result.  A transitive, closed AST IR binds the implementation paths
for the twenty v5.6.7.1 densities, their local helpers, parameter use-sites,
and the domain/subtraction assembly.  That IR is useful for killing semantic
source mutations, but an AST fingerprint is not a denotational proof that the
coordinate program equals the pinned mathematical action.

Consequently ``restricted_exact_real_twenty_component_S_rel_coordinate_\
realization_pass`` is deliberately false.  The structured axiom contract,
typed ledger, reference ledger, and source-mutant campaign are retained as
necessary evidence only.  No proof-assistant kernel, exact-real interpreter,
continuum theorem, numerical promotion, or physics result is claimed, and no
artifact is written.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
from itertools import combinations, permutations
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE / "artifacts"
SCHEMA = (
    "holo.one-omega-topological-so3-exact-coordinate-s-rel-"
    "realization-v5-6-7-7-gate.v1"
)

V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"
CONTRACT_BUNDLE = (
    ARTIFACTS
    / "one_omega_topological_so3_restricted_spectral_family_"
    "v5_6_4_2_pointwise_primitive_bundle.json"
)
V567_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
V567_TEST = HERE / "test_one_omega_topological_so3_route_c_full_t4_exact_primitives_v5_6_7.py"
V5671_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5671_TEST = HERE / "test_one_omega_topological_so3_route_c_full_t4_dual_local_action_v5_6_7_1.py"
V5672_SOURCE = HERE / "derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py"
V5672_TEST = HERE / "test_one_omega_topological_so3_geometric_bulk_diffeomorphism_naturality_v5_6_7_2_gate.py"
V56615_SOURCE = HERE / "derive_one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.py"
V56615_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_route_c_same_functional_pointwise_v5_6_6_15.json"
GAUSS_SOURCE = HERE / "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
GAUSS_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"
GAUSS_TEST = HERE / "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"

V5672_COMMIT = "91abcc1dcf73e597526c5fe4d510df0f00ade3b5"

SOURCE_PINS = {
    V52_ARTIFACT.name: "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    CONTRACT_BUNDLE.name: "bcbb0037a2b025d9ece7387b5962a910e31eced7294ccb5324ab764c3bc7cb26",
    V567_SOURCE.name: "df805ab77721446dded427c16c247b9685019dd0ed54e13bac4dad867d8f5d25",
    V567_TEST.name: "3fdcd09c3e575893dade6a396865a593349ebc62d28c07706d3f2b58a0caacd4",
    V5671_SOURCE.name: "afe410507da533dfff9037b5bd730d90d5931f82aaeb8d4839a48f9a4d18e0c9",
    V5671_TEST.name: "d7988e078fb81f9fa3001eaff2414962d45bfb240b024fbaacf8a9ab126b9694",
    V5672_SOURCE.name: "23d04b2d8347dca513389e0b4d7c8e329405a2e2eb4989dd1238e0d6dbf2687b",
    V5672_TEST.name: "6a26693799d22dfcba338add59d72260ec61c72ffe969ed8cefbf59a920d7fe6",
    V56615_SOURCE.name: "ca099da9f4f98a2a398cc0535ef2cd85e2e417e52fd8a7af0b87a3ef12664956",
    V56615_ARTIFACT.name: "09a98c369bfce6f04670b5be6443e78b32c0083e53e478c71f7787c364d26f7f",
    GAUSS_SOURCE.name: "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717",
    GAUSS_ARTIFACT.name: "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a",
    GAUSS_TEST.name: "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78",
}
PIN_PATHS = {
    path.name: path
    for path in (
        V52_ARTIFACT,
        CONTRACT_BUNDLE,
        V567_SOURCE,
        V567_TEST,
        V5671_SOURCE,
        V5671_TEST,
        V5672_SOURCE,
        V5672_TEST,
        V56615_SOURCE,
        V56615_ARTIFACT,
        GAUSS_SOURCE,
        GAUSS_ARTIFACT,
        GAUSS_TEST,
    )
}

EXACT_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
COEFFICIENT_ENVIRONMENT_SHA256 = "12bb13017541b0a08554f61e46775843870499bbfc80c15127ef9cdee8481fa3"
COMPACT_RELATIVE_CONTRACT_SHA256 = "16cb2a062e706aa4c92c7e43e09965cf9965ae8f488898f17c8aaa649e48775a"
TOPOLOGY_ORIENTATION_SHA256 = "3381d123147bcfdc7f81e900e2dc7e10adfc54194a5e4412df1dce72fff90d48"
GEOMETRY_CONVENTION_SHA256 = "69a24514ac0b4f2a0c7d1d6612fe94c7f42502dc9085cd141273dd93df8b6f54"
TYPED_SIGNATURE_SHA256 = "580b4dd1dfd1e82b97f6957631fde95dbe11d0a397746dd52851d20e6fadd0af"

SIDES = ("plus", "minus")
SIDE_RADIAL_SIGN = {"plus": -1, "minus": 1}
BULK_FAMILIES = ("EH", "Omega_kinetic", "Omega_potential", "P_kinetic", "full_V4", "BF")
INTERFACE_FAMILIES = ("wall", "K_foliation", "R", "R_squared", "a_squared", "Robin")
COMPONENTS = tuple(
    name
    for side in SIDES
    for name in tuple(f"{family}_bulk_{side}" for family in BULK_FAMILIES)
    + (f"GHY_{side}",)
) + INTERFACE_FAMILIES

WEIGHTS: Mapping[str, tuple[int, int, tuple[tuple[str, int], ...]]] = {
    "EH": (1, 2, (("M5", 3),)),
    "Omega_kinetic": (-1, 2, (("G", 1),)),
    "Omega_potential": (-1, 1, ()),
    "P_kinetic": (-1, 2, (("Z", 1),)),
    "full_V4": (-1, 1, (("M", 2), ("Z", 1))),
    "BF": (1, 1, ()),
    "GHY": (1, 1, (("M5", 3),)),
    "wall": (-1, 1, ()),
    "K_foliation": (1, 2, (("Mb", 2),)),
    "R": (1, 2, (("Mb", 2), ("xi", 1))),
    "R_squared": (-1, 32, (("B4_bar", 1), ("Mb", 2), ("k_infinity", -2))),
    "a_squared": (1, 2, (("Mb", 2), ("eta", 1))),
    "Robin": (-1, 2, (("kappa_hat", 1),)),
}

FORMULAS = {
    "EH": "vol5*R[g]",
    "Omega_kinetic": "vol5*g_inv(dOmega,dOmega)",
    "Omega_potential": "vol5*U[W,partial_Omega_W]",
    "P_kinetic": "vol5*g_inv*delta(P,P);P=dphi+A_cross_phi+(3/2)*phi*dlogOmega",
    "full_V4": "vol5*Omega^(-5)*V4(Omega^(3/2)*abs(phi))",
    "BF": "pair(Lambda3(J)*B,wedge,F[J_transpose*A]);pair=-tr3/2",
    "GHY": "vol4*trace_gamma(-n_rho*Gamma^rho_tangent_tangent)",
    "wall": "vol4*(2*W+beta*(Omega-1)^2/2)",
    "K_foliation": "vol4*(K_mn*K^mn-lambda_K*K^2)",
    "R": "vol4*Rcal",
    "R_squared": "vol4*Rcal^2",
    "a_squared": "vol4*a_mu*a^mu",
    "Robin": "vol4*h(E_Q*varphi-y*a_sharp,E_Q*varphi-y*a_sharp)",
}

AXIOMS = (
    {
        "id": "A01_pullback_components",
        "statement": "metric, covector, and differential-form pullbacks obey the stated coordinate component rules",
        "role": "assumption",
    },
    {
        "id": "A02_levi_civita_naturality",
        "statement": "the pinned Levi-Civita, Riemann, Ricci, and scalar-curvature conventions are natural under pullback",
        "role": "assumption",
    },
    {
        "id": "A03_so3_connection_naturality",
        "statement": "dA plus A cross A and the associated SO3 derivative transform in the pinned convention",
        "role": "assumption",
    },
    {
        "id": "A04_oriented_top_form",
        "statement": "oriented top forms transform by the signed Jacobian determinant exactly once",
        "role": "assumption",
    },
    {
        "id": "A05_ghy_definition",
        "statement": "the induced metric, outward unit conormal, second fundamental form, trace, and GHY sign use the pinned convention",
        "role": "assumption",
    },
    {
        "id": "A06_gauss_equation",
        "statement": "the contracted Gauss equation uses the pinned Riemann index order and extrinsic-curvature sign",
        "role": "assumption",
    },
    {
        "id": "A07_so3_pairing",
        "statement": "the SO3 adjoint pairing is minus one half of the three-dimensional trace",
        "role": "assumption",
    },
    {
        "id": "A08_positive_branches",
        "statement": "all square roots use the positive branch on the explicitly guarded admissible open domain",
        "role": "assumption",
    },
    {
        "id": "A09_flat_reference",
        "statement": "the fixed diagonal reference metric is constant and flat while its pulled coordinate components may vary with the embedding",
        "role": "assumption",
    },
    {
        "id": "A10_domain_linearity",
        "statement": "integration is linear only after each of the twelve bulk and eight boundary atoms is assigned to its stated domain",
        "role": "assumption",
    },
)

# Filled from the independently literal axiom table above and guarded again by
# a separate test-local oracle.  Changing both this value and AXIOMS is not a
# valid repair: the independent test deliberately rejects such a repin.
AXIOM_CONTRACT_SHA256 = "ffc551ea0222d04fff140d8ebdda4612f78fec4558b22358cd90727629c27c71"

TRUE_DECISION_KEYS = frozenset()
FALSE_DECISION_KEYS = frozenset(
    {
        "restricted_exact_real_twenty_component_S_rel_coordinate_realization_pass",
        "same_functional_symbolic_identity_pass",
        "integrated_action_pass",
        "quadrature_pass",
        "runtime_float64_exact_realization_pass",
        "margins_certified_pass",
        "uniform_N_to_infinity_bridge_pass",
        "uniform_N_to_infinity_numerical_certificate_pass",
        "all_N_q_zero_factorization_pass",
        "continuum_action_representative_independence_theorem_pass",
        "global_smooth_physical_gauge_quotient_manifold_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "P4_full_same_action_pass",
        "B4_pass",
        "B5_pass",
    }
)


class ExactCoordinateRealizationError(RuntimeError):
    """A pin, source binding, exact ledger, or quarantine boundary failed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _family(component: str) -> str:
    if component.startswith("GHY_"):
        return "GHY"
    for family in BULK_FAMILIES:
        if component.startswith(f"{family}_bulk_"):
            return family
    if component in INTERFACE_FAMILIES:
        return component
    raise ExactCoordinateRealizationError(f"unknown component: {component}")


def literal_normal_forms() -> list[dict[str, Any]]:
    """Independent exact semantic target for the twenty literal terms."""

    rows: list[dict[str, Any]] = []
    for component in COMPONENTS:
        family = _family(component)
        side = next((side for side in SIDES if component.endswith(f"_{side}")), None)
        is_bulk = "_bulk_" in component
        rows.append(
            {
                "component": component,
                "family": family,
                "domain": f"T4_x_[0,1]_{side}" if is_bulk else "T4_interface",
                "side": side,
                "reference_policy": "actual_minus_pulled_X_infinity" if is_bulk else "literal_unsubtracted",
                "coefficient": {
                    "numerator": WEIGHTS[family][0],
                    "denominator": WEIGHTS[family][1],
                    "powers": [list(item) for item in WEIGHTS[family][2]],
                },
                "formula_normal_form": FORMULAS[family],
                "pullback": (
                    "g'=J^T*g*J;A'=J^T*A;B'=Lambda3(J)*B"
                    if is_bulk
                    else "common_first_interface_fields"
                ),
                "orientation": (
                    f"det(J)={SIDE_RADIAL_SIGN[side]}" if is_bulk else "positive_T4_orientation"
                ),
                "producer": (
                    "_relative_bulk_densities_td3"
                    if is_bulk
                    else "_ghy_density_td3"
                    if family == "GHY"
                    else "_interface_component_densities_td3"
                ),
            }
        )
    return rows


# Patched to the independently serialized target after the table was fixed.
NORMAL_FORM_SHA256 = "4119a124f1419e9be3d57df13261a5af8513b8c2717d4e2a27bbeb64cea9f778"


def _literal_assignment(tree: ast.AST, name: str) -> Any:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        if node.value is None:
            break
        return ast.literal_eval(node.value)
    raise ExactCoordinateRealizationError(f"literal assignment missing: {name}")


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _assignment_expressions(node: ast.AST, name: str) -> tuple[str, ...]:
    values: list[str] = []
    for child in ast.walk(node):
        if not isinstance(child, (ast.Assign, ast.AnnAssign)):
            continue
        targets = child.targets if isinstance(child, ast.Assign) else [child.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            if child.value is not None:
                values.append(ast.unparse(child.value))
    return tuple(values)


def _return_dict(node: ast.AST) -> dict[str, str]:
    for child in ast.walk(node):
        if not isinstance(child, ast.Return) or not isinstance(child.value, ast.Dict):
            continue
        result: dict[str, str] = {}
        for key, value in zip(child.value.keys, child.value.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                result[key.value] = ast.unparse(value)
        if result:
            return result
    return {}


def _return_expressions(node: ast.AST) -> tuple[str, ...]:
    return tuple(
        ast.unparse(child.value)
        for child in ast.walk(node)
        if isinstance(child, ast.Return) and child.value is not None
    )


def _keyword_defaults(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, str]:
    return {
        argument.arg: ast.unparse(default)
        for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults)
        if default is not None
    }


SOURCE_SEMANTIC_IR_SCHEMA = "holo.v5-6-7-7.source-semantic-structural-ir.v2"
SEMANTIC_ROOTS = (
    "decode_common_first_boundary_td3",
    "_pullback_x64_and_reference15",
    "_regular_v4_td3",
    "td3_metric_geometry",
    "_bulk_component_densities_td3",
    "_relative_bulk_densities_td3",
    "_ghy_density_td3",
    "_foliation_geometry_td3",
    "_interface_component_densities_td3",
    "_bulk_components_from_boundary_td3",
    "_boundary_components_from_boundary_td3",
    "integrated_action_values_and_eta_jvps",
)
SEMANTIC_CLASSES = ("TaylorDual3", "RhoJet2")
SEMANTIC_REQUIRED_CONSTANTS = (
    "N_SPATIAL",
    "ZERO_ALPHA",
    "SIDES",
    "SIDE_RADIAL_SIGN",
    "SYMMETRIC4",
    "SYMMETRIC5",
    "B_TRIPLES",
    "REFERENCE_METRIC_DIAGONAL",
    "BULK_SECTORS",
    "INTERFACE_SECTORS",
    "LOCAL_DENSITY_COMPONENTS",
    "BULK_COMPONENTS",
    "BOUNDARY_COMPONENTS",
    "INTEGRATED_ACTION_OUTPUTS",
    "ACTION_COEFFICIENTS",
)
SEMANTIC_LANDMARK_SNIPPETS = {
    "embedding_Y_enters_jacobian_once": "jacobian_rows[4][i] = RhoJet2(Y_first[i])",
    "side_determinant_enters_jacobian_once": (
        "jacobian_rows[4][4] = RhoJet2(SIDE_RADIAL_SIGN[side])"
    ),
    "fixed_reference_metric_is_constructed": "def _reference_metric_td3()",
    "pulled_reference_channels_are_separate": "pulled_reference = _matmul(",
    "regular_V4_Omega_power_six": "radial_fourth = Omega**6 * phi_squared**2",
    "metric_inverse_is_formed": "inverse = _inverse_td3(g)",
    "metric_determinant_is_formed": "determinant = td3_determinant(g)",
    "christoffel_is_formed": "\n    christoffel = tuple(",
    "ricci_is_formed": "ricci = tuple(",
    "scalar_curvature_is_formed": "scalar_curvature = sum(",
    "riemann_lower_is_formed": "riemann_lower = tuple(",
    "curvature_dA_difference": "dconnection[m][n][a]\n                - dconnection[n][m][a]",
    "curvature_A_cross_A": "curvature_cross_sign * td3_cross(connection[m], connection[n])[a]",
    "BF_orientation_sign": "orientation = _permutation_sign(triple + complement)",
    "BF_pairing_component_sum": "primitives[\"B\"][triple_index][a]\n                * curvature[complement[0]][complement[1]][a]",
    "GHY_trace": "induced_inverse[mu][nu] * extrinsic[mu][nu]",
    "Gauss_projected_riemann": "geometry[\"riemann_lower\"][a][s][m][n]",
    "Gauss_Rcal_sign": "Rcal = projected_riemann + gauss_extrinsic_sign * (K_squared - Ktrace * Ktrace)",
    "Robin_minus_acceleration": (
        "robin_acceleration_sign * ACTION_COEFFICIENTS[\"Robin_y\"] * acceleration_vector[m]"
    ),
    "bulk_actual_minus_reference": (
        "return {sector: actual[sector] - reference[sector] for sector in BULK_SECTORS}"
    ),
    "GHY_uses_actual_boundary": (
        "components[f\"GHY_{side}\"] = _ghy_density_td3(\n            boundary_pulled,"
    ),
    "interface_is_unsubtracted": "components.update(_interface_component_densities_td3(boundary))",
    "boundary_domain_loop": "for name in BOUNDARY_COMPONENTS:",
    "bulk_domain_loop": "for name in BULK_COMPONENTS:",
    "total_after_component_integrals": (
        "math.fsum(records[name][\"value\"] for name in LOCAL_DENSITY_COMPONENTS)"
    ),
}

# Structural fingerprint of ``extract_source_semantic_IR`` on the pinned
# v5.6.7.1 source.  It is duplicated as a literal in the independent test.
SOURCE_SEMANTIC_IR_SHA256 = "97a28538504ea94ff9f6cd611da48165d0c181222f4dc4a5357ecbfebe64c471"


def _ast_sha256(node: ast.AST) -> str:
    encoded = ast.dump(node, annotate_fields=True, include_attributes=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _top_level_definitions(
    tree: ast.Module,
) -> tuple[
    dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
    dict[str, ast.ClassDef],
    dict[str, ast.AST],
]:
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    classes: dict[str, ast.ClassDef] = {}
    assignments: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node
        elif isinstance(node, ast.ClassDef):
            classes[node.name] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments[node.target.id] = node.value
    return functions, classes, assignments


def _name_calls(node: ast.AST) -> set[str]:
    return {
        child.func.id
        for child in ast.walk(node)
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
    }


def _loaded_names(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
    }


def _parameter_use_sites(owner: str, node: ast.AST) -> list[dict[str, str]]:
    sites: list[dict[str, str]] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Subscript):
            continue
        if not isinstance(child.value, ast.Name) or child.value.id != "ACTION_COEFFICIENTS":
            continue
        key_node = child.slice
        if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
            sites.append(
                {
                    "owner": owner,
                    "key": key_node.value,
                    "expression": ast.unparse(child),
                }
            )
    return sites


def extract_source_semantic_IR(text: str) -> dict[str, Any]:
    """Return a deterministic, transitively closed structural semantic IR.

    The closure includes every local function called by a root or by one of
    the two arithmetic carrier classes, plus recursively referenced module
    constants.  Per-node AST hashes retain operators, index order, literals,
    coefficient keys, and use-site names without pretending to evaluate them.
    ``closed`` therefore means source-graph closed, not denotationally proved.
    """

    tree = ast.parse(text)
    functions, classes, assignments = _top_level_definitions(tree)
    missing_roots = sorted(set(SEMANTIC_ROOTS) - set(functions))
    missing_classes = sorted(set(SEMANTIC_CLASSES) - set(classes))

    included_functions: set[str] = set()
    included_classes: set[str] = set()
    pending_functions = list(SEMANTIC_ROOTS)
    pending_classes = list(SEMANTIC_CLASSES)
    while pending_functions or pending_classes:
        if pending_functions:
            name = pending_functions.pop()
            if name in included_functions or name not in functions:
                continue
            included_functions.add(name)
            calls = _name_calls(functions[name])
        else:
            name = pending_classes.pop()
            if name in included_classes or name not in classes:
                continue
            included_classes.add(name)
            calls = _name_calls(classes[name])
        for called in sorted(calls):
            if called in functions and called not in included_functions:
                pending_functions.append(called)
            if called in classes and called not in included_classes:
                pending_classes.append(called)

    included_nodes: dict[str, ast.AST] = {
        **{name: functions[name] for name in sorted(included_functions)},
        **{name: classes[name] for name in sorted(included_classes)},
    }
    unresolved_private_calls = sorted(
        {
            called
            for node in included_nodes.values()
            for called in _name_calls(node)
            if called.startswith("_") and called not in included_functions
        }
    )

    included_constants: set[str] = set()
    pending_constants = [
        name
        for name in sorted(
            set(SEMANTIC_REQUIRED_CONSTANTS)
            | {
                loaded
                for node in included_nodes.values()
                for loaded in _loaded_names(node)
            }
        )
        if name in assignments
    ]
    while pending_constants:
        name = pending_constants.pop()
        if name in included_constants:
            continue
        included_constants.add(name)
        for loaded in sorted(_loaded_names(assignments[name])):
            if loaded in assignments and loaded not in included_constants:
                pending_constants.append(loaded)

    parameter_sites = sorted(
        (
            site
            for owner, node in included_nodes.items()
            for site in _parameter_use_sites(owner, node)
        ),
        key=lambda row: (row["owner"], row["key"], row["expression"]),
    )
    landmark_counts = {
        name: text.count(snippet)
        for name, snippet in SEMANTIC_LANDMARK_SNIPPETS.items()
    }
    required_parameter_keys = {
        "B4_bar",
        "M5_cubed",
        "Robin_kappa_hat",
        "Robin_y",
        "brane_Mb_squared",
        "brane_beta",
        "compensator_metric_G",
        "eta",
        "k_infinity",
        "lambda_K",
        "material_Z5_per_side",
        "material_mass_M",
        "xi",
    }
    observed_parameter_keys = {site["key"] for site in parameter_sites}
    missing_constants = sorted(set(SEMANTIC_REQUIRED_CONSTANTS) - included_constants)
    return {
        "schema": SOURCE_SEMANTIC_IR_SCHEMA,
        "roots": list(SEMANTIC_ROOTS),
        "classes": sorted(included_classes),
        "functions": sorted(included_functions),
        "function_ast_sha256": {
            name: _ast_sha256(functions[name]) for name in sorted(included_functions)
        },
        "class_ast_sha256": {
            name: _ast_sha256(classes[name]) for name in sorted(included_classes)
        },
        "constant_ast_sha256": {
            name: _ast_sha256(assignments[name]) for name in sorted(included_constants)
        },
        "call_graph": {
            owner: sorted(
                called
                for called in _name_calls(node)
                if called in included_functions or called in included_classes
            )
            for owner, node in sorted(included_nodes.items())
        },
        "parameter_use_sites": parameter_sites,
        "required_parameter_keys": sorted(required_parameter_keys),
        "observed_parameter_keys": sorted(observed_parameter_keys),
        "landmark_counts": landmark_counts,
        "missing_roots": missing_roots,
        "missing_classes": missing_classes,
        "missing_constants": missing_constants,
        "unresolved_private_calls": unresolved_private_calls,
        "closed": (
            not missing_roots
            and not missing_classes
            and not missing_constants
            and not unresolved_private_calls
            and observed_parameter_keys == required_parameter_keys
            and all(count == 1 for count in landmark_counts.values())
        ),
        "denotational_proof_claimed": False,
    }


EXPECTED_BULK_RETURNS = {
    "EH": "volume * M5_cubed * scalar_curvature / 2.0",
    "Omega_kinetic": "-volume * G * Omega_squared_gradient / 2.0",
    "Omega_potential": "-volume * U",
    "P_kinetic": "-volume * Z5 * P_squared / 2.0",
    "full_V4": "-volume * Z5 * material_mass ** 2 * Omega ** (-5) * V4",
    "BF": "bf_pullback_multiplier * BF_density",
}
EXPECTED_INTERFACE_RETURNS = {
    "wall": "measure * (-2.0 * W - ACTION_COEFFICIENTS['brane_beta'] * (Omega - 1.0) ** 2 / 2.0)",
    "K_foliation": "measure * Mb_squared * (K_squared - ACTION_COEFFICIENTS['lambda_K'] * Ktrace * Ktrace) / 2.0",
    "R": "measure * Mb_squared * ACTION_COEFFICIENTS['xi'] * Rcal / 2.0",
    "R_squared": "-measure * Mb_squared * ACTION_COEFFICIENTS['B4_bar'] * Rcal * Rcal / (32.0 * k_infinity ** 2)",
    "a_squared": "measure * Mb_squared * ACTION_COEFFICIENTS['eta'] * foliation['acceleration_squared'] / 2.0",
    "Robin": "-measure * ACTION_COEFFICIENTS['Robin_kappa_hat'] * robin_norm / 2.0",
}


def _source_checks(text: str) -> dict[str, bool]:
    try:
        tree = ast.parse(text)
        functions = _functions(tree)
        pullback = functions["_pullback_x64_and_reference15"]
        bulk = functions["_bulk_component_densities_td3"]
        relative = functions["_relative_bulk_densities_td3"]
        ghy = functions["_ghy_density_td3"]
        foliation = functions["_foliation_geometry_td3"]
        interface = functions["_interface_component_densities_td3"]
        boundary = functions["_boundary_components_from_boundary_td3"]
        integrated = functions["integrated_action_values_and_eta_jvps"]
    except (SyntaxError, KeyError, ExactCoordinateRealizationError):
        return {name: False for name in SOURCE_CHECK_NAMES}

    bulk_returns = _return_dict(bulk)
    interface_returns = _return_dict(interface)
    boundary_unparse = ast.unparse(boundary)
    integrated_unparse = ast.unparse(integrated)
    try:
        inventory_ok = (
            tuple(_literal_assignment(tree, "SIDES")) == SIDES
            and tuple(_literal_assignment(tree, "BULK_SECTORS")) == BULK_FAMILIES
            and tuple(_literal_assignment(tree, "INTERFACE_SECTORS")) == INTERFACE_FAMILIES
            and dict(_literal_assignment(tree, "SIDE_RADIAL_SIGN")) == {"plus": -1.0, "minus": 1.0}
        )
    except (ValueError, ExactCoordinateRealizationError):
        inventory_ok = False

    return {
        "component_inventory": inventory_ok,
        "metric_pullback": (
            "_matmul(_matmul(jacobian_transpose, metric, zero), jacobian, zero)"
            in _assignment_expressions(pullback, "pulled_metric")
        ),
        "connection_pullback": (
            "_matmul(jacobian_transpose, connection, zero)"
            in _assignment_expressions(pullback, "pulled_connection")
        ),
        "three_form_pullback": (
            "_det3(tuple((tuple((jacobian[s][t] for t in target)) for s in source)))"
            in _assignment_expressions(pullback, "minor")
        ),
        "bulk_coefficients_and_signs": bulk_returns == EXPECTED_BULK_RETURNS,
        "Omega_P_and_V4_definitions": (
            "log_omega.exp()" in _assignment_expressions(bulk, "Omega")
            and "tuple((Omega * entry for entry in dlog))" in _assignment_expressions(bulk, "dOmega")
            and "-G * Omega * W / (3.0 * M5_cubed)" in _assignment_expressions(bulk, "W_Omega")
            and "W_Omega * W_Omega / (2.0 * G) - 2.0 * W * W / (3.0 * M5_cubed)"
            in _assignment_expressions(bulk, "U")
            and "_regular_v4_td3(Omega, phi)" in _assignment_expressions(bulk, "V4")
            and "+ 1.5 * phi[a] * dlog[m]" in ast.unparse(bulk)
        ),
        "BF_curvature_orientation_pairing": (
            _keyword_defaults(bulk).get("curvature_cross_sign") == "1.0"
            and _keyword_defaults(bulk).get("bf_pullback_multiplier") == "1.0"
            and "_permutation_sign(triple + complement)"
            in _assignment_expressions(bulk, "orientation")
            and any(
                "primitives['B'][triple_index][a] * curvature[complement[0]][complement[1]][a]"
                in value
                for value in _assignment_expressions(bulk, "BF_density")
            )
        ),
        "bulk_reference_subtraction": (
            "tuple(pulled_reference15) + tuple((RhoJet2(0.0) for _ in range(49)))"
            in _assignment_expressions(relative, "reference_channels")
            and "{sector: actual[sector] - reference[sector] for sector in BULK_SECTORS}"
            in _return_expressions(relative)
        ),
        "GHY_outward_normal_and_sign": (
            _keyword_defaults(ghy).get("normal_sign") == "-1.0"
            and "normal_sign / inverse[4][4].sqrt()"
            in _assignment_expressions(ghy, "normal_covector_rho")
            and "tuple((tuple((-normal_covector_rho * geometry['christoffel'][4][mu][nu] for nu in range(4))) for mu in range(4)))"
            in _assignment_expressions(ghy, "extrinsic")
            and "ACTION_COEFFICIENTS['M5_cubed'] * induced_geometry['sqrt_abs_determinant'] * theta"
            in _return_expressions(ghy)
        ),
        "Gauss_sign_and_foliation": (
            _keyword_defaults(foliation).get("gauss_extrinsic_sign") == "1.0"
            and "projected_riemann + gauss_extrinsic_sign * (K_squared - Ktrace * Ktrace)"
            in _assignment_expressions(foliation, "Rcal")
            and "tuple((-tau_gradient[i] / normalization for i in range(4)))"
            in _assignment_expressions(foliation, "u_covector")
        ),
        "Robin_minus_y_and_interface_coefficients": (
            _keyword_defaults(interface).get("robin_acceleration_sign") == "-1.0"
            and "tuple((phi_H[m] + robin_acceleration_sign * ACTION_COEFFICIENTS['Robin_y'] * acceleration_vector[m] for m in range(4)))"
            in _assignment_expressions(interface, "robin_vector")
            and interface_returns == EXPECTED_INTERFACE_RETURNS
        ),
        "unsubtracted_GHY_and_shared_producer": (
            "boundary_pulled, _boundary_reference = _pullback_x64_and_reference15" in boundary_unparse
            and "components[f'GHY_{side}'] = _ghy_density_td3(boundary_pulled, side=side)"
            in boundary_unparse
            and "components.update(_interface_component_densities_td3(boundary))"
            in boundary_unparse
        ),
        "separate_domains_then_total": (
            "for name in BOUNDARY_COMPONENTS:" in integrated_unparse
            and "for rho, radial_weight in zip(rho_nodes, rho_weights):" in integrated_unparse
            and "for name in BULK_COMPONENTS:" in integrated_unparse
            and "combined_weight = float(tangential_weight) * float(radial_weight)"
            in integrated_unparse
            and "math.fsum((records[name]['value'] for name in LOCAL_DENSITY_COMPONENTS))"
            in integrated_unparse
        ),
    }


SOURCE_CHECK_NAMES = (
    "component_inventory",
    "metric_pullback",
    "connection_pullback",
    "three_form_pullback",
    "bulk_coefficients_and_signs",
    "Omega_P_and_V4_definitions",
    "BF_curvature_orientation_pairing",
    "bulk_reference_subtraction",
    "GHY_outward_normal_and_sign",
    "Gauss_sign_and_foliation",
    "Robin_minus_y_and_interface_coefficients",
    "unsubtracted_GHY_and_shared_producer",
    "separate_domains_then_total",
    "transitive_closed_structural_semantic_IR",
)


def audit_source_text(text: str, *, require_pin: bool = True) -> dict[str, Any]:
    checks = _source_checks(text)
    try:
        semantic_ir = extract_source_semantic_IR(text)
        semantic_ir_sha256 = _canonical_sha256(semantic_ir)
        semantic_ir_pass = (
            semantic_ir["closed"]
            and semantic_ir_sha256 == SOURCE_SEMANTIC_IR_SHA256
        )
    except (SyntaxError, KeyError, TypeError, ValueError):
        semantic_ir = None
        semantic_ir_sha256 = None
        semantic_ir_pass = False
    checks["transitive_closed_structural_semantic_IR"] = semantic_ir_pass
    observed = hashlib.sha256(text.encode("utf-8")).hexdigest()
    pin_pass = observed == SOURCE_PINS[V5671_SOURCE.name]
    passed = all(checks.values()) and (pin_pass or not require_pin)
    return {
        "pass": passed,
        "pin_required": require_pin,
        "pin_pass": pin_pass,
        "observed_sha256": observed,
        "checks": checks,
        "failed_checks": sorted(name for name, value in checks.items() if not value),
        "semantic_target_sha256": NORMAL_FORM_SHA256 if passed else None,
        "source_semantic_IR_sha256": semantic_ir_sha256,
        "expected_source_semantic_IR_sha256": SOURCE_SEMANTIC_IR_SHA256,
        "source_semantic_IR": semantic_ir,
    }


SOURCE_MUTANTS = {
    "coefficient_EH_half": (
        '"EH": volume * M5_cubed * scalar_curvature / 2.0',
        '"EH": volume * M5_cubed * scalar_curvature / 3.0',
    ),
    "bulk_kinetic_sign": (
        '"Omega_kinetic": -volume * G * Omega_squared_gradient / 2.0',
        '"Omega_kinetic": volume * G * Omega_squared_gradient / 2.0',
    ),
    "metric_pullback_order": (
        "pulled_metric = _matmul(_matmul(jacobian_transpose, metric, zero), jacobian, zero)",
        "pulled_metric = _matmul(_matmul(jacobian, metric, zero), jacobian_transpose, zero)",
    ),
    "connection_pullback_order": (
        "pulled_connection = _matmul(jacobian_transpose, connection, zero)",
        "pulled_connection = _matmul(jacobian, connection, zero)",
    ),
    "three_form_minor": (
        "minor = _det3(tuple(tuple(jacobian[s][t] for t in target) for s in source))",
        "minor = _det2(tuple(tuple(jacobian[s][t] for t in target) for s in source))",
    ),
    "BF_orientation": (
        "orientation = _permutation_sign(triple + complement)",
        "orientation = -_permutation_sign(triple + complement)",
    ),
    "GHY_normal": ("normal_sign: float = -1.0", "normal_sign: float = 1.0"),
    "Gauss_sign": (
        "Rcal = projected_riemann + gauss_extrinsic_sign * (K_squared - Ktrace * Ktrace)",
        "Rcal = projected_riemann + gauss_extrinsic_sign * (Ktrace * Ktrace - K_squared)",
    ),
    "Robin_sign": ("robin_acceleration_sign: float = -1.0", "robin_acceleration_sign: float = 1.0"),
    "reference_subtraction": (
        "actual[sector] - reference[sector]",
        "reference[sector] - actual[sector]",
    ),
    "reference_scope_GHY": (
        "components[f\"GHY_{side}\"] = _ghy_density_td3(\n            boundary_pulled,",
        "components[f\"GHY_{side}\"] = _ghy_density_td3(\n            _boundary_reference,",
    ),
    "shared_interface_producer": (
        "components.update(_interface_component_densities_td3(boundary))",
        "components.update({})",
    ),
    "domain_partition": ("for name in BOUNDARY_COMPONENTS:", "for name in BULK_COMPONENTS:"),
    "regular_V4_power": (
        "radial_fourth = Omega**6 * phi_squared**2",
        "radial_fourth = Omega**5 * phi_squared**2",
    ),
    "scalar_curvature_factor_two": (
        '"EH": volume * M5_cubed * scalar_curvature / 2.0',
        '"EH": volume * M5_cubed * (2.0 * scalar_curvature) / 2.0',
    ),
    "curvature_dA_sum": (
        "dconnection[m][n][a]\n                - dconnection[n][m][a]",
        "dconnection[m][n][a]\n                + dconnection[n][m][a]",
    ),
    "embedding_Y_deleted_from_jacobian": (
        "jacobian_rows[4][i] = RhoJet2(Y_first[i])",
        "jacobian_rows[4][i] = zero",
    ),
    "side_determinant_deleted_from_jacobian": (
        "jacobian_rows[4][4] = RhoJet2(SIDE_RADIAL_SIGN[side])",
        "jacobian_rows[4][4] = one",
    ),
    "GHY_factor_two": ("        * theta\n", "        * (2.0 * theta)\n"),
    "projected_Riemann_index_permutation": (
        'geometry["riemann_lower"][a][s][m][n]',
        'geometry["riemann_lower"][a][m][s][n]',
    ),
    "reference_metric_derived_from_actual": (
        "reference = tuple(tuple(RhoJet2(entry) for entry in row) for row in _reference_metric_td3())",
        "reference = metric",
    ),
    "Z5_rebound_to_equal_valued_mass": (
        'Z5 = ACTION_COEFFICIENTS["material_Z5_per_side"]',
        'Z5 = ACTION_COEFFICIENTS["material_mass_M"]',
    ),
    "permutation_sign_inverted": (
        "return -1 if inversions % 2 else 1",
        "return 1 if inversions % 2 else -1",
    ),
    "wrong_V4_call_with_source_rehash": (
        "V4 = _regular_v4_td3(Omega, phi)",
        "V4 = _regular_v4_td3(Omega * Omega, phi)",
    ),
}


def source_mutant_campaign(text: str) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, (old, new) in SOURCE_MUTANTS.items():
        occurrence_count = text.count(old)
        mutant = text.replace(old, new, 1)
        audit = audit_source_text(mutant, require_pin=False)
        records[name] = {
            "fixture_occurrence_count": occurrence_count,
            "killed": occurrence_count == 1 and not audit["pass"],
            "failed_checks": audit["failed_checks"],
        }
    return {
        "records": records,
        "all_mutants_killed": bool(records) and all(record["killed"] for record in records.values()),
    }


def _permutation_sign(values: Sequence[int]) -> int:
    inversions = sum(
        1
        for left in range(len(values))
        for right in range(left + 1, len(values))
        if values[left] > values[right]
    )
    return -1 if inversions % 2 else 1


def _bf_exact_ledger() -> dict[str, Any]:
    grouped: dict[tuple[int, int, int], list[int]] = {
        triple: [] for triple in combinations(range(5), 3)
    }
    for order in permutations(range(5)):
        triple_order = order[:3]
        pair_order = order[3:]
        triple = tuple(sorted(triple_order))
        contribution = (
            _permutation_sign(order)
            * _permutation_sign(tuple(triple.index(value) for value in triple_order))
            * _permutation_sign(tuple(sorted(pair_order).index(value) for value in pair_order))
        )
        grouped[triple].append(contribution)
    coefficients = {
        str(triple): sum(terms) // 12 for triple, terms in grouped.items()
    }
    expected = {
        str(triple): _permutation_sign(triple + tuple(sorted(set(range(5)) - set(triple))))
        for triple in combinations(range(5), 3)
    }

    def epsilon(i: int, j: int, k: int) -> int:
        if len({i, j, k}) < 3:
            return 0
        return _permutation_sign((i, j, k))

    generators = tuple(
        tuple(tuple(epsilon(i, j, k) for k in range(3)) for j in range(3))
        for i in range(3)
    )
    traces = tuple(
        tuple(
            sum(generators[a][j][k] * generators[b][k][j] for j in range(3) for k in range(3))
            for b in range(3)
        )
        for a in range(3)
    )
    return {
        "sorted_three_subsets": len(grouped),
        "permutation_terms_per_subset": sorted({len(terms) for terms in grouped.values()}),
        "normalized_coefficients": coefficients,
        "expected_orientation_coefficients": expected,
        "trace_Ta_Tb": [list(row) for row in traces],
        "pairing": "<X,Y>=-tr3(XY)/2",
        "pullback_determinants": SIDE_RADIAL_SIGN,
        "pass": (
            len(grouped) == 10
            and all(len(terms) == 12 for terms in grouped.values())
            and coefficients == expected
            and traces == ((-2, 0, 0), (0, -2, 0), (0, 0, -2))
        ),
    }


def _reference_ledger() -> dict[str, Any]:
    survivors = {
        "EH": "0: constant flat metric has R=0",
        "Omega_kinetic": "0: Omega=1 has dOmega=0",
        "Omega_potential": "-sqrt(abs(det(g_infinity)))*U(1)",
        "P_kinetic": "0: phi=A=0 and dphi=dlogOmega=0",
        "full_V4": "0: V4(0)=0",
        "BF": "0: B=0 and F[0]=0",
    }
    return {
        "bulk_reference_normal_forms": survivors,
        "only_nonzero_bulk_reference_family": "Omega_potential",
        "bulk_subtracted": True,
        "GHY_subtracted": False,
        "shared_interface_subtracted": False,
        "curved_graph_GHY_counterexample": {
            "formula": "Theta_s=s*Y_second/[b*e*(e^-1+b^-1*Y_prime^2)^(3/2)]",
            "exact_specialization": "b=e=1,Y_prime=1,Y_second=1/2 => Theta_s=s/(4*sqrt(2)) != 0",
            "meaning": "a flat ambient metric does not make GHY vanish on a curved graph",
        },
        "planar_fixed_reference": "Y_infinity=0 => Y_prime=Y_second=0 => Theta_s=0",
        "pass": set(survivors) == set(BULK_FAMILIES),
    }


def _axiom_ledger() -> dict[str, Any]:
    axiom_hash = _canonical_sha256(AXIOMS)
    ids = [record.get("id") for record in AXIOMS if isinstance(record, dict)]
    roles = [record.get("role") for record in AXIOMS if isinstance(record, dict)]
    structurally_valid = (
        len(AXIOMS) == 10
        and len(ids) == len(AXIOMS)
        and len(set(ids)) == len(ids)
        and all(isinstance(record.get("statement"), str) and record["statement"] for record in AXIOMS)
        and roles == ["assumption"] * len(AXIOMS)
    )
    return {
        "records": [dict(record) for record in AXIOMS if isinstance(record, dict)],
        "sha256": axiom_hash,
        "expected_sha256": AXIOM_CONTRACT_SHA256,
        "structurally_valid": structurally_valid,
        "pass": structurally_valid and axiom_hash == AXIOM_CONTRACT_SHA256,
        "meaning": (
            "These are explicit assumptions, not equations proved by this Python gate. "
            "Their hash protects the scope but cannot establish the theorem by itself."
        ),
    }


def _semantic_discharge_ledger() -> dict[str, Any]:
    obligations = [
        {
            "id": "D01_exact_real_denotation",
            "discharged": False,
            "reason": (
                "the audited producer executes custom Taylor objects and binary64 bodies; "
                "no independently defined exact-real denotational interpreter is compared"
            ),
        },
        {
            "id": "D02_formula_to_action_derivation",
            "discharged": False,
            "reason": (
                "the pinned action is prose-valued JSON rather than a parsed formal term whose "
                "normalization is checked against the source IR"
            ),
        },
        {
            "id": "D03_axiom_application",
            "discharged": False,
            "reason": (
                "the structured axioms are scope assumptions; their hypotheses and each rewrite "
                "step are not checked by a proof kernel"
            ),
        },
        {
            "id": "D04_external_helper_denotation",
            "discharged": False,
            "reason": (
                "the source-graph closure fingerprints dynamic pinned helpers but does not import "
                "their semantics into one closed mathematical IR"
            ),
        },
    ]
    return {
        "obligations": obligations,
        "all_obligations_discharged": all(row["discharged"] for row in obligations),
        "pass": False,
        "conclusion": (
            "The structural IR is mutation-sensitive evidence only. The restricted exact-real "
            "S_rel realization predicate must remain false."
        ),
    }


def _eval_float_expression(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_float_expression(node.operand)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "math"
        and node.func.attr == "sqrt"
        and len(node.args) == 1
        and not node.keywords
    ):
        return math.sqrt(_eval_float_expression(node.args[0]))
    raise ExactCoordinateRealizationError("unsupported coefficient expression")


def _source_action_coefficients(text: str) -> dict[str, float]:
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "ACTION_COEFFICIENTS" for target in node.targets):
            continue
        if not isinstance(node.value, ast.Dict):
            break
        result: dict[str, float] = {}
        for key, value in zip(node.value.keys, node.value.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                raise ExactCoordinateRealizationError("coefficient key is not a string literal")
            result[key.value] = _eval_float_expression(value)
        return result
    raise ExactCoordinateRealizationError("ACTION_COEFFICIENTS not found")


def _parameter_ledger(contract: Mapping[str, Any], source_text: str) -> dict[str, Any]:
    source = _source_action_coefficients(source_text)
    parameters = contract["coefficient_parameters"]
    bindings = {
        name: {
            "source_binary64": source[name].hex(),
            "contract_binary64": float(parameters[name]).hex(),
            "equal": source[name].hex() == float(parameters[name]).hex(),
        }
        for name in source
    }
    return {
        "bindings": bindings,
        "formal_weight_symbols_remain_named": sorted(
            {name for _n, _d, powers in WEIGHTS.values() for name, _power in powers}
        ),
        "Robin_y_squared_not_substituted_for_Robin_y": "Robin_y_squared" not in source,
        "pass": all(record["equal"] for record in bindings.values())
        and "Robin_y" in source
        and "Robin_y_squared" not in source,
    }


def _load_v5672() -> Any:
    name = "_v5672_exact_coordinate_realization_pin"
    spec = importlib.util.spec_from_file_location(name, V5672_SOURCE)
    if spec is None or spec.loader is None:
        raise ExactCoordinateRealizationError("cannot load pinned v5.6.7.2 producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


TYPED_REQUIRED_OPERATORS = {
    "EH": {"multiply_bulk_scalar_density", "scalar_curvature", "bulk_volume"},
    "Omega_kinetic": {"multiply_bulk_scalar_density", "contract_covectors5", "exterior_derivative_scalar5"},
    "Omega_potential": {"multiply_bulk_scalar_density", "bulk_potential_from_W", "superpotential_derivative"},
    "P_kinetic": {"multiply_bulk_scalar_density", "associated_one_form_norm", "conformal_P", "covariant_derivative_phi"},
    "full_V4": {"multiply_bulk_scalar_density", "weighted_full_V4", "associated_scalar_norm"},
    "BF": {"invariant_B_wedge_F", "connection_curvature"},
    "GHY": {"multiply_boundary_scalar_density", "outward_mean_curvature", "boundary_volume"},
    "wall": {"multiply_boundary_scalar_density", "wall_scalar", "boundary_trace_scalar"},
    "K_foliation": {"multiply_boundary_scalar_density", "khronon_K_quadratic"},
    "R": {"multiply_boundary_scalar_density", "khronon_spatial_curvature"},
    "R_squared": {"multiply_boundary_scalar_density", "square_boundary_scalar", "khronon_spatial_curvature"},
    "a_squared": {"multiply_boundary_scalar_density", "contract_covectors4", "khronon_acceleration"},
    "Robin": {"multiply_boundary_scalar_density", "Robin_groupoid_quadratic", "khronon_acceleration"},
}


def _signature_operators(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, (tuple, list)):
        if len(value) >= 2 and value[0] == "operator" and isinstance(value[1], str):
            result.add(value[1])
        for item in value:
            result.update(_signature_operators(item))
    return result


def _typed_geometric_ledger() -> dict[str, Any]:
    module = _load_v5672()
    expressions = module.build_component_expressions("baseline")
    signatures = {
        name: module._expression_signature(expression)
        for name, expression in expressions.items()
    }
    weights = {
        name: (
            module._green_component_weight(name).numerator,
            module._green_component_weight(name).denominator,
            module._green_component_weight(name).powers,
        )
        for name in expressions
    }
    expected_weights = {name: WEIGHTS[_family(name)] for name in COMPONENTS}
    operator_checks = {
        name: TYPED_REQUIRED_OPERATORS[_family(name)] <= _signature_operators(signature)
        for name, signature in signatures.items()
    }
    signature_hash = _canonical_sha256(signatures)
    return {
        "component_order": list(expressions),
        "signature_sha256": signature_hash,
        "expected_signature_sha256": TYPED_SIGNATURE_SHA256,
        "operator_checks": operator_checks,
        "weights": {
            name: [weight[0], weight[1], [list(item) for item in weight[2]]]
            for name, weight in weights.items()
        },
        "pass": (
            tuple(expressions) == COMPONENTS
            and signature_hash == TYPED_SIGNATURE_SHA256
            and weights == expected_weights
            and all(operator_checks.values())
        ),
    }


def _pinned_contracts() -> dict[str, Any]:
    v52 = json.loads(V52_ARTIFACT.read_text(encoding="utf-8"))
    bundle = json.loads(CONTRACT_BUNDLE.read_text(encoding="utf-8"))
    negative = json.loads(V56615_ARTIFACT.read_text(encoding="utf-8"))
    gauss = json.loads(GAUSS_ARTIFACT.read_text(encoding="utf-8"))
    action = bundle["action_contract"]
    v52_action = v52["exact_classical_charter"]["exact_action"]
    hashes = {
        "exact_action": _canonical_sha256(action["exact_action"]),
        "coefficient_environment": _canonical_sha256(action["coefficient_parameters"]),
        "compact_relative_contract": _canonical_sha256(action["compact_relative_action_contract"]),
        "topology_orientation": _canonical_sha256(action["topology_orientation"]),
        "geometry_convention": _canonical_sha256(bundle["geometry_convention"]),
    }
    expected = {
        "exact_action": EXACT_ACTION_SHA256,
        "coefficient_environment": COEFFICIENT_ENVIRONMENT_SHA256,
        "compact_relative_contract": COMPACT_RELATIVE_CONTRACT_SHA256,
        "topology_orientation": TOPOLOGY_ORIENTATION_SHA256,
        "geometry_convention": GEOMETRY_CONVENTION_SHA256,
    }
    return {
        "hashes": hashes,
        "expected_hashes": expected,
        "exact_action_equal_to_v5_2": action["exact_action"] == v52_action,
        "v5_6_6_15_negative_only": negative["decision"].get("same_functional_symbolic_identity_pass") is False,
        "Gauss_corrigendum_consumed": (
            gauss["decision"].get("Gauss_sign_mismatch_reproduced") is True
            and gauss["decision"].get("v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma") is False
        ),
        "action_contract": action,
        "pass": hashes == expected
        and action["exact_action"] == v52_action
        and negative["decision"].get("same_functional_symbolic_identity_pass") is False
        and gauss["decision"].get("Gauss_sign_mismatch_reproduced") is True
        and gauss["decision"].get("v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma") is False,
    }


def _source_pins() -> dict[str, Any]:
    observed = {name: _sha256(path) for name, path in PIN_PATHS.items()}
    matches = {name: observed[name] == expected for name, expected in SOURCE_PINS.items()}
    return {
        "expected": dict(SOURCE_PINS),
        "observed": observed,
        "matches": matches,
        "v5_6_7_2_commit_pin": V5672_COMMIT,
        "pass": all(matches.values()),
    }


def build_report() -> dict[str, Any]:
    pins = _source_pins()
    contracts = _pinned_contracts()
    source_text = V5671_SOURCE.read_text(encoding="utf-8")
    source_link = audit_source_text(source_text)
    mutants = source_mutant_campaign(source_text)
    typed = _typed_geometric_ledger()
    normal_forms = literal_normal_forms()
    normal_hash = _canonical_sha256(normal_forms)
    normal_pass = normal_hash == NORMAL_FORM_SHA256 and len(normal_forms) == 20
    bf = _bf_exact_ledger()
    reference = _reference_ledger()
    parameters = _parameter_ledger(contracts["action_contract"], source_text)
    axioms = _axiom_ledger()
    semantic_discharge = _semantic_discharge_ledger()
    structural_evidence_pass = all(
        (
            pins["pass"],
            contracts["pass"],
            source_link["pass"],
            mutants["all_mutants_killed"],
            typed["pass"],
            normal_pass,
            bf["pass"],
            reference["pass"],
            parameters["pass"],
            axioms["pass"],
        )
    )
    restricted_pass = structural_evidence_pass and semantic_discharge["pass"]
    decision = {
        "restricted_exact_real_twenty_component_S_rel_coordinate_realization_pass": restricted_pass,
        **{key: False for key in sorted(FALSE_DECISION_KEYS)},
    }
    return {
        "schema": SCHEMA,
        "title": "Fail-closed structural audit of the pinned finite S_rel coordinate program",
        "theorem": {
            "statement": (
                "The pinned v5.6.7.1 implementation has a closed, mutation-sensitive "
                "structural source IR covering its twenty density paths and named "
                "helpers. This does not prove that its exact-real denotation equals "
                "the compact-relative S_rel action; that predicate remains false."
            ),
            "relative_to_axioms": axioms["records"],
            "not_claimed": [
                "proof-assistant verification",
                "exact-real denotational equivalence",
                "float64 runtime exactness or numerical enclosure",
                "a physical detection or empirical physics result",
                "uniform all-N or q-continuum promotion",
            ],
        },
        "source_pins": pins,
        "contract_pins": {key: value for key, value in contracts.items() if key != "action_contract"},
        "source_AST_linkage": source_link,
        "normal_forms": {
            "rows": normal_forms,
            "component_count": len(normal_forms),
            "sha256": normal_hash,
            "expected_sha256": NORMAL_FORM_SHA256,
            "pass": normal_pass,
        },
        "typed_geometric_producer": typed,
        "parameter_environment": parameters,
        "axiom_contract": axioms,
        "BF_orientation_and_pairing": bf,
        "reference_subtraction": reference,
        "mutant_campaign": mutants,
        "structural_evidence_pass": structural_evidence_pass,
        "semantic_discharge": semantic_discharge,
        "decision": decision,
        "evidence_boundary": (
            "A closed AST/source graph is not a semantic identity proof. v5.6.6.15 "
            "is consumed solely as sampled negative history; no exact-real identity, "
            "sample, quadrature, finite margin, legacy bridge, C1/N1, P4, B4 or B5 "
            "result is promoted."
        ),
    }


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("schema") != SCHEMA:
        raise ExactCoordinateRealizationError("schema drift")
    decision = report.get("decision")
    if not isinstance(decision, dict):
        raise ExactCoordinateRealizationError("decision mapping missing")
    if {key for key, value in decision.items() if value} != set(TRUE_DECISION_KEYS):
        raise ExactCoordinateRealizationError("positive decision allowlist drift")
    if {key for key, value in decision.items() if not value} != set(FALSE_DECISION_KEYS):
        raise ExactCoordinateRealizationError("fail-closed decision allowlist drift")
    if decision["restricted_exact_real_twenty_component_S_rel_coordinate_realization_pass"] is not False:
        raise ExactCoordinateRealizationError("undischarged semantic predicate was promoted")
    if not report["source_AST_linkage"]["pass"]:
        raise ExactCoordinateRealizationError("v5.6.7.1 AST linkage failed")
    if not report["mutant_campaign"]["all_mutants_killed"]:
        raise ExactCoordinateRealizationError("source mutant survived")
    if report["structural_evidence_pass"] is not True:
        raise ExactCoordinateRealizationError("structural evidence ledger failed")
    if not report["axiom_contract"]["pass"]:
        raise ExactCoordinateRealizationError("structured axiom contract failed")
    if report["semantic_discharge"]["pass"] is not False:
        raise ExactCoordinateRealizationError("semantic discharge ledger drift")


def main() -> None:
    report = build_report()
    validate_report(report)
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
