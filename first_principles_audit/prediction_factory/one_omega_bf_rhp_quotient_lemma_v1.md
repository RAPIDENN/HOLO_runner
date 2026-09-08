# Lema del cociente BF lineal en el semiplano derecho

Estado: derivación algebraica escrita a mano; sin ejecución de un verificador
exterior y sin promoción de gates. Sólo el complejo BF lineal que se especifica
abajo. No es una certificación del espectro completo de la teoría.

## Acción y evidencia de origen

Se toma la acción candidata literal v5.2, no una acción BF antigua:

- `derive_one_omega_topological_so3_classical_v5_2_gate.py:239-276`:
  `S_BF = sum_eps int_Meps <B_eps wedge F[A_eps]>`,
  `<X,Y> = -tr_3(XY)/2`, y `D_A phi` en el cinético material.
- `:278-365`: dos semiespacios, interfaz `Sigma=R^(1,3)` sin borde,
  fibrados triviales, componente gauge nula homotópicamente y extendible;
  conexión transportada común, flujo B orientado y dominio de parámetros shift.
- `:292-317`: B es una **tres-forma** adjunta en cinco dimensiones;
  las iota son datos groupoid, no campos Euler independientes.
- `:640-741`: forma de Green y ecuaciones BF declaradas. Los controles de ese
  archivo comprueban incidencias finitas; no son por sí solos un complejo de
  formas ni un cálculo de su cohomología.

Identidad del artefacto leído:

`artifacts/one_omega_topological_so3_classical_v5_2_gate.json`

SHA256: `d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b`.

SHA256 de la fuente v5.2 leída:
`62096c08848044400c0f51ee126597db71b3dcf75e11aaddacbd0afad98a45e8`.

El antecedente v5.1 (`derive_one_omega_topological_so3_boundary_isomorphism_v5_1_gate.py:286-314`)
reduce sólo los representantes de las isomorfías mediante una matriz 6x9;
excluye explícitamente el complejo completo BF y A menos conexión del marco.
El antecedente Noether v5.5.1 (`derive_one_omega_topological_so3_bf_matter_gauge_noether_v5_5_1_gate.py:1-8,32-39,221-252`)
usa el mismo SHA v5.2, pero una reducción bidimensional periódica de la acción.
Su identidad gauge no sustituye el problema relativo de cinco dimensiones.
No se importa ni se ejecuta ninguno de esos antecedentes.

## Hipótesis precisas

Se linealiza alrededor de la solución considerada en los sectores auditados:
`Abar=Bbar=phibar=0`, con el fondo geométrico BPS fijo y aceleración de la
foliación de fondo nula. Se escribe `A=epsilon*alpha`, `B=epsilon*b`.
La conexión común de interfaz es independiente de la conexión Levi-Civita
inducida en el marco espacial; no se impone que coincidan.

El lema es por modo complejo `exp(s*t+i*q*x3)`, con `Re(s)>0` y `q` real.
Se trabaja con los coeficientes radiales del complejo Fourier-Laplace, no con
la afirmación de que la exponencial creciente sea un campo de energía finita
en todo el eje temporal. No se divide por q, por `s^2+q^2`, ni por una norma
lorentziana del momento.

El dominio admitido de soluciones y parámetros gauge debe ser estable bajo
la contracción `i_partial_t` y la multiplicación por `1/s`, debe tener trazas
UV que conmuten con esa operación y debe admitir los parámetros construidos
abajo. Una opción suficiente es usar coeficientes suaves con soporte radial
compacto y las mismas condiciones tangenciales de Fourier-Laplace en todas
las etapas del complejo. También sirven espacios de decaimiento radial cuya
compatibilidad con la contracción se haya fijado explícitamente.

La palabra «normalizable» de la carta no define por sí sola una norma para
formas de distinto grado y todos sus parámetros gauge. Si sólo se admiten
parámetros con soporte compacto más estricto que el de las soluciones, el
lema se restringe al subdominio estable indicado; no elimina automáticamente
las clases del dominio más amplio. Tampoco prueba una estimación uniforme
cuando `s` tiende a cero: la homotopía contiene `1/s`.

## Expansión y primera variación

Con la normalización de la carta, el coeficiente cuadrático BF es

    S_BF^(2) = sum_eps int_Meps <b_eps wedge d alpha_eps>.

El término no abeliano `B wedge A wedge A` empieza a orden tres. En el
material, `A*phi` empieza a orden dos dentro de P y a orden tres en P^2;
la corriente J4 de la ecuación de A es cuadrática en phi. Por tanto el
bloque BF de la Hessiana en este vacío no mezcla alpha o b con las
perturbaciones métricas, Omega ni phi. Esto es una afirmación a orden dos
en este fondo, no un desacoplamiento no lineal.

Como B tiene grado tres,

    B wedge D_A(delta A)
      = (D_A B) wedge delta A - d(B wedge delta A).

La variación completa BF es así

    delta S_BF = sum_eps int_Meps
                  (<delta B wedge F> + <delta A wedge D_A B>)
                - int_Sigma <(sum_eps s_eps*b_eps) wedge delta A_Sigma>,

con las incidencias de la carta `s_plus=+1`, `s_minus=-1`. Definiendo J4
por la variación material, las ecuaciones completas son `F=0` y
`D_A B+J4=0`; sus filas lineales en el vacío son

    d alpha_eps = 0,             d b_eps = 0.

Las condiciones de interfaz son

    alpha_plus|Sigma = alpha_minus|Sigma = alpha_Sigma
    b_plus|Sigma - b_minus|Sigma = 0

cuando las iota ya están representadas por la identidad. Para las trazas
adjuntas de b y sus parámetros se usa la misma identificación transportada.

No hace falta añadir un término local BF de interfaz para cancelar esta
forma de Green en el dominio declarado. La transformación shift cambia la
acción por `int_Sigma <(Lambda_plus-Lambda_minus) wedge F_Sigma>`; se anula
con los parámetros pegados que ya exige la carta, sin usar F=0. La forma
presimpléctica de interfaz también se cancela sobre tangentes que satisfacen
ambas condiciones de pegado. Esto no calcula cargas de esquinas temporales,
complejos BFV ni condiciones distintas de las declaradas.

## Homotopía exterior y signos

En cada lado sea

    d_s = dr wedge partial_r + s*dt wedge + i*q*dx3 wedge,
    h_s = i_partial_t / s.

Las otras derivadas tangenciales, si se conservan, anticommutan con la
contracción de la misma forma. La identidad de Cartan por modo da

    d_s h_s + h_s d_s = 1.

Para comprobar el signo sin una ecuación dinámica, se escribe cualquier
p-forma como `eta=dt wedge eta_t+eta_perp`, sin dt en sus dos coeficientes,
y `d_perp=dr wedge partial_r+i*q*dx3 wedge`. Entonces

    d_s eta = dt wedge (s*eta_perp-d_perp eta_t) + d_perp eta_perp,
    h_s eta = eta_t/s.

Los términos `d_perp eta_t/s` se cancelan en `d_s h_s eta+h_s d_s eta`.
La identidad vale también sobre cero-formas, donde `h_s=0` y
`h_s d_s f=f`. No usa la métrica ni una inversa de `d_s` radial.

Con la convención finita `A -> g A g^(-1) - (d g) g^(-1)`, la
transformación lineal es `delta alpha=-d_s epsilon_g`. Para una solución
cerrada se elige

    epsilon_g,eps = h_s alpha_eps,       grado 0,
    Lambda_eps = -h_s b_eps,             grado 2.

Entonces

    alpha_eps - d_s epsilon_g,eps = 0,
    b_eps + d_s Lambda_eps = 0.

El signo opuesto de los dos parámetros procede de sus distintas convenciones
gauge; las primitivas sin ese signo son simplemente `h_s alpha` y `h_s b`.
La prueba es idéntica para los tres generadores de so(3), pues los corchetes
con los campos de fondo nulos no contribuyen a la transformación lineal.

## Pegado, parámetros e iota

La inclusión UV es tangente a `partial_t`, por lo que el pullback conmuta
con h_s. Las trazas comunes de alpha y b dan parámetros comunes para los
gauges SO(3) y shift respectivamente. La construcción no integra desde el
IR ni añade una constante radial; conserva soporte radial y condiciones de
decaimiento expresadas en coeficientes dentro del dominio estable elegido.

También se puede incluir la perturbación de los representantes de iota sin
presuponer un gauge unitario. Sea `r_eps=1+chi_eps`; a primer orden,

    alpha_Sigma = alpha_eps|Sigma - d_Sigma chi_eps.

Defínanse `epsilon_Q=h_s alpha_Sigma` y `epsilon_eps=h_s alpha_eps`.
Como `h_s d_Sigma chi_eps=chi_eps`, se obtiene

    epsilon_eps|Sigma = epsilon_Q + chi_eps.

La acción groupoid `r_eps -> g_Q r_eps g_eps^(-1)` da

    delta chi_eps = epsilon_Q - epsilon_eps|Sigma = -chi_eps.

El mismo cambio gauge anula alpha en las dos caras, alpha_Sigma y los
representantes chi_eps. No se añade una ecuación Euler de iota: la carta
ya los declara datos de pegado modulo automorfismos. Los términos de
transporte `chi*b` y las contribuciones de movimiento `i_xi Fbar`,
`i_xi D_A Bbar` e `i_xi D_A phibar` se anulan a primer orden en este vacío.
Esto no elimina la variación geométrica del marco ni certifica el sistema
completo de embeddings.

## Reducibilidad y alcance del resultado

La cadena shift lineal tiene grados

    sigma_0 --d_s--> rho_1 --d_s--> Lambda_2 --d_s--> b_3.

Las redundancias `Lambda -> Lambda+d_s rho` y `rho -> rho+d_s sigma`
se tratan por la misma homotopía, con trazas compatibles en cada grado.
No es suficiente contar sólo los parámetros epsilon_g y Lambda sin esta
reducibilidad. En la teoría no abeliana `D_A^2=[F, .]`; esta identidad
lineal de complejos no construye el sistema BV fuera de F=0.

Resultado condicionado: el complejo relativo **de formas BF lineales**
(alpha, b y los representantes de iota) no tiene una clase de solución
no trivial por cada modo `Re(s)>0` en el dominio estable bajo h_s definido
arriba. No se identifica una obstrucción variacional que obligue a cambiar
la acción BF candidata para obtener este resultado restringido.

No se concluye que `A_Sigma - omega_frame` sea cero o esté eliminado. Fijar
`A_Sigma=0` también cambia el representante del marco bajo Aut(Q); la
conexión inducida en ese representante puede ser distinta de cero. El
acoplamiento de ese desajuste con la geometría y el resto del espacio de
configuraciones requiere un análisis adicional. El resultado anterior es
la aciclicidad del complejo BF especificado, no del cociente completo de
campos geométricos y materiales.

Quedan expresamente fuera:

- `s=0`, modos estáticos, holonomías, cohomología global y grandes gauges;
- otros fondos de conexión/materia, o una extensión no comprobada a dominios
  geométricos y condiciones al infinito distintos;
- existencia de un cociente global suave, causalidad y estimaciones uniformes
  de sus operadores, admisibilidad física de todos los modos;
- BV/BFV, ghosts, determinantes, cargas de esquina y cuantización;
- estabilidad escalar completa, embeddings/moving brane y toda promoción
  N2-N7, P4, B4 o B5.

El siguiente control acotado sería verificar con álgebra exterior exacta
`d_s^2=0`, `d_s h_s+h_s d_s=1` en todos los grados 0..5, los dos signos
gauge y el pegado de trazas, con mutantes de signo y con el caso excluido
`s=0`. No se ha ejecutado tal control en esta nota.
