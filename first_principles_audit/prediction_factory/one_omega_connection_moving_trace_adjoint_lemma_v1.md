# Traza móvil de conexión y adjunto sobre una interfaz común

Esta nota estudia el mapa tangente y su adjunto local para el término
**propuesto, no adoptado**

\[
 S_C=-\frac\chi2\int_\Sigma\langle C\wedge *_\gamma C\rangle,
 \qquad C=A_\Sigma-\omega(\gamma,T),\qquad \chi>0.
\]

No modifica la acción v5.2 congelada. Se mantienen la identificación
horizontal del fibrado Q, la primera variación covariante completa de S_C,
y el signo BF derivado de Stokes en la errata del 08-09. El resultado es
una regla de cadena con los términos de borde conservados. No identifica
por sí solo todo el Euler normal de Einstein–Hilbert más GHY, ni resuelve
la candidata o sus ecuaciones de evolución.

## 1. Mapa finito y carta objetivo

En cada lado hay un collar gaussiano suave con coordenadas (n,x^mu),
\(g_{nn}=1\), \(g_{n\mu}=0\) en el fondo de referencia y
\(g_{\mu\nu}|_{n=0}=\gamma_{\mu\nu}\). Se usa **el mismo normal**
n de M_minus a M_plus; \(K_{\pm,\mu\nu}=\partial_n g_{\pm,\mu\nu}/2\)
son sus dos curvaturas. Los normales exteriores son -n y +n en M_plus y
M_minus respectivamente. Las identificaciones locales del fibrado se han
trivializado de modo que sus valores de referencia sean la identidad.

Considérese un desplazamiento común
\(Y_\epsilon(x)=(\epsilon f(x),x)\), campos bulk \(g_\epsilon,A_\epsilon\),
y una identificación \(r_\epsilon(x)\in SO(3)\), con \(r_0=I\):

\[
 \gamma_\epsilon=Y_\epsilon^*g_\epsilon,\qquad
 A_{\Sigma,\epsilon}=r_\epsilon(Y_\epsilon^*A_\epsilon)r_\epsilon^{-1}
                         -d r_\epsilon r_\epsilon^{-1}.
 \tag{1}
\]

El representante objetivo se transporta horizontalmente al variar
\((\gamma,T)\), en el sentido de la nota covariante. Por tanto
\(\eta=\dot r_0\) se mide **respecto a ese representante horizontal**.
Si se emplea un representante objetivo que incorpora una rotación
adicional \(\rho_Q\), hay que convertir
\(a_h=a_{\rm raw}-D_A\rho_Q\) y \(\eta_h=\eta_{\rm raw}+\rho_Q\)
antes de usar el adjunto de abajo. Elegir una trivialización local no
prueba que el transporte horizontal sea plano o global.

Se denota por \(\delta g,\delta A\) la variación euleriana de los campos
bulk en la trivialización elegida. La variación del reloj intrínseco es
\(\vartheta=\delta T_\Sigma\). No se postula aquí un reloj bulk con
\(T_\Sigma=Y^*T_{bulk}\); si existe tal restricción, su mapa tangente y su
adjunto deben añadirse, incluido el término \(f\partial_n T_{bulk}\).

## 2. Derivación literal de las trazas

Al diferenciar el primer mapa de (1), los términos de \(\partial_\mu f\)
se multiplican por \(g_{n\nu}=0\) en el fondo, y se obtiene

\[
 h_{\Sigma,\mu\nu}=\delta g_{\parallel,\pm,\mu\nu}+2fK_{\pm,\mu\nu}.
 \tag{2}
\]

No se elimina ninguna contribución de primer orden de la métrica. El
producto \(\partial_\mu f\partial_\nu f\) empieza en orden dos.
La diferenciación del segundo mapa, antes de reescribirlo covariantemente,
es

\[
 a_{\Sigma,\mu}=\delta A_{\parallel,\mu}+f\partial_n A_\mu
   +A_n\partial_\mu f+[\eta,A_\mu]-\partial_\mu\eta.
 \tag{3}
\]

Con \(F_{n\mu}=\partial_n A_\mu-\partial_\mu A_n+[A_n,A_\mu]\),
\(D_\mu=\partial_\mu+[A_\mu,\cdot]\) y
\(\Lambda_f=f A_n-\eta\), los dos conmutadores adicionales se cancelan:

\[
 \boxed{a_{\Sigma,h}=\delta A_{\parallel,\pm}
            +f F_{n,\pm}+D_A\Lambda_{f,\pm}.}
 \tag{4}
\]

Se conservan tanto \(A_n\partial_\mu f\) como \(-D_\mu\eta\).
La identidad es no abeliana, no impone \(F=0\), y no requiere extensión
constante de los campos en n. Para el mapa finito de una difeomorfía
**tangente** X, elegir la compensación horizontal ya derivada
\(\eta_X=i_X\omega+\sigma_X\) recupera
\(\Lambda_X=i_XC-\sigma_X\). Esa especialización no determina
\(\eta_f\) de un desplazamiento normal: X pertenece a T Sigma y f n no.

## 3. Gluing de dos lados y número de sumandos

Las variaciones admisibles son tangentes a las igualdades de las trazas.
Para cualesquiera variaciones comunes \(h_\Sigma,a_\Sigma\), (2) y (4)
imponen, a cada lado,

\[
 \begin{split}
 \delta g_{\parallel,\pm}&=h_\Sigma-2fK_\pm,\\
 \delta A_{\parallel,\pm}&=a_\Sigma-fF_{n,\pm}-D_A\Lambda_{f,\pm}.
 \end{split} \tag{5}
\]

En general \(K_+\ne K_-\) y \(F_{n,+}\ne F_{n,-}\). Congelar ambos
campos bulk y permitir un f arbitrario violaría (5). No es una familia
admisible de variaciones del problema con trazas comunes. Una elección
como \(h_\Sigma=2f\bar K\), \(\bar K=(K_++K_-)/2\), requiere
\(\delta g_{\parallel,\pm}=2f(\bar K-K_\pm)\): no permite descartar
las variaciones ni los Euler bulk correspondientes.

S_C es una sola integral sobre Sigma. Usar el lado plus o el lado minus en
(4) produce dos representaciones de **la misma** variación. No se suman
como dos acciones. Tras imponer (5), ambas expresiones coinciden para los
mismos \(h_\Sigma,a_\Sigma,\vartheta\).

## 4. Adjunto de S_C con su borde

Se usan los coeficientes completos \(\tau_C,E_T,J^{\mu\nu\rho},V^\mu\)
de la nota covariante, incluidos los términos procedentes de variar el
marco. Con el producto \(\langle X,Y\rangle=-\operatorname{tr}(XY)/2\),

\[
 \delta S_C=\int_\Sigma\mathrm{vol}_\gamma
 [\tfrac12\tau_C:h_\Sigma+E_T\vartheta
                     -\chi\langle C^\mu,a_{\Sigma,h,\mu}\rangle]
       +\int_{\partial\Sigma}\iota_{\mathcal B}\mathrm{vol}_\gamma,
 \qquad
 \mathcal B^\rho=\tfrac12J^{\mu\nu\rho}h_{\Sigma,\mu\nu}
                                      -NV^\rho\vartheta.
 \tag{6}
\]

Sea \(G=D_AJ_\Sigma/\mathrm{vol}_\gamma=\chi(D_A)_\mu C^\mu\),
\(J_\Sigma=\chi *_\gamma C\). Sustituir (2), (4) en (6) y hacer una
sola integración por partes covariante produce, en cualquiera de las dos
parametrizaciones,

\[
 \begin{split}
 \delta S_C={}&\int_\Sigma\mathrm{vol}_\gamma
 \{\tfrac12\tau_C:\delta g_\parallel+E_T\vartheta
      -\chi\langle C^\mu,\delta A_{\parallel,\mu}\rangle\\
 &\hspace{15mm}+f[\tau_C:K-\chi\langle C^\mu,F_{n\mu}\rangle]
                                    +\langle G,\Lambda_f\rangle\}\\
 &+\int_{\partial\Sigma}\iota_{\widetilde{\mathcal B}}
                                      \mathrm{vol}_\gamma,\\
 \widetilde{\mathcal B}^{\mu}&=\mathcal B^\mu
                                  -\chi\langle C^\mu,\Lambda_f\rangle.
 \end{split} \tag{7}
\]

En particular, f no tiene que ser constante. El término que contiene G
no desaparece por las ecuaciones BF: la orientación correcta da
\([b]=-J_\Sigma\) y \(D_AJ_\Sigma=[j_4]\), que puede ser no nulo.
Con un transporte especificado como operador diferencial \(\eta=\mathcal R f\),
el término normal local adicional es
\(\langle G,A_n\rangle-\mathcal R^\dagger G\), conservando el borde
del adjunto. Para el ejemplo de primer orden
\(\eta[f]=R f+S^\mu\partial_\mu f\),

\[
 -\langle G,\eta[f]\rangle
 =f[-\langle G,R\rangle+\nabla_\mu\langle G,S^\mu\rangle]
                       -\nabla_\mu(f\langle G,S^\mu\rangle).
 \tag{8}
\]

Por tanto dejar \(\eta[f]\) sin identificar conserva una regla de cadena,
pero no determina el Euler normal completo de un transporte geométrico
particular. No se declara \(\eta=0\) como resultado de la geometría.

## 5. Adjunto de la rotación relativa de conexión y fila BF

La orientación \(\mathrm{vol}_5=dn\wedge\mathrm{vol}_\Sigma\) y la
acción literal \(+\int\langle B\wedge F\rangle\) dan originalmente
\(+\langle b_+\wedge\delta A_{\parallel,+}\rangle
-\langle b_-\wedge\delta A_{\parallel,-}\rangle\). Tras sustituir (5),
el sumando de traza común es \(+\langle[b]\wedge a_\Sigma\rangle\),
acompañado por
\(-\langle b_+\wedge(fF_{n,+}+D\Lambda_{f,+})\rangle
+\langle b_-\wedge(fF_{n,-}+D\Lambda_{f,-})\rangle\).
Estos complementos y la transgresión de movimiento del dominio permanecen
en el Green completo. Por ejemplo, con f=0, campos eulerianos fijos y una
misma rotación eta, \(a_\Sigma=-D\eta\): el término
\(-[b]\wedge D\eta\) se cancela con el complemento
\(+[b]\wedge D\eta\), como exige que BF no haya variado.
Sea \(Q=[b]+J_\Sigma\). En el **sumando de conexión** de ese Green, la parte
\(a_\Sigma=-D_A\eta\) satisface exactamente

\[
 -\langle Q\wedge D_A\eta\rangle
    =d\langle Q\eta\rangle-\langle D_AQ,\eta\rangle.
 \tag{9}
\]

Así, su adjunto interior es \(-D_A([b]+J_\Sigma)\). Usar los Euler bulk
\(D_AB+j_4=0\), con las conexiones tangenciales identificadas, reduce ese
coeficiente a

\[
 \boxed{[j_4]-D_AJ_\Sigma.} \tag{10}
\]

El borde \(d\langle Q\eta\rangle\) se conserva. (10) es combinación
de los Euler bulk y la derivada de la fila natural de conexión; no impone
una nueva ecuación física \(G=0\). Una rotación del representante de Q
que rote simultáneamente A, el marco y la materia es una transformación
gauge distinta de variar sólo A respecto al marco objetivo fijado. La
identidad gauge completa incluye también sus filas materiales. No se
infiere de (9) un grado de libertad adicional de r ni una eliminación de
sus términos sin aplicar el mapa tangente completo.

## 6. Contraste y alcance

El verificador diferencia un pullback finito no abeliano, con f variable,
componente normal de conexión no nula y curvatura mixta no nula. El mapa
métrico se contrasta con las derivadas de la inmersión y dos curvaturas
distintas. Los controles negativos deben detectar la pérdida de
\(A_n\,df\), del transporte \(-D\eta\), del ajuste de los dos lados,
del borde de integración, o el doble cómputo de S_C. El adjunto de
rotación se contrasta conservando el orden tres-forma por uno-forma.

Estas verificaciones finitas acompañan las identidades generales (2)–(10).
No constituyen una prueba formal del espacio funcional global ni del
sistema físico completo. El enlace pendiente con la identidad
\(\tau_{total}:\bar K-[T_{nn}]=[H]-\bar K:I\) exige ensamblar el Green
moving de Einstein–Hilbert más GHY, las trazas escalares y materiales y
su identificación de Q. La identidad de constraint, por sí sola, no
reemplaza ese ensamblado. No se promueven N4, N7, C1/N1, P4, B4/B5,
existencia acoplada, estabilidad, control del bulk ni resultados de IA.
