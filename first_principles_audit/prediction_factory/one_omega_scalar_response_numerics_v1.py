"""Numerical evaluation of the derived three-field scalar response.

This is the full (n,N3,zeta) block after ONLY the proven material and Omega
pivots have been eliminated. No shift/lapse pivot is dropped. Singular values
are numerical conditioning diagnostics, not a count of physical modes or a
proof of absence of zeros. q=0 and the light cone require different charts.
"""
from __future__ import annotations
import cmath
import hashlib
import json
import math
from pathlib import Path
import numpy as np
if __package__:
    from . import one_omega_bps_dtn_numerics_v1 as kernels
else:
    import one_omega_bps_dtn_numerics_v1 as kernels

HERE=Path(__file__).resolve().parent
CANDIDATE=HERE/'artifacts/one_omega_topological_so3_classical_v5_2_gate.json'
CANDIDATE_SHA='d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b'
PARAMETER_NAMES={'M':'M5_cubed','G':'compensator_metric_G','k':'k_infinity',
    'Mb':'brane_Mb_squared','beta':'brane_beta','lam':'lambda_K','eta':'eta',
    'xi':'xi','b4':'B4_bar','kap':'Robin_kappa_hat','Z5':'material_Z5_per_side',
    'y2':'Robin_y_squared'}


def frozen_parameters():
    data=CANDIDATE.read_bytes()
    if hashlib.sha256(data).hexdigest()!=CANDIDATE_SHA:
        raise ValueError('frozen candidate receipt changed')
    all_parameters=json.loads(data)['exact_classical_charter']['coefficient_policy']['parameters']
    # Literal decimals are retained. y_squared is explicitly selected in the
    # policy; the separately printed floating square root is not resquared.
    return {short:all_parameters[long] for short,long in PARAMETER_NAMES.items()}


def matrix_from_kernels(w,q,p,KT,Kv,parameters=None):
    """Algebraic matrix for independently supplied kernels; no branch claim.

    The caller may use arbitrary non-pole complex kernels to audit the
    transcription. The physical numerical evaluator below fixes the branch.
    """
    P=frozen_parameters() if parameters is None else dict(parameters)
    M,G,k,Mb,beta,lam,eta,xi,b4,kap,Z5,y2=(P[n] for n in PARAMETER_NAMES)
    w,p,KT,Kv=map(complex,(w,p,KT,Kv));q=float(q)
    values=(w,p,KT,Kv,q,*P.values())
    if not all(np.isfinite(v) for v in values):raise ValueError('nonfinite scalar input')
    if q<=0:raise ValueError('scalar spatial gauge requires q>0')
    p2=q*q-w*w
    if p2==0:raise ValueError('Lorentz projectors require nonzero p_squared')
    PC=kap+2*Z5*p;PD=beta+G*Kv
    if PC==0 or PD==0:raise ValueError('eliminated pivot vanishes')
    PiR=2*Z5*kap*y2*p/PC
    delta=G*Kv*beta/PD
    a0=-k*math.exp(-G/(6*M))
    H=np.zeros((3,3),dtype=complex)
    H[0,0]=(Mb*eta-PiR)*q*q
    H[0,2]=H[2,0]=2*Mb*xi*q*q
    H[1,1]=Mb*(1-lam)*q*q
    H[1,2]=H[2,1]=Mb*(1-3*lam)*w*q
    H[2,2]=Mb*((3-9*lam)*w*w+2*xi*q*q-b4*q**4/k**2)
    U=np.array([q*q,-w*q,-q*q],dtype=complex)
    Z=np.array([0,0,1],dtype=complex)+U/(3*p2)
    H-=2*M*KT*np.outer(U,U)/(3*p2*p2)
    H+=(-6*M*p2/a0-delta)*np.outer(Z,Z)
    return {'matrix':H,'P_material':PC,'P_Omega':PD,'Pi_R':PiR,
            'Delta_beta':delta,'p_squared':p2,'U':U,'Z':Z}


def evaluate_scalar(s,q,*,parameters=None,**solver_options):
    """Fresh BPS kernels and the full three-field response for Re(s)>0,q>0."""
    s=complex(s);q=float(q)
    if not np.isfinite(s) or s.real<=0:raise ValueError('Re(s)>0 required')
    if not np.isfinite(q) or q<=0:raise ValueError('q>0 required')
    P=frozen_parameters() if parameters is None else dict(parameters)
    p=cmath.sqrt(s*s+q*q)
    if p.real<=0:raise ValueError('regular momentum branch unresolved')
    if any(key in solver_options for key in ('sector','k','a')):
        raise ValueError('sector, k and deformation come from the action')
    rows={name:kernels.evaluate_dtn(p,sector=name,k=P['k'],a=P['G']/(6*P['M']),**solver_options)
          for name in ('TT','scalarR')}
    result=matrix_from_kernels(1j*s,q,p,rows['TT']['kernel'],rows['scalarR']['kernel'],P)
    H=result['matrix']
    scales=np.sqrt(np.maximum(np.max(abs(H),axis=1),np.finfo(float).tiny))
    balanced=H/scales[:,None]/scales[None,:]
    singular=np.linalg.svd(balanced,compute_uv=False)
    phase,logabs=np.linalg.slogdet(H)
    return {**result,'s':s,'q':q,'p':p,'parameters':P,'kernels':rows,
            'determinant':np.linalg.det(H),'det_phase':phase,'logabsdet':float(logabs),
            'balanced_singular_values':singular,'balanced_matrix':balanced,
            'smallest_to_largest_singular_value':float(singular[-1]/singular[0]),
            'no_RHP_zero_certified':False,'full_physical_mode_count_certified':False}
