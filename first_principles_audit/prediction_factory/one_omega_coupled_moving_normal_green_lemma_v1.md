# Ensamblado normal local: gravedad, escalares y BF

Estado del checkpoint de pausa (2026-09-08): derivación escrita y auditada
manualmente; verificador, pruebas ejecutables y recibo todavía pendientes.
No se presenta como un paquete computacional completado.

Esta nota ensambla el Green normal local en coordenadas de trazas comunes.
Su resultado es una identidad off shell con los Euler bulk y las corrientes
de borde **retenidos**, y una dependencia de la fila normal sobre soluciones
bulk suaves. No prueba que esas soluciones existan, no fija un dominio
funcional global y no promueve automáticamente los gates de la candidata.
El término S_C, cuando se incluye, sigue siendo una propuesta no adoptada.

## 1. Convenciones y coordenadas comunes

Se usa un normal unitario espacial n de M_minus a M_plus,
\(\mathrm{vol}_5=dn\wedge\mathrm{vol}_\Sigma\), y la etiqueta
\(\epsilon=+1\) en M_plus, \(-1\) en M_minus. El normal exterior y
la velocidad exterior son \(-\epsilon n\) y \(-\epsilon f\).
Todos los coeficientes de color se expresan en el mismo marco de Q sobre
Sigma. Las formas bulk se transportan antes de compararlas o restarlas.
La igualdad de conexiones tangenciales hace compatible D_A con ese
transporte y con el pullback a Sigma.

Los datos de traza independientes son la métrica gamma, Omega, las tres
componentes materiales phi en el representante horizontal, el reloj T y
la conexión A_Sigma. La conexión no se identifica con Levi-Civita. Se
escriben sus variaciones comunes
\(h_\Sigma,\Delta\Omega,\Delta\phi,\vartheta,a_\Sigma\).
Las dos inmersiones usan un f común y las identificaciones locales de
fibrado tienen velocidades \(\eta_\epsilon\) relativas al representante
objetivo horizontal. Defina \(\Lambda_\epsilon=f A_{n,\epsilon}-\eta_\epsilon\).

La diferenciación de los mapas finitos da

\[
 \begin{split}
 h_\Sigma&=\delta g_{\parallel,\epsilon}+2fK_\epsilon,\\
 a_\Sigma&=\delta A_{\parallel,\epsilon}+fF_{n,\epsilon}
                                            +D_A\Lambda_\epsilon,\\
 \Delta\Omega&=\delta\Omega_\epsilon+f\partial_n\Omega_\epsilon,\\
 \Delta\phi&=\delta\phi_\epsilon+f(D_n\phi)_\epsilon
                                            -\Lambda_\epsilon\phi.
 \end{split} \tag{1}
\]

En la última fila se ha diferenciado literalmente
\(\phi_{\Sigma,\epsilon}=r_\epsilon Y_\epsilon^*\phi_\epsilon\),
para lo cual \(\Delta\phi=\delta\phi+f\partial_n\phi+\eta\phi\).
Usar D_n sin conservar \(-\Lambda\phi\) duplicaría o perdería A_n.
El mapa material, incluido cualquier cambio adicional de carta de phi,
debe aplicarse también a sus momentos por la regla del adjunto.

## 2. Momento material y corriente de conexión

Para el sector escalar literal se usa
\(P_M=D_M\phi+3\phi\partial_M\Omega/(2\Omega)\),
con término cinético \(-Z\langle P_M,P^M\rangle/2\).
El momento normal material es \(p_\phi=-ZP_n\). Al variar A_n a métrica
y material fijos, el mismo término da

\[
 \delta_{A_n}L_s=-Z\langle P_n,\delta A_n\phi\rangle
                 =p_\phi\cdot(\delta A_n\phi).
 \tag{2}
\]

Defina j_4 por la variación bulk
\(\delta_A S_s=\int\langle j_4\wedge\delta A\rangle\).
Con el orden **cuatro-forma por uno-forma**, n espacial unitario y la
orientación fijada,

\[
 \langle Y^*j_4,\Lambda\rangle
       =[p_\phi\cdot(\Lambda\phi)]\,\mathrm{vol}_\Sigma.
 \tag{3}
\]

Esta relación define el signo de la corriente desde la acción; no se
presupone una convención de producto vectorial para las matrices SO(3).
El término mixto de Omega en P_n no altera (3), pues
\(\phi\cdot\Lambda\phi=0\). El momento de Omega conserva, no obstante,
ese acoplamiento mixto en el resto del Green escalar.

Por (1), la parte del Green material asociada al transporte en una cara es
\(-\epsilon p_\phi\cdot(\Lambda_\epsilon\phi)\), es decir
\(-\epsilon\langle Y^*j_{4,\epsilon},\Lambda_\epsilon\rangle\).
Los demás sumandos son sus momentos por \(\Delta\phi,\Delta\Omega\)
y el término normal \(-f[T_{nn}]\) al sumar ambas caras.

## 3. Green BF, movimiento de dominio y cancelación del transporte

La acción literal es \(+\int\langle B_3\wedge F_2\rangle\), con
\(\langle X,Y\rangle=-\operatorname{tr}(XY)/2\). Defina
\(b_\epsilon=Y^*B_\epsilon\), sin incidencia escondida en b.
Leibniz y Stokes dan en una cara

\[
 \epsilon\langle b_\epsilon\wedge\delta A_{\parallel,\epsilon}\rangle
 -\epsilon f\,Y^*i_n\langle B_\epsilon\wedge F_\epsilon\rangle.
 \tag{4}
\]

El segundo sumando ya es la variación de dominio; no se vuelve a añadir.
Sustituir (1), usar
\(i_n(B\wedge F)=i_nB\wedge F-B\wedge i_nF\), y conservar el borde
del producto covariante da exactamente

\[
 \begin{split}
 (4)={}&\epsilon\langle b_\epsilon\wedge a_\Sigma\rangle
 -\epsilon f\,\langle Y^*(i_nB_\epsilon)\wedge Y^*F_\epsilon\rangle\\
 &-\epsilon\langle D_Ab_\epsilon,\Lambda_\epsilon\rangle
                     +\epsilon d\langle b_\epsilon\Lambda_\epsilon\rangle.
 \end{split} \tag{5}
\]

El signo de la tercera fila procede de
\(d\langle b\Lambda\rangle=\langle D_Ab,\Lambda\rangle
-\langle b\wedge D_A\Lambda\rangle\). La curvatura en la segunda
fila es su pullback tangencial; no se puede reinterpretar como un término
adicional F_n independiente.

Con \(\mathcal E_A=D_AB+j_4\) y \(\mathcal E_B=F\), combinar (3)
y (5) demuestra que **todo** el transporte de ese sumando es

\[
 \boxed{-\sum_\epsilon\epsilon
             \langle Y^*\mathcal E_{A,\epsilon},\Lambda_\epsilon\rangle.}
 \tag{6}
\]

El restante término normal BF es

\[
 \boxed{-f\sum_\epsilon\epsilon
    \langle Y^*(i_nB_\epsilon)\wedge Y^*\mathcal E_{B,\epsilon}\rangle.}
 \tag{7}
\]

Son sumandos Euler bulk explícitos, no cero off shell. En particular, no
se ha impuesto \(D_AJ_\Sigma=0\) ni se ha perdido una corriente material.
Si el transporte \(\eta\) depende de derivadas de f o de otras
variaciones, sus adjuntos actúan sobre \(Y^*\mathcal E_A\), y sus
corrientes tangenciales también se conservan. Para soluciones bulk suaves
hasta Sigma, \(\mathcal E_A=\mathcal E_B=0\) anula (6)–(7), incluidas
las derivadas de Euler presentes en esos adjuntos. La regularidad hasta
la frontera y la existencia de trazas no se presuponen en un dominio débil
que todavía no se haya construido.

## 4. Ensamblado y cambio de coordenada normal

El Green métrico EH+GHY en trazas comunes es
\(M[\pi]:h_\Sigma/2+f[H_g]\), como se obtiene diferenciando la acción
con GHY. El Green escalar aporta sus momentos de traza y \(-f[T_{nn}]\).
Una sola acción de pared intrínseca aporta su Euler métrico **completo**
tau, sus filas materiales y de reloj, y J_Sigma por a_Sigma. Incluye la
variación de su marco dependiente, no sólo el estrés explícito de volumen.
No se añade dependencia radial extrínseca a esa pared.

Escriba
\(I=-M[\pi]-\tau\), \(H=H_g-T_{nn}\), y R_Omega,R_phi para las filas
naturales escalares **tras aplicar todos los cambios de carta declarados**.
El Green local de este ensamblado es

\[
 \begin{split}
 \Theta_\Sigma={}&\mathrm{vol}_\Sigma
 [-\tfrac12 I:h_\Sigma+R_\Omega\Delta\Omega
       +R_\phi\cdot\Delta\phi+E_T\vartheta+f[H]]\\
 &+\langle([b]+J_\Sigma)\wedge a_\Sigma\rangle\\
 &-\sum_\epsilon\epsilon
            \langle Y^*\mathcal E_{A,\epsilon},\Lambda_\epsilon\rangle
 -f\sum_\epsilon\epsilon
        \langle Y^*(i_nB_\epsilon)\wedge Y^*\mathcal E_{B,\epsilon}\rangle
 +d\mathcal B.
 \end{split} \tag{8}
\]

La parte de \(\mathcal B\) procedente de (5) es
\(\sum_\epsilon\epsilon\langle b_\epsilon\Lambda_\epsilon\rangle\).
El resto procede de GHY y de los adjuntos intrínsecos ya presentes. Los
integrales Euler bulk de la primera variación permanecen fuera de (8);
no se omiten cuando los campos se ajustan para conservar el gluing.

Tome \(h_\Sigma=h_0+2f\bar K\), \(\bar K=(K_++K_-)/2\).
Entonces \(h_0=(\delta g_{\parallel,+}+\delta g_{\parallel,-})/2\)
es la **media** de las trazas eulerianas; no se impone que éstas coincidan.
Se mantienen a_Sigma, DeltaOmega, Deltaphi y vartheta como coordenadas
comunes independientes. En la capa Euler bulk BF, el
coeficiente de f es

\[
 [H]-\bar K:I=\tau:\bar K-[T_{nn}],
 \tag{9}
\]

con las filas naturales restantes aún visibles. Si una parametrización
adicional hace depender también a_Sigma u otra traza de f, hay que sumar
el adjunto de esa regla de cadena multiplicando sus filas naturales; no
se descarta. Sobre todas las constraints bulk y la fila Israel, (9) se
anula. Israel por sí sola no basta.

## 5. Límite preciso del resultado

La familia considerada tiene un único desplazamiento común f. Su
equivalencia con todas las variaciones de dos embeddings independientes
requeriría un argumento adicional de gauge y del mapa tangente; no se
declara demostrada aquí.

(6)–(8) prueban el mecanismo local por el que se combinan transporte
material y BF. No proporcionan valores nuevos de tau ni de R_phi: esos
coeficientes exigen la variación completa de la acción de pared y de cada
mapa material concreto. No constituyen una identificación global de Q,
un dominio funcional para el quotient BF, una prueba de existencia de
soluciones bulk, ni la equivalencia del Hessiano completo con los bloques
reducidos. No hay conclusión sobre estabilidad no lineal, control del bulk
o aprendizaje de IA. Todos los gates físicos generales permanecen false.
