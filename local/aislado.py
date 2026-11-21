"""Ejecuta cada evaluación en un proceso aparte, con límite de tiempo.

Qué protege: un bucle infinito o un error grave en el código evaluado no
cuelga ni rompe el juego, y los archivos que el código cree van a una
carpeta temporal.

Qué NO protege: no es un sandbox. El código se ejecuta con los permisos del
usuario del sistema, puede leer archivos y usar la red. Por eso la versión
local solo debe ejecutar código escrito por quien la usa.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from evaluador.comprobaciones import Informe, ResultadoCaso

from .trabajador import MARCA

RAIZ = Path(__file__).parent.parent
SEGUNDOS = 10


def _fallo(nombre: str, mensaje: str) -> Informe:
    return Informe([ResultadoCaso(nombre, [mensaje])])


def evaluar(tipo: str, **datos) -> Informe:
    """Lanza el trabajo en un proceso hijo y devuelve su informe."""
    arranque = (
        f"import sys; sys.path.insert(0, {str(RAIZ)!r}); "
        "from local.trabajador import main; main()"
    )
    trabajo = json.dumps({"tipo": tipo, "datos": datos}).encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="plu_") as carpeta:
        try:
            proceso = subprocess.run(
                [sys.executable, "-I", "-c", arranque],
                input=trabajo, capture_output=True, cwd=carpeta, timeout=SEGUNDOS,
            )
        except subprocess.TimeoutExpired:
            return _fallo(
                "Tiempo agotado",
                f"Tu programa tardó más de {SEGUNDOS} segundos y se detuvo. "
                "Suele pasar cuando el código se queda repitiendo algo sin parar.",
            )
    salida = proceso.stdout.decode("utf-8", errors="replace")
    lineas = [linea for linea in salida.splitlines() if linea.startswith(MARCA)]
    if not lineas:
        detalle = proceso.stderr.decode("utf-8", errors="replace").strip().splitlines()
        return _fallo(
            "Evaluación interrumpida",
            "El evaluador se detuvo antes de terminar. "
            + (f"Último mensaje: {detalle[-1]}" if detalle else ""),
        )
    casos = json.loads(lineas[-1][len(MARCA):])["casos"]
    return Informe([ResultadoCaso(caso["nombre"], caso["fallos"]) for caso in casos])
