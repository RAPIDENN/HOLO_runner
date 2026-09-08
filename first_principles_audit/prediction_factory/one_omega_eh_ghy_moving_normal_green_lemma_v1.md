# Green normal móvil de Einstein–Hilbert más GHY

Esta nota identifica, mediante variación de la acción, el sumando normal
local del sector Einstein–Hilbert más GHY y su emparejamiento con el Green
escalar. Es un paso adicional a la identidad algebraica de constraints;
no identifica todavía el Green completo del sistema SO(3), BF y sus mapas
materiales dependientes. La acción congelada no se cambia y N4/N7 siguen
sin promoverse.

## 1. Convenciones, variables y alcance de la carta

La métrica bulk tiene firma (-,+,+,+,+). Sigma es una hipersuperficie
timelike suave, con métrica Lorentziana común gamma y normal unitario
espacial. Se considera

\[
 S_g=\frac M2\sum_{\epsilon=\pm}\int_{M_\epsilon}\!R_g\,\mathrm{vol}_g
       +M\sum_{\epsilon=\pm}\int_\Sigma\!K_{out,\epsilon}\,
                                             \mathrm{vol}_\gamma,
 \qquad M>0\text{ constante}.
 \tag{1}
\]

El signo y la normalización son los de la acción literal. Se usan
\(R^\rho{}_{\sigma\mu\nu}=\partial_\mu\Gamma^\rho_{\nu\sigma}
-\partial_\nu\Gamma^\rho_{\mu\sigma}+\cdots\) y
\(K_{ab}=\gamma_a{}^M\gamma_b{}^N\nabla_M n_N\).

Las derivaciones se realizan en un collar gaussiano local. Las variaciones
conservan las trazas comunes y se toman compactamente soportadas respecto
a otros bordes; equivalentemente, se conservan explícitamente las
corrientes tangenciales indicadas. No se declara tratada una intersección
con fronteras externas que necesite acción y variación de esquina.

Para una cara, n denota primero su normal **exterior**, y f su velocidad
respecto a ese normal. Se escriben
\(k=\operatorname{tr}_\gamma K\),
\(\pi^{ab}=K^{ab}-k\gamma^{ab}\) y
\(H_g=M(k^2-K:K-R_\gamma)/2\).
El coeficiente de variación métrica se normaliza por unidad de
\(\mathrm{vol}_\gamma\), sin esconder un factor de densidad en p.

## 2. Cancelación de los jets normales en el Green métrico

En un collar \(g=dn^2+\gamma(n,x)\), \(K=\partial_n\gamma/2\).
Para contrastar el Green se eligen variaciones gaussianas
\(\delta g_{nn}=\delta g_{na}=0\), con \(h_{ab}=\delta\gamma_{ab}\)
y \(h'_{ab}=\partial_n h_{ab}\) arbitrarios. No se congela ni h ni h'.
Palatini da en la frontera el coeficiente

\[
 \Theta_{EH}^n=\frac M2(\nabla_\nu h^{n\nu}-\nabla^n\operatorname{tr}h)
              =\frac M2(K:h-\gamma^{ab}h'_{ab}).
 \tag{2}
\]

Aunque \(h^{n\nu}=0\), su derivada covariante es
\(\nabla_\nu h^{n\nu}=-K:h\), no cero. Además
\(\partial_n(\gamma^{ab}h_{ab})=\gamma^{ab}h'_{ab}-2K:h\).
La variación de GHY es

\[
 \frac{\delta(M\sqrt{-\gamma}\,k)}{\sqrt{-\gamma}}
     =\frac M2\gamma^{ab}h'_{ab}-M K:h+\frac M2 k\operatorname{tr}h.
 \tag{3}
\]

Los jets h' se cancelan entre (2) y (3). Queda el Green de Dirichlet,

\[
 \boxed{p^{ab}h_{ab},\qquad p^{ab}=-\frac M2\pi^{ab}.} \tag{4}
\]

La elección gaussiana deja libre toda la métrica inducida y proporciona
un representante local para este sumando. No fija por ese motivo las
constraints de lapse y shift en el interior ni permite omitir los Euler
bulk de una variación que cambia de representante.

El integrando ADM de primer orden, con sus divergencias tangenciales
retenidas, ofrece un contraste:
\(L_g=M\sqrt{-\gamma}(R_\gamma+k^2-K:K)/2\) da
\(\partial L_g/\partial(\partial_n\gamma_{ab})
=\sqrt{-\gamma}\,p^{ab}\). Aquí este momento no sustituye la
cancelación explícita (2)–(3).

## 3. Variación real de la superficie y término de Legendre

Manteniendo fijos los campos bulk, la inmersión normal
\(Y_\epsilon(x)=(\epsilon f(x),x)\) satisface

\[
 \delta\gamma_{ab}=2fK_{ab},\qquad
 \delta\sqrt{-\gamma}=f k\sqrt{-\gamma},\qquad
 \delta k=-\Box_\gamma f-f(\operatorname{Ric}_{nn}+K:K).
 \tag{5}
\]

La última igualdad se obtiene diferenciando la normal unitaria y la
segunda forma fundamental, y contrayendo también la **inversa métrica
variada**. En particular, no se puede mantener fija esa inversa: su
contribución es \(-2fK:K\). La forma no contraída en el representante
normal es
\(\delta K_{ab}=-D_aD_b f+f(K_a{}^cK_{cb}-R_{nanb})\).

El teorema de transporte aporta \(M f R_g/2\) desde el dominio bulk.
Combinándolo con la variación de GHY antes de usar ninguna ecuación,

\[
 \frac{\delta_{shape}S_g|_\Sigma}{\mathrm{vol}_\gamma}
   =\frac{Mf}{2}[R_g-2\operatorname{Ric}_{nn}-2K:K+2k^2]
                                                 -M\Box_\gamma f.
 \tag{6}
\]

La identidad de Gauss con estas convenciones es
\(R_g=R_\gamma+2\operatorname{Ric}_{nn}+K:K-k^2\). Por tanto

\[
 \boxed{\frac{\delta_{shape}S_g|_\Sigma}{\mathrm{vol}_\gamma}
  =\frac{Mf}{2}(R_\gamma+k^2-K:K)-M\Box_\gamma f
  =p:(2fK)-f H_g-M\Box_\gamma f.} \tag{7}
\]

La corriente tangencial retenida es \(-M D^a f\). f puede variar en los
cuatro ejes intrínsecos, incluido el tiempo; el operador es el d'Alembertiano
Lorentziano, no un Laplaciano espacial introducido a mano. (6) incluye la
variación de dominio una sola vez. Añadir después otro \(f L_{EH}\)
contaría dos veces el mismo movimiento.

La superposición con una variación euleriana bulk da, en coordenadas de
traza material \(h_\Sigma=\delta g_\parallel+2fK\),

\[
 \Theta_{g,\Sigma}=p:h_\Sigma-fH_g+D_a\mathcal B_g^a,
 \qquad\mathcal B_g^a=-M D^a f
 \tag{8}
\]

para la contribución de forma, además de los bordes tangenciales del
representante métrico. Los integrales Euler bulk multiplican la variación
euleriana de g, no h_Sigma; se mantienen en la primera variación total.

Un contraste que no impone BPS usa
\(g=dn^2+e^{2A(n)}\eta_{ab}dx^a dx^b\), con a=A' y a' libres:
\(R_g=-8a'-20a^2\), \(\operatorname{Ric}_{nn}=-4a'-4a^2\),
\(k=4a\). (6) cancela a' y da \(6Ma^2 f-M\Box_\gamma f\), igual a
(7). La geometría plana con f variable conserva el segundo término aunque
K=0; un contraste limitado a f constante no lo detectaría.

## 4. Dos caras y filas comunes que deben conservarse

Ahora n apunta de M_minus a M_plus en ambos collares. Sus normales
exteriores son \(n_{out,-}=n\), \(n_{out,+}=-n\), y las velocidades
exteriores son \(f_{out,-}=f\), \(f_{out,+}=-f\). Se usan
\(K_\pm\) respecto al **normal común** y
\([X]=X_+-X_-\). Como H_g es par en K, sumar (8) produce

\[
 \Theta_{g,\Sigma}/\mathrm{vol}_\gamma
       =\frac M2[\pi]:h_\Sigma+f[H_g]+D_a\mathcal B^a.
 \tag{9}
\]

Las corrientes de forma \(-MD^a f_{out,\pm}\) se cancelan entre las dos
caras con la misma gamma y M. Esta cancelación no sustituye el tratamiento
de esquinas o fronteras externas. Las variaciones admisibles satisfacen
\(\delta g_{\parallel,\pm}=h_\Sigma-2fK_\pm\); no se congelan ambos
bulks cuando \(K_+\ne K_-\).

Para un sector escalar de primer orden
\(L_s=-C_{AB}(q)\nabla q^A\cdot\nabla q^B/2-V(q)\), escriba
\(v_\pm=\partial_n q_\pm\), \(p_{s,\pm}=-C v_\pm\).
La identidad \(L_s-p_s\cdot v=T_{nn}\) y el Green escalar móvil ya
derivado dan

\[
 (p_{s,-}-p_{s,+})\cdot\Delta q_\Sigma-f[T_{nn}],\qquad
 \delta q_\pm=\Delta q_\Sigma-fv_\pm.
 \tag{10}
\]

Si el sector es gauged o q representa el material en un marco dependiente,
(10) es el sumando escalar en su carta correspondiente: las variaciones de
A, del transporte de q y de la identificación del marco añaden sus propios
adjuntos. No se declara que (10) los haya incluido automáticamente.

Una única acción intrínseca de pared aporta
\(\tau^{ab}h_{\Sigma,ab}/2+\ell_{q,A}\Delta q_\Sigma^A+E_T\vartheta\)
y su corriente tangencial. Tau es su **Euler métrico completo**, incluido
el marco si depende de gamma; no se lo sustituye por sólo el estrés
explícito de volumen. No hay dependencia extrínseca radial adicional en
esa acción de pared. Con

\[
 I=-M[\pi]-\tau,\quad H=H_g-T_{nn},\quad
 R_A=p_{s,-,A}-p_{s,+,A}+\ell_{q,A},
\]

el Green del sector declarado queda

\[
 \boxed{\Theta_\Sigma/\mathrm{vol}_\gamma
 =-\tfrac12 I:h_\Sigma+R_A\Delta q_\Sigma^A+E_T\vartheta
                         +f[H]+D_a\mathcal B^a.} \tag{11}
\]

Las filas \(R_A\Delta q_\Sigma^A\) y \(E_T\vartheta\) no se descartan
sin fijar esas trazas o imponer sus ecuaciones. La acción de pared se
cuenta una vez. A (11) deben añadirse los sumandos de conexión/BF y los
adjuntos materiales cuando se estudie la candidata completa.

## 5. Enlace variacional con la identidad normal

Cambie ahora de coordenada tangente a
\(h_\Sigma=h_0+2f\bar K\), con \(\bar K=(K_++K_-)/2\). Entonces

\[
 \Theta_\Sigma/\mathrm{vol}_\gamma
 =-\tfrac12 I:h_0+R_A\Delta q_\Sigma^A+E_T\vartheta
                       +f([H]-\bar K:I)+D_a\mathcal B^a.
 \tag{12}
\]

La identidad tensorial previamente comprobada establece
\([H]-\bar K:I=\tau:\bar K-[T_{nn}]\). Las ecuaciones (2)–(11)
identifican **de dónde procede ese coeficiente en la variación**, dentro
del sector y la carta aquí declarados. No se lo introduce simplemente
porque sea una combinación algebraica atractiva de constraints.

Al variar f con h_0=0, la variación euleriana de cada bulk es
\(\delta g_{\parallel,\pm}=2f(\bar K-K_\pm)\), y los escalares
requieren las variaciones de (10). Esas variaciones no son cero. Los
Euler bulk deben permanecer off shell, o imponerse antes de interpretar
(12) como una acción reducida sobre soluciones bulk. Imponer Israel sin
las constraints bulk no fuerza a desaparecer el coeficiente normal.

No se deducen existencia, unicidad, hiperbolicidad ni estabilidad del
sistema acoplado. El transporte material, la fila BF móvil, la equivalencia
del sistema completo con H18 y su dominio funcional siguen pendientes.
Los gates N4/N7, C1/N1, P2–P4 y B4/B5 permanecen false. La afirmación
acotada es la identificación local (11)–(12) desde la variación de
Einstein–Hilbert más GHY y el sumando escalar, con sus límites explícitos.
