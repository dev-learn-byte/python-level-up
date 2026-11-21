"""Une el contenido público con el privado para evaluar misiones y jefes.

El contenido privado (soluciones y pruebas oficiales) vive en otro
repositorio. Se busca en la carpeta que indique la variable de entorno
`PLU_CONTENIDO_PRIVADO` o, si no existe, en `contenido_privado/`. Si no
está, solo se pueden hacer las comprobaciones de práctica.
"""
import os
from pathlib import Path

from .comprobaciones import Informe, evaluar_codigo, evaluar_jefe, evaluar_prediccion

RAIZ = Path(__file__).parent.parent
PUBLICO = RAIZ / "contenido"


def ruta_privada() -> Path | None:
    """Carpeta del contenido privado, o None si no está disponible."""
    ruta = Path(os.environ.get("PLU_CONTENIDO_PRIVADO", RAIZ / "contenido_privado"))
    return ruta if (ruta / "sagas").is_dir() else None


def practicar_mision(mision: dict, codigo: str) -> Informe:
    """Comprobación de práctica: usa solo lo que es público."""
    if mision["formato"] == "predecir":
        return evaluar_prediccion(codigo, mision["preguntas"])
    return evaluar_codigo(codigo, mision["casos"], requiere=mision.get("requiere", ()))


class EntregaOficialNoDisponible(Exception):
    """Falta el contenido privado: no se puede juzgar una entrega oficial."""


def entregar_mision(mision: dict, codigo: str, privado: dict | None) -> Informe:
    """Entrega final: práctica más los casos oficiales, que usan otros datos.

    `privado` es la entrada de esta misión en `soluciones.toml`. Sin ella la
    entrega se rechaza: una entrega oficial nunca se juzga solo con la práctica.
    """
    if not privado or "solucion" not in privado:
        raise EntregaOficialNoDisponible(mision["id"])
    con_datos = "# === DATOS" in mision["plantilla"]
    if con_datos and not privado.get("casos"):
        raise EntregaOficialNoDisponible(mision["id"])
    informe = practicar_mision(mision, codigo)
    if mision["formato"] == "predecir" or not privado.get("casos"):
        return informe
    oficial = evaluar_codigo(
        codigo, privado["casos"], referencia=privado["solucion"],
        requiere=mision.get("requiere", ()), mostrar_esperado=False,
    )
    for numero, caso in enumerate(oficial.casos, start=1):
        caso.nombre = f"Prueba oficial {numero}"
    return Informe(informe.casos + oficial.casos)


def practicar_jefe(jefe: dict, codigo: str) -> Informe:
    return evaluar_codigo(codigo, jefe["practica"])


def enfrentar_jefe(jefe: dict, codigo: str, privado: dict | None) -> Informe:
    """Entrega oficial del jefe: un resultado por requisito."""
    if not privado or not privado.get("casos") or "solucion" not in privado:
        raise EntregaOficialNoDisponible(jefe["id"])
    return evaluar_jefe(codigo, privado["casos"], jefe["requisitos"], privado["solucion"])
