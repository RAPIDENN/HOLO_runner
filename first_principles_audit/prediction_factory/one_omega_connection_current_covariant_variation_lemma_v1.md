# Variación covariante del término candidato de conexión

Esta nota deriva la contribución de **una extensión propuesta, no adoptada**,
\[
 S_C=-\frac\chi2\int_\Sigma\langle C\wedge *_\gamma C\rangle,
 \qquad C=A_\Sigma-\omega(\gamma,T),\qquad\chi>0,
\]
con \(\chi\) constante, de dimensión masa al cuadrado y sin valor elegido.
No cambia la acción v5.2 congelada. \(A_\Sigma\) sigue siendo una conexión
independiente en el fibrado SO(3) dependiente de \((\gamma,T)\); no se la
identifica con Levi-Civita. La nota complementa la
[propuesta de corriente](one_omega_interface_connection_current_candidate_lemma_v1.md)
y la [variación lineal proyectada](one_omega_projected_connection_linear_lemma_v1.md).

El resultado es una identidad de primera variación en una carta geométrica
regular. No cierra el mapa variacional moving/gluing, todas las ecuaciones
BF ni N4/N7. El verificador contrasta los 36 componentes de la conexión
espacial con jets independientes; esos contrastes finitos respaldan la
identidad tensorial derivada abajo, no una declaración de teoría completa.

## 1. Marco horizontal y normal dependiente

Sea \(\gamma\) Lorentziana con firma \((-+++)\), y \(T\) una función
con gradiente temporal en la carta considerada. Escribimos
\[
 u_\mu=-N\partial_\mu T,\quad
 N=(-\gamma^{\mu\nu}\partial_\mu T\partial_\nu T)^{-1/2}>0,
 \quad u^2=-1,\quad \Pi_\mu{}^\nu=\delta_\mu{}^\nu+u_\mu u^\nu.
\]
Las tres columnas \(e_a{}^\mu\) satisfacen
\(\gamma(e_a,e_b)=\delta_{ab}\) y \(u\cdot e_a=0\). Definimos
\[
 \omega_{\mu,ab}=\gamma(e_a,\nabla_\mu e_b),\qquad
 \kappa_{\mu,a}=\gamma(e_a,\nabla_\mu u).
\]
No se supone nula \(\kappa\). Para \(h_{\mu\nu}=\delta\gamma_{\mu\nu}\),
la elección horizontal, sin rotación espacial añadida, es
\[
 \delta e_a{}^\nu=-\frac12\gamma^{\nu\rho}h_{\rho\sigma}e_a{}^\sigma
                         +u^\nu\beta_a,
 \qquad\beta_a=e_a{}^\sigma\left(\delta u_\sigma
                               -\frac12h_{\sigma\rho}u^\rho\right).
                                                               \tag{1}
\]
Derivar las restricciones de normalización y ortogonalidad comprueba (1).
En particular \(u^\mu\delta u_\mu=h(u,u)/2\); \(\delta u_\mu\) es la
variación del covector, no el índice bajado de \(\delta u^\mu\).

Diferenciando el lapse y \(u=-N\,dT\), con \(f=\delta T\), se obtiene
\[
 \frac{\delta N}{N}=-\frac12h(u,u)-N u^\nu\partial_\nu f,
 \quad\delta u_\mu=-\frac12u_\mu h(u,u)
                       -N\Pi_\mu{}^\nu\partial_\nu f,
 \quad\beta_a=-N e_a{}^\nu\partial_\nu f-\frac12h(e_a,u).
                                                               \tag{2}
\]
Esta identificación horizontal sirve para comparar los fibrados Q próximos.
No afirma que ese transporte sea plano, global o independiente del camino.

## 2. Derivación de la conexión, sin congelar el marco

Se varía la definición, conservando cada contribución:
\[
 \delta\omega_{\mu,ab}=h(e_a,\nabla_\mu e_b)
 +\gamma(\delta e_a,\nabla_\mu e_b)
 +\gamma(e_a,\nabla_\mu\delta e_b)
 +\gamma(e_a,\delta\Gamma_\mu e_b).
\]
Los dos primeros términos son
\(h(e_a,\nabla_\mu e_b)/2-\beta_a\kappa_{\mu,b}\).
El tercero es
\[
 -\tfrac12(\nabla_\mu h)(e_a,e_b)
 -\tfrac12h(e_a,\nabla_\mu e_b)+\kappa_{\mu,a}\beta_b,
\]
porque \((\partial_\mu\beta_b)\gamma(e_a,u)=0\). Finalmente
\[
 \gamma(e_a,\delta\Gamma_\mu e_b)
 =\tfrac12e_a{}^\nu e_b{}^\rho
  (\nabla_\mu h_{\nu\rho}+\nabla_\rho h_{\mu\nu}
                              -\nabla_\nu h_{\mu\rho}).
\]
Se cancelan tanto \(h(e_a,\nabla e_b)\) como \(\nabla_\mu h_{ab}\),
y queda la identidad exacta
\[
 \boxed{\delta\omega_{\mu,ab}
 =\frac12e_a{}^\nu e_b{}^\rho
       (\nabla_\rho h_{\mu\nu}-\nabla_\nu h_{\mu\rho})
       +\kappa_{\mu,a}\beta_b-\kappa_{\mu,b}\beta_a}.          \tag{3}
\]
El resultado es antisimétrico en \(a,b\). La desaparición de la derivada
de \(\beta\) no procede de fijar \(u\), \(T\), el marco o \(\kappa\).
En el fondo plano de \(T=t\), \(\kappa=0\), (3) recupera el curl métrico
lineal de la nota proyectada, incluidos sus factores de un medio.

## 3. Adjunto métrico y Euler de T

Usamos la norma \(\langle X,Y\rangle=\frac12\sum_{a,b}X_{ab}Y_{ab}\)
sobre matrices antisimétricas; en lo siguiente los índices \(a,b\) se
suman **sin** restringir a \(a<b\). Definimos los tensores de espacio-tiempo
\[
 J^{\mu\nu\rho}=\chi C^{\mu ab}e_a{}^\nu e_b{}^\rho,
 \qquad V^\sigma=\chi C^{\mu ab}\kappa_{\mu,a}e_b{}^\sigma,
 \qquad V^\sigma u_\sigma=0.                                \tag{4}
\]
La parte que varía \(\omega\), con \(A_\Sigma\) fijo en la identificación
horizontal, es \(\delta_\omega S_C=\frac\chi2\int\sqrt{-\gamma}
 C^{\mu ab}\delta\omega_{\mu,ab}\). Contrayendo (3),
\[
 \frac{\delta_\omega S_C}{\sqrt{-\gamma}}
 =\frac12J^{\mu\nu\rho}\nabla_\rho h_{\mu\nu}
       +V^\sigma\delta u_\sigma
       -\frac12V^\sigma u^\rho h_{\sigma\rho}.               \tag{5}
\]
El primer medio resulta de la suma completa de los dos índices de color;
no se debe eliminar ni duplicar al pasar a tres componentes independientes.
Por (2) y \(V\cdot u=0\), el término de \(f\) en (5) es
\(-N V^\sigma\nabla_\sigma f\).

El cambio explícito de volumen e inversa métrica, manteniendo C covariante
fijo, da el tensor
\[
 T_C^{\mu\nu}=\chi\left[\langle C^\mu,C^\nu\rangle
       -\tfrac12\gamma^{\mu\nu}\langle C_\rho,C^\rho\rangle\right].
\]
Integrando por partes en una carta de \(\Sigma\), la primera variación es
\[
 \delta S_C=\int_\Sigma\sqrt{-\gamma}
       [\tfrac12\tau_C^{\mu\nu}h_{\mu\nu}+E_T f]
       +\int_\Sigma J_\Sigma\wedge\delta A_\Sigma
       +\int_{\partial\Sigma}\iota_{\mathcal B}\mathrm{vol}_\gamma,
                                                               \tag{6}
\]
con
\[
 \boxed{\tau_C^{\mu\nu}=T_C^{\mu\nu}
       -\nabla_\rho J^{(\mu\nu)\rho}-V^{(\mu}u^{\nu)},
 \quad E_T=\nabla_\sigma(NV^\sigma),
 \quad J_\Sigma=\chi *_\gamma C},                            \tag{7}
\]
\[
 \mathcal B^\rho=\tfrac12J^{\mu\nu\rho}h_{\mu\nu}-NV^\rho f.
                                                               \tag{8}
\]
Los paréntesis tienen peso un medio. El signo de \(J_\Sigma\) usa el
orden \(J_\Sigma\wedge\delta A\); invertirlo cambia el signo. Las
integraciones se entienden para variaciones compactas o con el término
(8) retenido. No se añade a mano una condición nula en un borde de borde.

## 4. Rotaciones y límites del resultado

Al añadir una rotación espacial \(\rho\), con \(\rho^T=-\rho\),
la variación de (1) cambia en \(\delta e=e\rho\). Las conexiones varían
simultáneamente:
\[
 \delta_\rho\omega=d\rho+[\omega,\rho],\qquad
 \delta_\rho A=d\rho+[A,\rho],\qquad
 \delta_\rho C=[C,\rho].                                   \tag{9}
\]
Por invariancia de la norma, \(\langle C,[C,\rho]\rangle=0\).
Rotar sólo el marco dejando A fijo crea una variación relativa física de
C; no es el cambio de representante de (9). El marco dependiente Q no
aporta una nueva variable libre que permita descartar sus términos.

La cancelación de \(d\beta\) en (3) evita segundas derivadas de
\(\delta T\) en **esta primera variación horizontal**. No establece una
reducción global del orden de los Euler: \(\kappa\) contiene \(\nabla u\)
y, en general, segundas derivadas de T; además (7) deriva sus coeficientes.
Quedan por cotejar la cadena completa con el gluing, el transporte del
fibrado, las variaciones independientes de embedding y las otras partes
de la acción. No se deduce una energía positiva ni ausencia de grados
adicionales de esta identidad de adjunto.

La propuesta permanece no adoptada, \(\chi\) simbólico, y los gates
N4/N7, P4, B4/B5, estabilidad no lineal y dominio BF/global permanecen sin
promoverse. El resultado concreto es (3) y la contribución (7), con sus
convenciones y el término de borde (8), no un cierre de la candidata.
