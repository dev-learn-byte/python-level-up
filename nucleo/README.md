# nucleo

Motor de reglas en Python puro, sin dependencias. Es la única copia de las
reglas; el servidor la usa como autoridad. Las reglas están explicadas en
`docs/reglas.md`.

| Módulo | Contenido |
|---|---|
| `config.py` | Todos los números del juego |
| `catalogo.py` | Niveles, misiones, jefes y eventos que existen |
| `cargador.py` | Construye el catálogo leyendo las carpetas de `contenido/` |
| `estado.py` | El progreso del jugador y su guardado en JSON |
| `progresion.py` | Entregas, evaluaciones y jefes |
| `economia.py` | XP, puntos, recompensas únicas y tienda |
| `saltos.py` | Saltos de nivel y penalización |
| `extras.py` | Misión diaria y eventos |
| `acciones.py` | Entrada del servidor: `aplicar(estado, catalogo, accion)` |
| `consultas.py` | Preguntas que no modifican el progreso |
| `resultado.py` | Qué pasó en una acción |

Cada acción recibe un estado y devuelve `(estado_nuevo, resultado)` sin
modificar el original. Si la regla no lo permite, lanza `AccionInvalida`.
