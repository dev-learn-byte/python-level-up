"""Genera la misión diaria y el repaso, con variaciones reales.

La elección depende solo de la fecha (o de la semilla), así que es la misma
en la computadora y en el celular. Las respuestas no se guardan en ningún
sitio: se calculan ejecutando el código de la pregunta.
"""
import random
from datetime import date


def variantes(plantilla: dict) -> int:
    """Cuántas preguntas distintas puede producir una plantilla."""
    total = 1
    for valores in plantilla["valores"].values():
        total *= len(valores)
    return total


def mision_diaria(fecha: date, plantillas: list[dict], niveles_aprobados: set[int]) -> dict | None:
    """Devuelve la pregunta del día, o None si aún no hay niveles aprobados.

    Solo usa plantillas de niveles que el jugador ya aprobó.
    """
    disponibles = [p for p in plantillas if p["nivel"] in niveles_aprobados]
    if not disponibles:
        return None
    azar = random.Random(fecha.toordinal())
    plantilla = azar.choice(disponibles)
    codigo = plantilla["codigo"]
    for nombre, valores in sorted(plantilla["valores"].items()):
        codigo = codigo.replace(f"<<{nombre}>>", str(azar.choice(valores)))
    return {
        "familia": plantilla["familia"],
        "nivel": plantilla["nivel"],
        "texto": plantilla["texto"],
        "codigo": codigo,
        "mirar": plantilla["mirar"],
    }


def elegir_repaso(repaso: dict, semilla: int) -> list[dict]:
    """Elige las preguntas de un repaso. Cada intento de nivel usa otra semilla."""
    cantidad = repaso["preguntas_por_repaso"]
    return random.Random(semilla).sample(repaso["preguntas"], cantidad)
