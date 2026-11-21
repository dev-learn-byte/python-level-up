# Python Level Up

Aprender Python de cero a avanzado como una aventura RPG, inspirada
principalmente en Dragon Ball y con misiones especiales de otros animes.
Aplicación web responsive para estudiar desde la computadora o el celular.

## Estado

| Etapa | Contenido | Estado |
|---|---|---|
| 0. Preparación | Rama y estructura de carpetas | Hecha |
| 1. Núcleo | Reglas: vidas, XP, puntos, saltos y penalizaciones | Hecha |
| 2. Saga 1 | Entrenamiento de Goku: 3 niveles, jefe final y mazmorra | Hecha |
| 2.5 Versión local | Jugar la Saga 1 desde la consola (provisional) | Hecha |
| 3. Servidor | API, base de datos y acceso | Pendiente |
| 4. Web | Interfaz para PC y celular | Pendiente |
| 5. Publicación | Alojamiento y prueba desde el celular | Pendiente |

## Carpetas

| Carpeta | Para qué sirve |
|---|---|
| `nucleo/` | Motor de reglas en Python puro |
| `evaluador/` | Ejecuta los ejercicios, comprueba el resultado y explica los errores |
| `contenido/` | Teoría, ejemplos, misiones y pistas |
| `local/` y `jugar.py` | Versión local para la consola |
| `servidor/` | API con FastAPI |
| `web/` | Interfaz en JavaScript |
| `pruebas/` | Pruebas automáticas (`python -m pytest`) |
| `docs/` | Documentación |

## Jugar ahora

La Saga 1 se puede jugar en la consola. Las instrucciones para Windows
están en `docs/version_local.md`.

```
py jugar.py ayuda
```

Las soluciones de referencia y las evaluaciones no están en este
repositorio. Ver `docs/contenido_privado.md`.
