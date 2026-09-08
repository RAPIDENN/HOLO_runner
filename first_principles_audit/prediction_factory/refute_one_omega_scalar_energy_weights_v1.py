#!/usr/bin/env python3
"""Independent certification (Claude, from the v2.2 bulk ODEs) of the scalar-master identity and of the
weights of the beta Robin form used in Codex's spectral energy proof (5acd2e1 / 14bbf29).

Inputs: my own artifact one_omega_charter_linear_junction_v2_2_gate.json (17 helicity ODEs in Gaussian-normal
gauge, proper w), Codex's scalar ansatz h = 2P eta + 2 dd E, delta Omega = C (read from rows:76-119, not imported),
BPS with A = log Omega. Checks: (1) L_R = R'' + 6A'R' + e^{-2A}(W^2-q^2)R equals (C_m)' + 6A'C_m - E_Omega/(G Omega)
+ E_44/(3M) exactly, R = P - C/Omega, C_m = P' + G Omega' C/(3M); (2) momentum constraints E_04 = 3iMW C_m,
E_34 = -3iMq C_m; (3) the density -G[Omega^6 R'^2 + Omega^4 (dR)^2]/2 has Euler-Lagrange G Omega^6 L_R, so the
weights Omega^6|R'|^2 in L^2(Omega^4) of the Robin form are certified; (4) W''(1) = G a0 (1 - G/(3M)), a0 = A'(0).
Nothing physical is promoted.  Writes artifacts/refute_one_omega_scalar_energy_weights_v1.json.
"""
import hashlib, json, platform, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "refute_one_omega_scalar_energy_weights_v1.json"

import json, sympy as sp
SRC = HERE / 'artifacts' / 'one_omega_charter_linear_junction_v2_2_gate.json'
doc = json.load(open(SRC)); SRC_SHA = hashlib.sha256(SRC.read_bytes()).hexdigest()
w = sp.Symbol('w', real=True); q, W = sp.symbols('q_mom W_freq', real=True)
M5c, kinf, G = sp.symbols('M5c k_inf G', positive=True); s = sp.Symbol('s')
A = sp.Function('A'); Om = sp.Function('Omega')
names = ['H00','H01','H02','H03','H11','H12','H13','H22','H23','H33','Wm','X0']
funcs = {n: sp.Function(n) for n in names}
loc = {'w': w, 'q_mom': q, 'W_freq': W, 'M5c': M5c, 'k_inf': kinf, 'G': G, 's': s, 'A': A, 'Omega': Om, **funcs}
odes = {k: sp.sympify(v, locals=loc) for k, v in doc['helicity_odes'].items() if k in ('04','34','44','Omega','00','11','33','03')}
# ansatz: P, E, C como funciones de w
P, E, C = sp.Function('P')(w), sp.Function('E')(w), sp.Function('C')(w)
prof = {'H00': -2*P - 2*W**2*E, 'H03': 2*W*q*E, 'H11': 2*P, 'H22': 2*P, 'H33': 2*P - 2*q**2*E, 'Wm': C,
        'H01': 0, 'H02': 0, 'H12': 0, 'H13': 0, 'H23': 0, 'X0': 0}
sub = {funcs[n](w): prof[n] for n in names}
rows = {k: sp.expand(v.subs(sub).doit().subs(s, 1)) for k, v in odes.items()}
# fondo BPS (lado +): A' = -k e^{-G Om^2/(6M)}, Om' = A' Om ; segundas derivadas por regla de la cadena
Ap = -kinf*sp.exp(-G*Om(w)**2/(6*M5c)); Op = Ap*Om(w)
def bps(e):
    e = e.subs(sp.Derivative(A(w),(w,2)), sp.diff(Ap, w)).subs(sp.Derivative(Om(w),(w,2)), sp.diff(Op, w))
    for _ in range(2): e = e.subs({sp.Derivative(A(w),w): Ap, sp.Derivative(Om(w),w): Op})
    return sp.expand(e)
O = sp.Symbol('Om', positive=True)   # Omega(w) como símbolo positivo; A = log Omega (BPS, A(0)=0)
def canon(e):
    e = e.subs(A(w), sp.log(Om(w)))
    e = e.replace(lambda x: x.is_Pow and x.base.func == sp.exp, lambda x: sp.exp(x.base.args[0]*x.exp))
    return sp.expand(sp.powsimp(sp.expand(e), force=True))
rows = {k: canon(bps(v)) for k, v in rows.items()}
R = P - C/Om(w)
LR = bps(sp.diff(R, w, 2) + 6*Ap*sp.diff(R, w) + sp.exp(-2*A(w))*(W**2 - q**2)*R)
Cm = sp.diff(P, w) + G*Op*C/(3*M5c)
comb = bps(sp.diff(Cm, w) + 6*Ap*Cm - rows['Omega']/(G*Om(w)) + rows['44']/(3*M5c))
res = sp.simplify(canon(LR) - canon(comb))
res = sp.simplify(res.subs(Om(w), O))
checks = {"master_identity_exact": bool(res == 0)}
# ligaduras de momento (sus formas): rows['04'] = 3 i M W C_m ; rows['34'] = -3 i M q C_m
r04 = sp.simplify(rows['04'] - 3*sp.I*M5c*W*Cm); r34 = sp.simplify(rows['34'] + 3*sp.I*M5c*q*Cm)
checks["time_momentum_constraint_04"] = bool(r04 == 0); checks["space_momentum_constraint_34"] = bool(r34 == 0)
# EL de la densidad por cara -G[Om^6 R'^2 + Om^4 (dR)^2]/2 con (dR)^2 -> e^{-2A}·... en el ansatz: comprobar que reproduce L_R (salvo factor)
Rf = sp.Function('Rf')(w)
dens = -G*(Om(w)**6*sp.diff(Rf,w)**2 + Om(w)**4*(q**2 - W**2)*Rf**2)/2   # onda plana: (dR)^2 -> (q^2-W^2) R^2 con signatura
EL = sp.diff(dens, Rf) - sp.diff(sp.diff(dens, sp.diff(Rf,w)), w)
EL = bps(sp.expand(EL))
LR_f = bps(sp.diff(Rf,w,2) + 6*Ap*sp.diff(Rf,w) + sp.exp(-2*A(w))*(W**2-q**2)*Rf)
ratio = sp.simplify(canon(EL)/canon(LR_f)).subs(Om(w), O)
ratio = sp.simplify(ratio)
checks["beta_form_density_EL_equals_G_Omega6_L_R"] = bool(sp.simplify(ratio - G*O**6) == 0)
# W''(1) = G a0 (1 - G/3M) con a0 = A'(0) = -k e^{-G/6M}
qq = sp.Symbol('qq', positive=True); Wq = 3*M5c*kinf*sp.exp(-G*qq**2/(6*M5c)); Wpp1 = sp.diff(Wq, qq, 2).subs(qq, 1)
a0 = -kinf*sp.exp(-G/(6*M5c)); checks["Wpp1_equals_G_a0_1_minus_G_over_3M"] = bool(sp.simplify(Wpp1 - G*a0*(1 - G/(3*M5c))) == 0)

payload = {"schema": "holo.refute-one-omega-scalar-energy-weights.v1",
           "source_bulk_v2_2_sha256": SRC_SHA, "ansatz": "h = 2P eta + 2 dd E; delta Omega = C; plane wave e^{i(q x3 - W t)}; BPS A = log Omega, side +",
           "definitions": {"R": "P - C/Omega", "C_m": "P' + G Omega' C/(3M)", "L_R": "R'' + 6A'R' + e^{-2A}(W^2 - q^2) R",
                           "beta_form_density_per_side": "-G[Omega^6 R'^2 + Omega^4 (dR)^2]/2"},
           "checks": checks, "verdict": "PESAS CERTIFICADAS" if all(checks.values()) else "SIN VEREDICTO",
           "not_certified": ["reduced density L_3 (03a6956)", "static all-q bound (d7e7f31)", "brane J_D = -2G R' - beta D with no W'' remainder (rows:derive_boundary; only W''(1) = G a0(1-G/3M) checked here)"],
           "provenance": {"generator": Path(__file__).name, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sympy": sp.__version__, "python": platform.python_version()}}
payload["calculation_digest"] = hashlib.sha256(json.dumps({k: payload[k] for k in ("schema","source_bulk_v2_2_sha256","ansatz","definitions","checks","verdict","not_certified")}, sort_keys=True, separators=(",",":")).encode()).hexdigest()
OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(json.dumps({"verdict": payload["verdict"], "checks": checks}))
