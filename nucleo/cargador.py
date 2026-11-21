"""Construye el catálogo de reglas leyendo las carpetas de `contenido/`.

Agregar una saga es agregar una carpeta: este módulo la encuentra sola y
las reglas no cambian.

Estructura que espera:

    contenido/
    ├── sagas/<NN_nombre>/
    │   ├── saga.toml              id, nombre
    │   ├── jefe.toml              (opcional) id, transformacion, requisitos...
    │   └── nivel_<NN>_<tema>/
    │       ├── nivel.toml         numero, titulo, retos_evaluacion
    │       └── misiones/*.toml    id, xp, puntos...
    └── eventos/*.toml             id, xp, puntos, requiere_nivel
"""
import tomllib
from pathlib import Path

from .catalogo import Catalogo, Evento, Jefe, Mision, Nivel
from .config import Config


def leer_toml(ruta: Path) -> dict:
    with open(ruta, "rb") as archivo:
        return tomllib.load(archivo)


def carpetas_de_sagas(raiz: Path) -> list[Path]:
    return sorted(c for c in (raiz / "sagas").iterdir() if (c / "saga.toml").exists())


def carpetas_de_niveles(saga: Path) -> list[Path]:
    return sorted(c for c in saga.iterdir() if (c / "nivel.toml").exists())


def archivos_de_misiones(nivel: Path) -> list[Path]:
    return sorted((nivel / "misiones").glob("*.toml"))


def archivos_de_eventos(raiz: Path) -> list[Path]:
    return sorted((raiz / "eventos").glob("*.toml"))


def cargar_catalogo(raiz: str | Path, config: Config | None = None) -> Catalogo:
    """Lee `contenido/` y devuelve el catálogo que usan las reglas."""
    raiz = Path(raiz)
    niveles, jefes = [], []
    sagas = carpetas_de_sagas(raiz)
    for posicion, carpeta in enumerate(sagas):
        saga = leer_toml(carpeta / "saga.toml")
        for carpeta_nivel in carpetas_de_niveles(carpeta):
            datos = leer_toml(carpeta_nivel / "nivel.toml")
            misiones = tuple(
                Mision(m["id"], m["xp"], m["puntos"])
                for m in map(leer_toml, archivos_de_misiones(carpeta_nivel))
            )
            niveles.append(Nivel(
                numero=datos["numero"], saga=saga["id"], misiones=misiones,
                retos_evaluacion=datos.get("retos_evaluacion", 10),
            ))
        if (carpeta / "jefe.toml").exists():
            jefe = leer_toml(carpeta / "jefe.toml")
            jefes.append(Jefe(
                saga=saga["id"], transformacion=jefe["transformacion"],
                requisitos=len(jefe["requisitos"]), xp=jefe["xp"], puntos=jefe["puntos"],
                final=jefe.get("final", False),
            ))
    eventos = [
        Evento(e["id"], e["xp"], e["puntos"], e.get("requiere_nivel", 0))
        for e in map(leer_toml, archivos_de_eventos(raiz))
    ]
    niveles.sort(key=lambda nivel: nivel.numero)
    return Catalogo(niveles, jefes, eventos, config)
