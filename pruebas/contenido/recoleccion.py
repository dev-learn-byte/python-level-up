"""Reúne el contenido público y, si está disponible, el privado."""
from pathlib import Path

from evaluador.contenido import PUBLICO, ruta_privada
from nucleo.cargador import (
    archivos_de_eventos, archivos_de_misiones, carpetas_de_niveles,
    carpetas_de_sagas, leer_toml,
)

PRIVADO = ruta_privada()


def niveles() -> list[Path]:
    return [n for saga in carpetas_de_sagas(PUBLICO) for n in carpetas_de_niveles(saga)]


def sagas() -> list[Path]:
    return carpetas_de_sagas(PUBLICO)


def misiones() -> list[tuple[Path, dict]]:
    """(carpeta del nivel, misión) de todas las misiones."""
    return [(n, leer_toml(a)) for n in niveles() for a in archivos_de_misiones(n)]


def eventos() -> list[dict]:
    return [leer_toml(a) for a in archivos_de_eventos(PUBLICO)]


def espejo(ruta: Path) -> Path:
    """La ruta equivalente dentro del contenido privado."""
    return PRIVADO / ruta.relative_to(PUBLICO)


def soluciones(nivel: Path) -> dict:
    return leer_toml(espejo(nivel) / "soluciones.toml")


def evaluaciones() -> list[tuple[str, dict, dict]]:
    """(nombre, datos del nivel, evaluación) de cada versión de cada nivel."""
    resultado = []
    for nivel in niveles():
        for version in ("A", "B"):
            archivo = espejo(nivel) / f"evaluacion_{version}.toml"
            resultado.append((f"{nivel.name}-{version}", leer_toml(nivel / "nivel.toml"), leer_toml(archivo)))
    return resultado


def retos() -> list[tuple[str, dict]]:
    return [
        (f"{nombre}-reto{numero}", reto)
        for nombre, _, evaluacion in evaluaciones()
        for numero, reto in enumerate(evaluacion["retos"], start=1)
    ]
