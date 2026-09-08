# Regular temporal vector chart for the proposed H18 response

This note changes a gauge chart of the already assembled linear response.
It does not change the proposed action, adopt chi or claim a global gauge
fixing of the bulk/embedding system. The previous H_a3=0 reconstruction
contains 1/q; that formula remains singular as q->0. The present chart
uses N_a=0 instead, allowed for w=i*s with Re(s)>0, so w is nonzero.
It gives a distinct representative with coefficient bounds uniform in
spatial q at fixed s. It is not a uniform theorem at s=0 or on the whole
imaginary axis.

## 1. Vector action and Ward row

For either transverse axis, let H=H_a3, N=N_a and theta denote its coupled
orientation. The sign o is +1 for (H13,theta2) and -1 for (H23,theta1).
Write

    z=s²+q²=q²-w², w=i*s, Re(s)=sigma>0,
    B=b+m(z), b>0, m(z)=integral lambda/(lambda+z) dmu_m,
    chi>0, q>=0.

The positive finite measure and its energy-domain origin are those of the
pinned H18 response lemma. This is not a fitted rational kernel. The exact
three-field quadratic density from that assembly is

    L=B(qN+wH)²/4
      +chi/2[(w theta+o qN/2)²-q²(theta-oH/2)²].             (1)

The spatial diffeomorphism, including the horizontal-frame compensation,
acts as

    delta(N,H,theta)=i*(-w,q,o*q/2)*xi.                    (2)

Its Noether row is, off shell,

    E_N=(q/w)(E_H+o E_theta/2).                            (3)

Thus imposing N=0 does not lose an independent equation when the two
remaining equations hold. With a forcing vector f, the same conclusion
requires its Ward compatibility

    f_N=(q/w)(f_H+o f_theta/2).                            (4)

An arbitrary force violating (4) is not made solvable by gauge fixing.
At q=0 the condition reduces to f_N=0. No division by q is used.

This source condition is the diffeomorphism Ward condition of the selected
response. It does not supply a BF lift for arbitrary orientation forcing:
a nonzero theta source changes the current-divergence equation. Extending
such a forced response requires corresponding BF/interface source data;
the homogeneous-current BF reconstruction cannot simply be reused.

## 2. Invariant variables and the N=0 chart

Define

    U=qN+wH, Psi=theta-oH/2.

Both are invariant under (2). Setting N=0 is possible since w!=0. In this
chart the inverse change of the two remaining coordinates is

    H=U/w, theta=Psi+o U/(2w).                             (5)

The Jacobian from (U,Psi) to (H,theta) has determinant 1/w and is invertible
also at q=0. Direct substitution into (1), before eliminating any field,
gives

    L=B U²/4+chi/2[(wPsi+oU/2)²-q²Psi²].                   (6)

For the quadratic Hessian in (U,Psi),

    P_U=(2B+chi)/4,
    K_U,Psi=o*chi*w/2,
    K_Psi,Psi=chi*(w²-q²).

Its retained-pivot Schur factor is

    S_Psi=Keff*w²-chi*q², Keff=2chi B/(2B+chi).            (7)

The positive-real arguments in the H18 lemma imply both P_U!=0 and
S_Psi!=0 for Re(s)>0, including q=0. Nothing is cancelled from the
determinant. In the original N=0 variables,

    det K_(H,theta)=w² P_U S_Psi.                         (8)

Equation (8) also retains the invertibility condition w!=0 of the chart.
At q=0 the directly assembled matrix is diagonal with entries B*w²/2 and
chi*w², giving det=chi*B*w^4/2. This equals (8). The metric response has
not disappeared into the new orientation factor.

## 3. Reconstruction and bounds

Let f_U=(f_H+o f_theta/2)/w and f_Psi=f_theta, obtained by the covector
transformation corresponding to (5). The U equation gives

    U=4 f_U/(2B+chi)-2o chi*w*Psi/(2B+chi),
    H=4 f_U/[w(2B+chi)]-2o chi*Psi/(2B+chi),
    theta=2o f_U/[w(2B+chi)]+2B*Psi/(2B+chi).             (9)

The remaining equation is

    S_Psi Psi=f_Psi-2o chi*w*f_U/(2B+chi).

For f_U=0, (9) has no q denominator. In particular it remains finite as
q->0 at fixed s, rather than following the singular H=0 representative.
The argument applies to compatible forcing as well, not just to the
trivial unforced kernel of a strictly invertible response.

For an atom lambda>=0 of the finite positive measure,

    Re[s*lambda/(lambda+s²+q²)]
      = sigma*lambda*(|s|²+q²+lambda)/|lambda+s²+q²|² >= 0.

The integrand lambda/(lambda+z) is uniformly bounded in lambda on each
compact subset of the slit z plane; its large-lambda limit is 1.
Finite mass therefore suffices for locally dominated integration and
holomorphy. No first moment of the measure is assumed. For lambda=0 the
integrand is zero in this domain. Integration gives Re(sB)>=b*sigma.
The reciprocal positive-real identity

    s*Keff = [1/(chi*s)+1/(2*s*B)]^(-1)

and its K0-subtracted version in the pinned H18 lemma give the strict
Schur lower bound used below. In particular, the spectral representation
gives

    Re[s(2B+chi)] >= (2b+chi)*sigma > 0.

Consequently, putting d=2b+chi,

    |1/(2B+chi)| <= |s|/(d*sigma),
    |1/[w(2B+chi)]| <= 1/(d*sigma).                        (10)

The bounds are uniform in q>=0. They yield

    |H| <= 4|f_U|/(d*sigma)+2chi|s||Psi|/(d*sigma),
    |theta| <= 2|f_U|/(d*sigma)
                +(1+chi|s|/(d*sigma))|Psi|.              (11)

The field N is zero in this representative. Joint continuity follows
from holomorphy of m off its negative-real spectral cut and the same
nonvanishing denominator. The previously proved bound

    Re[-S_Psi/s] >= sigma[2chi*b/(2b+chi)+chi*q²/|s|²]

continues to apply, including the q=0 value obtained here directly.

This also bounds the actual forced response, rather than assuming Psi is
bounded. Put r=|s| and K0=2chi*b/(2b+chi)>0. Then

    |S_Psi| >= r*sigma*K0+chi*sigma*q²/r,
    |Psi| <= [|f_Psi|+2chi*r²|f_U|/(d*sigma)]
              / [r*sigma*K0+chi*sigma*q²/r].               (12)

The numerator uses (10) on the mixed source in the Schur equation. Its
denominator follows from |S_Psi/s|>=Re[-S_Psi/s] and is strictly positive.
Moreover |f_U|<=(|f_H|+|f_theta|/2)/r. Combining (12) with (11) therefore
gives coefficient bounds for compatible forcing in the original retained
fields, uniform in q>=0 at each fixed s in the open right half-plane.
These bounds do not replace the force compatibility condition (4).

On a compact subset of Re(s)>0, the constants in (10)-(11) are bounded
independently of spatial momentum. These are amplitude/response bounds
for this chart and its transformed force. They do not by themselves
supply a global spacetime Sobolev estimate: (5) and the spatial
transformation of a bulk diffeomorphism carry their own regularity
requirements. At large |Im(s)| with sigma fixed the displayed bounds
can grow in |s|. No imaginary-axis limit or nonlinear reconstruction is
asserted.

## 4. Meaning of the comparison at zero momentum

In the direct homogeneous chart, the added three orientation entries are
chi*w² and the original metric response stays unchanged. In the present
coordinates Psi mixes theta with a homogeneous metric component H. Its
Schur coefficient Keff therefore differs from chi without contradicting
the homogeneous calculation: the pivot P_U and the factor w² in (8)
retain the other response. This is a change of coordinates and elimination
of one response equation at nonzero w, not an elimination of a physical
metric degree of freedom from the theory.

The old H=0 chart requires xi proportional to H/q and reconstructs
N proportional to w*Psi/q. The N=0 chart uses xi proportional to N/w and
reconstructs H by (9). A pole of the former representative at q=0 is not
by itself a gauge-invariant instability. Conversely this regular chart
does not prove the complete BF/embedding quotient, a Dirac count, physical
energy positivity or global stability. It establishes (3)-(12) for the
same selected linear vector response. The proposal remains unadopted,
chi stays symbolic, and general N4/N7/P4/B4/B5 gates remain unpromoted.
