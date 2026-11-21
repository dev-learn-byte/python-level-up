# local

Versión provisional para la consola. Instrucciones de uso en
`docs/version_local.md`.

| Módulo | Contenido |
|---|---|
| `consola.py` | Las órdenes de `jugar.py`: solo muestra, no decide nada |
| `partida.py` | Coordina archivos, evaluación, núcleo y guardado |
| `aislado.py` | Lanza cada evaluación en un proceso aparte con límite de tiempo |
| `trabajador.py` | El proceso hijo que ejecuta la evaluación |

No contiene reglas del juego: las aplica `nucleo/`. No juzga ejercicios: lo
hace `evaluador/`. El proceso aparte no es un sandbox; ver las restricciones
en `docs/version_local.md`.
