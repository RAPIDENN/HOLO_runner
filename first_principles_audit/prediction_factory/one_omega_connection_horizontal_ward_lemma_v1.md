# Ward difeomorfo horizontal del término candidato de conexión

Se considera únicamente la propuesta no adoptada
\[
 S_C=-\frac\chi2\int_\Sigma\langle C\wedge *_\gamma C\rangle,
 \qquad C=A_\Sigma-\omega(\gamma,T),\qquad\chi>0.
\]
\(\chi\) tiene dimensión masa al cuadrado y no tiene valor elegido.
\(A_\Sigma\) permanece independiente de \(\omega\). La acción v5.2
congelada no se altera por esta identidad. Se usa la primera variación de
[la nota covariante](one_omega_connection_current_covariant_variation_lemma_v1.md),
con el fibrado Q dependiente y su identificación horizontal retenidos.

La identidad siguiente vale localmente **off shell**: no impone
\(F_A=0\), \(G=0\), \(E_T=0\) ni las ecuaciones de Einstein. Las
variaciones compactas permiten extraerla sin descartar una contribución de
borde física. No cierra el mapa variacional de gluing o embedding ni N4/N7.

## 1. Convenciones y primera variación

La firma es \((-+++)\), \(u=-N\,dT\), \(u^2=-1\), y el marco espacial
satisface \(\gamma(e_a,e_b)=\delta_{ab}\), \(u\cdot e_a=0\).
\[
 \omega_{\mu,ab}=\gamma(e_a,\nabla_\mu e_b),\quad
 \kappa_{\mu,a}=\gamma(e_a,\nabla_\mu u),\quad
 \langle X,Y\rangle=\tfrac12\sum_{a,b}X_{ab}Y_{ab}.
\]
El orden del emparejamiento de conexión es \(J_\Sigma\wedge\delta A\),
con \(J_\Sigma=\chi *_\gamma C\); por tanto
\[
 J_\Sigma\wedge\delta A=-\chi\langle C^\mu,\delta A_\mu\rangle
                         \mathrm{vol}_\gamma.
\]
Denotando \(h=\delta\gamma\), \(f=\delta T\), la primera variación
horizontal, con su divergencia de borde separada, es
\[
 \delta S_C=\int\mathrm{vol}_\gamma
 [\tfrac12\tau_C^{\mu\nu}h_{\mu\nu}+E_T f
                  -\chi\langle C^\mu,\delta A_{h,\mu}\rangle]. \tag{1}
\]
La nota covariante establece
\[
 \begin{split}
 J^{\mu\nu\rho}&=\chi C^{\mu ab}e_a{}^\nu e_b{}^\rho,
 &V^\sigma&=\chi C^{\mu ab}\kappa_{\mu,a}e_b{}^\sigma,\\
 T_C^{\mu\nu}&=\chi[\langle C^\mu,C^\nu\rangle
 -\tfrac12\gamma^{\mu\nu}\langle C_\rho,C^\rho\rangle],\\
 \tau_C^{\mu\nu}&=T_C^{\mu\nu}-\nabla_\rho J^{(\mu\nu)\rho}
                         -V^{(\mu}u^{\nu)},
 &E_T&=\nabla_\sigma(NV^\sigma).
 \end{split}                                                   \tag{2}
\]
Las simetrizaciones tienen peso un medio. Estas son contribuciones del
nuevo término, no el tensor y los Euler totales de la candidata.

## 2. Rotación entre el marco natural y el horizontal

Tomamos la variación difeomorfa con signo de pullback positivo:
\(h=\mathcal L_\xi\gamma\), \(f=\xi^\nu\partial_\nu T\), y el
marco natural \(\delta_\mathrm{nat}e=\mathcal L_\xi e\).
La variación horizontal es
\[
 \delta_h e_a=-\tfrac12 h^\sharp e_a+u\beta_a,
 \quad\beta_a=e_a{}^\mu(\delta u_\mu-h_{\mu\nu}u^\nu/2).
\]
Ambas variaciones cumplen las mismas restricciones de marco con el mismo
\(h,f\); su diferencia es una rotación espacial, sin componente de boost.
Su proyección se obtiene de la definición, no de una ley postulada para A:
\[
 \begin{split}
 \gamma(e_c,\mathcal L_\xi e_a-\delta_h e_a)
 &=\xi^\mu\omega_{\mu,ca}
 -e_c{}^\mu e_a{}^\nu\nabla_\nu\xi_\mu+\tfrac12h(e_c,e_a)\\
 &=i_\xi\omega_{ca}+\sigma_{\xi,ca},\\
 \sigma_{\xi,ab}&=\tfrac12e_a{}^\mu e_b{}^\nu
                  (\nabla_\mu\xi_\nu-\nabla_\nu\xi_\mu).
 \end{split}                                                   \tag{3}
\]
Por tanto \(\mathcal L_\xi e=\delta_h e+e\rho_\xi\), con
\(\rho_\xi=i_\xi\omega+\sigma_\xi\). Un cambio de representante
\(\delta e=e\rho\) requiere \(\delta A=D_A\rho\), al igual que
\(\delta\omega=D_\omega\rho\). Restar esa rotación del representante
natural da
\[
 \begin{split}
 \delta A_h&=\mathcal L_\xi A-D_A\rho_\xi\\
 &=i_\xi F_A+D_A\Lambda_\xi,
 \qquad\Lambda_\xi=i_\xi C-\sigma_\xi.                       \tag{4}
 \end{split}
\]
Aquí \(F_{\nu\mu}=\partial_\nu A_\mu-\partial_\mu A_\nu
+[A_\nu,A_\mu]\), y \((i_\xi F)_\mu=\xi^\nu F_{\nu\mu}\).
La segunda igualdad es la fórmula de Cartan de la conexión.
Tratar A como una 1-forma sobre un fibrado fijo omitiría el último término
de \(\Lambda_\xi\); no es el transporte horizontal de este problema.

## 3. Identidad covariante off shell

Definimos la 0-forma adjunta y su imagen espacial
\[
 G=\frac{D_AJ_\Sigma}{\mathrm{vol}_\gamma}
   =\chi(D_A)_\mu C^\mu,
 \qquad G_H^{\mu\nu}=G_{ab}e_a{}^\mu e_b{}^\nu.
                                                               \tag{5}
\]
\(G_H\) es antisimétrico. Al sustituir (4) en (1), la invariancia del
producto interno e integración por partes covariante dan
\[
 -\chi\langle C^\mu,D_\mu\Lambda_\xi\rangle
 \simeq\langle G,\Lambda_\xi\rangle
 =\xi^\nu\langle G,C_\nu\rangle-\langle G,\sigma_\xi\rangle.
\]
El símbolo \(\simeq\) conserva igualdad salvo una divergencia explícita.
Con la norma de la sección 1, la última contracción es precisamente
\[
 -\langle G,\sigma_\xi\rangle
 =-\tfrac12G_H^{\mu\nu}\nabla_\mu\xi_\nu
 \simeq+\tfrac12\nabla_\mu G_H^{\mu\nu}\,\xi_\nu.            \tag{6}
\]
Al integrar también \(\tau_C^{\mu\nu}\nabla_\mu\xi_\nu\) y usar la
invariancia difeomorfa de la densidad para \(\xi\) compacto, su coeficiente
local arbitrario queda
\[
 \boxed{\nabla_\mu\tau_C^\mu{}_{\nu}
 =E_T\partial_\nu T-\chi\langle C^\mu,F_{\nu\mu}\rangle
       +\langle G,C_\nu\rangle
       +\tfrac12\nabla_\mu G_H^\mu{}_{\nu}}.                 \tag{7}
\]
Equivalentemente, el tensor no simétrico
\(\tau_C^\mu{}_{\nu}-G_H^\mu{}_{\nu}/2\) tiene como divergencia
los tres primeros términos de la derecha. No se ha impuesto ninguna fila
Euler para obtener (7), y no se descarta \(G\) como si fuese nulo off shell.
En una interfaz con borde, las divergencias que llevan a (7) deben formar
parte de la cadena de Green y gluing; esta identidad local no la sustituye.

## 4. Oráculos independientes de la prueba estructural

El compañero deriva Christoffel, \(\omega,\kappa\), los tensores (2),
\(F,G\) y las divergencias de una geometría dada. No define la divergencia
de \(\tau\) mediante el lado derecho de (7).

**Contraste plano.** En Minkowski, \(T=t\), se toma sólo
\(C_{1,13}=\epsilon c(x^1,x^3)\), \(C_{1,31}=-\epsilon c\),
con \(A=C\), \(c=x^1x^3\). A primer orden,
\[
 \tau_{11}=-\chi\partial_3c,\qquad
 \tau_{13}=\tau_{31}=\tfrac\chi2\partial_1c,
 \quad(\nabla\tau)_1=-\tfrac\chi2,\quad
 \tfrac12(\nabla G_H)_1=-\tfrac\chi2.                        \tag{8}
\]
Las otras contribuciones de (7) empiezan en orden dos. Este ejemplo
refuta inmediatamente omitir la última derivada, cambiar su signo o
perder el medio. El compañero contrasta también las cuatro filas completas,
sin limitarse a su coeficiente lineal.

**Contraste curvo.** Se elige \(a>0\), \(N=1+a(x^1)^2>0\),
\[
 \gamma=-N^2dt^2+\sum_i(dx^i)^2,\quad T=t,\quad
 A_0=x^1x^3T_2,\quad A_1=x^1T_1,\quad A_3=x^3T_3,\quad A_2=0,
\]
con \((T_I)^J{}_K=\epsilon_{IJK}\). En el marco cartesiano espacial,
\(\omega=0\), pero \(\kappa_{0,1}=N'=2ax^1\) no es cero.
Además \(R^1{}_{010}=NN''=2aN\ne0\); no es sólo un cambio de coordenadas
plano como lo sería un lapse afín de Rindler. El cálculo directo da
\[
 E_T=\frac{2\chi a(x^1)^2}{N}\not\equiv0,
 \qquad G=\chi\left[\frac{1+3a(x^1)^2}{N}T_1+T_3\right].    \tag{9}
\]
Las conexiones no conmutan y \(F\) no se anula. Todas las filas de (7)
se contrastan antes de aplicar ninguna condición BF o de materia.
Omitir \(E_TdT\) deja un residuo temporal no nulo. No se afirma que esta
geometría y esta conexión resuelvan otra parte de la candidata: son datos
suaves admisibles para una identidad off shell.

**Signo de la compensación H18.** En el fondo plano, una difeomorfía
\(\xi^1(t,x^3)\) da \(\sigma_{13}=-\partial_3\xi^1/2\).
Como \((T_2)_{13}=-1\), su componente de color es
\(\sigma_2=+\partial_3\xi^1/2\). En la convención \(A=-d\theta\),
(4) da \(\delta\theta_2=+iq\xi^1/2\). Para \(\xi^2\),
\(\delta\theta_1=-iq\xi^2/2\). Se conserva así la combinación
\(\theta_2-H_{13}/2\), sin congelar el marco.

La demostración general es (1)--(7), no una extrapolación de los oráculos.
La propuesta sigue no adoptada, \(\chi\) sin seleccionar, y N4/N7, P4,
B4/B5, dominio BF/global y estabilidad no lineal permanecen sin promoverse.
