"""Evaluador de ejercicios de Python Level Up (Python puro, sin dependencias).

Decide si un ejercicio está bien resuelto ejecutándolo con datos distintos
y explica los errores con palabras sencillas. No aplica reglas del juego:
eso lo hace `nucleo`.
"""
from .comprobaciones import (
    Informe, ResultadoCaso, evaluar_codigo, evaluar_jefe, evaluar_prediccion,
    evaluar_reto, iguales, valor_mirado,
)
from .ejecucion import MARCA_CODIGO, Ejecucion, ejecutar
from .errores import ErrorAlumno

__all__ = [
    "MARCA_CODIGO", "Ejecucion", "ErrorAlumno", "Informe", "ResultadoCaso",
    "ejecutar", "evaluar_codigo", "evaluar_jefe", "evaluar_prediccion",
    "evaluar_reto", "iguales", "valor_mirado",
]
