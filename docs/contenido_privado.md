# Contenido privado (soluciones y evaluaciones)

Este repositorio es público, así que aquí solo hay teoría, ejemplos,
enunciados, plantillas, pistas y comprobaciones de práctica. Lo que revela
respuestas vive en el repositorio privado `python-level-up-privado`.

## Qué contiene el repositorio privado

Repite las rutas de `contenido/`:

```
python-level-up-privado/
├── sagas/01_entrenamiento_goku/
│   ├── jefe.toml                    solución y participantes del combate oficial
│   └── nivel_01_variables/
│       ├── soluciones.toml          solución y casos oficiales de cada misión
│       ├── evaluacion_A.toml        diez retos
│       └── evaluacion_B.toml        la misma estructura con otros datos
└── eventos/soluciones.toml
```

## Cómo se conecta

El código lo busca en la carpeta que indique la variable de entorno
`PLU_CONTENIDO_PRIVADO`. Si no está definida, en `contenido_privado/` dentro
de este repositorio.

```
git clone https://github.com/dev-learn-byte/python-level-up-privado contenido_privado
```

Sin el contenido privado todo sigue funcionando en modo práctica, y las
pruebas que lo necesitan se omiten solas.

## Protecciones contra fugas

| Protección | Qué hace |
|---|---|
| `.gitignore` | Git ignora `contenido_privado`, así que no se sube aunque se añada todo |
| Marca de privado | Todo archivo privado empieza con una línea de marca |
| `pruebas/test_fugas.py` | Falla si un archivo publicado lleva la marca, tiene nombre de archivo privado o contiene soluciones o retos de evaluación |

## Qué llega al navegador

- Siempre: teoría, enunciado, plantilla, pistas y comprobaciones de práctica.
- Solo durante una evaluación: el enunciado y la plantilla de cada reto.
- Nunca: las soluciones de referencia.
