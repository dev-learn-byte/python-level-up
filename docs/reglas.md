# Reglas del juego

Estas son las reglas que aplica `nucleo/`. Todos los números están en
`nucleo/config.py` y cada regla tiene pruebas en `pruebas/nucleo/`.

## Niveles

| Estado | Significado |
|---|---|
| Bloqueado | Aún no se puede entrar |
| Desbloqueado | Se puede entrar, pero no se ha empezado |
| Actual | El nivel que se está cursando |
| Aprobado | Evaluación superada |
| Pendiente | Saltado con puntos; hay que completarlo antes del jefe final |

- Aprobar un nivel desbloquea el siguiente de la misma saga.
- El último nivel de una saga no abre la saga siguiente: hay que vencer al jefe.
- Solo se juegan niveles en estado actual o pendiente.

## Vidas

- Cada nivel empieza con 5 vidas. Practicar no cuesta nada.
- Entrega final de una misión que falla: 1 vida.
- Evaluación: 1 vida por cada reto fallado.
- Con 0 vidas el nivel se reinicia: las misiones vuelven a estar sin
  entregar y las vidas vuelven a 5. Los XP y los puntos se conservan.
- Recuperar vidas (máximo 5): Semilla del Ermitaño (50 puntos) y repaso
  perfecto, cada uno una vez por intento de nivel.

## Evaluaciones

- Exigen haber entregado todas las misiones del nivel.
- Se aprueban con 70 % o más de aciertos y al menos 1 vida.
- Reprobar con vidas restantes repite solo la evaluación, en la otra versión.

## XP y puntos

| Acción | XP | Puntos |
|---|---|---|
| Misión | 10 | 10 |
| Evaluación aprobada | 50 | 30, más 5 por vida restante |
| Jefe de saga | 150 | 100 |
| Evento o mazmorra | 40 | 50 |
| Misión diaria | 5 | 15 |
| Tres misiones nuevas seguidas | — | 10 |
| Salto superado | 100 | — |

- Los XP nunca se pierden.
- Cada misión, evaluación, jefe y evento paga solo la primera vez.
- Los puntos se gastan en saltos (100 por nivel), semillas (50) y pistas (10).

## Jefes

- Disponibles cuando todos los niveles de su saga están aprobados.
- 5 vidas propias. Una entrega con requisitos sin cumplir cuesta 1 vida.
- Con 0 vidas se repite solo el jefe.
- Vencerlo da la transformación y abre la saga siguiente.
- El jefe final exige todos los niveles aprobados y los demás jefes vencidos.

## Saltos de nivel

- Requisitos: sin penalización, niveles anteriores al actual aprobados,
  destino bloqueado, como máximo 5 niveles y puntos suficientes.
- Los puntos se descuentan al empezar el examen. Mientras dura, no se
  admite ninguna otra acción.
- El examen tiene 2 retos por nivel de distancia, un único intento y se
  supera con 80 %. No usa vidas.
- Si se supera: el destino pasa a ser el nivel actual y los niveles
  intermedios quedan pendientes (también el actual, si no estaba aprobado).
- Si se fracasa: se pierden los puntos, no cambia el nivel y se activa la
  penalización.

## Penalización

- Bloquea los saltos hasta ganar en puntos nuevos el doble de lo invertido.
- Los puntos que ya se tenían no cuentan. Gastar puntos no reduce lo ganado.
- Mientras tanto se puede estudiar, ganar XP y puntos y comprar en la tienda.
- Se levanta sola al alcanzar la meta y queda en el historial.

## Misión diaria y eventos

- Diaria: una recompensa por día. Fallarla no cuesta nada y perder un día
  solo reinicia la racha.
- Eventos: fallarlos no cuesta vidas.

## Qué decide el servidor

El navegador envía qué hizo el jugador, nunca cantidades. Una acción con
campos como `puntos`, `xp` o `vidas` se rechaza. Cada acción lleva un
identificador y, si llega repetida, no se aplica dos veces.
