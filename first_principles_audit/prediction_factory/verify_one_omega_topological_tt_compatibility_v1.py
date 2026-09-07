#!/usr/bin/env python3
"""Independent restricted TT variation and source compatibility for topological v5.2.

Only h12=h21=epsilon*h(t,z,r) varies. Each bulk domain is r>=0, with UV outward
normal -partial_r; the common wall is counted once. The scalar BPS background,
T=t, and phi=A_connection=B=a_mu=0 are declared. The inverse spatial frame varies
with h; A_Sigma is independent of the Levi-Civita connection and may be zero in
the common moving-frame trivialization with r_plus=r_minus=I.

The radial ADM identity, including its EH total derivative and GHY cancellation,
and temporal ADM/spatial Gaussian-foliation curvature identities are translated
manually. No previous generator is imported and no source formulas are parsed.
The independent tests use direct Christoffels and rotated diagonal shear.

A solution of this restricted action is not proof that every omitted Euler row
or constraint is satisfied. Full TT subspace closure, physical admissibility,
BF edge elimination, spectrum, BRST and coupled stability remain uncertified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

if __package__:
    from . import verify_one_omega_scalar_interface_reparam_v1 as source_oracle
    from . import verify_one_omega_bps_tensor_weight_v1 as weight_oracle
else:
    import verify_one_omega_scalar_interface_reparam_v1 as source_oracle
    import verify_one_omega_bps_tensor_weight_v1 as weight_oracle

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CHARTER = source_oracle.CHARTER
CANDIDATE = HERE / "artifacts" / "one_omega_topological_so3_classical_v5_2_gate.json"
CANDIDATE_SHA256 = "d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b"
CANDIDATE_ACTION_SHA256 = "3011119e8d50c2b17471b464afa7fdd74b0a73ecc1e7708a6c95e06c2901551a"
CANDIDATE_SCHEMA = "holo.one-omega-topological-so3-classical-v5-2-gate.v1"
SCHEMA = "holo.one-omega-topological-tt-compatibility.v1"
OUTPUT = HERE / "artifacts" / "one_omega_topological_tt_compatibility_v1.json"
TEST = HERE / "test_one_omega_topological_tt_compatibility_v1.py"
canonical_digest = source_oracle.canonical_digest


class TopologicalTTError(ValueError):
    """A pinned input, exact restricted identity or receipt failed verification."""


def symbols_context() -> dict:
    result = dict(zip(("epsilon", "h", "ht", "hz", "hr", "htt", "hzz", "hrr", "A", "Ap", "App", "Op", "h0", "hr_plus", "hr_minus", "outward_plus", "outward_minus", "freq", "lambda_K"),
                     sp.symbols("epsilon h ht hz hr htt hzz hrr A Ap App Op h0 hr_plus hr_minus outward_plus outward_minus freq lambda_K", real=True)))
    result.update(dict(zip(("omega", "G", "M5c", "k", "Mb2", "xi", "eta", "B4bar", "mu_X", "v", "q", "Z", "material_M", "kappa", "beta"),
                           sp.symbols("Omega G M5c k Mb2 xi eta B4bar mu_X v q Z material_M kappa beta", positive=True))))
    result["y"] = sp.Symbol("y", real=True)
    return result


def _truncate(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    expanded = sp.expand(expression)
    return sum(expanded.coeff(epsilon, n)*epsilon**n for n in range(3))


def _matrix_truncate(matrix: sp.MatrixBase, epsilon: sp.Symbol) -> sp.Matrix:
    return sp.Matrix(matrix).applyfunc(lambda value: _truncate(value, epsilon))


def _zero(expression: sp.Expr | sp.MatrixBase) -> bool:
    if isinstance(expression, sp.MatrixBase):
        return all(sp.simplify(value) == 0 for value in expression)
    return sp.simplify(expression) == 0


def load_sources(candidate_path: Path = CANDIDATE, charter_path: Path = CHARTER) -> dict:
    """Read the two immutable actions; report their differences, not inheritance."""
    try:
        old = source_oracle.load_charter(charter_path)
        raw = Path(candidate_path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != CANDIDATE_SHA256:
            raise TopologicalTTError("candidate byte hash differs from pinned source")
        candidate = source_oracle._read_json(raw)
        if candidate.get("schema") != CANDIDATE_SCHEMA:
            raise TopologicalTTError("candidate schema mismatch")
        new_charter = candidate["exact_classical_charter"]
        new_action = new_charter["exact_action"]
        if canonical_digest(new_action) != CANDIDATE_ACTION_SHA256:
            raise TopologicalTTError("candidate exact-action digest mismatch")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise TopologicalTTError("canonical source verification failed") from exc
    old_action = old["action_charter"]["exact_action"]
    exact_names = ("superpotential", "bulk_potential", "full_V4", "wall_background")
    identical = {name: old_action[name] == new_action[name] for name in exact_names}
    if not all(identical.values()):
        raise TopologicalTTError("background literals differ between the pinned actions")
    old_parameters = old["action_charter"]["coefficient_policy"]["parameters"]
    new_parameters = new_charter["coefficient_policy"]["parameters"]
    changes = sorted(name for name in old_parameters.keys() & new_parameters.keys()
                     if old_parameters[name] != new_parameters[name])
    comparisons = {name: {"old": old_parameters.get(name), "candidate": new_parameters.get(name),
                         "status": ("added" if name not in old_parameters else "removed" if name not in new_parameters
                                    else "identical" if old_parameters[name] == new_parameters[name] else "changed")}
                   for name in sorted(old_parameters.keys() | new_parameters.keys())}
    literal_pairs = {name: {"old": old_action[name], "candidate": new_action[name], "relation": "exact string identity"}
                     for name in exact_names}
    for label, old_key, new_key, explanation in (
        ("GHY", "GHY", "GHY", "manual translation: same +M5^3 normalization and outward spacelike-normal convention"),
        ("foliation", "foliation", "foliation_lower", "manual translation: same displayed lower-order operators; lambda_K is changed"),
        ("solid", "solid", "removed_terms", "S_X removed; no elastic TT contact may be inherited"),
        ("bulk_derivative", "bulk", "bulk_gauged", "ordinary internal derivative replaced by the SO3 covariant derivative D_A"),
        ("Robin", "Robin", "Robin_intrinsic", "intrinsic associated-vector trace glued by iota; its metric-dependent frame varies")):
        literal_pairs[label] = {"old": old_action[old_key], "candidate": new_action[new_key], "relation": explanation}
    literal_pairs["BF"] = {"old": None, "candidate": new_action["BF"], "relation": "new BF sector; no claim of edge-mode elimination"}
    compatibility = {
        "literal_comparisons": literal_pairs, "parameter_comparisons": comparisons,
        "identical_background_literals": identical,
        "shared_parameter_changes": changes,
        "old_lambda_K": old_parameters["lambda_K"], "candidate_lambda_K": new_parameters["lambda_K"],
        "only_shared_numeric_parameter_change_is_lambda_K": changes == ["lambda_K"],
        "full_action_identity": False, "legacy_scalar_sector_inherited": False,
        "candidate_gauged_conformal_derivative": new_action["gauged_conformal_derivative"],
        "candidate_connection_trace": new_charter["definitions"]["connection_trace"],
    }
    if changes != ["lambda_K"] or new_action["removed_terms"] != "S_X=0 and every bulk screen-clock term=0":
        raise TopologicalTTError("unexpected candidate compatibility contract")
    return {"old_charter": old, "candidate": candidate, "compatibility": compatibility}


def derive_model() -> dict:
    s = symbols_context()
    e,h,ht,hz,hr,htt,hzz,hrr,A,Ap,App,Op = (s[name] for name in ("epsilon","h","ht","hz","hr","htt","hzz","hrr","A","Ap","App","Op"))
    o,G,M,k,Mb2,xi,lam,eta,B4,mu,v = (s[name] for name in ("omega","G","M5c","k","Mb2","xi","lambda_K","eta","B4bar","mu_X","v"))
    h0,hp,hm,freq,q = (s[name] for name in ("h0","hr_plus","hr_minus","freq","q"))
    def trunc(value): return _truncate(value,e)
    def mt(value): return _matrix_truncate(value,e)
    def quad(value): return sp.expand(value).coeff(e,2)
    def dr(value): return sp.diff(value,A)*Ap+sp.diff(value,Ap)*App+sp.diff(value,o)*Op+sp.diff(value,h)*hr+sp.diff(value,hr)*hrr
    def dz(value): return sp.diff(value,h)*hz+sp.diff(value,hz)*hzz
    def dt(value): return sp.diff(value,h)*ht+sp.diff(value,ht)*htt
    flat = sp.diag(-1,1,1,1)
    S4 = sp.zeros(4); S4[1,2]=S4[2,1]=h
    gamma = sp.exp(2*A)*(flat+e*S4)
    gamma_inverse = sp.exp(-2*A)*(flat-e*S4+e**2*S4*S4)
    sqrt_gamma = sp.exp(4*A)*(1-e**2*h**2/2)
    determinant = sp.factor(gamma.det())
    K_rad = mt(gamma_inverse*gamma.applyfunc(dr)/2)
    trace_K = trunc(sp.trace(K_rad))
    trace_K_squared = trunc(sp.trace(K_rad*K_rad))
    W = 3*M*k*sp.exp(-G*o**2/(6*M))
    Wprime = sp.diff(W,o)
    U = Wprime**2/(2*G)-2*W**2/(3*M)
    bps = {Ap:-W/(3*M), Op:Wprime/G, App:-Wprime**2/(3*M*G)}
    raw_radial = trunc(M*sqrt_gamma*(trace_K**2-trace_K_squared)/2-sqrt_gamma*(G*Op**2/2+U))
    raw_radial_L2 = sp.expand(quad(raw_radial))
    cross_primitive = -3*M*sp.exp(4*A)*Ap*h**2/2
    radial_L2_reduced = -M*sp.exp(4*A)*hr**2/4
    radial_mass_after_parts = sp.expand(raw_radial_L2-dr(cross_primitive)-radial_L2_reduced)
    radial_mass_BPS = sp.simplify(radial_mass_after_parts.subs(bps, simultaneous=True))
    # sqrt(gamma) R5 = sqrt(gamma)[R4+K^2-tr(K^2)] - 2 D_r(sqrt(gamma) K).
    EH_total_derivative = -M*dr(sqrt_gamma*trace_K)
    EH_UV_boundary = M*sqrt_gamma*trace_K
    GHY_UV = -M*sqrt_gamma*trace_K  # outward normal is -partial_r.

    S3 = sp.zeros(3); S3[0,1]=S3[1,0]=h
    spatial_metric = sp.eye(3)+e*S3
    spatial_inverse = sp.eye(3)-e*S3+e**2*S3*S3
    sqrt_spatial = 1-e**2*h**2/2
    frame = sp.eye(3)-e*S3/2+3*e**2*S3*S3/8
    frame_residual = mt(frame.T*spatial_metric*frame-sp.eye(3))
    K_time = mt(spatial_inverse*spatial_metric.applyfunc(dt)/2)
    K_z = mt(spatial_inverse*spatial_metric.applyfunc(dz)/2)
    trace_K_time = trunc(sp.trace(K_time))
    norm_K_time = trunc(sp.trace(K_time*K_time))
    trace_K_z = trunc(sp.trace(K_z))
    # Spatial Gaussian foliation in z; checked independently against Christoffels.
    R3 = trunc(-2*dz(trace_K_z)-trace_K_z**2-sp.trace(K_z*K_z))
    R3_raw_L2 = sp.expand(quad(sqrt_spatial*R3))
    R3_divergence = dz(2*h*hz)
    raw_tangential_L2 = sp.expand(quad(M*sp.exp(2*A)*sqrt_spatial*(norm_K_time-trace_K_time**2+R3)/2))
    tangential_L2 = sp.expand(raw_tangential_L2-M*sp.exp(2*A)*R3_divergence/2)
    acceleration = sp.zeros(3,1)  # T=t and unit lapse: a_i=partial_i log(1)=0.
    raw_brane = Mb2*sqrt_spatial*(norm_K_time-lam*trace_K_time**2+xi*R3+eta*acceleration.dot(acceleration)-B4*R3**2/(16*k**2))/2
    raw_brane_L2 = sp.expand(quad(raw_brane))
    brane_L2 = sp.expand(raw_brane_L2-Mb2*xi*R3_divergence/2)
    # Associated trace and acceleration are zero for every metric in this family,
    # even though the representative frame itself varies with the metric.
    varphi_H = frame*sp.zeros(3,1)
    robin_vector = varphi_H-s["y"]*acceleration
    Robin_TT_density = -s["kappa"]*(robin_vector.T*spatial_metric*robin_vector)[0]/2
    P_vacuum = sp.zeros(5,3)
    material_radius_squared = sp.S.Zero
    V4_vacuum = material_radius_squared**2/(2*sp.sqrt(1+material_radius_squared**2))
    material_TT_density = -s["Z"]*sum(value**2 for value in P_vacuum)/2-s["Z"]*s["material_M"]**2*o**-5*V4_vacuum
    B_dual_vacuum = sp.zeros(3)
    F_vacuum = sp.zeros(3)
    BF_TT_density = -sp.trace(B_dual_vacuum*F_vacuum)/2

    W0 = W.subs(o,1)
    wall_L2 = sp.expand(quad(-2*W0*sqrt_spatial.subs(h,h0)))
    F_UV = cross_primitive.subs({A:0,Ap:-W0/(3*M),h:h0}, simultaneous=True)
    bilateral_boundary_residual = sp.simplify(-2*F_UV+wall_L2)
    F_constant_IR = cross_primitive.subs({A:sp.log(o),Ap:-W/(3*M),h:h0}, simultaneous=True)
    F_constant_IR_limit = sp.limit(F_constant_IR,o,0,dir="+")
    radial_momentum = sp.diff(radial_L2_reduced,hr)
    original_radial_momentum = sp.diff(raw_radial_L2,hr)
    J_bulk = -radial_momentum.subs({A:0,hr:hp})-radial_momentum.subs({A:0,hr:hm})
    J_brane_position = -dt(sp.diff(brane_L2,ht))-dz(sp.diff(brane_L2,hz))
    J_brane = J_brane_position.subs({htt:-freq**2*h0,hzz:-q**2*h0})
    J_TT = sp.expand(J_bulk+J_brane)
    J_bulk_outward = J_bulk.subs({hp:-s["outward_plus"],hm:-s["outward_minus"]})
    original_J = -original_radial_momentum.subs({A:0,Ap:-W0/(3*M),h:h0,hr:hp}, simultaneous=True)-original_radial_momentum.subs({A:0,Ap:-W0/(3*M),h:h0,hr:hm}, simultaneous=True)+sp.diff(wall_L2,h0)+J_brane
    bulk_L2 = radial_L2_reduced+tangential_L2
    bulk_Euler = sp.expand(-dr(sp.diff(bulk_L2,hr))-dt(sp.diff(bulk_L2,ht))-dz(sp.diff(bulk_L2,hz)))
    null_wave = {hr:0,hrr:0,htt:-q**2*h,hzz:-q**2*h}
    null_boundary = {hp:0,hm:0,xi:1,freq:q}
    strain = v**2*(spatial_inverse-sp.eye(3))
    old_solid_L2 = sp.expand(quad(-mu*sp.trace(strain*strain)/4))
    old_solid_contact_H = sp.diff(old_solid_L2,h,2)
    old_solid_J = sp.diff(old_solid_L2,h).subs(h,h0)
    old_J_TT = J_TT+old_solid_J
    weight = weight_oracle.derive_model()
    ws = weight["symbols"]
    weight_subs = {ws["a"]:G/(6*M),ws["M5c"]:M,ws["k"]:k}
    M4_bulk_squared = weight["positive_norm_form"].subs(weight_subs, simultaneous=True)
    M4_bulk_squared_closed_form = weight["M4_bulk_squared"].subs(weight_subs, simultaneous=True)
    zero_mode_kinetic_coefficient = (Mb2+M4_bulk_squared)/4
    rows = {
        "inverse_series": mt(gamma*gamma_inverse-sp.eye(4)),
        "determinant_series": determinant+sp.exp(8*A)*(1-e**2*h**2),
        "sqrt_determinant_series": trunc(sqrt_gamma**2+determinant),
        "radial_trace": trace_K-(4*Ap-e**2*h*hr),
        "radial_trace_of_square": trace_K_squared-(4*Ap**2-2*Ap*e**2*h*hr+e**2*hr**2/2),
        "EH_GHY_outward_UV_cancellation": trunc(EH_UV_boundary+GHY_UV),
        "radial_integrated_BPS_mass": radial_mass_BPS,
        "frame_orthonormal_through_second_order": frame_residual,
        "spatial_curvature_density": R3_raw_L2-(3*hz**2/2+2*h*hzz),
        "spatial_curvature_integration_by_parts": R3_raw_L2-R3_divergence+hz**2/2,
        "bulk_tangential_kinetic": tangential_L2-M*sp.exp(2*A)*(ht**2-hz**2)/4,
        "brane_TT_kinetic": brane_L2-Mb2*(ht**2-xi*hz**2)/4,
        "lambda_no_quadratic_TT_term": sp.diff(brane_L2,lam),
        "eta_no_quadratic_TT_term": sp.diff(brane_L2,eta),
        "B4_no_quadratic_TT_term": sp.diff(brane_L2,B4),
        "material_vacuum_density": material_TT_density,
        "Robin_vacuum_density": Robin_TT_density,
        "BF_vacuum_density": BF_TT_density,
        "two_sides_wall_cancellation": bilateral_boundary_residual,
        "constant_profile_IR_primitive_vanishes": F_constant_IR_limit,
        "junction_from_original_and_integrated_actions": original_J-J_TT,
        "outward_momentum_orientation": J_bulk_outward+M*(s["outward_plus"]+s["outward_minus"])/2,
        "bulk_null_wave_in_restricted_equation": bulk_Euler.subs(null_wave),
        "boundary_null_wave_at_xi_one": J_TT.subs(null_boundary),
        "old_solid_contact_normalization": old_solid_contact_H+mu*v**4,
        "bulk_weight_positive_rewrite": M4_bulk_squared.rewrite(sp.exp)-M4_bulk_squared_closed_form,
    }
    residuals = {name: value.applyfunc(sp.simplify) if isinstance(value,sp.MatrixBase) else sp.simplify(value) for name,value in rows.items()}
    checks = {name:_zero(value) for name,value in residuals.items()}
    checks["positive_zero_mode_kinetic_weight"] = zero_mode_kinetic_coefficient.is_positive is True
    checks["BPS_weight_oracle_checks"] = all(weight["checks"].values())
    negative = {
        "frozen_frame_breaks_orthonormality": not _zero(mt(spatial_metric-sp.eye(3))),
        "omitted_second_bulk_UV_term": not _zero(-F_UV+wall_L2),
        "wrong_outward_momentum_sign": not _zero(J_bulk_outward-M*(s["outward_plus"]+s["outward_minus"])/2),
        "restored_solid_excludes_this_gapless_profile": not _zero(old_J_TT.subs(null_boundary)),
        "reversed_radial_kinetic_sign": not _zero(radial_L2_reduced-M*sp.exp(4*A)*hr**2/4),
    }
    return {"symbols":s,"S4":S4,"gamma":gamma,"gamma_inverse":gamma_inverse,"sqrt_gamma":sqrt_gamma,
            "determinant":determinant,"K_rad":K_rad,"trace_K":trace_K,"trace_K_squared":trace_K_squared,
            "S3":S3,"spatial_metric":spatial_metric,"spatial_inverse":spatial_inverse,"frame":frame,
            "frame_residual":frame_residual,"K_time":K_time,"R3":R3,"R3_raw_L2":R3_raw_L2,"R3_divergence":R3_divergence,
            "W":W,"U":U,"bps_substitutions":bps,"raw_radial_L2":raw_radial_L2,"cross_primitive":cross_primitive,
            "radial_mass_after_parts":radial_mass_after_parts,"radial_mass_BPS":radial_mass_BPS,"radial_L2_reduced":radial_L2_reduced,
            "EH_total_derivative":EH_total_derivative,"EH_UV_boundary":EH_UV_boundary,"GHY_UV":GHY_UV,
            "raw_tangential_L2":raw_tangential_L2,"tangential_L2":tangential_L2,"raw_brane_L2":raw_brane_L2,"brane_L2":brane_L2,
            "acceleration":acceleration,"material_TT_density":material_TT_density,"Robin_TT_density":Robin_TT_density,"BF_TT_density":BF_TT_density,
            "wall_L2":wall_L2,"F_UV":F_UV,"bilateral_boundary_residual":bilateral_boundary_residual,"F_constant_IR_limit":F_constant_IR_limit,
            "radial_momentum":radial_momentum,"original_radial_momentum":original_radial_momentum,
            "J_bulk":J_bulk,"J_bulk_outward":J_bulk_outward,"J_brane":J_brane,"J_TT":J_TT,"original_J_TT":original_J,
            "bulk_L2":bulk_L2,"bulk_Euler":bulk_Euler,"old_solid_L2":old_solid_L2,"old_solid_contact_H":old_solid_contact_H,
            "old_solid_J":old_solid_J,"old_J_TT":old_J_TT,"M4_bulk_squared":M4_bulk_squared,
            "M4_bulk_squared_closed_form":M4_bulk_squared_closed_form,"zero_mode_kinetic_coefficient":zero_mode_kinetic_coefficient,
            "checks":checks,"residuals":residuals,"negative_controls":negative}


def _provenance(path: Path) -> dict:
    return {"path":str(path.resolve().relative_to(REPO)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def _serialize(value: Any) -> Any:
    if isinstance(value,sp.MatrixBase): return [[sp.sstr(value[i,j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value,sp.Basic): return sp.sstr(value)
    if isinstance(value,dict): return {str(key):_serialize(item) for key,item in value.items()}
    if isinstance(value,(tuple,list)): return [_serialize(item) for item in value]
    return value


def build_payload(candidate_path: Path = CANDIDATE, charter_path: Path = CHARTER) -> dict:
    sources = load_sources(candidate_path,charter_path)
    model = derive_model()
    if not all(model["checks"].values()) or not all(model["negative_controls"].values()):
        raise TopologicalTTError("restricted TT identity or negative control failed")
    decision = {name:False for name in ("full_linear_TT_subspace_closure","physical_mode_admissibility","full_first_variation_pass",
        "C1_ACTION_pass","N1_ACTION_pass","C2_BRST_pass","C4_HESSIAN_pass","N2_CONSTRAINTS_pass","N3_CHARACTERISTICS_pass",
        "N4_JUNCTION_BENDING_pass","N5_COUPLED_BVP_pass","N6_GLOBAL_STABILITY_pass","N7_LINEAR_REDUCTION_pass",
        "BF_edge_modes_eliminated","finite_momentum_DtN_solved","complete_TT_spectrum_pass","P4_full_same_action_pass","B4_pass","B5_pass")}
    decision.update({"pinned_actions_restricted_TT_compatibility_verified":True,
                     "restricted_TT_bulk_and_boundary_solution_with_positive_norm":True,
                     "absence_of_elastic_contact_in_restricted_topological_TT":True})
    equations = {name:_serialize(value) for name,value in model.items() if name not in ("symbols","checks","residuals","negative_controls","bps_substitutions")}
    payload = {
        "schema":SCHEMA,
        "sources":{"old_charter":{"path":str(CHARTER.relative_to(REPO)),"sha256":source_oracle.CHARTER_BYTES_SHA256,
                                  "action_sha256":source_oracle.ACTION_SHA256,"calculation_sha256":source_oracle.CALCULATION_SHA256},
                   "candidate":{"path":str(CANDIDATE.relative_to(REPO)),"sha256":CANDIDATE_SHA256,"exact_action_sha256":CANDIDATE_ACTION_SHA256}},
        "compatibility":sources["compatibility"],
        "scope":{
            "domain":"G,M5c,k,Mb2>0; positive Omega; h12=h21=epsilon*h(t,z,r); each bulk r>=0 with UV outward normal -partial_r",
            "background":"decreasing one-Omega scalar BPS branch; A(0)=0,Omega(0)=1; phi=A_connection=B=a_mu=0; T=t; common fixed wall",
            "expansion":"epsilon through order two; one off-diagonal TT polarization; compactly supported variations, with IR primitive vanishing for the bounded constant radial profile",
            "geometry_translation":"radial and temporal ADM identities plus spatial Gaussian-foliation Ricci identity, manually translated and checked by independent Christoffel/shear tests",
            "frame":"inverse normalized spatial frame varies as I-epsilon*S/2+3*epsilon^2*S^2/8; bulk full inverse frame includes exp(-A)",
            "connection_gluing":"A_Sigma is not identified with the Levi-Civita connection; A_Sigma=0 is allowed in the common moving-frame trivialization with r_plus=r_minus=I",
            "material_BF_reason":"With phi=0,D_A phi=0,F=0,B=0 and acceleration=0, the displayed material/Robin/BF densities vanish identically on this TT family; no representation-spin argument or BF edge elimination is used",
            "restricted_variation_limit":"Varying S[h] does not establish the omitted Omega,T,lapse,shift,bending or gauge equations, their constraints or the full linear TT subspace closure",
            "null_profile":"radially constant generalized plane wave exp(-i*freq*t+i*q*z), q>0, freq^2=q^2, xi=1 solves the restricted bulk equation and natural TT junction; finite tangential energy requires wave packets",
            "norm":"positive coefficient (Mb2+M4_bulk_squared)/4 for this restricted mode; not a coupled stability or quantum-graviton theorem",
            "legacy_scalar_sector_inherited":False,"legacy_lambda_K_reused":False,"numerical_sampling_used_as_proof":False},
        "equations":equations,"checks":model["checks"],"residuals":_serialize(model["residuals"]),
        "negative_controls":model["negative_controls"],"decision":decision,
        "provenance":{"verifier":_provenance(Path(__file__)),"test":_provenance(TEST),
                      "canonical_source_reader":_provenance(Path(source_oracle.__file__)),
                      "BPS_weight_verifier":_provenance(Path(weight_oracle.__file__)),"sympy_version":sp.__version__}}
    payload["calculation_digest"]={"algorithm":"sha256(canonical-json(payload without calculation_digest))","sha256":canonical_digest(payload)}
    return payload


def validate_payload(doc: Any, candidate_path: Path = CANDIDATE, charter_path: Path = CHARTER) -> None:
    if not isinstance(doc,dict) or not isinstance(doc.get("calculation_digest"),dict):
        raise TopologicalTTError("receipt and calculation_digest must be dictionaries")
    try:
        actual = canonical_digest({key:value for key,value in doc.items() if key!="calculation_digest"})
    except (TypeError,ValueError) as exc:
        raise TopologicalTTError("receipt is not finite canonical JSON") from exc
    if doc["calculation_digest"].get("sha256") != actual:
        raise TopologicalTTError("receipt digest mismatch")
    if canonical_digest(doc) != canonical_digest(build_payload(candidate_path,charter_path)):
        raise TopologicalTTError("receipt differs from freshly derived equations, sources, scope or provenance")


def main(argv: list[str] | None = None) -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--write",nargs="?",const=OUTPUT,type=Path,help="create a new receipt exclusively")
    group.add_argument("--verify",type=Path,help="recompute an existing receipt")
    args=parser.parse_args(argv)
    if args.verify:
        try: payload=weight_oracle._read_payload(args.verify)
        except ValueError as exc: raise TopologicalTTError("invalid receipt JSON") from exc
        validate_payload(payload)
    else:
        payload=build_payload()
        if args.write:
            with args.write.open("x",encoding="utf-8") as stream:
                stream.write(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"schema":SCHEMA,"checks_passed":sum(payload["checks"].values()),
                      "negative_controls_rejected":sum(payload["negative_controls"].values()),
                      "calculation_sha256":payload["calculation_digest"]["sha256"],"decision":payload["decision"]},sort_keys=True))


if __name__ == "__main__":
    main()
