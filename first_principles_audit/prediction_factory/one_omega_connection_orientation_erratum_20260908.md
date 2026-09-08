# Corrección de la incidencia BF y sus fuentes

La auditoría conjunta del 8 de septiembre encontró un error de signo en
la unión de la nueva corriente con BF. La acción congelada v5.2 y sus
bytes históricos se conservan. Lo que se corrige es la derivación de su
Green orientado y los paquetes de la extensión que habían heredado ese
signo textual sin contrastarlo con una corriente de interfaz no nula.

## Derivación desde la acción literal

Para S_BF=+sum integral <B3 wedge F> y las convenciones
vol5=dn wedge volSigma, Mplus={n>=0}, Mminus={n<=0},

    delta(B wedge F)=delta B wedge F+(DB) wedge delta A
                     -d(B wedge delta A).

Los normales exteriores en la interfaz son -partial_n y +partial_n;
sus orientaciones inducidas son -volSigma y +volSigma. Por ello el
borde total es +[b] wedge delta A, donde b es el pullback transportado
Trans_iota(B)=Ad_r(Y*B), sin signo de incidencia oculto en su definición.
El caso de prueba anterior bplus=bminus no podía distinguir +[b] de
-[b]. Una prueba basada sólo en ese caso no certificaba el signo.

Un oráculo independiente toma B=b(n) dx wedge dy wedge dz y
delta A=a(n)dt. El integrando es b a_prime vol5. Su integral por partes
en las dos mitades tiene borde común -(bplus-bminus)a volSigma.
Eso es precisamente +[b_form] wedge delta A, porque el intercambio de
una 3-forma y una 1-forma lleva signo menos.

La variación de S_C=-chi/2 integral <C wedge *C> aporta
+J_Sigma wedge delta A, con J_Sigma=chi*C. En consecuencia,

    [b]=-J_Sigma,
    DB+J4=0  =>  DJ_Sigma=[j4].

Invertir la orientación común de forma coherente cambia también la
identificación de [j4] con la corriente normal material; no permite
conservar sólo el signo favorable de una de estas filas.

## Segundo contraste y alcance de la corrección

En el puerto estático, rho=[j4]/volSigma=+kappa*y*(a cross phi).
Con A=-d exp(epsilon²Theta) exp(-epsilon²Theta), la materia on shell
aporta +rho deltaTheta a la variación reducida, y S_C aporta
+chi DeltaTheta deltaTheta. La compatibilidad correcta es entonces

    chi DeltaTheta=-rho,
    Theta_hat=+rho_hat/(chi|xi|²).

El signo anterior dejaba 2rho. Dado el testigo localizado estrictamente
no nulo, esto era un fallo real de la reconstrucción anterior, no una
diferencia de notación que pudiera ignorarse. La existencia, regularidad
y las cotas de energía sobreviven al invertir coherentemente Theta.

El levantamiento afín sin fuente usa ahora Bplus=-d(fhJ)/2 y
Bminus=+d(fhJ)/2. En el problema estático con fuente, Bpart=-hJ4 se
mantiene: su salto es -J_Sigma. La solución de Poisson tiene ahora
J_Sigma=+h[j4]; el resto cerrado es J_Sigma-h[j4]. Las normas y los
dominios auxiliares no cambian.

La primera variación covariante de S_C, su identidad de Ward, el H18
homogéneo y su forma cinética ADM no cambian de fórmula por esta
corrección. Sus vínculos a fuentes sí se regeneran. En el puerto, la
reacción métrica satisface div tau_C^(2)=-curl rho/2; su norma es
||tau_C^(2)||²=||rho||²/2, independiente de chi.

Los recibos antiguos de corriente, torque, BF afín y BF estático son
históricos y quedan sustituidos por los recibos corregidos que vincula
el índice vigente. No se presenta el recuento de pruebas previo como
validación de este signo. Las pruebas nuevas incluyen la derivación
Stokes, un contraste por acción reducida y mutaciones con el signo viejo.
La corrección no modifica la obstrucción original con J_Sigma=0 ni
promueve ningún gate general o una solución Einstein completa.
