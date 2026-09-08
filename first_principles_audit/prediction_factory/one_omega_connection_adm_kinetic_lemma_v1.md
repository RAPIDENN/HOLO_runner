# Hessiana cinética ADM del término candidato de conexión

Se estudia la contribución local de la **propuesta no adoptada**
\[
 S_C=-\frac\chi2\int\langle(A-\omega)\wedge *_\gamma(A-\omega)\rangle,
 \qquad\chi>0,
\]
con \(\chi\) de dimensión masa al cuadrado y sin valor elegido.
No se cambia la acción v5.2 ni se identifica \(A\) con Levi-Civita.
La [variación covariante](one_omega_connection_current_covariant_variation_lemma_v1.md)
y el [Ward horizontal](one_omega_connection_horizontal_ward_lemma_v1.md)
conservan el fibrado dependiente Q y las contribuciones del marco.

El resultado es una Hessiana de velocidades en una carta regular local.
No es una reducción Dirac, un conteo de partículas, la eliminación dinámica
de la orientación ni una demostración de estabilidad de la teoría completa.
La condición \(T=t\) se usa sólo donde \(dT\) es temporal y define una
coordenada; no se declara una eliminación global de T o de sus ecuaciones.

## 1. Carta unitaria y sección del marco

Escribimos, con \(N>0\) y \(h\) simétrica definida positiva,
\[
 ds^2=-N^2dt^2+h_{ij}(dx^i+N^i dt)(dx^j+N^jdt),\quad
 N_i=h_{ij}N^j,
 \quad u_\mu=(-N,0),\quad u^\mu=(1,-N^i)/N.
\]
Un marco espacial tiene \(e_a^0=0\), \(e_a^i=E^i{}_a\),
\(E^T h E=I_3\). Se elige una **sección suave \(E=E(h)\)**,
por ejemplo \(E=h^{-1/2}\) en la carta SPD. Entonces \(\dot E\) es
lineal en \(\dot h\) a campos fijos. El transporte horizontal del espacio
de campos no se supone integrable: no se exige que una única sección
satisfaga \(\delta E=-h^{-1}\delta h E/2\) para todas las variaciones.
Cambiar de sección rota simultáneamente el representante de A y del marco.

De la definición \(\omega_{\mu,ab}=e_{a,\nu}\nabla_\mu e_b^\nu\),
con el índice de Christoffel bajado, se obtiene
\[
 \Gamma_{i t j}=\tfrac12(\dot h_{ij}+\partial_jN_i-\partial_iN_j),
 \qquad
 \omega_t=E^Th\dot E+\tfrac12E^T\dot h E
           +\tfrac12E^T(\partial_jN_i-\partial_iN_j)E.
\]
La identidad \(\partial_t(E^ThE)=0\) convierte esto exactamente en
\[
 \boxed{\omega_t=L_E(\dot h)+W_N,
 \quad L_E(\dot h)=\operatorname{skew}(E^Th\dot E),
 \quad W_N=\tfrac12E^T(\partial_jN_i-\partial_iN_j)E}.       \tag{1}
\]
Se usa \(\operatorname{skew}X=(X-X^T)/2\). Las entradas \(\omega_i\)
son la conexión tridimensional de \(h\) en el marco E:
\[
 \omega_i=E^Th\partial_iE+
 \tfrac12E^T(\partial_i h_{jk}+\partial_kh_{ji}-\partial_jh_{ik})E,
                                                               \tag{2}
\]
donde \(j,k\) son los dos índices matriciales. No contienen derivadas
temporales. (1) no contiene \(\dot N\) ni \(\dot N^i\): el lapse
no aparece en \(\Gamma_{itj}\), y el shift aparece con derivadas espaciales.
Esto retiene \(\dot E\); congelar E destruiría la cancelación de la
parte simétrica de la conexión.

## 2. Hodge ADM y dependencia exacta de las velocidades

La inversa y el volumen ADM son
\[
 \gamma^{00}=-N^{-2},\quad\gamma^{0i}=N^i/N^2,\quad
 \gamma^{ij}=h^{ij}-N^iN^j/N^2,\quad\sqrt{-\gamma}=N\sqrt{\det h}.
\]
Por tanto, para cualquier 1-forma adjunta C,
\[
 L_C=\frac{\chi\sqrt{\det h}}{2N}
             |C_t-N^iC_i|^2
       -\frac{\chi N\sqrt{\det h}}2 h^{ij}\langle C_i,C_j\rangle.
                                                               \tag{3}
\]
La norma es \(\langle X,Y\rangle=\operatorname{tr}(X^TY)/2\)
sobre matrices antisimétricas; los generadores \((T_I)_{jk}=\epsilon_{Ijk}\)
son ortonormales. El signo positivo temporal procede del Hodge Lorentziano.

En la parametrización local de una conexión plana,
\[
 A=-dg\,g^{-1},\quad g\in SO(3),\quad q_g=-\dot g\,g^{-1},
 \quad C_i=-\partial_i g\,g^{-1}-\omega_i,
\]
(1) da
\[
 C_t-N^iC_i=q_g-L_E(\dot h)-B_{\rm sp},\quad
 B_{\rm sp}=W_N+N^iC_i.                                    \tag{4}
\]
A campos y jets espaciales fijos, \(B_{\rm sp}\) y el segundo término
de (3) no dependen de velocidades. Esta parametrización no prueba por sí
sola la equivalencia con todo el dominio BF o sus modos de borde.

## 3. Hessiana, rango y Schur exclusivamente cinético

Identifiquemos las seis componentes independientes de \(\dot h\) con
\(v\in\mathbb R^6\), y \(q_g\) con sus tres componentes de color
\(q\in\mathbb R^3\). En una sección y punto dados, \(L_E\) es una
matriz real \(3\times6\). Sea \(c=\chi\sqrt{\det h}/N>0\).
La parte dependiente de velocidades es
\[
 L_{\rm vel}=\tfrac c2|q-L_Ev-B_{\rm sp}|^2.
\]
Su Hessiana se deriva por diferenciación, y factoriza
\[
 \boxed{K=c\begin{pmatrix}L_E^TL_E&-L_E^T\\-L_E&I_3\end{pmatrix}
       =c[-L_E,I_3]^T[-L_E,I_3]\ \geq0}.                    \tag{5}
\]
La fila matricial tiene rango tres por el bloque identidad. Así K tiene
rango exactamente tres y núcleo \(\{(v,L_Ev):v\in\mathbb R^6\}\).
El bloque \(K_{qq}=cI_3\) es invertible y su Schur cinético es
\[
 K_{vv}-K_{vq}K_{qq}^{-1}K_{qv}=0_{6\times6}.                \tag{6}
\]
Al añadir \(\dot N,\dot N^1,\dot N^2,\dot N^3\), sus filas y columnas
son nulas. No se infiere el rango de las restricciones secundarias.

\(q_g\) es una cuasivelocidad: la traslación en el grupo identifica
\(T_gSO(3)\) con su álgebra. En cualquier carta regular de tres coordenadas
\(\theta\), \(q_g=R(\theta)\dot\theta\) con R invertible. La
Hessiana cambia por congruencia y conserva signo y rango. No se necesita
una única carta exponencial global ni se atraviesan sus singularidades.

(6) **no elimina el campo g**: su Euler contiene derivadas temporales y
espaciales y depende del potencial de (3). Es un Schur de velocidades a
campos fijos, no una solución algebraica de la ecuación de orientación.
Tampoco declara positiva la Hessiana completa de gravedad después de sus
restricciones; sólo esta contribución añadida es semidefinida positiva.

## 4. Derivada de la raíz SPD y oráculo no conmutativo

Para \(E=h^{-1/2}\), sea \(S=h^{1/2}\). Derivar \(S^2=h\) da la
ecuación de Sylvester \(S\dot S+\dot S S=\dot h\), y derivar la inversa
da \(\dot E=-E\dot S E\). En un punto con
\(h=\operatorname{diag}(a_1^2,a_2^2,a_3^2)\), \(a_i>0\),
\[
 \dot E_{ij}=-\frac{\dot h_{ij}}{a_i a_j(a_i+a_j)},\qquad
 [L_E(\dot h)]_{ij}=
 \frac{\dot h_{ij}(a_j-a_i)}{2a_i a_j(a_i+a_j)}.              \tag{7}
\]
Los denominadores son positivos incluso con valores propios repetidos.
No se ha supuesto conmutación entre \(h\) y \(\dot h\). En un fondo
isotrópico \(L_E=0\), pero la anisotropía y una velocidad fuera de la
diagonal producen una mezcla no nula con q en (5).

Un oráculo independiente es la familia SPD exacta
\[
 h(t)=R(t)\operatorname{diag}(1,4,9)R(t)^T,\quad
 E(t)=R(t)\operatorname{diag}(1,1/2,1/3)R(t)^T,
\]
donde R rota los ejes 1,2 un ángulo t. En \(t=0\),
\[
 \dot h_{12}=-3,\quad\dot E_{12}=1/2,\quad
 [\omega_t]_{12}=[L_E(\dot h)]_{12}=-1/4,\quad\omega_{t,21}=1/4.
                                                               \tag{8}
\]
Aquí \([h,\dot h]\ne0\). Se deriva (8) desde la familia finita y
\(E^Th\dot E+E^T\dot h E/2\), sin usar (7) como entrada.
Omitir el acoplamiento a \(\dot h\) daría cero y falla en esta familia.
Con velocidades en el orden \((h_{11},h_{22},h_{33},h_{12},h_{13},h_{23})\),
(7) da \(\partial L_{E,3}/\partial\dot h_{12}=1/12\) en ese punto,
así \(K_{h_{12},q_3}=-c/12\ne0\).

## Alcance

Se prueba la dependencia exacta de velocidades de este término en una
carta unitaria local y una sección suave, su Hessiana Gram y el Schur
cinético. Los contrastes no conmutativos impiden sustituir el marco por
uno congelado o extrapolar el desacoplo isotrópico. No se prueban el
conteo Dirac, la eliminación dinámica de g, una reducción global de T,
la consistencia del dominio BF completo, el sistema moving/gluing ni
estabilidad global o no lineal. N4/N7, P4, B4/B5 y los gates BF/global no
se promueven; la acción permanece propuesta y \(\chi\) sin seleccionar.
