# evaluador

Decide si un ejercicio está bien resuelto. Python puro, sin dependencias,
para poder ejecutarse igual en el servidor y en el navegador.

| Módulo | Contenido |
|---|---|
| `ejecucion.py` | Ejecuta el código con datos y teclado simulados |
| `comprobaciones.py` | Compara el resultado con lo esperado, caso por caso |
| `errores.py` | Explica los errores de Python con palabras sencillas |
| `contenido.py` | Une el contenido público con el privado: practicar y entregar |
| `diaria.py` | Genera la misión diaria y elige las preguntas de repaso |

Se evalúa por comportamiento: se ejecuta el código y se mira qué variables
quedaron y qué se imprimió. Cualquier solución que funcione es válida.

Este paquete no aísla el código: lo ejecuta en el mismo proceso. El
aislamiento se añade alrededor en las etapas 3 (servidor) y 4 (navegador).
Tampoco aplica reglas del juego: eso lo hace `nucleo/`.
