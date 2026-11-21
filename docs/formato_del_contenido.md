# Formato del contenido

Cómo se escribe una saga, un nivel o una misión. El motor (`nucleo/`) y el
evaluador (`evaluador/`) no cambian al añadir contenido.

## Estructura de una saga

```
contenido/sagas/<NN_nombre>/
├── saga.toml              id, numero, nombre
├── jefe.toml              el jefe final de la saga
└── nivel_<NN>_<tema>/
    ├── nivel.toml         numero, titulo, retos_evaluacion
    ├── teoria.md          tres partes obligatorias (ver abajo)
    ├── ejemplos.py        código que se puede ejecutar
    ├── repaso.toml        preguntas de niveles anteriores (opcional)
    └── misiones/*.toml    una misión por archivo, en orden alfabético
```

La teoría debe tener las secciones `## Para niños`,
`## Así lo dice un programador` y `## Errores típicos`.

## Una misión

| Campo | Significado |
|---|---|
| `id` | Identificador único en todo el juego |
| `titulo`, `anime` | Lo que se muestra. `Dragon Ball` o un anime especial |
| `formato` | `escribir`, `corregir`, `completar` o `predecir` |
| `dispositivo` | `celular` o `pc` |
| `xp`, `puntos` | 10 y 10 para Dragon Ball; 15 y 15 para misiones especiales |
| `enunciado` | Texto en Markdown |
| `plantilla` | El código inicial que recibe el alumno |
| `pistas` | Tres pistas, de la más general a la más concreta |
| `requiere` | Textos que deben aparecer en el código (opcional) |

### Misiones de código

La plantilla puede tener dos secciones:

```python
# === DATOS (no los cambies) ===
ataque = "kamehameha"

# === TU CÓDIGO ===
grito = ...
```

Cada `[[casos]]` ejecuta el código una vez. Si trae `datos`, esos valores
sustituyen a los de la sección DATOS; así una respuesta escrita a mano falla.

| Campo del caso | Comprueba |
|---|---|
| `datos` | Valores que sustituyen a los de la sección DATOS |
| `entradas` | Lo que se "escribe" en cada `input()` |
| `variables` | Valor y tipo exactos de cada variable |
| `tipos` | Solo el tipo de una variable |
| `clases` | Que la variable guarde un tipo, como el resultado de `type()` |
| `salida` | Las líneas impresas con `print()` |
| `pista` | Texto que acompaña al fallo |

Toda misión con sección DATOS debe tener al menos un caso con otros datos.

### Misiones de predicción

El alumno guarda sus respuestas en `respuesta_1`, `respuesta_2`... Cada
`[[preguntas]]` trae `codigo` y `mirar`. La respuesta correcta no se
escribe: se calcula ejecutando el código.

| `mirar` | Respuesta correcta |
|---|---|
| `"x"` | El valor final de la variable `x` |
| `"tipo:x"` | El nombre del tipo de `x`, como texto |
| `"salida"` | Lo que se imprime |

## El jefe

`jefe.toml` lleva además `transformacion`, los casos de `[[practica]]` y los
`[[requisitos]]`. Cada requisito se comprueba con todos los participantes:

| Campo | Comprueba |
|---|---|
| `entradas = n` | Se llama a `input()` exactamente n veces |
| `lineas = n` | Se imprimen exactamente n líneas |
| `linea = n` | La línea n coincide con la de la solución de referencia |

## Eventos y misión diaria

- `contenido/eventos/*.toml`: una misión con `requiere_nivel` y su recompensa.
- `contenido/diarias/plantillas.toml`: preguntas de predicción con huecos
  `<<a>>`, `<<b>>`... y la lista de valores posibles de cada hueco.

## Contenido privado

Cada misión con datos necesita al menos dos casos oficiales con datos que no
aparezcan en los casos públicos. Ver `contenido_privado.md`.

## Comprobación

`python -m pytest` valida todo el contenido: plantillas que no aprueban,
soluciones que sí, respuestas escritas a mano que fallan y conceptos que
todavía no se han enseñado.
