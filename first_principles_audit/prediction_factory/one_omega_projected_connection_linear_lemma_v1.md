# Conexión SO(3) proyectada: geometría lineal y término candidato C²

Este paquete examina una extensión PROPUESTA, no contenida en la acción
v5.2 fijada por SHA256. No modifica esa acción, no identifica A=omega y no
hereda sus gates. El resultado es local, alrededor de Minkowski, T=t y
A=omega=0. Se mantienen dinámicas las perturbaciones geométricas.

Fuente base: artifacts/one_omega_topological_so3_classical_v5_2_gate.json,
SHA256 d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b.

## Convenciones y marco

Signatura (-,+,+,+), coordenadas x0=t y x1,x2,x3 espaciales. Escribimos

    gamma00=-1-2 epsilon n, gamma0i=epsilon N_i,
    gammaij=deltaij+epsilon H_ij, T=t+epsilon tau.

El shift contravariante y covariante coinciden a este orden. Los índices
internos a,b recorren las tres direcciones espaciales. El marco tiene
columnas e_a^mu y satisface gamma(e_a,e_b)=delta_ab y u_mu e_a^mu=0,
con u_mu=-N_T partial_mu T y N_T=(-gamma^-1(dT,dT))^(-1/2).

    N_T=1+epsilon(n-dot(tau)),
    u_0=-1-epsilon n, u_i=-epsilon partial_i tau,
    e_a^0=-epsilon partial_a tau,
    e_a^i=delta_a^i-epsilon H_ia/2.

Se fija la rotación espacial del marco a cero: es la elección horizontal,
no una restricción sobre la conexión gauge A. Los jets de n, N, H y tau
permanecen independientes, salvo H simétrica y las segundas derivadas
ordinarias simétricas de tau. No se imponen ecuaciones de movimiento.

## Conexión obtenida de gamma y e

La convención de signo es

    omega_mu,ab = e_a,nu (partial_mu e_b^nu + Gamma^nu_mu,rho e_b^rho).

La variación literal de Christoffel y la derivada del marco dan

    omega_mu,ab^(1)
      = -partial_mu H_ab/2 + Gamma^a_mu,b^(1)
      = (partial_b h_a,mu-partial_a h_mu,b)/2,

    omega_0,ab^(1)=(partial_b N_a-partial_a N_b)/2,
    omega_i,ab^(1)=(partial_b H_ai-partial_a H_ib)/2.

Aquí a,b se entienden espaciales cuando aparecen como índices de h.
Las cuatro matrices omega son antisimétricas. Las derivadas temporales de
H cancelan entre el marco y Christoffel. Los jets de lapse, tau y sus
segundas derivadas no aparecen. En particular, el término temporal del
marco tiene contracción nula con el marco espacial de fondo a este orden.
En coordenadas adaptadas a T, la misma ausencia de tau se verifica porque
el shift adquiere partial_i tau y partial_[a partial_b] tau=0.

No se ha congelado gamma: la ausencia de esas derivadas es un resultado
de la variación. No se extiende aquí a fondos con C distinto de cero ni
a todos los órdenes de perturbación.

## Rotación de marco y gauge

Para e -> e R, R en SO(3), la ley es

    omega -> R^T omega R + R^T dR.

Alrededor del fondo trivial R=I+epsilon rho, rho^T=-rho:

    omega^(1) -> omega^(1)+d rho,
    A^(1) -> A^(1)+d rho,
    C^(1)=A^(1)-omega^(1) -> C^(1).

El verificador deriva el signo d rho desde el marco rotado; no lo toma
como una prescripción independiente. También contrasta una rotación
constante propia no trivial. Fijar A=0 y marco horizontal simultáneamente
no es una elección gauge disponible para una geometría arbitraria.

## Hodge Lorentziano y expansión cuadrática

La extensión candidata usa Hodge de la métrica Lorentziana CUATRIDIMENSIONAL
y el producto positivo <X,Y>=sum_(a<b) X_ab Y_ab=tr(X^T Y)/2:

    S_C=-chi/2 int <C wedge *_gamma C>, chi>0.

Si C de fondo es cero, las correcciones de gamma^-1 y del volumen sólo
entran desde orden epsilon^3. El coeficiente de epsilon^2 es

    L_C2=chi/2 ||A_0-omega_0||^2
         -chi/2 sum_i ||A_i-omega_i||^2.

No contiene velocidades geométricas directamente. Sí modifica las filas
de shift y de métrica espacial. Si el dominio y las ecuaciones BF permiten
escribir localmente A=d theta, aparece (dot(theta)-omega_0)^2: resolver las
restricciones puede cambiar la cinética reducida. Esta observación no
cuenta modos físicos ni prueba su salud, existencia o admisibilidad.

## Restricciones tensorial, escalar y vectorial comprobadas

Se toma dependencia sólo en t,z=x3 y la norma SO(3) anterior.

* Tensor: H12=H21=h(t,z), demás geometría cero. En la restricción A=0,
  omega_1,23=h_z/2, omega_2,13=h_z/2 y
  L_C2=-chi*h_z^2/4. No se añade dot(h)^2.
* Escalar: H_ij=2 zeta delta_ij. En la restricción A=0,
  omega_1,13=zeta_z, omega_2,23=zeta_z y
  L_C2=-chi*zeta_z^2. Si A=d theta depende sólo de t,z, su parte
  longitudinal mu=0,3 no se mezcla con estas conexiones mu=1,2.
* Shift transversal: sólo N1(t,z), H3a=0. Entonces
  omega_0,13=N1_z/2 y L_C2|A=0=chi*N1_z^2/8.
* Vector de conexión: A_0,13=theta_t, A_3,13=theta_z y el mismo shift.
  Se obtiene L_C2=chi/2[(theta_t-N1_z/2)^2-theta_z^2].

Sin fijar H13=0, el sector vectorial anterior tiene

    C0,13=theta_t-N1_z/2, C3,13=theta_z-H13_z/2.

La combinación U=N1_z-H13_t y Psi=theta-H13/2 da exactamente

    L_vector=B*U^2/4+chi/2[(Psi_t-U/2)^2-Psi_z^2].

En la convención delta gamma_mu,nu=partial_mu xi_nu+partial_nu xi_mu,
una difeomorfía espacial xi1(t,z) produce delta N1=partial_t xi1,
delta H13=partial_z xi1. Mantener el marco horizontal requiere la
rotación de conexión delta theta=partial_z xi1/2. U y Psi son invariantes.
Esto comprueba el signo sin fijar prematuramente H13; no certifica otras
filas de la teoría extendida. Con partial_t=-i*w y partial_z=i*q,
U lleva la amplitud i*(q*N1+w*H13), compatible con la elección de fases
real usada abajo.

Estos cálculos son restricciones de la densidad completa; imponer A=0
no se presenta como una solución de las demás ecuaciones de borde. El
paquete no ha rederivado pivots escalares de la teoría extendida.

Para controlar los factores, se permite una eliminación algebraica
adicional en un modo real de Fourier de momento q>0, con fases compatibles
N1_z=q*N y theta_z^2=q^2*theta^2. Si otra parte aporta

    L_old=q^2*B*N^2/4,

la estacionariedad en N de L_old+L_C2 da

    N_star=2*chi*theta_t/[q*(2*B+chi)],
    L_eff=K_eff*theta_t^2/2-chi*q^2*theta^2/2,
    K_eff=2*chi*B/(2*B+chi).

B puede representar un kernel; se exige 2B+chi distinto de cero para
esta eliminación. No se certifica aquí esa condición para un kernel ni
se usa la carta para q=0. La identidad armónica
s*K_eff=[1/(chi*s)+1/(2*s*B)]^(-1) es algebraica, con denominadores
no nulos. La propiedad positiva-real y la ausencia de polos requieren
pruebas adicionales sobre B y su dominio, no incluidas en este paquete.

## Alcance

Se verifican métrica/inversa/marco/normal, las 36 entradas de omega, el
Hodge Lorentziano, las restricciones anteriores y los factores del Schur
vectorial. Hay controles negativos de marco congelado, curl con signo
incorrecto, Hodge Euclídeo, rotación no acompañada en A, factores TT/traza
y eliminación vectorial. Los hashes y un digest reencuadernado no sustituyen
la recomputación fresca.

Siguen fuera: acción candidata completa con este término, variación no
lineal y moving, corriente BF/Robin resultante, nuevo dominio de borde,
constraints completas, propiedades analíticas de B, modos físicos,
estabilidad global, BV/BFV y N4/N7/P4/B4/B5. La nota es evidencia para
examinar una propuesta; no promueve la v5.2 ni una teoría extendida.
