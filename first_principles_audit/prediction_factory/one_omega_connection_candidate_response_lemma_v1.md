# Respuesta lineal de la extensión candidata con corriente de conexión

Esta nota estudia una **propuesta no adoptada**: añadir
\(S_C=-\chi\int_\Sigma\langle C\wedge *_\gamma C\rangle/2\),
\(C=A_\Sigma-\omega(\gamma,T)\), con \(\chi>0\), a la candidata v5.2.
El nuevo coeficiente tiene dimensión masa al cuadrado y no tiene un valor
elegido. La acción v5.2 congelada no contiene este término y no se modifica
por esta nota. La conexión \(A_\Sigma\) permanece independiente de la
conexión geométrica; no se impone \(A_\Sigma=\omega\).

El objeto considerado es el ensamblado lineal seleccionado \(H_{18}\):
la respuesta \(H_{15}\) del fondo BPS y sus ramas radiales de energía
finita, más el Hessiano literal de \(L_C^{(2)}\) en una carta local plana
de la conexión BF con tres amplitudes de orientación. No representa todos
los Euler de la teoría extendida. La identificación de sus cortes, filas
gauge y pivotes con el ensamblado completo es una obligación algebraica
del verificador compañero; no se sustituye por flags de fuentes anteriores.

Los insumos analíticos y geométricos son:

* [Existencia variacional y normalización de los DtN](one_omega_variational_dtn_lemma_v1.md).
* [Realización espectral de la respuesta escalar](one_omega_scalar_spectral_energy_lemma_v1.md),
  incluida su prueba estática independiente en todos los momentos positivos.
* [Reducción directa del bloque homogéneo](one_omega_zero_momentum_linear_lemma_v1.md).
* [Variación de la conexión geométrica proyectada](one_omega_projected_connection_linear_lemma_v1.md).

## 1. Dominio, convenciones y medida espectral

Se usa firma \((-+++ )\), fondo de borde Minkowski, \(T=t\),
\(A_\Sigma=\omega=0\), y momento espacial dirigido según \(x^3\).
Escribimos
\[
 s=\sigma+i\tau,\quad \sigma>0,\quad w=is,\quad q\geq0,
 \quad z=s^2+q^2=q^2-w^2,\quad b=M_b^2>0,\quad M=M5c>0.
\]
Los productos de amplitudes en las densidades siguientes conservan el
adjunto formal entre modos Fourier opuestos, con las fases indicadas en
la derivación geométrica. La continuación analítica en \(w\) no convierte
esas densidades en formas Hermíticas positivas para \(s\) complejo.

El fondo satisface \(A=\log\Omega\), \(\Omega(0)=1\) y
\(\Omega'=-k\Omega e^{-G\Omega^2/(6M)}\). Los dos exteriores usan la
normal UV saliente \(-\partial_r\). Los pesos TT son
\(P_T=\Omega^4,W_T=\Omega^2\), y los escalares
\(P_R=\Omega^6,W_R=\Omega^4\). La construcción variacional determina
\(K_T,K_v\), incluyendo su condición IR, y prueba
\(\Re(K_T/s)>0\), \(\Re(K_v/s)>0\).

La representación espectral exacta de esa misma rama TT es
\[
 m(z):=\frac{MK_T(z)}z
      =\int_{[0,\infty)}\frac{\lambda}{\lambda+z}\,d\mu_m(\lambda),
 \qquad \mu_m\geq0,\qquad
 m_0:=\int d\mu_m=2M\int_0^\infty\Omega^2dr<\infty.       \tag{1}
\]
Es la medida del vector constante para el operador de la forma radial
Dirichlet; no es un ajuste por polos. No se supone finito
\(\int\lambda\,d\mu_m\). En particular no se desplaza un auxiliar TT
por un vector que necesitase ese primer momento.

Para \(\sigma>0\), \(z\notin(-\infty,0]\). Si \(s\) recorre un
compacto de ese semiplano, su imagen en \(z\) tiene distancia positiva
\(\delta\) a dicho corte. La cota
\[
 \left|\frac{\lambda}{\lambda+z}\right|
 \leq 1+\frac{|z|}{\delta}                                  \tag{2}
\]
da integrabilidad y dominación local uniforme respecto de la medida finita.
Por integración de funciones holomorfas dominadas, \(m\) es holomorfa
en este dominio y \(m(\bar z)=\overline{m(z)}\). No se necesita un
momento adicional para justificar diferenciación holomorfa local.

En lo sucesivo \(B=b+m(z)\) designa exclusivamente el coeficiente
vectorial. No es el coeficiente escalar
\(b(1-3\lambda_K)-2m(z)\) de otras notas. Una identidad clave es
\[
 \Re(sB)=b\sigma+
 \sigma\int\frac{\lambda(|s|^2+q^2+\lambda)}
 {|s^2+q^2+\lambda|^2}\,d\mu_m\ \geq b\sigma>0.             \tag{3}
\]
La integral es finita por (2). Es una identidad continua de la medida real,
no una conclusión extraída de muestras de frecuencias o de polos finitos.

## 2. Adición literal y eliminación vectorial con su pivote

La conexión geométrica lineal, en marco horizontal, es
\[
 \omega_{0,ab}=\frac{\partial_bN_a-\partial_aN_b}{2},\qquad
 \omega_{i,ab}=\frac{\partial_bH_{ai}-\partial_aH_{ib}}2.     \tag{4}
\]
Esta fórmula incluye la variación del marco y de Christoffel. No congela
la geometría. Al ser \(C\) nulo en el fondo, su densidad cuadrática usa
solamente el Hodge Lorentziano de fondo:
\[
 L_C^{(2)}=\frac\chi2\|C_0^{(1)}\|^2
           -\frac\chi2\sum_i\|C_i^{(1)}\|^2,
 \quad\|X\|^2=\sum_{a<b}X_{ab}^2.                          \tag{5}
\]
Las correcciones del Hodge y del volumen entran desde orden tres.

En la convención de color \(A=-d\theta\), las fases del vector \(x\)
permiten escribir
\[
 C_{0,y}=w\theta_y+qN_x/2,\qquad
 C_{3,y}=-q\theta_y+qH_{13}/2,
 \quad U=qN_x+wH_{13},\quad\Psi=\theta_y-H_{13}/2.
\]
Así, el corte vectorial completo es exactamente
\[
 L_{\rm vec}=\frac B4U^2+
  \frac\chi2\left[(w\Psi+U/2)^2-q^2\Psi^2\right].          \tag{6}
\]
Las combinaciones \(U,\Psi\) son invariantes bajo la difeomorfía
transversal acompañada de la rotación que mantiene horizontal el marco.
El vector \(y\) da el mismo corte con la orientación opuesta de
\(\theta_x\). Cambiar de convención de color cambia ambos signos
correspondientes, no los factores reducidos.

Para \(q>0\) se puede elegir \(H_{13}=0\), de modo que
\(U=qN_x,\Psi=\theta_y\). La ecuación algebraica de \(U\) da
\[
 \frac{2B+\chi}{4}U+\frac{\chi w}{2}\Psi=0,\qquad
 U_*=-\frac{2\chi w}{2B+\chi}\Psi.                          \tag{7}
\]
El pivote del shift y el Schur resultante son
\[
 H_{NN}=\frac{q^2(2B+\chi)}4,\qquad
 L_{\rm vec,red}=\frac12(K_{\rm eff}w^2-\chi q^2)\Psi^2,
 \quad K_{\rm eff}=\frac{2\chi B}{2B+\chi}.                 \tag{8}
\]
Para \(w=is\), el Schur de acción es \(-D_\theta\), con
\[
 D_\theta=s^2K_{\rm eff}+\chi q^2,
 \qquad \det H_{(N,\Psi)}=-H_{NN}D_\theta.                 \tag{9}
\]
Se conserva por tanto el factor eliminado; no basta probar el último
denominador. La identidad (3) implica
\[
 \Re\{s(2B+\chi)\}\geq(2b+\chi)\sigma>0.                 \tag{10}
\]
En particular \(B\), \(2B+\chi\) y \(H_{NN}\) no se anulan en
el dominio \(\sigma>0,q>0\), y estas eliminaciones son holomorfas.

## 3. Positividad real estricta y una cota de los canales nuevos

La identidad algebraica
\[
 sK_{\rm eff}=
 \left[\frac1{\chi s}+\frac1{2sB}\right]^{-1}              \tag{11}
\]
permite usar (3): ambos sumandos tienen parte real positiva, al igual que
su suma y su inversa. Por consiguiente
\[
 \Re\frac{D_\theta}s
 =\Re(sK_{\rm eff})+\frac{\chi q^2\sigma}{|s|^2}>0.        \tag{12}
\]
Esto prueba simultáneamente ausencia de ceros y regularidad del canal,
sin elegir un valor de \(\chi\).

Existe una cota más explícita. Sean
\(d=2b+\chi\) y \(K_0=2\chi b/d>0\). Se tiene
\[
 s(K_{\rm eff}-K_0)=\frac{2\chi^2}{d}
                         \frac{sm}{d+2m}.                  \tag{13}
\]
Si la medida tiene masa fuera de \(\lambda=0\), (3) sin el término
\(b\sigma\) da \(\Re(sm)>0\), y
\[
 \frac{sm}{d+2m}=\left[\frac d{sm}+\frac2s\right]^{-1}
\]
tiene parte real positiva. Si \(m\equiv0\), el resto de (13) es cero.
Así, en ambos casos,
\[
 \boxed{\Re(D_\theta/s)\geq
  \sigma\left[\frac{2\chi b}{2b+\chi}
                      +\frac{\chi q^2}{|s|^2}\right]>0}.   \tag{14}
\]
El tercer canal, longitudinal respecto del momento espacial, no se mezcla
con (4) en sus componentes \(\mu=0,3\). Su respuesta es
\[
 D_{\theta\parallel}=\chi(s^2+q^2),\qquad
 \Re(D_{\theta\parallel}/s)
       =\chi\sigma(1+q^2/|s|^2)>0.                         \tag{15}
\]
Estos son enunciados sobre respuestas seleccionadas y sus variables de
orientación; no constituyen un conteo de partículas físicas de BF.

## 4. Cortes tensorial y escalar y restantes factores

Para cada polarización TT con amplitud no normalizada por Frobenius,
por ejemplo \(H_{12}=H_{21}=h\), (5) añade
\(-\chi q^2h^2/4\). Por tanto
\[
 F_T^{\rm new}=F_T+\chi q^2,\quad
 F_T=b(s^2+\xi q^2)+MK_T,\quad H_{hh}^{\rm new}=-F_T^{\rm new}/2.
                                                                    \tag{16}
\]
La polarización \(H_{11}=h,H_{22}=-h\) tiene el mismo factor. Para
\(\xi\geq0\), el lema DtN y \(b>0\) dan
\(\Re(F_T^{\rm new}/s)>0\). Aquí el punto congelado tiene \(\xi=1\).

En el corte escalar \(H_{ij}=2\zeta\delta_{ij}\), la adición es
\(-\chi q^2\zeta^2\); no introduce filas de lapse, shift longitudinal,
\(\tau\), \(\Omega\) ni material. Los pivotes escalares anteriores
se conservan, y el último Schur satisface
\[
 S_\zeta^{\rm new}=S_\zeta-2\chi q^2,
 \qquad D_\zeta^{\rm new}:=-S_\zeta^{\rm new}=D_\zeta+2\chi q^2.
                                                                    \tag{17}
\]
La realización espectral escalar citada prueba
\(\Re(D_\zeta/s)>0\) en todos los \(q>0\), **con sus condiciones
de coeficientes y prueba estática**. En particular se aplica al punto
literal
\[
 M=k=1,\quad G=6/5,\quad b=\beta=2,\quad\bar B_4=4/5,
 \quad\kappa=Z_5=1,\quad y^2=3,
 \quad\lambda_K=-0.5535068954004245,\quad
 \eta=3.107013790800849.
\]
No se transforma ningún decimal en una identidad exponencial exacta.
En ese dominio (17) conserva la positividad real estricta. No se afirma
esta conclusión escalar para coeficientes arbitrarios por conocer sólo
la positividad de los DtN.

Los factores materiales \(\kappa+2Z_5p\), \(p=\sqrt z\) con
\(\Re p>0\), y el pivote \(\beta+GK_v\) siguen no nulos por sus
identidades previas. También permanecen los pivotes de shift longitudinal
y de lapse del sector escalar: (17) no altera sus filas. Su exclusión de
ceros es la del lema escalar y sus pruebas de pivotes, no una cancelación
formal del determinante. Junto con (10), (12), (15) y (16), estos factores
excluyen un núcleo adicional del cociente seleccionado de \(H_{18}\) en
el semiplano abierto, una vez comprobada su identificación algebraica.

## 5. Momento cero desde la conexión literal

El caso \(q=0\) se evalúa en la matriz completa antes de elegir cartas
que dividan por \(q\). Todas las entradas de (4) tienen derivadas
espaciales; por ello \(\omega^{(1)}=0\) para perturbaciones homogéneas,
incluidas las perturbaciones temporales de la geometría. Las tres
orientaciones contribuyen directamente
\[
 L_C^{(2)}(q=0)=\frac\chi2\sum_{a=1}^3\dot\theta_a^2,
 \qquad\Delta H_{18}(q=0,w)
        =\operatorname{diag}(0_{15},\chi w^2 I_3).          \tag{18}
\]
El bloque geométrico homogéneo es exactamente el \(H_{15}\) tratado
en su propia carta. Sus cinco direcciones gauge, cinco componentes
espaciales sin traza, bloque \((\zeta,D)\) y triplete material se
conservan; no se impone isotropía espacial como condición gauge.
Las orientaciones añaden las respuestas \(\chi s^2 I_3\), cuya razón
por \(s\) tiene parte real \(\chi\sigma I_3>0\).
Así el nuevo bloque no añade ceros en \(\sigma>0,q=0\), suponiendo
el mismo cociente homogéneo y dominio radial ya identificados.

La prueba es (4)--(5), no el límite de (8). En efecto, la reconstrucción
\(N_x=-2\chi w\Psi/[q(2B+\chi)]\) sólo existe en la carta \(q>0\).
Puede ser singular cuando \(q\to0\), incluso aunque (14) sea estricta.
La desigualdad del Schur reducido no prueba una cota uniforme del shift
reconstruido en un espacio de campos. Los modos de orientación constantes
en tiempo y espacio pertenecen a \(s=q=0\), fuera del dominio de esta nota.

## 6. Qué prueba y qué queda fuera

Las identidades y argumentos anteriores dan una prueba analítica por modo:
en la rama radial de energía finita, al punto congelado para el sector
escalar y para cualquier \(\chi>0\), los factores nuevos son holomorfos
y no nulos en \(\Re s>0\). Su ensamblado exacto con \(H_{15}\) conserva
la ausencia de ceros del cociente de respuesta seleccionado, incluyendo
el tratamiento directo de \(q=0\). La medida finita basta para el nuevo
argumento vectorial; no se introduce un primer momento TT oculto.

El resultado es de la **respuesta extendida propuesta**, no de la acción
v5.2 intacta. No demuestra que las orientaciones satisfagan además todos
los Euler BF, el mapa variacional de gluing o las ecuaciones de embedding.
Tampoco construye el dominio global de BF/edge, una equivalencia no lineal,
una reparación total de la compatibilidad Robin, una cota uniforme de
eliminación del shift, control del eje imaginario, resonancias o estabilidad
no lineal. No se deducen propiedades de aprendizaje a partir de esta prueba.
La acción extendida no se adopta y \(\chi\) queda simbólico. Los gates
generales, incluidos N4/N7, P4, B4/B5 y el dominio BF/global, siguen sin
promoverse. El compañero verifica álgebra y vincula fuentes; sus identidades
finitas no sustituyen las hipótesis de dominio ni los argumentos analíticos.
