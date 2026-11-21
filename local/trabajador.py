"""Proceso hijo que ejecuta una evaluación y devuelve el informe.

Recibe un trabajo en JSON por la entrada estándar y escribe el informe en
una línea marcada. Lo lanza `local.aislado`; no se usa directamente.
"""
import json
import sys

from evaluador import evaluar_prediccion, evaluar_reto
from evaluador.contenido import (
    enfrentar_jefe, entregar_mision, practicar_jefe, practicar_mision,
)

MARCA = "@@INFORME@@"
TRABAJOS = {
    "practicar_mision": practicar_mision,
    "entregar_mision": entregar_mision,
    "practicar_jefe": practicar_jefe,
    "enfrentar_jefe": enfrentar_jefe,
    "evaluar_reto": evaluar_reto,
    "evaluar_prediccion": evaluar_prediccion,
}


def main() -> None:
    trabajo = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    informe = TRABAJOS[trabajo["tipo"]](**trabajo["datos"])
    casos = [{"nombre": caso.nombre, "fallos": caso.fallos} for caso in informe.casos]
    linea = MARCA + json.dumps({"casos": casos})
    sys.stdout.buffer.write(("\n" + linea + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
