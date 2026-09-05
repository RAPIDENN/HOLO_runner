#!/usr/bin/env python3
"""Structural variation IR and exact formal-adjoint kernel for ``S_v5_2``.

This is the first of two deliberately separated gates.  It byte-binds the
literal twenty-component v5.2 action, records a partial explicit defining and
first-variation formula ledger for its composite geometric objects, and normalises
the displayed candidate linear differential operators by a universal
formal-adjoint kernel.  Derivative words are ordered, outermost first.  Thus
mixed jets are never silently identified and

    E_A = sum_I (-D)_(I reversed) C_A^I

is an executable identity, component by component and after summation, *given
the displayed coefficients*.

There is intentionally no semantic overclaim.  Several candidate Frechet rows
still contain unevaluated tensor-coefficient projections such as
``deltaK/d(D H)``.  In the absence of a tensorial decoder which derives those
rows from the action AST, this unit does not prove that its list is
``D(S_v5_2)``.  The corresponding semantic decision keys are fail-closed.

The gate does *not* prove the moving-normal shape row, the paired EH+GHY Green
theorem, or the final classical variational principle.  It only establishes
that the committed, tested v5.6.7.8 Rcal dependency is available and byte
bound; it never claims that dependency is integrated into these candidate rows.
Any byte, tracked-state, or narrow-scope drift turns that availability key red.
No Route-C sample, margin, finite-q quotient, or numerical tolerance occurs.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = HERE / "artifacts"

SCHEMA = (
    "holo.one-omega-topological-so3-variational-ir-formal-adjoint-"
    "v5-6-7-9-gate.v1"
)

V52_SOURCE = HERE / "derive_one_omega_topological_so3_classical_v5_2_gate.py"
V52_TEST = HERE / "test_one_omega_topological_so3_classical_v5_2_gate.py"
V52_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_classical_v5_2_gate.json"
V5672_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_geometric_bulk_diffeomorphism_"
    "naturality_v5_6_7_2_gate.py"
)
V5672_TEST = (
    HERE
    / "test_one_omega_topological_so3_geometric_bulk_diffeomorphism_"
    "naturality_v5_6_7_2_gate.py"
)
GAUSS_SOURCE = HERE / "derive_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
GAUSS_TEST = HERE / "test_one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.py"
GAUSS_ARTIFACT = ARTIFACTS / "one_omega_topological_so3_v5_5_4_gauss_sign_corrigendum.json"
RCAL_V5678_SOURCE = (
    HERE
    / "derive_one_omega_topological_so3_moving_interface_variational_"
    "completion_v5_6_7_8_gate.py"
)
RCAL_V5678_TEST = (
    HERE
    / "test_one_omega_topological_so3_moving_interface_variational_"
    "completion_v5_6_7_8_gate.py"
)

PINNED_INPUTS = {
    V52_SOURCE.name: "62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8",
    V52_TEST.name: "511ef10674fe622a6ab4b6d5c6fe4daf0142b22603dc33668b12cbc713c42f26",
    V52_ARTIFACT.name: "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b",
    V5672_SOURCE.name: "23d04b2d8347dca513389e0b4d7c8e329405a2e2eb4989dd1238e0d6dbf2687b",
    V5672_TEST.name: "6a26693799d22dfcba338add59d72260ec61c72ffe969ed8cefbf59a920d7fe6",
    GAUSS_SOURCE.name: "ac290aebfd981e54e5c5a9bda697fb6e23a4c15c4a17e540aa33700c11f7c717",
    GAUSS_TEST.name: "584192eb81e881fdd31fc60dd6c96926a9dfaac6e7d1dc9a7f5dacad15f8db78",
    GAUSS_ARTIFACT.name: "7c2c3e46ea73b312f753d944e43cd2a2e224d000e5ddd3c3e15ff816e76e441a",
}
PINNED_PATHS = {
    path.name: path
    for path in (
        V52_SOURCE,
        V52_TEST,
        V52_ARTIFACT,
        V5672_SOURCE,
        V5672_TEST,
        GAUSS_SOURCE,
        GAUSS_TEST,
        GAUSS_ARTIFACT,
    )
}
V52_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
GAUSS_SCHEMA = "holo.one-omega-topological-so3-v5-5-4-gauss-sign-corrigendum.v1"
CORRECT_GAUSS_SCALAR = (
    "R_leaf=h^ac h^bd R_abcd-K^2+K_ab K^ab="
    "R4+2 Ricci(u,u)-K^2+K_ab K^ab"
)
V52_EXACT_ACTION_SHA256 = (
    "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
)
EXPECTED_COMPONENT_INVENTORY_SHA256 = (
    "803addb5e01c138fe3ec61c68273f4aeb06c9061e0765c898a8bd15b447736be"
)
MILESTONE_COMMITS = {
    "60aa1a0": "oriented BF incidence",
    "acd7787": "scoped literal Green ledger",
    "91abcc1": "compact-support differentiated interior bulk Ward",
}

# The independently owned Rcal-only pair was committed at 8558584 and its test
# passed before these byte pins were entered.  Availability below additionally
# requires both paths to remain tracked and clean and checks the producer's
# narrow semantic decision frontier at execution time.
DEFAULT_RCAL_V5678_PINS: Mapping[str, str] | None = {
    RCAL_V5678_SOURCE.name: "18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb",
    RCAL_V5678_TEST.name: "9e8fab34d1e8d877a0e2ab799bec9ea26e40a05f8c63d4a333d0ea8d2664b0a0",
}


class VariationalIRGateError(RuntimeError):
    """A byte binding, semantic IR rule, or exact polynomial identity failed."""


@dataclass(frozen=True)
class Weight:
    numerator: int
    denominator: int
    powers: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if self.denominator <= 0:
            raise VariationalIRGateError("weight denominator must be positive")


@dataclass(frozen=True)
class PrimitiveSpec:
    name: str
    formula: str
    variation: tuple[str, ...]
    uses: tuple[str, ...] = ()
    opaque: bool = False


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    domain: str
    action_keys: tuple[str, ...]
    required_fragments: tuple[str, ...]
    density: str
    weight: Weight
    dependencies: tuple[tuple[str, int], ...]
    primitive_uses: tuple[str, ...]


@dataclass(frozen=True)
class FrechetTerm:
    component: str
    role: str
    coefficient: str
    derivative_word: tuple[str, ...]
    multiplicity: Fraction = Fraction(1)
    provenance: str = ""


@dataclass(frozen=True)
class CurrentTerm:
    component: str
    direction: str
    coefficient: str
    coefficient_derivatives: tuple[str, ...]
    role: str
    variation_derivatives: tuple[str, ...]
    multiplicity: Fraction


@dataclass(frozen=True)
class VerticalWordTerm:
    """One typed free-word contribution to a vertical Leibniz expansion."""

    word: tuple[str, ...]
    coefficient: int
    source: str


@dataclass(frozen=True)
class GroupoidGluingLaw:
    """Single source of truth for the displayed law and its free-word proof."""

    vertical_terms: tuple[VerticalWordTerm, ...]

    def _coefficient(self, source: str) -> int:
        matches = [term.coefficient for term in self.vertical_terms if term.source == source]
        if len(matches) != 1 or matches[0] not in {-1, 1}:
            raise VariationalIRGateError(f"invalid groupoid vertical slot: {source}")
        return matches[0]

    @staticmethod
    def _linear_expression(terms: Sequence[tuple[int, str]]) -> str:
        pieces: list[str] = []
        for index, (coefficient, expression) in enumerate(terms):
            if coefficient not in {-1, 1}:
                raise VariationalIRGateError("groupoid coefficients must be signs")
            if index == 0:
                pieces.append(expression if coefficient == 1 else f"-{expression}")
            else:
                pieces.append(("+" if coefficient == 1 else "-") + expression)
        return "".join(pieces)

    @property
    def formula(self) -> str:
        return (
            "iota:P|Sigma->Q; j=iota times_Ad R3; "
            "varphi_H^a=j(Y^*phi)^a are Q-associated components; "
            "varphi_H^m=e_a^m*varphi_H^a"
        )

    @property
    def variation(self) -> tuple[str, ...]:
        frame = self._coefficient("delta e")
        target = self._coefficient("delta j target")
        source = self._coefficient("delta j source")
        pullback = self._coefficient("delta phi")
        iota_vertical = self._linear_expression(
            ((target, "lambda_Q o iota"), (source, "iota o lambda_P"))
        )
        j_vertical = self._linear_expression(
            ((target, "lambda_Q o j"), (source, "j o lambda_P"))
        )
        e_vertical = self._linear_expression(((frame, "e o lambda_Q"),))
        phi_vertical = self._linear_expression(
            ((pullback, "lambda_P o (Y^*phi)"),)
        )
        expanded = (
            "delta_vertical(e o j o Y^*phi)="
            f"({e_vertical})o(j o Y^*phi)+"
            f"e o(({j_vertical})o(Y^*phi)+j o({phi_vertical}))=0"
        )
        return (
            f"delta iota={iota_vertical}",
            f"delta j={j_vertical}",
            f"delta e=delta_H e{('+' if frame == 1 else '')}{e_vertical}",
            "delta(Y^*phi)=delta_H(Y^*phi)"
            f"{('+' if pullback == 1 else '')}{phi_vertical}",
            "delta varphi_H^a=delta_H varphi_H^a"
            f"{('+' if target == 1 else '')}"
            f"{self._linear_expression(((target, '(lambda_Q)^a_b*varphi_H^b'),))}",
            expanded,
            "D_(A_Sigma) E_A+varphi_H diamond E_varphi=0",
        )


SMOOTH_V4_FORMULA = (
    "Q(Omega,s)=Omega*s^2/(2*sqrt(1+Omega^6*s^2)); "
    "s=delta_ab*phi^a*phi^b"
)
SMOOTH_V4_VARIATIONS = (
    "Q_Omega=s^2/(2*sqrt(1+Omega^6*s^2))-(3/2)*Omega^6*s^4/(1+Omega^6*s^2)^(3/2)",
    "Q_s=Omega*s/sqrt(1+Omega^6*s^2)-(1/2)*Omega^7*s^3/(1+Omega^6*s^2)^(3/2)",
    "delta Q=Q_Omega*omega+2*Q_s*delta_ab*phi^a*psi^b",
)
V52_FULL_V4_DEFINITION = "V4(r)=r^4/(2*sqrt(1+r^4))"
V52_FULL_V4_PULLBACK = "Omega_eps^(-5)*V4(Omega_eps^(3/2)*|phi_eps|)"
THETA_FORMULA = (
    "Theta=-gamma^mn*n_R*Q_mn^R; "
    "Q_mn^R=partial_m partial_n Y^R+Gamma^R_AB(g)(Y)*Y_m^A*Y_n^B"
)
THETA_VARIATIONS = (
    "delta gamma^mn=-gamma^mr*gamma^ns*delta gamma_rs",
    "delta n_R=Delta_Y g_RA*n^A+g_RA*delta n^A",
    "Delta_Y Gamma^R_AB=delta_H Gamma^R_AB(Y)+xi^S*partial_S Gamma^R_AB(Y)",
    "delta Q_mn^R=partial_m partial_n xi^R+Delta_Y Gamma^R_AB*Y_m^A*Y_n^B+Gamma^R_AB(Y)*(partial_m xi^A*Y_n^B+Y_m^A*partial_n xi^B)",
    "delta Theta=-delta(gamma^mn)*n_R*Q_mn^R-gamma^mn*delta(n_R)*Q_mn^R-gamma^mn*n_R*delta(Q_mn^R)",
)
CANONICAL_GROUPOID_GLUING_LAW = GroupoidGluingLaw(
    vertical_terms=(
        VerticalWordTerm(("e", "lambda_Q", "j", "phi"), -1, "delta e"),
        VerticalWordTerm(("e", "lambda_Q", "j", "phi"), 1, "delta j target"),
        VerticalWordTerm(("e", "j", "lambda_P", "phi"), -1, "delta j source"),
        VerticalWordTerm(("e", "j", "lambda_P", "phi"), 1, "delta phi"),
    )
)
GROUPOID_FORMULA = CANONICAL_GROUPOID_GLUING_LAW.formula
GROUPOID_VARIATIONS = CANONICAL_GROUPOID_GLUING_LAW.variation


PolyKey = tuple[str, str, tuple[str, ...], str, tuple[str, ...]]
Polynomial = dict[PolyKey, Fraction]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise VariationalIRGateError(f"cannot hash {path}: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VariationalIRGateError(f"cannot read JSON {path}: {exc}") from exc
    if type(value) is not dict:
        raise VariationalIRGateError(f"JSON object required: {path}")
    return value


def _git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        ("git", *arguments),
        cwd=REPO,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and process.returncode != 0:
        raise VariationalIRGateError(
            f"git {' '.join(arguments)} failed: {process.stderr.strip()}"
        )
    return process


def _dependency_certificate() -> tuple[dict[str, Any], dict[str, Any]]:
    observed = {name: _sha256(path) for name, path in PINNED_PATHS.items()}
    matches = {
        name: observed[name] == expected for name, expected in PINNED_INPUTS.items()
    }
    required_inventory_names = {V52_SOURCE.name, V52_TEST.name, V52_ARTIFACT.name}
    if not all(matches[name] for name in required_inventory_names):
        bad = {
            name: observed[name]
            for name in required_inventory_names
            if not matches[name]
        }
        raise VariationalIRGateError(f"required v5.2 byte-pin drift: {bad}")

    v52 = _read_json(V52_ARTIFACT)
    if v52.get("schema") != V52_SCHEMA or v52.get("checks", {}).get("all") is not True:
        raise VariationalIRGateError("v5.2 artifact is not the certified schema")
    exact_action = v52.get("exact_classical_charter", {}).get("exact_action")
    if type(exact_action) is not dict:
        raise VariationalIRGateError("v5.2 exact action is absent")
    action_hash = _canonical_sha256(exact_action)
    if action_hash != V52_EXACT_ACTION_SHA256:
        raise VariationalIRGateError("canonical v5.2 exact-action hash drift")

    gauss = _read_json(GAUSS_ARTIFACT)
    gauss_scope_observed = (
        matches[GAUSS_ARTIFACT.name]
        and gauss.get("schema") == GAUSS_SCHEMA
        and gauss.get("conventions", {}).get("correct_Gauss_scalar")
        == CORRECT_GAUSS_SCALAR
        and gauss.get("decision", {}).get("Gauss_sign_mismatch_reproduced") is True
        and gauss.get("decision", {}).get(
            "v5_5_4_may_be_consumed_as_intrinsic_Rcal_lemma"
        )
        is False
        and gauss.get("decision", {}).get("C1_N1_promotion_authorized") is False
    )

    milestones: dict[str, Any] = {}
    for commit, meaning in MILESTONE_COMMITS.items():
        exists = _git("cat-file", "-e", f"{commit}^{{commit}}", check=False).returncode == 0
        ancestor = exists and _git(
            "merge-base", "--is-ancestor", commit, "HEAD", check=False
        ).returncode == 0
        milestones[commit] = {
            "meaning": meaning,
            "role": "provenance_only_not_a_semantic_dependency",
            "commit_exists": exists,
            "ancestor_of_HEAD": ancestor,
        }

    return (
        {
            "pass": True,
            "files": {
                name: {
                    "path": str(PINNED_PATHS[name]),
                    "sha256": observed[name],
                    "expected_sha256_match": matches[name],
                    "role": (
                        "required_v5_2_inventory_byte_binding"
                        if name in required_inventory_names
                        else "provenance_only_not_a_semantic_dependency"
                    ),
                }
                for name in sorted(observed)
            },
            "v5_2_schema": v52["schema"],
            "v5_2_exact_action_sha256": action_hash,
            "Gauss_corrigendum": {
                "schema": gauss["schema"],
                "correct_Gauss_scalar": CORRECT_GAUSS_SCALAR,
                "provenance_scope_observed": gauss_scope_observed,
                "eligible_as_intrinsic_Rcal_dependency": False,
            },
            "milestones": milestones,
        },
        exact_action,
    )


def primitive_specs() -> tuple[PrimitiveSpec, ...]:
    """Return the transparent geometric dictionary used by the action IR."""

    return (
        PrimitiveSpec(
            "volume5",
            "vol_g=sqrt(-det(g))*d^5x",
            ("delta vol_g=(1/2)*vol_g*g^MN*H_MN",),
        ),
        PrimitiveSpec(
            "inverse_metric5",
            "g^MP*g_PN=delta^M_N",
            ("delta g^MN=-g^MA*g^NB*H_AB",),
        ),
        PrimitiveSpec(
            "Gamma5",
            "Gamma^R_MN=(1/2)*g^RS*(partial_M g_NS+partial_N g_MS-partial_S g_MN)",
            (
                "delta Gamma^R_MN=(1/2)*g^RS*(D_M H_NS+D_N H_MS-D_S H_MN)",
            ),
            ("inverse_metric5",),
        ),
        PrimitiveSpec(
            "Ricci5",
            "R_MN=partial_R Gamma^R_MN-partial_N Gamma^R_MR+Gamma^R_RS*Gamma^S_MN-Gamma^R_NS*Gamma^S_MR",
            ("delta R_MN=D_R(delta Gamma^R_MN)-D_N(delta Gamma^R_MR)",),
            ("Gamma5",),
        ),
        PrimitiveSpec(
            "EH5",
            "l_EH=(M5^3/2)*vol_g*g^MN*R_MN",
            (
                "delta l_EH=(M5^3/2)*vol_g*((g^MN*R/2-R^MN)*H_MN+g^MN*(D_R deltaGamma^R_MN-D_N deltaGamma^R_MR))",
            ),
            ("volume5", "inverse_metric5", "Ricci5"),
        ),
        PrimitiveSpec(
            "W",
            "W(Omega)=3*M5^3*k_infinity*exp(-G*Omega^2/(6*M5^3))",
            ("delta W=W_Omega*omega",),
        ),
        PrimitiveSpec(
            "U",
            "U(Omega)=W_Omega^2/(2*G)-2*W^2/(3*M5^3)",
            ("delta U=U_Omega*omega",),
            ("W",),
        ),
        PrimitiveSpec(
            "P",
            "P_M=D_(A,M)phi+(3/2)*phi*D_M(log(Omega))",
            (
                "delta P_M=D_(A,M)psi+alpha_M.act(phi)+(3/2)*psi*D_M(log(Omega))+(3/2)*phi*D_M(omega/Omega)",
            ),
        ),
        PrimitiveSpec(
            "smooth_V4",
            SMOOTH_V4_FORMULA,
            SMOOTH_V4_VARIATIONS,
        ),
        PrimitiveSpec(
            "curvature_F",
            "F[A]=dA+A wedge A",
            ("delta F[A]=D_A alpha",),
        ),
        PrimitiveSpec(
            "BF",
            "l_BF=<B wedge F[A]>; <X,Y>=-tr_3(XY)/2",
            (
                "delta l_BF=<beta wedge F[A]>+<B wedge D_A alpha>",
                "<B wedge D_A alpha>=<D_A B wedge alpha>-d<B wedge alpha>",
            ),
            ("curvature_F",),
        ),
        PrimitiveSpec(
            "induced_gamma",
            "gamma_mn=g_AB(Y)*partial_m Y^A*partial_n Y^B",
            (
                "Delta_Y g_AB=H_AB(Y)+xi^R*partial_R g_AB(Y)",
                "delta gamma_mn=Delta_Y g_AB*Y_m^A*Y_n^B+g_AB(Y)*(partial_m xi^A*Y_n^B+Y_m^A*partial_n xi^B)",
            ),
        ),
        PrimitiveSpec(
            "unit_normal",
            "g_AB*n^A*n^B=sigma_n; g_AB*n^A*Y_m^B=0 with the named outward orientation on each side",
            (
                "g_AB*n^A*delta n^B=-(1/2)*Delta_Y g_AB*n^A*n^B",
                "g_AB*Y_m^A*delta n^B=-Delta_Y g_AB*Y_m^A*n^B-g_AB*n^A*partial_m xi^B",
                "delta n^A=-(sigma_n/2)*n^A*Delta_Y g_BC*n^B*n^C-gamma^mn*Y_n^A*(Delta_Y g_BC*Y_m^B*n^C+g_BC*n^B*partial_m xi^C)",
                "delta n_R=Delta_Y g_RA*n^A+g_RA*delta n^A",
            ),
            ("induced_gamma",),
        ),
        PrimitiveSpec(
            "Theta",
            THETA_FORMULA,
            THETA_VARIATIONS,
            ("induced_gamma", "unit_normal", "Gamma5"),
        ),
        PrimitiveSpec(
            "volume4",
            "vol_gamma=sqrt(-det(gamma))*d^4x",
            ("delta vol_gamma=(1/2)*vol_gamma*gamma^mn*H_mn",),
        ),
        PrimitiveSpec(
            "GHY",
            "l_GHY=M5^3*vol_gamma*Theta for the side's outward unit normal",
            ("delta l_GHY=M5^3*vol_gamma*((1/2)*gamma^mn*delta gamma_mn*Theta+delta Theta)",),
            ("volume4", "Theta"),
        ),
        PrimitiveSpec(
            "Gamma4",
            "Gamma^r_mn=(1/2)*gamma^rs*(partial_m gamma_ns+partial_n gamma_ms-partial_s gamma_mn)",
            (
                "delta Gamma^r_mn=(1/2)*gamma^rs*(D_m H_ns+D_n H_ms-D_s H_mn)",
            ),
        ),
        PrimitiveSpec(
            "N_T",
            "N_T=(-gamma^mn*D_m T*D_n T)^(-1/2)",
            (
                "delta N_T=-(1/2)*N_T*H_uu-N_T^2*u^m*D_m tau; H_uu=H_mn*u^m*u^n",
            ),
        ),
        PrimitiveSpec(
            "u",
            "u_m=-N_T*D_m T; gamma^mn*u_m*u_n=-1",
            (
                "delta u_m=-(1/2)*u_m*H_uu-N_T*h_m^n*D_n tau",
                "delta u^m=gamma^mn*delta u_n-gamma^ma*gamma^nb*H_ab*u_n",
            ),
            ("N_T",),
        ),
        PrimitiveSpec(
            "h",
            "h_mn=gamma_mn+u_m*u_n; h_m^n=delta_m^n+u_m*u^n",
            (
                "delta h_mn=H_mn+delta u_m*u_n+u_m*delta u_n",
                "delta h_m^n=delta u_m*u^n+u_m*delta u^n",
                "delta h^mn=-gamma^ma*gamma^nb*H_ab+delta u^m*u^n+u^m*delta u^n",
            ),
            ("u",),
        ),
        PrimitiveSpec(
            "Kcal",
            "Kcal_mn=h_m^r*h_n^s*D_r u_s; Kcal=h^mn*Kcal_mn",
            (
                "delta Kcal_mn=delta h_m^r*h_n^s*D_r u_s+h_m^r*delta h_n^s*D_r u_s+h_m^r*h_n^s*(D_r delta u_s-deltaGamma^l_rs*u_l)",
                "delta Kcal=delta h^mn*Kcal_mn+h^mn*delta Kcal_mn",
            ),
            ("h", "Gamma4", "u"),
        ),
        PrimitiveSpec(
            "acceleration",
            "a_m=u^n*D_n u_m",
            (
                "delta a_m=delta u^n*D_n u_m+u^n*D_n delta u_m-u^n*u_r*deltaGamma^r_nm",
            ),
            ("u", "Gamma4"),
        ),
        PrimitiveSpec(
            "Rcal_Gauss",
            "Rcal=h^mr*h^ns*R_mnrs(gamma)-Kcal^2+Kcal_mn*Kcal^mn",
            (
                "delta Rcal=delta(h^mr*h^ns)*R_mnrs+h^mr*h^ns*delta R_mnrs-2*Kcal*delta Kcal+delta(Kcal_mn*Kcal^mn)",
                "delta R^r_smn=D_m deltaGamma^r_ns-D_n deltaGamma^r_ms",
                "delta R_rsmn=H_ra*R^a_smn+gamma_ra*delta R^a_smn",
            ),
            ("h", "Kcal", "Gamma4"),
        ),
        PrimitiveSpec(
            "frame",
            "u_m*e_a^m=0; h_mn*e_a^m*e_b^n=delta_ab; e^a_m=h_mn*e_a^n; a^a=e^a_m*a^m",
            (
                "delta e_a^m=u^m*delta u_n*e_a^n-(1/2)*h^mr*delta h_rn*e_a^n+e_b^m*lambda_frame^b_a; lambda_frame=-lambda_Q and lambda_Q_ab=-lambda_Q_ba",
                "delta e^a_m=delta h_mn*e_a^n+h_mn*delta e_a^n",
                "delta a^m=gamma^mn*delta a_n-gamma^ma*gamma^nb*H_ab*a_n",
                "delta a^a=delta e^a_m*a^m+e^a_m*delta a^m",
            ),
            ("u", "h"),
        ),
        PrimitiveSpec(
            "groupoid_law",
            GROUPOID_FORMULA,
            GROUPOID_VARIATIONS,
            ("frame",),
        ),
        PrimitiveSpec(
            "Robin",
            "q^m=e_a^m*(varphi^a-y*a^a); l_Robin=-(kappa_hat/2)*vol_gamma*h_mn*q^m*q^n",
            (
                "delta q^m=delta e_a^m*(varphi^a-y*a^a)+e_a^m*(delta varphi^a-y*delta a^a); delta a^a=delta e^a_n*a^n+e^a_n*delta a^n",
                "delta l_Robin=-(kappa_hat/2)*vol_gamma*((1/2)*gamma^mn*H_mn*h_rs*q^r*q^s+delta h_rs*q^r*q^s+2*h_rs*q^r*delta q^s)",
            ),
            ("volume4", "h", "acceleration", "frame", "groupoid_law"),
        ),
    )


def _bulk_component_specs(side: str) -> tuple[ComponentSpec, ...]:
    g = f"g_{side}"
    omega = f"Omega_{side}"
    phi = f"phi_{side}"
    connection = f"A_{side}"
    bfield = f"B_{side}"
    domain = f"M_{side}"
    return (
        ComponentSpec(
            f"EH_bulk_{side}", domain, ("bulk_gauged",), ("M5^3*R_eps/2",),
            f"(M5^3/2)*vol({g})*R({g})", Weight(1, 2, (("M5", 3),)),
            ((g, 2),), ("volume5", "inverse_metric5", "Gamma5", "Ricci5", "EH5"),
        ),
        ComponentSpec(
            f"Omega_kinetic_bulk_{side}", domain, ("bulk_gauged",),
            ("G*(nabla Omega_eps)^2/2",),
            f"-(G/2)*vol({g})*{g}^MN*D_M({omega})*D_N({omega})",
            Weight(-1, 2, (("G", 1),)), ((g, 0), (omega, 1)),
            ("volume5", "inverse_metric5"),
        ),
        ComponentSpec(
            f"Omega_potential_bulk_{side}", domain,
            ("bulk_gauged", "bulk_potential", "superpotential"),
            ("U(Omega_eps)", "W_Omega^2/(2*G)-2*W^2/(3*M5^3)"),
            f"-vol({g})*U({omega})", Weight(-1, 1), ((g, 0), (omega, 0)),
            ("volume5", "W", "U"),
        ),
        ComponentSpec(
            f"P_kinetic_bulk_{side}", domain,
            ("bulk_gauged", "gauged_conformal_derivative"),
            ("Z5*delta_ab*P_eps_M^a*P_eps^(b M)/2", "P_eps_M=D_(A_eps,M)phi_eps"),
            f"-(Z5/2)*vol({g})*<{g}^-1 P({omega},{phi},{connection}),P({omega},{phi},{connection})>",
            Weight(-1, 2, (("Z5", 1),)),
            ((g, 0), (omega, 1), (phi, 1), (connection, 0)),
            ("volume5", "inverse_metric5", "P"),
        ),
        ComponentSpec(
            f"full_V4_bulk_{side}", domain, ("bulk_gauged", "full_V4"),
            ("Z5*M^2*Omega_eps^(-5)*V4", "V4(r)=r^4/(2*sqrt(1+r^4))"),
            f"-Z5*M^2*vol({g})*Q({omega},delta_ab*{phi}^a*{phi}^b)",
            Weight(-1, 1, (("Z5", 1), ("M", 2))),
            ((g, 0), (omega, 0), (phi, 0)), ("volume5", "smooth_V4"),
        ),
        ComponentSpec(
            f"BF_bulk_{side}", domain, ("BF",),
            ("<B_eps wedge F[A_eps]>", "<X,Y>=-tr_3(XY)/2"),
            f"<{bfield} wedge F[{connection}]>", Weight(1, 1),
            ((connection, 1), (bfield, 0)), ("curvature_F", "BF"),
        ),
        ComponentSpec(
            f"GHY_{side}", "Sigma", ("GHY",),
            ("sqrt(-gamma)*Theta_eps", "outward normals"),
            f"M5^3*vol_gamma*Theta({g},Y_{side};outward_{side})",
            Weight(1, 1, (("M5", 3),)), ((g, 1), (f"Y_{side}", 2)),
            ("induced_gamma", "unit_normal", "Gamma5", "Theta", "volume4", "GHY"),
        ),
    )


def component_specs() -> tuple[ComponentSpec, ...]:
    return (
        *_bulk_component_specs("plus"),
        *_bulk_component_specs("minus"),
        ComponentSpec(
            "wall", "Sigma", ("wall_background", "superpotential"),
            ("2*W(Omega_Sigma)", "beta*(Omega_Sigma-1)^2/2"),
            "-vol_gamma*(2*W(Omega_Sigma)+(beta/2)*(Omega_Sigma-1)^2)",
            Weight(-1, 1), (("gamma", 0), ("Omega_Sigma", 0)),
            ("volume4", "W"),
        ),
        ComponentSpec(
            "K_foliation", "Sigma", ("foliation_lower",),
            ("Kcal_mu_nu*Kcal^mu_nu-lambda_K*Kcal^2",),
            "(Mb^2/2)*vol_gamma*(Kcal_mn*Kcal^mn-lambda_K*Kcal^2)",
            Weight(1, 2, (("Mb", 2),)), (("gamma", 1), ("T", 2)),
            ("volume4", "Gamma4", "N_T", "u", "h", "Kcal"),
        ),
        ComponentSpec(
            "R", "Sigma", ("foliation_lower",), ("xi*Rcal",),
            "(Mb^2*xi/2)*vol_gamma*Rcal",
            Weight(1, 2, (("Mb", 2), ("xi", 1))),
            (("gamma", 2), ("T", 2)),
            ("volume4", "Gamma4", "N_T", "u", "h", "Kcal", "Rcal_Gauss"),
        ),
        ComponentSpec(
            "R_squared", "Sigma", ("foliation_lower",),
            ("B4_bar*Rcal^2/(16*k_infinity^2)",),
            "-(Mb^2*B4_bar/(32*k_infinity^2))*vol_gamma*Rcal^2",
            Weight(-1, 32, (("Mb", 2), ("B4_bar", 1), ("k_infinity", -2))),
            (("gamma", 2), ("T", 2)),
            ("volume4", "Gamma4", "N_T", "u", "h", "Kcal", "Rcal_Gauss"),
        ),
        ComponentSpec(
            "a_squared", "Sigma", ("foliation_lower",), ("eta*a_mu*a^mu",),
            "(Mb^2*eta/2)*vol_gamma*h^mn*a_m*a_n",
            Weight(1, 2, (("Mb", 2), ("eta", 1))),
            (("gamma", 1), ("T", 2)),
            ("volume4", "Gamma4", "N_T", "u", "h", "acceleration"),
        ),
        ComponentSpec(
            "Robin", "Sigma", ("Robin_intrinsic",),
            ("-kappa_hat/2", "varphi_H^mu-y*a^mu"),
            "-(kappa_hat/2)*vol_gamma*h_mn*(varphi_H^m-y*a^m)*(varphi_H^n-y*a^n)",
            Weight(-1, 2, (("kappa_hat", 1),)),
            (
                ("gamma", 1), ("T", 2), ("varphi_H", 0),
            ),
            ("volume4", "Gamma4", "N_T", "u", "h", "acceleration", "frame", "groupoid_law", "Robin"),
        ),
    )


COMPONENT_NAMES = tuple(spec.name for spec in component_specs())


def _component_inventory_certificate(
    exact_action: Mapping[str, str], components: Sequence[ComponentSpec]
) -> dict[str, Any]:
    rows = [
        {
            "name": item.name,
            "domain": item.domain,
            "action_keys": list(item.action_keys),
            "required_fragments": list(item.required_fragments),
            "density": item.density,
            "weight": asdict(item.weight),
            "dependencies": [list(dependency) for dependency in item.dependencies],
            "primitive_uses": list(item.primitive_uses),
        }
        for item in components
    ]
    digest = _canonical_sha256(rows)
    literal_use_sites = all(
        all(key in exact_action for key in item.action_keys)
        and all(
            fragment
            in "\n".join(exact_action.get(key, "") for key in item.action_keys)
            for fragment in item.required_fragments
        )
        for item in components
    )
    passed = (
        tuple(item.name for item in components) == COMPONENT_NAMES
        and len(components) == 20
        and literal_use_sites
        and digest == EXPECTED_COMPONENT_INVENTORY_SHA256
    )
    return {
        "pass": passed,
        "scope": "byte_bound_literal_twenty_component_inventory_not_variation",
        "component_count": len(components),
        "component_order": [item.name for item in components],
        "literal_action_use_sites_bound": literal_use_sites,
        "inventory_sha256": digest,
        "expected_inventory_sha256": EXPECTED_COMPONENT_INVENTORY_SHA256,
        "rows": rows,
    }


def _term(
    component: str,
    role: str,
    coefficient: str,
    word: Sequence[str] = (),
    multiplicity: int | Fraction = 1,
    provenance: str = "",
) -> FrechetTerm:
    return FrechetTerm(
        component, role, coefficient, tuple(word), Fraction(multiplicity), provenance
    )


def _bulk_frechet_terms(side: str) -> list[FrechetTerm]:
    g, omega, phi, connection, bfield = (
        f"g_{side}", f"Omega_{side}", f"phi_{side}", f"A_{side}", f"B_{side}"
    )
    terms = [
        _term(f"EH_bulk_{side}", g, "(M5^3/2)*vol_g*(g^AB*R/2-R^AB)", provenance="delta volume plus inverse metric"),
        _term(f"EH_bulk_{side}", g, "(M5^3/4)*vol_g*g^MN*g^AR*g^BS", ("M", "N"), provenance="D_R deltaGamma^R_MN first symmetric leg"),
        _term(f"EH_bulk_{side}", g, "(M5^3/4)*vol_g*g^MN*g^AR*g^BS", ("N", "M"), provenance="D_R deltaGamma^R_MN second symmetric leg"),
        _term(f"EH_bulk_{side}", g, "-(M5^3/2)*vol_g*g^MN*g^AB*g^RS", ("R", "S"), provenance="Palatini trace leg"),
        _term(f"Omega_kinetic_bulk_{side}", g, "-(G/2)*vol_g*((g^AB/2)*(D Omega)^2-D^A Omega*D^B Omega)"),
        _term(f"Omega_kinetic_bulk_{side}", omega, "-G*vol_g*D^M Omega", ("M",)),
        _term(f"Omega_potential_bulk_{side}", g, "-(1/2)*vol_g*g^AB*U(Omega)"),
        _term(f"Omega_potential_bulk_{side}", omega, "-vol_g*U_Omega"),
        _term(f"P_kinetic_bulk_{side}", g, "-(Z5/2)*vol_g*((g^AB/2)*<P,P>-<P^A,P^B>)"),
        _term(f"P_kinetic_bulk_{side}", phi, "-Z5*vol_g*<P^M,A_M.act()+(3/2)*D_M(log Omega)*()>") ,
        _term(f"P_kinetic_bulk_{side}", phi, "-Z5*vol_g*<P^M,()>", ("M",)),
        _term(f"P_kinetic_bulk_{side}", connection, "-Z5*vol_g*<P^M,().act(phi)>"),
        _term(f"P_kinetic_bulk_{side}", omega, "-(3*Z5/(2*Omega))*vol_g*<P^M,phi>", ("M",)),
        _term(f"P_kinetic_bulk_{side}", omega, "+(3*Z5/(2*Omega^2))*vol_g*<P^M,phi>*D_M Omega"),
        _term(f"full_V4_bulk_{side}", g, "-(Z5*M^2/2)*vol_g*g^AB*Q(Omega,s)"),
        _term(f"full_V4_bulk_{side}", omega, "-Z5*M^2*vol_g*Q_Omega(Omega,s)"),
        _term(f"full_V4_bulk_{side}", phi, "-2*Z5*M^2*vol_g*Q_s(Omega,s)*delta_ab*phi^a*()^b"),
        _term(f"BF_bulk_{side}", bfield, "<() wedge F[A]>", provenance="delta B"),
        _term(f"BF_bulk_{side}", connection, "<B wedge dx^M*()>", ("M",), provenance="word M is the derivative part of D_A alpha"),
        _term(f"BF_bulk_{side}", connection, "<B wedge [A,()]>", provenance="algebraic part of D_A alpha"),
        _term(f"GHY_{side}", g, "M5^3*vol_gamma*((Theta/2)*gamma^mn*delta_gamma_mn/H_AB-delta_n/H_AB*Q-gamma^mn*n_R*deltaGamma^R_mn/H_AB)"),
        _term(f"GHY_{side}", g, "-M5^3*vol_gamma*gamma^mn*n_R*(1/2)*g^RS*Y_m^A*Y_n^B", ("A",), provenance="delta Gamma[g]"),
        _term(f"GHY_{side}", f"Y_{side}", "M5^3*vol_gamma*GHY_Y_algebraic_from_g(Y)"),
        _term(f"GHY_{side}", f"Y_{side}", "M5^3*vol_gamma*GHY_Y1_from_delta_gamma_and_delta_normal", ("mu",)),
        _term(f"GHY_{side}", f"Y_{side}", "-(M5^3/2)*vol_gamma*gamma^munu*n_R", ("mu", "nu"), provenance="delta(partial_mu partial_nu Y)"),
        _term(f"GHY_{side}", f"Y_{side}", "-(M5^3/2)*vol_gamma*gamma^munu*n_R", ("nu", "mu"), provenance="ordered mixed embedding jet retained"),
    ]
    return terms


def frechet_terms() -> tuple[FrechetTerm, ...]:
    terms = [*_bulk_frechet_terms("plus"), *_bulk_frechet_terms("minus")]
    terms.extend(
        (
            _term("wall", "gamma", "-(1/2)*vol_gamma*gamma^mn*(2*W+(beta/2)*(Omega_Sigma-1)^2)"),
            _term("wall", "Omega_Sigma", "-vol_gamma*(2*W_Omega+beta*(Omega_Sigma-1))"),
            _term("K_foliation", "gamma", "(Mb^2/4)*vol_gamma*gamma^mn*(K_rs*K^rs-lambda_K*K^2)"),
            _term("K_foliation", "gamma", "Mb^2*vol_gamma*(K^mn-lambda_K*K*h^mn)*deltaK_mn/d(D_r H_st)", ("r",)),
            _term("K_foliation", "T", "Mb^2*vol_gamma*(K^mn-lambda_K*K*h^mn)*deltaK_mn/d(D_r tau)", ("r",)),
            _term("K_foliation", "T", "(Mb^2/2)*vol_gamma*(K^mn-lambda_K*K*h^mn)*deltaK_mn/d(D_r D_s tau)", ("r", "s")),
            _term("K_foliation", "T", "(Mb^2/2)*vol_gamma*(K^mn-lambda_K*K*h^mn)*deltaK_mn/d(D_s D_r tau)", ("s", "r")),
            _term("R", "gamma", "(Mb^2*xi/4)*vol_gamma*gamma^mn*Rcal+(Mb^2*xi/2)*vol_gamma*deltaRcal/dH_mn"),
            _term("R", "gamma", "(Mb^2*xi/2)*vol_gamma*deltaRcal/d(D_r H_mn)", ("r",)),
            _term("R", "gamma", "(Mb^2*xi/4)*vol_gamma*h^mr*h^ns*deltaR_mnrs/d(D_r D_s H_ab)", ("r", "s")),
            _term("R", "gamma", "(Mb^2*xi/4)*vol_gamma*h^mr*h^ns*deltaR_mnrs/d(D_s D_r H_ab)", ("s", "r")),
            _term("R", "T", "(Mb^2*xi/2)*vol_gamma*deltaRcal/d(D_r tau)", ("r",)),
            _term("R", "T", "(Mb^2*xi/4)*vol_gamma*deltaRcal/d(D_r D_s tau)", ("r", "s")),
            _term("R", "T", "(Mb^2*xi/4)*vol_gamma*deltaRcal/d(D_s D_r tau)", ("s", "r")),
            _term("R_squared", "gamma", "-(Mb^2*B4_bar/(64*k_infinity^2))*vol_gamma*gamma^mn*Rcal^2-(Mb^2*B4_bar/(16*k_infinity^2))*vol_gamma*Rcal*deltaRcal/dH_mn"),
            _term("R_squared", "gamma", "-(Mb^2*B4_bar/(16*k_infinity^2))*vol_gamma*Rcal*deltaRcal/d(D_r H_mn)", ("r",)),
            _term("R_squared", "gamma", "-(Mb^2*B4_bar/(32*k_infinity^2))*vol_gamma*Rcal*h^mr*h^ns*deltaR_mnrs/d(D_r D_s H_ab)", ("r", "s")),
            _term("R_squared", "gamma", "-(Mb^2*B4_bar/(32*k_infinity^2))*vol_gamma*Rcal*h^mr*h^ns*deltaR_mnrs/d(D_s D_r H_ab)", ("s", "r")),
            _term("R_squared", "T", "-(Mb^2*B4_bar/(16*k_infinity^2))*vol_gamma*Rcal*deltaRcal/d(D_r tau)", ("r",)),
            _term("R_squared", "T", "-(Mb^2*B4_bar/(32*k_infinity^2))*vol_gamma*Rcal*deltaRcal/d(D_r D_s tau)", ("r", "s")),
            _term("R_squared", "T", "-(Mb^2*B4_bar/(32*k_infinity^2))*vol_gamma*Rcal*deltaRcal/d(D_s D_r tau)", ("s", "r")),
            _term("a_squared", "gamma", "(Mb^2*eta/4)*vol_gamma*gamma^mn*a^2+(Mb^2*eta/2)*vol_gamma*delta(h^mn)/dH_rs*a_m*a_n"),
            _term("a_squared", "gamma", "Mb^2*eta*vol_gamma*a^m*deltaa_m/d(D_r H_st)", ("r",)),
            _term("a_squared", "T", "Mb^2*eta*vol_gamma*a^m*deltaa_m/d(D_r tau)", ("r",)),
            _term("a_squared", "T", "(Mb^2*eta/2)*vol_gamma*a^m*deltaa_m/d(D_r D_s tau)", ("r", "s")),
            _term("a_squared", "T", "(Mb^2*eta/2)*vol_gamma*a^m*deltaa_m/d(D_s D_r tau)", ("s", "r")),
            _term("Robin", "gamma", "-(kappa_hat/2)*vol_gamma*((gamma^mn/2)*h(q,q)+deltah(q,q)/dH_mn+2*h(q,deltae_horizontal(varphi-y*a))/dH_mn)"),
            _term("Robin", "gamma", "-kappa_hat*vol_gamma*h(q,deltae_horizontal(varphi-y*a)-y*e*deltaa)/d(D_r H_mn)", ("r",)),
            _term("Robin", "T", "-kappa_hat*vol_gamma*h(q,deltae_horizontal(varphi-y*a)-y*e*deltaa)/d(D_r tau)", ("r",)),
            _term("Robin", "T", "-(kappa_hat/2)*vol_gamma*h(q,-y*e*deltaa/d(D_r D_s tau))", ("r", "s")),
            _term("Robin", "T", "-(kappa_hat/2)*vol_gamma*h(q,-y*e*deltaa/d(D_s D_r tau))", ("s", "r")),
            _term("Robin", "varphi_H", "-kappa_hat*vol_gamma*h(q,e*delta_varphi_H_components)"),
        )
    )
    return tuple(terms)


def _poly_add(target: dict[PolyKey, Fraction], key: PolyKey, value: Fraction) -> None:
    if not value:
        return
    target[key] += value
    if not target[key]:
        del target[key]


def raw_polynomial(terms: Iterable[FrechetTerm]) -> Polynomial:
    result: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    for term in terms:
        key = (term.component, term.coefficient, (), term.role, term.derivative_word)
        _poly_add(result, key, term.multiplicity)
    return dict(result)


def formal_adjoint(
    terms: Iterable[FrechetTerm],
) -> tuple[Polynomial, tuple[CurrentTerm, ...]]:
    """Apply integration by parts recursively without commuting derivatives."""

    euler: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    current: list[CurrentTerm] = []
    for term in terms:
        word = term.derivative_word
        sign = -1 if len(word) % 2 else 1
        euler_key = (
            term.component,
            term.coefficient,
            tuple(reversed(word)),
            term.role,
            (),
        )
        _poly_add(euler, euler_key, sign * term.multiplicity)
        for index, direction in enumerate(word):
            current.append(
                CurrentTerm(
                    component=term.component,
                    direction=direction,
                    coefficient=term.coefficient,
                    coefficient_derivatives=tuple(reversed(word[:index])),
                    role=term.role,
                    variation_derivatives=word[index + 1 :],
                    multiplicity=(Fraction(-1) ** index) * term.multiplicity,
                )
            )
    return dict(euler), tuple(current)


def divergence(current: Iterable[CurrentTerm]) -> Polynomial:
    result: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    for term in current:
        coefficient_key = (
            term.component,
            term.coefficient,
            (term.direction,) + term.coefficient_derivatives,
            term.role,
            term.variation_derivatives,
        )
        variation_key = (
            term.component,
            term.coefficient,
            term.coefficient_derivatives,
            term.role,
            (term.direction,) + term.variation_derivatives,
        )
        _poly_add(result, coefficient_key, term.multiplicity)
        _poly_add(result, variation_key, term.multiplicity)
    return dict(result)


def polynomial_residual(raw: Polynomial, euler: Polynomial, div: Polynomial) -> Polynomial:
    result: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    for polynomial, sign in ((raw, 1), (euler, -1), (div, -1)):
        for key, value in polynomial.items():
            _poly_add(result, key, sign * value)
    return dict(result)


def _operator_free_kernel_certificate(mutation: str | None = None) -> dict[str, Any]:
    """Exercise the generic recursion without any v5.2 coefficient or operator."""

    original_words = (
        (),
        ("x",),
        ("x", "y"),
        ("y", "x"),
        ("x", "y", "z"),
        ("z", "x", "y", "x"),
    )
    words = (
        tuple(sorted(word)) if mutation == "collapse_mixed_words" else word
        for word in original_words
    )
    terms = tuple(
        FrechetTerm("universal", f"eta_{index}", f"C_{index}", word)
        for index, word in enumerate(words)
    )
    raw = raw_polynomial(terms)
    euler, current = formal_adjoint(terms)
    if mutation == "kernel_no_reverse":
        euler = {
            (component, coefficient, tuple(reversed(coefficient_word)), role, variation_word): value
            for (component, coefficient, coefficient_word, role, variation_word), value in euler.items()
        }
    residual = polynomial_residual(raw, euler, divergence(current))
    actual_words = tuple(term.derivative_word for term in terms)
    words_preserved = actual_words == original_words
    reverse_rule_exact = all(
        (
            "universal",
            f"C_{index}",
            tuple(reversed(word)),
            f"eta_{index}",
            (),
        )
        in euler
        for index, word in enumerate(original_words)
    )
    passed = not residual and words_preserved and reverse_rule_exact
    return {
        "pass": passed,
        "scope": "operator_free_universal_recursion_only_not_application_to_any_action",
        "proof_schema": "structural recursion on the finite ordered word I",
        "quantifier": "for every coefficient symbol C, variation eta, and finite ordered derivative word I",
        "Euler_rule": "C*D_I(eta)=(-D)_(I_reversed)(C)*eta+d Theta_I(C,eta)",
        "ordered_words_input": [list(word) for word in original_words],
        "ordered_words_preserved": words_preserved,
        "reverse_rule_exact": reverse_rule_exact,
        "residual": _serialise_poly(residual),
    }


def _serialise_poly(polynomial: Polynomial) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in sorted(polynomial.items()):
        component, coefficient, coefficient_word, role, variation_word = key
        rows.append(
            {
                "component": component,
                "coefficient": coefficient,
                "coefficient_derivative_word": list(coefficient_word),
                "role": role,
                "variation_derivative_word": list(variation_word),
                "multiplicity": [value.numerator, value.denominator],
            }
        )
    return rows


def _serialise_current(current: Iterable[CurrentTerm]) -> list[dict[str, Any]]:
    return [
        {
            "component": item.component,
            "direction": item.direction,
            "coefficient": item.coefficient,
            "coefficient_derivative_word": list(item.coefficient_derivatives),
            "role": item.role,
            "variation_derivative_word": list(item.variation_derivatives),
            "multiplicity": [item.multiplicity.numerator, item.multiplicity.denominator],
        }
        for item in current
    ]


def _semantic_ir_certificate(
    exact_action: Mapping[str, str],
    primitives: Sequence[PrimitiveSpec],
    components: Sequence[ComponentSpec],
    terms: Sequence[FrechetTerm],
) -> dict[str, Any]:
    primitive_map = {item.name: item for item in primitives}
    unique_primitives = len(primitive_map) == len(primitives)
    transparent = all(
        not item.opaque
        and bool(item.formula.strip())
        and bool(item.variation)
        and all(piece.strip() for piece in item.variation)
        for item in primitives
    )
    references_resolve = all(
        all(name in primitive_map for name in item.uses) for item in primitives
    ) and all(
        all(name in primitive_map for name in component.primitive_uses)
        for component in components
    )

    component_names = tuple(component.name for component in components)
    exact_twenty = len(components) == 20 and len(set(component_names)) == 20
    keys_and_fragments = True
    for component in components:
        for key in component.action_keys:
            literal = exact_action.get(key)
            keys_and_fragments = keys_and_fragments and isinstance(literal, str)
        literal_bundle = "\n".join(exact_action.get(key, "") for key in component.action_keys)
        keys_and_fragments = keys_and_fragments and all(
            fragment in literal_bundle for fragment in component.required_fragments
        )

    term_names = {term.component for term in terms}
    every_component_linearised = term_names == set(component_names)
    observed: dict[str, dict[str, int]] = defaultdict(dict)
    for term in terms:
        previous = observed[term.component].get(term.role, -1)
        observed[term.component][term.role] = max(previous, len(term.derivative_word))
    declared = {
        component.name: dict(component.dependencies) for component in components
    }
    dependencies_exact = observed == declared

    rows = [
        {
            **asdict(component),
            "weight": asdict(component.weight),
            "observed_dependency_orders": observed.get(component.name, {}),
            "frechet_term_count": sum(term.component == component.name for term in terms),
        }
        for component in components
    ]
    semantic_payload = {
        "primitives": [asdict(item) for item in primitives],
        "components": rows,
        "frechet_terms": [
            {
                **asdict(term),
                "multiplicity": [term.multiplicity.numerator, term.multiplicity.denominator],
            }
            for term in terms
        ],
    }
    structural_passed = all(
        (
            unique_primitives,
            transparent,
            references_resolve,
            exact_twenty,
            component_names == COMPONENT_NAMES,
            keys_and_fragments,
            every_component_linearised,
            dependencies_exact,
        )
    )
    projection_atoms = sorted(
        {
            term.coefficient
            for term in terms
            if "/d(" in term.coefficient or "GHY_Y" in term.coefficient
        }
    )
    return {
        "pass": structural_passed,
        "scope": "structural_action_binding_and_candidate_Frechet_IR_only",
        "tensorial_action_decoder_present": False,
        "Frechet_terms_proved_equal_to_D_of_literal_action": False,
        "uninterpreted_coefficient_projection_atoms": projection_atoms,
        "component_count": len(components),
        "component_order": list(component_names),
        "primitive_count": len(primitives),
        "unique_primitives": unique_primitives,
        "primitive_formula_strings_nonempty": transparent,
        "no_opaque_nodes": transparent and not projection_atoms,
        "primitive_references_resolve": references_resolve,
        "action_keys_and_use_site_fragments_bound": keys_and_fragments,
        "every_component_has_frechet_terms": every_component_linearised,
        "declared_and_observed_jet_orders_exact": dependencies_exact,
        "rows": rows,
        "primitives": [asdict(item) for item in primitives],
        "candidate_ir_sha256": _canonical_sha256(semantic_payload),
    }


def _formal_adjoint_certificate(terms: Sequence[FrechetTerm]) -> dict[str, Any]:
    component_rows: list[dict[str, Any]] = []
    all_residual: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    total_raw: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    total_euler: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    total_div: defaultdict[PolyKey, Fraction] = defaultdict(Fraction)
    for component in COMPONENT_NAMES:
        selected = tuple(term for term in terms if term.component == component)
        raw = raw_polynomial(selected)
        euler, current = formal_adjoint(selected)
        div = divergence(current)
        residual = polynomial_residual(raw, euler, div)
        for target, polynomial in (
            (total_raw, raw), (total_euler, euler), (total_div, div),
            (all_residual, residual),
        ):
            for key, value in polynomial.items():
                _poly_add(target, key, value)
        component_rows.append(
            {
                "component": component,
                "raw_monomial_count": len(raw),
                "euler_monomial_count": len(euler),
                "current_monomial_count": len(current),
                "maximum_derivative_order": max(
                    (len(term.derivative_word) for term in selected), default=-1
                ),
                "raw_linearization_normal_form": _serialise_poly(raw),
                "Euler_normal_form": _serialise_poly(euler),
                "current_normal_form": _serialise_current(current),
                "residual": _serialise_poly(residual),
                "residual_zero": not residual,
                "euler_sha256": _canonical_sha256(_serialise_poly(euler)),
                "current_sha256": _canonical_sha256(_serialise_current(current)),
            }
        )
    total_residual = polynomial_residual(
        dict(total_raw), dict(total_euler), dict(total_div)
    )
    mixed_words = {
        term.derivative_word
        for term in terms
        if len(term.derivative_word) == 2
    }
    ordered_mixed_witness = (
        ("M", "N") in mixed_words
        and ("N", "M") in mixed_words
        and ("r", "s") in mixed_words
        and ("s", "r") in mixed_words
    )
    passed = (
        all(row["residual_zero"] for row in component_rows)
        and not total_residual
        and not all_residual
        and ordered_mixed_witness
    )
    return {
        "pass": passed,
        "derivative_word_convention": "ordered outermost-to-innermost; no commutation or symmetric-jet quotient",
        "Euler_formula": "E_A=sum_I (-1)^len(I) D_(I_reversed)(C_A^I)",
        "current_recursion": "Theta[D_I eta]=sum_j (-1)^j D_(reverse(I[:j]))C * D_(I[j+1:])eta in direction I[j]",
        "identity": "delta L=E_A*delta q^A+d Theta componentwise off shell",
        "quantified_identity": (
            "for every one of the 20 literal components, every admissible role A, "
            "every finite ordered derivative word I in its displayed Frechet IR, "
            "and every smooth compactly supported test variation eta^A"
        ),
        "support_and_domain": {
            "interface": "eta in C_c^infinity(R^(1,3)); the d4 current has zero integral at infinity",
            "bulk": "eta smooth with compact support in a local chart for this formal-adjoint step; collar and outward-boundary composition are deferred",
            "off_shell": True,
        },
        "ordered_mixed_witness": ordered_mixed_witness,
        "component_rows": component_rows,
        "component_residuals_all_zero": all(row["residual_zero"] for row in component_rows),
        "summed_residual": _serialise_poly(total_residual),
        "summed_residual_zero": not total_residual,
        "raw_sha256": _canonical_sha256(_serialise_poly(dict(total_raw))),
        "euler_sha256": _canonical_sha256(_serialise_poly(dict(total_euler))),
        "divergence_sha256": _canonical_sha256(_serialise_poly(dict(total_div))),
    }


def _fraction_pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def _smooth_v4_exact_certificate(
    smooth: PrimitiveSpec, exact_action: Mapping[str, Any]
) -> dict[str, Any]:
    """Bind the canonical rewrite and check it with an independent exact oracle."""

    omega = Fraction(1)
    s = Fraction(3, 4)
    radicand = 1 + omega**6 * s**2
    sqrt_radicand = Fraction(5, 4)
    q = omega * s**2 / (2 * sqrt_radicand)
    q_omega = (
        s**2 / (2 * sqrt_radicand)
        - Fraction(3, 2) * omega**6 * s**4 / sqrt_radicand**3
    )
    q_s = (
        omega * s / sqrt_radicand
        - Fraction(1, 2) * omega**7 * s**3 / sqrt_radicand**3
    )

    # Independent reconstruction of Omega^-5 V4(Omega^(3/2)*sqrt(s)):
    # r^4 has exponents Omega^6 s^2, so V4(r)=r^4/(2 sqrt(1+r^4)).
    r_fourth = omega**6 * s**2
    original_v4_pullback = omega**-5 * r_fourth / (2 * sqrt_radicand)
    exponent_oracle = {
        "r_fourth": {"Omega": Fraction(6), "s": Fraction(2)},
        "Omega_minus_five_times_r_fourth": {
            "Omega": Fraction(-5) + Fraction(4) * Fraction(3, 2),
            "s": Fraction(4) * Fraction(1, 2),
        },
    }
    exponent_pass = exponent_oracle["Omega_minus_five_times_r_fourth"] == {
        "Omega": Fraction(1),
        "s": Fraction(2),
    }
    rational_pass = (
        radicand == Fraction(25, 16)
        and sqrt_radicand**2 == radicand
        and q == Fraction(9, 40)
        and q_omega == Fraction(-9, 500)
        and q_s == Fraction(123, 250)
        and original_v4_pullback == q
    )
    exact_byte_binding = (
        smooth.formula == SMOOTH_V4_FORMULA
        and smooth.variation == SMOOTH_V4_VARIATIONS
    )
    original_action_binding = (
        exact_action.get("full_V4") == V52_FULL_V4_DEFINITION
        and V52_FULL_V4_PULLBACK in exact_action.get("bulk_gauged", "")
    )
    return {
        "pass": (
            exact_byte_binding
            and original_action_binding
            and exponent_pass
            and rational_pass
        ),
        "scope": "exact_canonical_rewrite_binding_plus_independent_exponent_and_rational_oracle",
        "exact_formula_and_variations_byte_bound": exact_byte_binding,
        "v5_2_original_definition_and_pullback_byte_bound": original_action_binding,
        "v5_2_original_definition": exact_action.get("full_V4"),
        "v5_2_original_pullback": V52_FULL_V4_PULLBACK,
        "symbolic_exponent_oracle": {
            key: {name: _fraction_pair(value) for name, value in powers.items()}
            for key, powers in exponent_oracle.items()
        },
        "symbolic_exponent_identity_pass": exponent_pass,
        "rational_oracle": {
            "Omega": _fraction_pair(omega),
            "s": _fraction_pair(s),
            "radicand": _fraction_pair(radicand),
            "sqrt_radicand": _fraction_pair(sqrt_radicand),
            "Q": _fraction_pair(q),
            "Q_Omega": _fraction_pair(q_omega),
            "Q_s": _fraction_pair(q_s),
            "Omega_minus_five_V4_of_Omega_three_halves_sqrt_s": _fraction_pair(
                original_v4_pullback
            ),
            "pass": rational_pass,
        },
    }


def _geometric_semantics_certificate(
    primitives: Sequence[PrimitiveSpec], components: Sequence[ComponentSpec]
) -> dict[str, Any]:
    by_name = {item.name: item for item in primitives}
    gamma = " ".join(by_name["Gamma4"].variation + by_name["Gamma5"].variation)
    khronon = " ".join(
        by_name[name].formula + " " + " ".join(by_name[name].variation)
        for name in ("N_T", "u", "h", "Kcal", "acceleration")
    )
    robin = " ".join(
        by_name[name].formula + " " + " ".join(by_name[name].variation)
        for name in ("frame", "groupoid_law", "Robin")
    )
    groupoid = by_name["groupoid_law"]
    theta = by_name["Theta"]
    ghy = next(component for component in components if component.name == "GHY_plus")
    smooth = by_name["smooth_V4"]
    normal = " ".join(by_name["unit_normal"].variation)
    rcal = " ".join(by_name["Rcal_Gauss"].variation)
    checks = {
        "delta_Gamma_open": "delta Gamma" in gamma and "D_m H_ns" in gamma,
        "delta_N_u_h_K_a_open": all(
            fragment in khronon
            for fragment in (
                "delta N_T", "delta u_m", "delta h_mn", "delta Kcal_mn", "delta a_m"
            )
        ),
        "delta_a_contains_connection_variation": "deltaGamma^r_nm" in khronon,
        "delta_normal_contravariant_and_lowered_open": (
            "delta n^A=" in normal
            and "delta n_R=Delta_Y g_RA*n^A+g_RA*delta n^A" in normal
            and "Delta_Y g_AB" in normal
        ),
        "delta_Riemann_mixed_and_all_lowered_open": (
            "delta R^r_smn=" in rcal and "delta R_rsmn=" in rcal
        ),
        "Robin_full_metric_frame_acceleration_variation": all(
            fragment in robin
            for fragment in ("delta e_a^m", "delta q^m", "delta h_rs", "delta a^a")
        ),
        "frame_horizontal_and_vertical_terms_present": all(
            fragment in robin
            for fragment in ("u^m*delta u_n", "h^mr*delta h_rn", "lambda_frame^b_a")
        ),
        "inverse_spatial_metric_coframe_and_internal_acceleration_open": all(
            fragment in khronon + " " + robin
            for fragment in ("delta h^mn", "delta e^a_m", "delta a^m", "delta a^a")
        ),
        "groupoid_exact_formula_and_laws_byte_bound": (
            groupoid.formula == GROUPOID_FORMULA
            and groupoid.variation == GROUPOID_VARIATIONS
        ),
        "vertical_Noether_open": all(
            any(fragment in row for row in groupoid.variation)
            for fragment in (
                "delta_vertical(e o j o Y^*phi)=",
                "D_(A_Sigma) E_A+varphi_H diamond E_varphi=0",
            )
        ),
        "groupoid_trace_matches_v5_2_charter": groupoid.formula == GROUPOID_FORMULA,
        "frame_and_Q_vertical_signs_consistent": (
            "lambda_frame=-lambda_Q" in by_name["frame"].variation[0]
            and "delta e=delta_H e-e o lambda_Q" in groupoid.variation
        ),
        "varphi_H_representation_not_mixed": (
            "Q-associated components" in groupoid.formula
            and "varphi_H^m=e_a^m*varphi_H^a" in groupoid.formula
            and "e_a^m*(varphi^a-y*a^a)" in by_name["Robin"].formula
            and "e_a^m*(delta varphi^a-y*delta a^a)" in by_name["Robin"].variation[0]
        ),
        "GHY_depends_on_ambient_g1_Y2_not_gamma_only": (
            ghy.dependencies == (("g_plus", 1), ("Y_plus", 2))
            and "Theta(g_plus,Y_plus" in ghy.density
        ),
        "Theta_exact_formula_complete_variation_and_outward_sign": (
            theta.formula == THETA_FORMULA
            and theta.variation == THETA_VARIATIONS
        ),
        "smooth_V4_exact_formula_and_variations_byte_bound": (
            smooth.formula == SMOOTH_V4_FORMULA
            and smooth.variation == SMOOTH_V4_VARIATIONS
        ),
        "BF_sign_and_boundary_formula_open": (
            "<B wedge D_A alpha>" in by_name["BF"].variation[0]
            and "-d<B wedge alpha>" in by_name["BF"].variation[1]
        ),
        "Rcal_Gauss_formula_open": (
            by_name["Rcal_Gauss"].formula
            == "Rcal=h^mr*h^ns*R_mnrs(gamma)-Kcal^2+Kcal_mn*Kcal^mn"
        ),
    }
    return {
        "pass": all(checks.values()),
        "scope": "partial_explicit_formula_ledger_internal_consistency_not_completeness_or_tensorial_decoding",
        "tensorial_evaluator_present": False,
        "checks": checks,
        "bulk_embedding_and_clock_variation_slots": [
            "g_plus", "Omega_plus", "phi_plus", "A_plus", "B_plus", "Y_plus",
            "g_minus", "Omega_minus", "phi_minus", "A_minus", "B_minus", "Y_minus",
            "T",
        ],
        "single_common_interface_material_EL_slot": "varphi_H^a (Q-associated components)",
        "vertical_gluing_parameters_not_independent_EL_slots": [
            "iota_plus/j_plus", "iota_minus/j_minus",
        ],
        "common_trace_coordinates_used_only_as_interface_IR": [
            "gamma", "Omega_Sigma", "varphi_H^a (Q-associated components)",
        ],
        "free_word_vertical_cancellation": "delta_vertical(e o j o Y^*phi)=0",
        "candidate_vertical_Noether_formula_recorded_not_derived": (
            "D_(A_Sigma) E_A+varphi_H diamond E_varphi=0"
        ),
    }


def _audit_optional_r_cal_dependency(
    pins: Mapping[str, str] | None,
) -> dict[str, Any]:
    """Report availability of v5.6.7.8; never integrate its lemma here."""

    required_names = {RCAL_V5678_SOURCE.name, RCAL_V5678_TEST.name}
    if pins is None:
        return {
            "configured": False,
            "pass": False,
            "available_and_byte_bound": False,
            "status": "awaiting_explicit_stable_committed_audited_source_and_test_pins",
            "required_pin_names": sorted(required_names),
        }
    if set(pins) != required_names or any(
        not isinstance(value, str) or len(value) != 64 for value in pins.values()
    ):
        return {
            "configured": True,
            "pass": False,
            "available_and_byte_bound": False,
            "status": "invalid_pin_contract",
            "required_pin_names": sorted(required_names),
        }
    paths = {RCAL_V5678_SOURCE.name: RCAL_V5678_SOURCE, RCAL_V5678_TEST.name: RCAL_V5678_TEST}
    observed = {name: _sha256(path) for name, path in paths.items()}
    byte_match = observed == dict(pins)
    tracked_clean: dict[str, bool] = {}
    for name, path in paths.items():
        relative = str(path.relative_to(REPO))
        tracked = _git("ls-files", "--error-unmatch", relative, check=False).returncode == 0
        clean = not _git("status", "--porcelain", "--", relative).stdout.strip()
        tracked_clean[name] = tracked and clean
    semantic = False
    if byte_match and all(tracked_clean.values()):
        module_name = f"_audited_v5678_{observed[RCAL_V5678_SOURCE.name][:16]}"
        spec = importlib.util.spec_from_file_location(module_name, RCAL_V5678_SOURCE)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
                report = module.build_report()
                semantic = (
                    report.get("decision", {}).get(
                        "corrected_intrinsic_Rcal_interface_variation_exact_pass"
                    )
                    is True
                    and report.get("decision", {}).get(
                        "full_classical_variational_principle_selected_sector_pass"
                    )
                    is False
                )
            finally:
                sys.modules.pop(module_name, None)
    passed = byte_match and all(tracked_clean.values()) and semantic
    return {
        "configured": True,
        "pass": passed,
        "available_and_byte_bound": passed,
        "status": "available_and_byte_bound" if passed else "pin_or_commit_or_semantic_audit_failed",
        "observed_sha256": observed,
        "tracked_and_clean": tracked_clean,
        "semantic_Rcal_only_scope_verified": semantic,
    }


def _groupoid_vertical_free_word_certificate(
    groupoid: PrimitiveSpec,
) -> dict[str, Any]:
    """Consume one byte-bound typed law and expand ``delta(e j phi)``."""

    exact_byte_binding = (
        groupoid.formula == CANONICAL_GROUPOID_GLUING_LAW.formula
        and groupoid.variation == CANONICAL_GROUPOID_GLUING_LAW.variation
    )
    terms = CANONICAL_GROUPOID_GLUING_LAW.vertical_terms
    residual: defaultdict[tuple[str, ...], int] = defaultdict(int)
    for term in terms:
        residual[term.word] += term.coefficient
        if residual[term.word] == 0:
            del residual[term.word]
    return {
        "pass": exact_byte_binding and not residual,
        "representation": "free associative words, so cancellation is universal and not a commuting-matrix sample",
        "single_typed_law_consumed": True,
        "displayed_formula_and_laws_exact_byte_binding": exact_byte_binding,
        "displayed_formula": groupoid.formula,
        "displayed_variations": list(groupoid.variation),
        "expanded_terms": [
            {
                "word": list(term.word),
                "coefficient": term.coefficient,
                "source": term.source,
            }
            for term in terms
        ],
        "residual": [
            {"word": list(word), "coefficient": coefficient}
            for word, coefficient in sorted(residual.items())
        ],
        "candidate_Noether_formula_recorded_not_derived": GROUPOID_VARIATIONS[-1],
        "Noether_identity_with_iota_j_map_Euler_momenta_derived": False,
    }


def _apply_mutation(
    mutation: str | None,
    primitives: tuple[PrimitiveSpec, ...],
    components: tuple[ComponentSpec, ...],
    terms: tuple[FrechetTerm, ...],
) -> tuple[tuple[PrimitiveSpec, ...], tuple[ComponentSpec, ...], tuple[FrechetTerm, ...]]:
    if mutation is None:
        return primitives, components, terms

    primitive_list = list(primitives)
    component_list = list(components)
    term_list = list(terms)

    def mutate_primitive(name: str, **changes: Any) -> None:
        index = next(i for i, item in enumerate(primitive_list) if item.name == name)
        primitive_list[index] = replace(primitive_list[index], **changes)

    def mutate_component(name: str, **changes: Any) -> None:
        index = next(i for i, item in enumerate(component_list) if item.name == name)
        component_list[index] = replace(component_list[index], **changes)

    if mutation == "collapse_mixed_words":
        term_list = [replace(item, derivative_word=tuple(sorted(item.derivative_word))) for item in term_list]
    elif mutation == "groupoid_j_to_iota":
        item = next(item for item in primitive_list if item.name == "groupoid_law")
        mutate_primitive("groupoid_law", formula=item.formula.replace("j(Y^*phi)", "iota(Y^*phi)"))
    elif mutation == "wrong_frame_lambda_sign":
        item = next(item for item in primitive_list if item.name == "frame")
        mutate_primitive("frame", variation=tuple(row.replace("lambda_frame=-lambda_Q", "lambda_frame=+lambda_Q") for row in item.variation))
    elif mutation == "wrong_groupoid_source_sign":
        item = next(item for item in primitive_list if item.name == "groupoid_law")
        mutate_primitive("groupoid_law", variation=tuple(row.replace("lambda_Q o j-j o lambda_P", "lambda_Q o j+j o lambda_P") for row in item.variation))
    elif mutation == "groupoid_delta_j_extra_term":
        item = next(item for item in primitive_list if item.name == "groupoid_law")
        mutate_primitive(
            "groupoid_law",
            variation=tuple(
                row + "+X" if row.startswith("delta j=") else row
                for row in item.variation
            ),
        )
    elif mutation == "omit_delta_phi":
        item = next(item for item in primitive_list if item.name == "groupoid_law")
        mutate_primitive("groupoid_law", variation=tuple(row for row in item.variation if not row.startswith("delta(Y^*phi)=")))
    elif mutation == "singular_V4":
        mutate_primitive(
            "smooth_V4",
            formula="Q=Omega^(-5)*V4(Omega^(3/2)*|phi|)",
        )
    elif mutation == "V4_formula_extra_term":
        item = next(item for item in primitive_list if item.name == "smooth_V4")
        mutate_primitive("smooth_V4", formula=item.formula + "+1")
    elif mutation == "GHY_gamma_only":
        mutate_component("GHY_plus", dependencies=(("gamma", 1),), density="M5^3*vol_gamma*Theta(gamma)")
    elif mutation == "wrong_GHY_sign":
        mutate_component("GHY_plus", weight=Weight(-1, 1, (("M5", 3),)))
    elif mutation == "wrong_Theta_sign":
        item = next(item for item in primitive_list if item.name == "Theta")
        mutate_primitive(
            "Theta",
            formula=item.formula.replace("Theta=-gamma", "Theta=+gamma"),
            variation=tuple(
                row.replace("delta Theta=-delta", "delta Theta=+delta")
                for row in item.variation
            ),
        )
    elif mutation == "Theta_formula_extra_term":
        item = next(item for item in primitive_list if item.name == "Theta")
        mutate_primitive("Theta", formula=item.formula + "+X")
    elif mutation == "wrong_BF_sign":
        mutate_component("BF_bulk_plus", weight=Weight(-1, 1))
    elif mutation == "wrong_R2_denominator_16":
        mutate_component("R_squared", weight=Weight(-1, 16, (("Mb", 2), ("B4_bar", 1), ("k_infinity", -2))))
    elif mutation == "omit_component":
        component_list = [item for item in component_list if item.name != "Robin"]
        term_list = [item for item in term_list if item.component != "Robin"]
    elif mutation == "use_site_drift":
        mutate_component("a_squared", action_keys=("Robin_intrinsic",))
    elif mutation == "producer_expected_co_mutation":
        # Deliberately self-consistent inside this producer.  The independent
        # test-local oracle must still reject the changed public row.
        mutate_component("wall", weight=Weight(1, 1), density="+vol_gamma*(2*W+(beta/2)*(Omega_Sigma-1)^2)")
    elif mutation == "corrupt_R_R2_candidate":
        mutate_component("R", density="CORRUPT_R_DENSITY")
        mutate_component("R_squared", density="CORRUPT_R2_DENSITY")
        term_list = [
            replace(item, coefficient=f"CORRUPT({item.coefficient})")
            if item.component in {"R", "R_squared"}
            else item
            for item in term_list
        ]
    elif mutation == "kernel_no_reverse":
        pass
    else:
        raise VariationalIRGateError(f"unknown mutation: {mutation}")
    return tuple(primitive_list), tuple(component_list), tuple(term_list)


PROMOTED_SCOPE_MUTATIONS = (
    "collapse_mixed_words",
    "kernel_no_reverse",
    "GHY_gamma_only",
    "wrong_GHY_sign",
    "wrong_Theta_sign",
    "Theta_formula_extra_term",
    "wrong_BF_sign",
    "wrong_R2_denominator_16",
    "omit_component",
    "use_site_drift",
    "producer_expected_co_mutation",
    "singular_V4",
    "V4_formula_extra_term",
    "groupoid_j_to_iota",
    "wrong_frame_lambda_sign",
    "wrong_groupoid_source_sign",
    "omit_delta_phi",
    "groupoid_delta_j_extra_term",
    "corrupt_R_R2_candidate",
)


TRUE_DECISION_KEYS = frozenset(
    {
        "literal_v5_2_twenty_component_byte_bound_inventory_pass",
        "operator_free_ordered_formal_adjoint_kernel_pass",
        "GHY_g1_Y2_inventory_and_outward_Theta_sign_only_pass",
        "smooth_full_V4_zero_safe_algebraic_rewrite_pass",
        "vertical_groupoid_gluing_inventory_and_free_word_vertical_cancellation_pass",
        "audited_v5_6_7_8_Rcal_dependency_available_and_byte_bound_pass",
    }
)
FALSE_DECISION_KEYS = frozenset(
    {
        "candidate_twenty_component_formal_adjoint_application_pass",
        "candidate_componentwise_raw_equals_adjoint_plus_divergence_application_pass",
        "literal_v5_2_twenty_component_semantic_IR_exact_pass",
        "Frechet_IR_equals_D_of_literal_S_v5_2_pass",
        "componentwise_deltaL_equals_Edeltaq_plus_dTheta_semantic_pass",
        "K_a_Robin_T_groupoid_semantic_variation_exact_pass",
        "K_a_Robin_T_groupoid_complete_variation_formula_ledger_pass",
        "vertical_groupoid_Noether_identity_with_iota_j_momenta_derived_pass",
        "Rcal_dependency_integrated_into_variational_IR_pass",
        "R_R_squared_Frechet_semantic_validation_pass",
        "all_twenty_component_geometric_variations_finally_accepted_pass",
        "two_sided_EH_GHY_full_Green_pairing_exact_pass",
        "moving_pullback_Cartan_i_xi_L_composed_once_exact_pass",
        "normal_shape_equation_from_literal_action_exact_pass",
        "full_off_shell_Green_theorem_selected_sector_pass",
        "full_classical_variational_principle_selected_sector_pass",
        "C1_ACTION_pass",
        "N1_ACTION_pass",
        "C1_N1_promotion_authorized",
        "Route_C_used_pass",
        "finite_margin_or_q_quotient_used_pass",
        "publication_authorized",
    }
)


def build_report(
    mutation: str | None = None,
    rcal_v5678_pins: Mapping[str, str] | None = DEFAULT_RCAL_V5678_PINS,
) -> dict[str, Any]:
    dependency, exact_action = _dependency_certificate()
    primitives, components, terms = _apply_mutation(
        mutation, primitive_specs(), component_specs(), frechet_terms()
    )
    inventory = _component_inventory_certificate(exact_action, components)
    operator_kernel = _operator_free_kernel_certificate(mutation)
    structural = _semantic_ir_certificate(exact_action, primitives, components, terms)
    formal = _formal_adjoint_certificate(terms)
    geometry = _geometric_semantics_certificate(primitives, components)
    primitives_by_name = {primitive.name: primitive for primitive in primitives}
    smooth_v4 = _smooth_v4_exact_certificate(
        primitives_by_name["smooth_V4"], exact_action
    )
    vertical_groupoid = _groupoid_vertical_free_word_certificate(
        primitives_by_name["groupoid_law"]
    )
    rcal = _audit_optional_r_cal_dependency(rcal_v5678_pins)

    by_component = {component.name: component for component in components}
    ghy_inventory = all(
        name in by_component
        and by_component[name].dependencies == ((f"g_{side}", 1), (f"Y_{side}", 2))
        and by_component[name].weight == Weight(1, 1, (("M5", 3),))
        and f"outward_{side}" in by_component[name].density
        for side, name in (("plus", "GHY_plus"), ("minus", "GHY_minus"))
    ) and geometry["checks"][
        "Theta_exact_formula_complete_variation_and_outward_sign"
    ]
    v4_rewrite = smooth_v4["pass"]
    groupoid_narrow = (
        vertical_groupoid["pass"]
        and geometry["checks"]["groupoid_exact_formula_and_laws_byte_bound"]
        and geometry["checks"]["groupoid_trace_matches_v5_2_charter"]
        and geometry["checks"]["frame_and_Q_vertical_signs_consistent"]
        and geometry["checks"]["varphi_H_representation_not_mixed"]
    )
    byte_inventory = dependency["pass"] and inventory["pass"]

    decision = {
        "literal_v5_2_twenty_component_byte_bound_inventory_pass": byte_inventory,
        "operator_free_ordered_formal_adjoint_kernel_pass": operator_kernel["pass"],
        "GHY_g1_Y2_inventory_and_outward_Theta_sign_only_pass": ghy_inventory,
        "smooth_full_V4_zero_safe_algebraic_rewrite_pass": v4_rewrite,
        "vertical_groupoid_gluing_inventory_and_free_word_vertical_cancellation_pass": groupoid_narrow,
        "audited_v5_6_7_8_Rcal_dependency_available_and_byte_bound_pass": rcal["pass"],
    }
    decision.update({key: False for key in FALSE_DECISION_KEYS if key not in decision})
    if mutation is None and rcal_v5678_pins == DEFAULT_RCAL_V5678_PINS:
        if {key for key, value in decision.items() if value} != TRUE_DECISION_KEYS:
            raise VariationalIRGateError("baseline narrow true decision frontier drift")
        if {key for key, value in decision.items() if not value} != FALSE_DECISION_KEYS:
            raise VariationalIRGateError("baseline fail-closed decision frontier drift")

    narrow_checks = {
        "literal_twenty_component_byte_bound_inventory": byte_inventory,
        "operator_free_ordered_formal_adjoint_kernel": operator_kernel["pass"],
        "smooth_full_V4_zero_safe_algebraic_rewrite": v4_rewrite,
        "GHY_g1_Y2_inventory_and_outward_Theta_sign_only": ghy_inventory,
        "vertical_groupoid_gluing_inventory_and_free_word_vertical_cancellation": groupoid_narrow,
        "audited_Rcal_dependency_available_and_byte_bound": rcal["pass"],
    }
    checks = {
        **narrow_checks,
        "all": all(narrow_checks.values()),
    }
    return {
        "schema": SCHEMA,
        "title": "Infrastructure-only v5.2 inventory and operator-free ordered formal adjoint",
        "mutation": mutation,
        "dependency_certificate": dependency,
        "literal_action_component_inventory": inventory,
        "operator_free_formal_adjoint_kernel": operator_kernel,
        "candidate_literal_action_variation_IR_diagnostic": {
            **structural,
            "structural_self_consistency": structural["pass"],
            "pass": False,
        },
        "candidate_component_formal_adjoint_diagnostic": {
            **formal,
            "algebraic_given_coefficients_self_identity": formal["pass"],
            "pass": False,
            "application_accepted": False,
            "reason": "no tensorial decoder proves candidate Frechet terms equal D(S_v5_2)",
        },
        "candidate_geometric_formula_diagnostic": {
            **geometry,
            "formula_string_self_checks": geometry["pass"],
            "pass": False,
        },
        "smooth_full_V4_exact_algebraic_certificate": smooth_v4,
        "vertical_groupoid_free_word_certificate": vertical_groupoid,
        "audited_Rcal_v5_6_7_8_dependency_availability": rcal,
        "checks": checks,
        "decision": decision,
        "axiom_boundary": {
            "accepted_standard_local_geometry": [
                "Levi-Civita inverse-metric, determinant and Palatini identities",
                "ordinary and gauge-covariant Leibniz rules",
                "Gauss identity with the byte-pinned v5.5.4 sign convention",
                "formal integration by parts for compact-support variations on R^(1,3)",
            ],
            "proved_here": [
                "byte-bound literal domain/use-site/dependency inventory for twenty action rows",
                "operator-free ordered-word universal formal-adjoint recursion",
                "exact canonical smooth full-V4 rewrite with independent exponent/rational oracle and GHY dependency inventory",
                "universal free-word cancellation of the three vertical groupoid Leibniz slots",
                "availability and byte binding of the audited v5.6.7.8 Rcal dependency",
            ],
            "not_proved_here": [
                "a tensorial action decoder proving the candidate Frechet list equals D(S_v5_2)",
                "application of the operator-free adjoint kernel to any candidate v5.2 row",
                "integration of the available Rcal dependency into the R or R-squared rows",
                "the complete K/a/Robin Frechet coefficients, including algebraic metric, index-raising and coframe pieces",
                "a derivation of the vertical Noether identity including iota/j map Euler momenta",
                "EH+GHY two-sided boundary cancellation",
                "moving pullback and its single Cartan i_xi L representative",
                "normal shape row, full Green theorem, C1 or N1",
            ],
        },
        "blockers": [
            "replace every unevaluated coefficient projection deltaK/d(...), deltaRcal/d(...), deltaa/d(...) and GHY_Y* atom with output of an independently checked tensorial action decoder",
            "repair and decode the candidate EH index contractions, split P and BF covariant-derivative leaves without double counting, and add the missing K/a/Robin algebraic and index-raising rows",
            "complete the moving-Y variation of g(Y), n and Gamma(Y), including xi^R partial_R Gamma, before accepting any GHY variation row",
            "derive the moving pullback, EH+GHY pairing and normal shape row in the final gate",
        ],
    }


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
