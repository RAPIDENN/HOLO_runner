#!/usr/bin/env python3
"""Independent scalar-master identity in pinned Gaussian-normal bulk rows.

The row combination never divides by frequency or the Lorentzian momentum
square. It remains an identity on the null cone; solving constraints there,
and global gauge/zero-mode admissibility, require additional analysis.
"""
from __future__ import annotations
import hashlib
import sympy as sp
if __package__:
    from . import verify_one_omega_topological_tt_closure_v1 as source
else:
    import verify_one_omega_topological_tt_closure_v1 as source

BULK=source.BULK
BULK_SHA=source.BULK_SHA


def context():
    symbols=dict(source.SYMBOLS)
    symbols.update({n:sp.Symbol(n,real=True) for n in ('P','P1','P2','E','E1','E2','C','C1','C2')})
    return symbols


def project_rows(doc):
    s=context();w=s['w'];F,q=s['W_freq'],s['q_mom']
    P=[s[n] for n in ('P','P1','P2')]
    E=[s[n] for n in ('E','E1','E2')]
    C=[s[n] for n in ('C','C1','C2')]
    profiles={'H00':[-2*P[j]-2*F**2*E[j] for j in range(3)],
              'H03':[2*F*q*E[j] for j in range(3)],
              'H11':[2*P[j] for j in range(3)],
              'H22':[2*P[j] for j in range(3)],
              'H33':[2*P[j]-2*q**2*E[j] for j in range(3)],'Wm':C}
    sub={s['s']:1,source.FUNCTIONS['A'](w):s['A_value'],
         source.FUNCTIONS['Omega'](w):s['Omega_value']}
    for name in source.PROFILE_NAMES:
        for order in range(3):
            sub[sp.diff(source.FUNCTIONS[name](w),w,order)]=profiles.get(name,[0,0,0])[order]
    result={name:sp.simplify(source.parse_expression(doc['helicity_odes'][name]).xreplace(sub))
            for name in ('04','34','44','Omega')}
    return s,result


def derive_rows(doc=None):
    if doc is None:
        doc=source._load(BULK,BULK_SHA)
    s,rows=project_rows(doc)
    G,M,k,O,A,F,q=(s[n] for n in ('G','M5c','k_inf','Omega_value','A_value','W_freq','q_mom'))
    P,P1,P2,E,E1,E2,C,C1,C2=(s[n] for n in ('P','P1','P2','E','E1','E2','C','C1','C2'))
    Ap=-k*sp.exp(-G*O**2/(6*M));Op=Ap*O
    def radial(expression):
        return sp.diff(expression,A)*Ap+sp.diff(expression,O)*Op+sum(
            sp.diff(expression,x)*dx for x,dx in [(P,P1),(P1,P2),(E,E1),(E1,E2),(C,C1),(C1,C2)])
    curvature=P-C/O
    curvature_first=radial(curvature)
    master=sp.expand(radial(curvature_first)+6*Ap*curvature_first+
                     sp.exp(-2*A)*(F**2-q**2)*curvature)
    momentum=P1+G*Op*C/(3*M)
    combination=radial(momentum)+6*Ap*momentum-rows['Omega']/(G*O)+rows['44']/(3*M)
    residuals={
        'time_momentum_constraint':sp.simplify(rows['04']-3*sp.I*M*F*momentum),
        'space_momentum_constraint':sp.simplify(rows['34']+3*sp.I*M*q*momentum),
        'master_identity':sp.simplify(master-combination),
        'null_cone_identity':sp.simplify((master-combination).subs(F,q)),
    }
    return {'symbols':s,'rows':rows,'background':{'A_prime':Ap,'Omega_prime':Op},
            'curvature':curvature,'curvature_first':curvature_first,'master_operator':master,
            'momentum_constraint':momentum,'row_combination':combination,
            'identity_coefficients':{'D_momentum':sp.Integer(1),'momentum':6*Ap,
                                     'Omega_row':-1/(G*O),'44_row':1/(3*M)},
            'residuals':residuals,'checks':{name:value==0 for name,value in residuals.items()}}


def derive_boundary(model=None):
    """Canonical GN momenta and constraint-reduced bilateral boundary response.

    The wall stays at r=0 in this representative, so Z=P and D=deltaOmega.
    In invariant notation R=Z-D. Independent moving-embedding equations are
    not derived here. The radial response K_v is left symbolic; it denotes
    the canonical regular bulk response, not a fitted or subtracted kernel.
    """
    model=derive_rows() if model is None else model
    s=model['symbols'];G,M,k=(s[n] for n in ('G','M5c','k_inf'))
    F,q=s['W_freq'],s['q_mom'];d=F**2-q**2
    Z,D,Rp,Kv=sp.symbols('Z D R_prime K_v',real=True)
    beta=sp.Symbol('beta_wall',positive=True)
    a0=-k*sp.exp(-G/(6*M));t0=G/(3*M)
    Wp0=G*a0;Wpp0=G*a0*(1-t0)
    P1=-G*a0*D/(3*M)
    C1=a0*(1-t0)*D-Rp
    longitudinal=sp.Symbol('d_E_prime',real=True)
    trace_h_prime=8*P1+2*longitudinal
    J_Z_before=-3*M*trace_h_prime-8*Wp0*D
    J_D_before=2*G*C1-(2*Wpp0+beta)*D
    longitudinal_solution=-d*Z/a0-t0*Rp
    J_Z=sp.expand(J_Z_before.subs(longitudinal,longitudinal_solution))
    J_D=sp.expand(J_D_before)
    substitutions={s['A_value']:0,s['Omega_value']:1,s['P']:Z,s['P1']:P1,
                   s['C']:D,s['C1']:C1}
    projected_hamiltonian=model['rows']['44'].subs(substitutions,simultaneous=True)
    # Compare coefficients without dividing by d, including its zero locus.
    constraint_reference=3*M*a0*(d*s['E1']-longitudinal_solution)
    currents=sp.Matrix([J_Z,J_D])
    force=currents.subs(Rp,-Kv*(Z-D)/2)
    H=force.jacobian(sp.Matrix([Z,D])).applyfunc(sp.simplify)
    reference=sp.Matrix([[6*M*d/a0-G*Kv,G*Kv],[G*Kv,-G*Kv-beta]])
    energy=(sp.Matrix([Z,D]).T*H*sp.Matrix([Z,D]))[0]/2
    # v_b=sqrt(G)*(D-Z); compare to canonical master plus the beta coupling.
    vb=sp.Symbol('v_boundary',real=True)
    in_v=sp.expand(energy.subs(D,Z+vb/sp.sqrt(G)))
    expected_v=3*M*d*Z**2/a0-Kv*vb**2/2-beta*(Z+vb/sp.sqrt(G))**2/2
    residuals={
        'hamiltonian_fixes_d_Eprime_without_inverting_d':sp.simplify(projected_hamiltonian-constraint_reference),
        'metric_force_from_canonical_momentum':sp.simplify(J_Z-(6*M*d*Z/a0+2*G*Rp)),
        'scalar_force_from_canonical_momentum':sp.simplify(J_D-(-2*G*Rp-beta*D)),
        'symmetric_boundary_response':H-reference,
        'canonical_master_plus_local_Z_contact':sp.simplify(in_v-expected_v),
        'null_cone_contact':sp.simplify((H-reference).subs(F,q)),
    }
    residuals={key:value.applyfunc(sp.simplify) if isinstance(value,sp.MatrixBase) else sp.simplify(value)
               for key,value in residuals.items()}
    checks={key:all(v==0 for v in value) if isinstance(value,sp.MatrixBase) else value==0
            for key,value in residuals.items()}
    return {'symbols':{'Z':Z,'D':D,'R_prime':Rp,'K_v':Kv,'beta':beta,'v_boundary':vb},
            'A_prime_UV':a0,'W_prime_UV':Wp0,'W_second_UV':Wpp0,
            'd_Eprime_solution':longitudinal_solution,'canonical_metric_force':J_Z,
            'canonical_scalar_force':J_D,'response_matrix':H,'quadratic_action':energy,
            'action_in_Z_v':in_v,'residuals':residuals,'checks':checks,
            'scope':{'bilateral_fixed_GN_boundary_data':True,
                     'moving_embedding_equations_certified':False,
                     'regular_kernel_computed_in_closed_form':False,
                     'complete_brane_ADM_khronon_tensor_constraints_assembled':False,
                     'full_N7':False,'full_P4':False}}
