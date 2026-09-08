# Reducción lineal directa a momento espacial cero

Estado: identidad simbólica comprobada en una sola ejecución acotada del
modelo completo, sin suite global ni recibo nuevo. Se conserva el dominio
lineal de frontera y la rama DtN regular seleccionada. No es un conteo de
todos los grados físicos de la teoría ni una promoción N7/P4.

## Fuente y dominio

La única matriz utilizada para la reducción fue `H_full` de
`verify_one_omega_topological_boundary_assembly_v1.py:60-107`, derivada
fresca con `derive_model()`. No se sustituyó q=0 en la carta escalar que
requiere q distinto de cero.

SHA256 de la fuente de ensamblado leída:
`13f366199e5166e35cb5112ca02d6fbd8e2e0a99e99a01e559eec3629972847a`.

Recibo de ensamblado identificado:
`artifacts/one_omega_topological_boundary_assembly_v1.json`, SHA256
`c3c93cd779fe684329419012202d2cf697aee926efe5efbaee1cb0e47f781bce`.
La ejecución de esta nota no volvió a verificar ese recibo: comparó el
modelo simbólico derivado de la fuente indicada.

La acción candidata vinculada por el ensamblado es la v5.2, artefacto
`artifacts/one_omega_topological_so3_classical_v5_2_gate.json`, SHA256
`d9d12e8bffb98b48c92476515f2a06cf582c4c072fedfe671949c2977208306b`.
Sus coeficientes decimales se mantienen literales; lambda_K no se sustituye
por una igualdad exponencial pretendidamente exacta.

Se fija `q=0`, `frequency=w=i*s`, `Re(s)>0`. Por tanto el cuadrado del
momento lorentziano utilizado por los proyectores es `q^2-w^2=s^2 != 0`.
Esta evaluación sí pertenece al dominio del ensamblado completo. No
establece una extensión a `s=0`, al cono nulo o a condiciones IR distintas.

Notación:

    M = M5c > 0,           b = Mb2 = M_b^2 > 0,
    k_b = k_inf*exp[-G/(6*M)],      A'_UV = -k_b,
    C0 = M/k_b,
    Bstar = b*(1-3*lambda_K)-2*C0,
    F_T = b*s^2 + M*K_T,
    P_D = G*K_v+beta,
    P_chi = kappa_hat+2*Z5*p_material.

En q=0, la raíz material seleccionada por `Re(p_material)>0` es
`p_material=s`. Los núcleos K_T y K_v son las respuestas completas, no
sus expansiones IR ni valores ajustados.

## Las cinco direcciones nulas y el papel del khronon

Las cinco filas y columnas de `n,N1,N2,N3,tau` se anulan exactamente en
`H_full(q=0,w=i*s)`. Los vectores gauge del ensamblado se reducen a

    g_time = s*e_n + e_tau,
    g_space_i = s*e_Ni,          i=1,2,3.

Además, a momento espacial cero la simetría declarada `T -> f(T)` permite
la perturbación temporal homogénea `g_T=e_tau` alrededor de `T=t`.
Junto con los cuatro vectores anteriores, el menor en las cinco filas
citadas tiene determinante `s^4`, que no se anula en RHP.

Así se obtienen por combinaciones regulares

    e_n = (g_time-g_T)/s,      e_Ni = g_space_i/s,      e_tau = g_T.

Se puede eliminar el lapse manteniendo tau=0 combinando la difeomorfía
temporal con esa reparametrización de T. No aparece una ecuación dinámica
de lapse perdida: su fila es nula en la matriz completa evaluada en este
sector. La justificación es infinitesimal por modo Fourier-Laplace; no
construye una transformación finita globalmente monótona en todo el tiempo.

En q=0 las difeomorfías espaciales no modifican H_ij: su acción sobre esas
componentes lleva una derivada espacial. Por eso no puede imponerse una
métrica espacial isotrópica como si todavía fuese una condición gauge
espacial. Las cinco componentes sin traza deben conservarse.

## Separación SO(3) de la matriz completa

Escríbase la perturbación espacial simétrica como

    H_ij = 2*zeta*delta_ij + sum_A t_A*(E_A)_ij,

con cinco matrices simétricas sin traza ortonormales por Frobenius:

    E1 = diag(1,-1,0)/sqrt(2),
    E2 = diag(1,1,-2)/sqrt(6),
    E3 = (e12+e21)/sqrt(2),
    E4 = (e13+e31)/sqrt(2),
    E5 = (e23+e32)/sqrt(2).

Entonces `tr(E_A E_B)=delta_AB` y el proyector completo da
`Z=tr(H_ij)/6=zeta`. Las cinco t_A forman la representación espacial
simétrica sin traza de SO(3); no se importan los nombres de helicidad de
la carta q distinto de cero. El triplete material phi_i permanece aparte.

En el orden

    (n,N1,N2,N3,tau ; t1,t2,t3,t4,t5 ; zeta,D ; phi1,phi2,phi3),

el cambio de base S, construido directamente en los quince campos originales,
tiene determinante `sqrt(6)/2`. Se comprobó que sus 225 entradas satisfacen

    S^T H_full(q=0,w=i*s) S
      = diag( 0_5,  -(F_T/4)*I_5,  H_zetaD,  -P_chi*I_3 ),

    H_zetaD = [ -3*Bstar*s^2-G*K_v,       G*K_v     ]
              [        G*K_v,          -G*K_v-beta ].

No quedan cruces entre esos bloques. El factor 1/4 del bloque t_A corresponde
a la base Frobenius elegida. Si se usa directamente h12=H12=H21 como
amplitud independiente, `t3=sqrt(2)*h12` y su entrada Hessiana es `-F_T/2`,
en acuerdo con la normalización TT ya auditada.

Esta descomposición también se comprueba a mano en la densidad local:

    L_fol^(2)(q=0) = -b*s^2/8 * [tr(H^2)-lambda_K*(tr H)^2].

El bloque bulk TT añade `-M*K_T*tr(H_TT^2)/8`; el contacto escalar aporta
`+3*C0*s^2*zeta^2`, y la carga escalar exacta y Robin aportan
`-G*K_v*(zeta-D)^2/2-beta*D^2/2`. No se añade un segundo término EH4.
Los gradientes espaciales y la aceleración lineal se anulan en q=0,
por lo que xi, eta, B4_bar y el acoplamiento Robin y no alteran esta matriz.

## Schur escalar y ausencia condicionada de ceros RHP

El pivote D es `-P_D`. En la rama de energía finita y flujo IR final nulo,
la identidad de Green previamente establecida proporciona

    Re(K_T/s)>0,       Re(G*K_v/s)>0       cuando Re(s)>0.

La existencia y el dominio seleccionados de esos núcleos son hipótesis
vinculadas al lema variacional anterior, no una conclusión nueva de esta
manipulación de matrices. Véanse `one_omega_variational_dtn_lemma_v1.md`
y `verify_one_omega_variational_dtn_v1.py`.

El pivote no se anula porque

    Re(P_D/s) = Re(G*K_v/s) + beta*Re(1/s) > 0.

Su eliminación deja exactamente

    S_zeta = -3*Bstar*s^2 - Delta_beta,
    Delta_beta = beta*G*K_v/(beta+G*K_v).

No se ha dividido por q ni por una entrada dinámica sin certificar su
pivote. Para comprobar el signo de la carga completa, sea

    z = G*K_v/s = x+i*y,      x>0,
    s = sigma+i*tau,          sigma>0.

Entonces

    Delta_beta/s = beta*z/(beta+s*z) = 1/(1/z+s/beta),

    Re(Delta_beta/s)
      = beta*[beta*x+sigma*(x^2+y^2)]
        / [(beta+sigma*x-tau*y)^2+(sigma*y+tau*x)^2] > 0.

La última identidad se comprobó simbólicamente en variables reales. En
particular, si `Bstar>0`,

    Re(-S_zeta/s) = 3*Bstar*sigma + Re(Delta_beta/s) > 0.

Por tanto S_zeta no se anula en RHP. También

    Re(F_T/s) = b*sigma + M*Re(K_T/s) > 0,
    Re(P_chi) = kappa_hat + 2*Z5*sigma > 0.

Los cinco componentes sin traza y los tres materiales tampoco adquieren
ceros de sus denominadores en ese dominio. El bloque no gauge tiene rango
diez cuando se cumplen estas hipótesis. Esto es una afirmación algebraica
sobre la respuesta de frontera seleccionada, no sobre diez partículas ni
sobre la positividad del Hamiltoniano completo.

## Coeficientes de la candidata y validación realizada

Para los valores literales `M=k_inf=1`, `G=6/5`, `b=2` y
`lambda_K=-0.5535068954004245`,

    Bstar = 2*(1-3*(-0.5535068954004245))-2*exp(1/5)
          = 2.878235856082207332157856... > 0.

La positividad no depende del redondeo de esa evaluación: lambda_K es
menor que -1/2 y `exp(1/5)<1/(1-1/5)=5/4`, de modo que `Bstar>5/2`.
No se ha convertido el decimal de lambda_K en una fórmula exacta de C0.

La única ejecución SymPy duró 2.427 s tras la importación, en un proceso
con BLAS/OMP limitados a un hilo. Se comprobaron las 225 entradas del
cambio de base, las cinco filas nulas, la ortonormalidad de las cinco
matrices, la invertibilidad de S, el menor gauge `s^4`, Z a q=0, el Schur
y la identidad real de Delta_beta/s. No se ejecutó una suite global ni
se generó un artefacto de recibo.

Permanecen fuera el límite estático `s=0`, la extensión uniforme hacia el
eje imaginario, otras condiciones IR, los embeddings independientes, el
sistema BF/marco completo y la estabilidad no lineal. El lema BF RHP se
mantiene separado hasta cotejar los dominios de todas las reducciones.
N7/P4/B4/B5 no se promueven por esta nota.
