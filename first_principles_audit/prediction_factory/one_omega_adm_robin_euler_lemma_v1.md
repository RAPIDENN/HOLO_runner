# Variación ADM no lineal de foliación y Robin, con sus corrientes

Esta nota fija las variables de variación y deriva las filas locales por
integración por partes (IBP). El verificador asociado reconstruye el álgebra
de la acción literal y usa jets independientes; no ajusta filas a una Hessiana.
No completa por sí solo la variación moving-brane de todo el modelo.

Fuente: `derive_one_omega_topological_so3_classical_v5_2_gate.py:264-275,690-714`,
acción candidata en `artifacts/one_omega_topological_so3_classical_v5_2_gate.json`,
SHA256 `d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b`.
El inventario `derive_one_omega_topological_so3_moving_interface_variational_completion_v5_6_7_8_gate.py:1951-1954`
(SHA256 `18eb511418017a86c05ba506d3c6dac7c13b10b39ebdad607d8143d9a2872acb`)
marca K/a/Robin, la fila shape y la fila groupoid como pendientes de una
derivación semántica. No se heredan sus gates ni su cobertura nominal.

## Variables y acción

Se trabaja en T=t con

    gamma = -N^2 dt^2 + h_ij (dx^i+N^i dt)(dx^j+N^j dt),
    K_ij = (partial_t h_ij - Lie_N h_ij)/(2N),
    a_i = D_i log N,
    F_K = K_ij K^ij - lambda K^2,
    C^ij = K^ij - lambda K h^ij,
    f(R) = xi R - B4_bar R^2/(16 k_inf^2).

    S_fol = (b/2) int N sqrt(h) [F_K + f(R) + eta a^2],  b=Mb^2.

Variables independientes ADM: **N, N^i contravariante y h_ij covariante**.
Las variaciones son n=delta N/N, Q_ij=delta h_ij y v^i=delta N^i.
En particular, delta N_i=h_ij v^j+N^j Q_ij; cambiar a N_i independiente
modifica la fila métrica mediante un adjunto proporcional a la fila shift.

Lie_N sobre `sqrt(h) C^ij` significa la derivada de Lie de una densidad
tensorial contravariante de **peso +1**:

    Lie_N pi^ij = N^k partial_k pi^ij - pi^kj partial_k N^i
                 - pi^ik partial_k N^j + pi^ij partial_k N^k.

La última contribución no puede omitirse. Las identidades tensoriales se
pueden comprobar en coordenadas normales espaciales en un punto, conservando
arbitrarios N, K, a, Ricci, shift y sus jets. Eso no fija un fondo plano,
N=1, shift=0, K=0 ni a=0.

## K: variación literal, filas y corriente

Usando delta h^ij=-Q^ij,

    delta K_ij = [(partial_t-Lie_N)Q_ij-D_i v_j-D_j v_i]/(2N)-n K_ij,

    delta F_K = 2 C^ij delta K_ij
                +[-2 K^i_k K^jk+2 lambda K K^ij] Q_ij.

La variación se escribe

    delta S_K = (b/2) int N sqrt(h) [E_n,K n + E_h,K^ij Q_ij
                                    +(2/N) D_j C^j_i v^i]
                + int partial_mu theta_K^mu,

    E_n,K = -F_K,
    E_h,K^ij = -(partial_t-Lie_N)(sqrt(h) C^ij)/(N sqrt(h))
               + h^ij F_K/2 - 2 K^i_k K^jk + 2 lambda K K^ij,

    theta_K^t = (b/2) sqrt(h) C^ij Q_ij,
    theta_K^i = -(b/2) sqrt(h) [N^i C^jk Q_jk+2 C^i_j v^j].

Así, la fila de delta N^i sin normalizar es b sqrt(h) D_j C^j_i.
La ecuación homogénea D_j C^ij=0 de v5.2 omite un prefactor común, no un
factor relativo. El verificador conserva el término completo y la corriente.

## Curvatura espacial y aceleración

La variación del escalar de Ricci se obtiene de la variación de Christoffel:

    delta Gamma^k_ij = (D_i Q_j^k+D_j Q_i^k-D^k Q_ij)/2,
    delta R = -R^ij Q_ij + D_i D_j Q^ij - D^2 Q,  Q=h^ij Q_ij.

Con F=N f_R y f_R=xi-B4_bar R/(8 k_inf^2), dos IBP dan

    E_n,f = f,
    E_shift,f = 0,
    E_h,f^ij = h^ij f/2 - f_R R^ij
               +(D^iD^j-h^ij D^2)(N f_R)/N,

    theta_f^i = (b/2) sqrt(h) [F(D_j Q^ij-D^i Q)
                                  -(D_j F)Q^ij+(D^i F)Q],
    theta_f^t = 0.

Los jets de Q de segundo orden se conservan ordenados; no se presupone que
sus derivadas covariantes conmuten. La simetría de Q basta para las
contracciones utilizadas. F es un escalar y sus segundas derivadas sí
conmutan. Los factores N dentro de las derivadas no se congelan.

Para a_i=D_i log N, delta a_i=D_i n:

    E_n,a = -eta(a^2+2 D_i a^i),
    E_shift,a = 0,
    E_h,a^ij = eta(h^ij a^2/2-a^i a^j),
    theta_a^i = b eta N sqrt(h) a^i n,    theta_a^t=0.

Sumando K,f,a se recuperan las filas S_fol de v5.2 bajo las convenciones
anteriores. Son correctas. La fórmula métrica impresa necesita explicitar
la densidad de peso +1 y la variable shift para no cambiar de ecuación.

## Robin en dos cartas de campos

Sea v^i=varphi_H^i, v_i=h_ij v^j, r_i=v_i-y a_i y

    S_R = -kappa/2 int N sqrt(h) h^ij r_i r_j.

Aquí v_i es un campo material; no es el símbolo v^i usado antes para la
variación del shift. En las fórmulas siguientes se escribe delta v_i
explícitamente para evitar confundirlos.

En la carta de **covectora material independiente** (N,h_ij,v_i):

    delta S_R = -kappa/2 int N sqrt(h) [r^2 n
                 +(h^ij r^2/2-r^i r^j)Q_ij
                 +2r^i delta v_i-2y r^i D_i n].

Es la identidad impresa en v5.2. Después de IBP,

    E_n,R = -kappa/2 [r^2+2y(D_i r^i+a_i r^i)],
    E_h,R,cov^ij = -kappa/2 [h^ij r^2/2-r^i r^j],
    E_v,R^i = -kappa r^i,       E_shift,R=0,
    theta_R^i = +kappa y N sqrt(h) r^i n,  theta_R^t=0.

La carta declarada en el modelo usa componentes internas phi_a y un marco
ortogonal dependiente de h. En la variación horizontal, a rotación de marco
compensada,

    v_i=e_i^a phi_a,
    delta v_i=e_i^a delta phi_a + Q_ij v^j/2.

Por tanto la fila métrica Robin **a phi_a fija** es

    E_h,R,hor^ij = -kappa/2 [h^ij r^2/2+y r^(i a^j)],
    E_phi,R,a = -kappa e_i^a r^i.

Los paréntesis denotan simetrización con factor 1/2. E_n,R y la corriente
no cambian en T=t. Para y=0, la norma de phi_a es independiente de h y sólo
queda la variación de volumen: es un control contra congelar la covectora
y llamarlo, incorrectamente, variación a phi interna fija.

## El adjunto debe aplicarse al Green material total

El punto de partida canónico es **-Pi_a delta phi_a**, porque los campos
bulk independientes son internos. Con v^i=e_a^i phi_a y frame horizontal,

    delta v^i=e_a^i delta phi_a-h^ik Q_kj v^j/2,
    delta phi_a=(e_inverse)_a_i [delta v^i+h^ik Q_kj v^j/2].

Por tanto las tres cartas dan el mismo Green, pero con diferentes filas:

    interno:    -Pi_a delta phi_a,
    vectorial:  -Pi_i delta v^i - Pi^(i v^j) Q_ij/2,
    covectorial:-Pi^i delta v_i + Pi^(i v^j) Q_ij/2.

La fila métrica bulk es respectivamente 0, -Pi^(i v^j)/2 y
+Pi^(i v^j)/2. No se puede empezar sólo por el sumando -Pi_i delta v^i:
el adjunto -Pi v Q/2 ya está presente al cambiar desde la carta interna.
Al regresar a componentes internas horizontales se cancela exactamente.

Si E_v,total^i=-Pi^i-kappa r^i y E_h,cov contiene ese adjunto bulk
**con factor 1/2**, la relación entre las filas TOTALES es

    E_h,int^ij = E_h,cov^ij + v^(i E_v,total^j)/2.

En la carta vectorial la relación es

    E_h,int^ij = E_h,vec^ij - v^(i E_v,total^j)/2,

con los índices de E_v adecuados a cada carta. No se impone E_v,total=0
para demostrarlas. Sólo sobre esa fila material nula coinciden las filas
métricas de distintas cartas. El estrés Robin no se sustituye de manera
aislada. Una rotación de marco compensada por delta phi=-rho phi deja
v invariante y no añade un campo físico.

La forma de Green escrita en v5.2 necesita esta precisión: si su
Delta varphi_H denota la variación vectorial ordinaria (incluida delta j),
el término -Pi_i Delta varphi_H^i debe acompañarse del adjunto métrico
- Pi^(i v^j)Q_ij/2 en la carta considerada. Alternativamente debe definirse
una variación horizontal compensada que ya represente e_a^i delta phi_a.
No basta conservar el símbolo Delta sin distinguir estas convenciones.
La derivación presente se limita a esa cadena ADM; no presupone resueltos
sus términos adicionales bajo desplazamiento normal o variación de T.

## Khronon y límites que permanecen

Para gamma fija, la definición literal u_mu=-N_T D_mu T da

    delta_T u_mu = -N_T h_mu^nu D_nu(delta T).

Si E_u^mu es la fila Euler TOTAL respecto a u_mu, **después** de las IBP
y de las cadenas de h, marco y material, entonces

    E_T = D_nu[N_T h^nu_mu E_u^mu],
    theta_T^nu = -sqrt(-gamma) N_T h^nu_mu E_u^mu delta T.

El signo de v5.2 es correcto. Nombrar E_u no equivale a haber expandido
esa fila a partir de todos los campos. La comprobación asociada verifica
la definición de u y el adjunto con su corriente; no afirma haber producido
la variación covariante completa de todos los embeddings y bulk.

Persisten para N4: ensamblar en una misma convención el Green completo
bulk+GHY+tensión+filas intrínsecas, su transgresión moving y sus bordes/corners;
transportar delta j y los momentos de ambas caras; comprobar las filas
normales y groupoid y las identidades de Noether fuera de ecuaciones. Las
corrientes de esta nota se conservan para ese ensamblado, aunque con soporte
compacto sus integrales de borde desaparezcan. No se infiere ausencia de
modos BF/marco, cierre BV/BFV, estabilidad global ni N4/N7/P4/B4/B5 completos.
