# Reconstrucción BF afín con corriente: cociente seleccionado por fibra

Este lema se refiere a la extensión propuesta S_C=-chi/2 int<C wedge *C>,
C=A_Sigma-omega(gamma,T), chi>0. No adopta ese término en la carta v5.2 ni
prueba todas las ecuaciones de la teoría extendida. Se fijan una geometría
de fondo BPS y los datos geométricos lineales de la interfaz. La extensión
BF construida abajo no modifica esos datos.

Fuentes fijadas por bytes: acción candidata v5.2
(d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b),
recibo de la homotopía BF lineal anterior
(c14cf8d7b5820114837a4fb7f432ef250001224b8946f386c55350d2a829871d)
y recibo de la corriente candidata
(e14bba98d1c9d6976c1ed2f6c902d9a603e7f20a09796c2dddc9c31095331a1e).
Se recomputa aquí el álgebra exterior; no se heredan sus gates.

## Complejo lineal e incidencia

Cada lado es Sigma x [0,infinity), r crece hacia el bulk y r=0 es UV.
Se utiliza una trivialización común de las trazas transportadas. El fondo
A=B=phi=0 abelianiza por separado los tres generadores de so(3):

    d_5 A_plus=d_5 A_minus=0,
    d_5 B_plus=d_5 B_minus=0,
    A_plus|Sigma=A_minus|Sigma=A_Sigma,
    b_plus-b_minus=J_Sigma,       J_Sigma=chi *_Sigma C.

Aquí la corriente material bulk lineal J4_bulk es cero. La construcción
no resuelve dB=-J4_bulk a orden epsilon^2; esa reconstrucción sourced es
un problema distinto, aunque ya se haya cerrado una compatibilidad de salto.

A es una 1-forma, B una 3-forma y J una 3-forma en Sigma4. Las incidencias
son (+1,-1), las mismas de la forma de Green -<(b_plus-b_minus) wedge delta A>.
No se añade otro signo por el normal exterior: las b son pullbacks a la
misma Sigma orientada y la incidencia ya contiene esa información.
La variación de S_C es +<chi *C wedge delta A>, por el intercambio de
una 1-forma con una 3-forma; así el salto es +J, no -J.

La fibra es exp(s t+i k.x), Re(s)>0, k real. Escribimos

    d_Sigma=s dt wedge+i sum_j k_j dxj wedge,
    d_5=d_Sigma+dr wedge partial_r,
    h=i_partial_t/s.

Entonces d h+h d=1 y d^2=0 en todos los grados 0,...,5. Se conserva la
derivada radial real de los coeficientes, no se sustituye por cero.
El pullback UV conmuta con d y con h.

## Datos de interfaz y extensión explícita

Como d_Sigma A_Sigma=0, la elección

    theta=-h A_Sigma

satisface A_Sigma=-d_Sigma theta. Es única en esta fibra: d_Sigma theta=0
implica s theta=0. theta parametriza los datos de conexión relativos al
marco geométrico; no se borra mediante los gauges relativos usados abajo.

La ecuación de theta es d_Sigma J(theta,gamma,T)=0. Con A_Sigma=-d theta,
la fila Euler tiene signo -dJ, pues -J wedge d(delta theta)
=d(J delta theta)-dJ delta theta. La ecuación homogénea es dJ=0.
También es necesaria por los dos dB=0 y el salto.

Sea f suave, f=1 cerca de r=0 y f=0 para r>=R, con R finito. Definimos

    E_f(A)_plus=E_f(A)_minus=-d_5[f theta],
    E_f(B)_plus=+d_5[f hJ]/2,
    E_f(B)_minus=-d_5[f hJ]/2.

En componentes tangenciales y radiales,

    A_eps=-f d_Sigma theta-f' dr theta,
    B_eps=eps/2 [f J+f' dr wedge hJ], eps=+1 o -1.

Se usó d_Sigma hJ=J, válida porque dJ=0. Las dos extensiones son cerradas
por d^2=0. Sus trazas son A_Sigma y +/-J/2, y el salto es exactamente J.
Los términos con f' son necesarios: eliminarlos hace fallar dA=0 o dB=0.
El corte radial no exige modificar omega ni imponer A=omega.

## Unicidad afín y biyección seleccionada

Sea R la restricción de una solución bulk a theta=-h A_Sigma y sus datos
geométricos. R E_f=id exactamente. Para comparar una solución con E_f R,
sea Delta el valor original menos el representante reconstruido.

    d Delta A_eps=0,       tr Delta A_eps=0,
    d Delta B_eps=0,       tr Delta B_plus=tr Delta B_minus.

Con las convenciones delta_g A=-d epsilon y delta_g B=d Lambda, se elige

    epsilon_eps=+h Delta A_eps,
    Lambda_eps=-h Delta B_eps.

Las diferencias se anulan. Los epsilon tienen traza cero; las Lambda
tienen trazas comunes. Así son gauges relativos permitidos y conservan
A_Sigma y el salto J. El signo MENOS de Lambda es indispensable.

Por tanto, en el dominio seleccionado abajo, R y E_f inducen una biyección
entre datos de interfaz que cumplen dJ=0 y clases bulk bajo esos gauges.
Cada fibra sobre los datos de interfaz es un espacio afín de soluciones
con una sola clase relativa. Cambiar f o repartir J de otra forma entre
las dos caras cambia sólo el representante.

No se afirma que B particular pueda anularse: para J distinto de cero,
los parámetros -h B_eps tienen salto -hJ, no trazas comunes. Tampoco se
usa un epsilon de traza no nula para eliminar theta. La redundancia de
Lambda por d(rho_1), y la de rho_1 por d(sigma_0), obedecen a la misma
homotopía con trazas comunes; esto no construye BV/BFV.

## Dominio máximo y norma auxiliar BPS

Para definir L2 de formas se usa la métrica POSITIVA auxiliar

    g_aux=dr^2+Omega(r)^2(dt^2+dx1^2+dx2^2+dx3^2),
    0<Omega(r)<=1, Omega(0)=1.

No se la presenta como energía física Lorentziana. En una p-forma,
un coeficiente con k índices tangenciales tiene peso radial Omega^(4-2k).
La contracción por partial_t elimina un índice tangencial. Su peso después
de h es exactamente Omega^2/|s|^2 veces el anterior. En consecuencia

    ||h alpha||_L2 <= ||alpha||_L2/|s|,
    ||d h alpha||_L2 <= ||alpha||_L2+||d alpha||_L2/|s|.

La identidad de Cartan se extiende distribucionalmente. Por tanto h es
continuo en el dominio graph máximo D_max(d)={alpha en L2: d alpha en L2},
con el grado de forma correspondiente. Para campos cerrados, d(h alpha)=alpha.
Se permite el mismo dominio graph para los parámetros gauge relativos.
Si se exigiera a esos parámetros soporte compacto más estricto que el de
las soluciones, la unicidad sólo alcanzaría el subdominio compatible.

La biyección no exige que toda solución sea de soporte compacto. E_f sí
selecciona un representante con soporte radial compacto; el gauge que
relaciona una solución no compacta con él pertenece al graph máximo y no
tiene por qué tener soporte compacto. Esta distinción forma parte del
dominio seleccionado, no se deduce de la palabra «normalizable» de la carta.

## Traza débil y regularidad necesaria para E_f

Por fibra tangencial fija, alpha=alpha_T+dr wedge alpha_R cumple

    (d alpha)_radial=partial_r alpha_T-d_Sigma alpha_R.

En un collar UV compacto los pesos son equivalentes a los euclídeos y
d_Sigma es una matriz finita acotada. Para alpha en D_max(d), se deduce
alpha_T en H1 local radial y su traza UV existe. Coincide con la traza
definida por Green y conmuta con h y d_Sigma. No se necesita una traza del
coeficiente radial alpha_R para el pegado.

Para superposiciones tangenciales generales la traza natural de H(d) puede
ser una distribución, no una función L2. El levantamiento simple f(r)
NO prueba extensión L2 de toda esa clase débil. Seleccionamos datos con

    theta en L2 tangencial, d_Sigma theta en L2 tangencial,
    J en L2 tangencial y d_Sigma J=0 distribucionalmente.

Por una sola fibra son amplitudes finitas. Para paquetes son requisitos
adicionales de regularidad; las trazas comunes individuales de B pueden
seguir tratándose débilmente. Se comparan soluciones del graph máximo
cuyos datos de conexión y salto cumplen la regularidad anterior.

En cada cara las normas de la extensión son exactamente

    ||A_eps||^2 = [int f^2 Omega^2 dr] ||d_Sigma theta||^2
                   +[int (f')^2 Omega^4 dr] ||theta||^2,
    ||B_eps||^2 = 1/4 [int f^2 Omega^-2 dr] ||J||^2
                   +1/4 [int (f')^2 dr] ||hJ||^2.

No hay términos cruzados entre componentes radiales y tangenciales en la
norma auxiliar. Si m=min_[0,R] Omega>0, F0=int f^2 dr y F1=int(f')^2 dr,

    ||A_eps||^2 <= F0 ||d_Sigma theta||^2+F1 ||theta||^2,
    ||B_eps||^2 <= (m^-2 F0+F1/|s|^2) ||J||^2/4.

Son finitas. Como dA=dB=0, también pertenecen al graph de d. No se exige
una derivada tangencial adicional de J: la clausura convierte d(hJ) en J.
Estas constantes dependen del corte y no son una cota uniforme cuando
s tiende a cero. Para un contorno Re(s)>=sigma0>0, 1/|s|<=1/sigma0.

## Qué demuestra el certificado algebraico y qué queda condicionado

El verificador deriva las identidades exteriores en las 32 bases de formas
con coeficientes radiales variables, la extensión, incidencias, restricción
y homotopías relativas. Calcula los pesos de la norma por cada componente y
comprueba los factores de las estimaciones. La continuidad y la pertenencia
funcional utilizan las hipótesis explícitas de este lema; no proceden de un
contador finito de checks ni de los hashes de las fuentes.

No se afirma L2 en todo el tiempo para exp(s t), ni energía espacial finita
de una onda plana. El enunciado es por fibra Fourier-Laplace; paquetes físicos
requieren las integrabilidades tangenciales indicadas. Tampoco se cierra el
dominio graph de un operador distinto de d, una gauge-fixing adicional o
otras condiciones en el IR sin auditarlas.

Fuera de alcance: s=0, topología/holonomías globales, grandes gauges, fondos
A/B/phi no triviales, reconstrucción no lineal con corriente bulk material,
filas Einstein y moving completas, modos físicos, BRST/BV/BFV y promociones
N4/N7/P4/B4/B5. theta queda como dato de interfaz; A no se identifica con omega.
