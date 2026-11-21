"""Etapa 0: la estructura base existe y el respaldo es una copia fiel."""
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
CARPETAS = ["nucleo", "contenido/sagas", "contenido/eventos", "contenido/diarias",
            "servidor", "web", "pruebas", "docs", "respaldo_original"]
RESPALDADOS = {
    "sistema.py": "sistema.py",
    "README_original.md": "README.md",
    "rango_E_novato/misiones.py": "rango_E_novato/misiones.py",
    "rango_E_novato/pruebas.py": "rango_E_novato/pruebas.py",
    "rango_E_novato/ejemplos.py": "rango_E_novato/ejemplos.py",
    "rango_E_novato/leccion.md": "rango_E_novato/leccion.md",
}
COMMIT_ORIGINAL = "76a3bbb"


@pytest.mark.parametrize("carpeta", CARPETAS)
def test_carpeta_existe(carpeta):
    assert (RAIZ / carpeta).is_dir()


@pytest.mark.parametrize("copia, original", RESPALDADOS.items())
def test_respaldo_identico_al_original(copia, original):
    en_git = subprocess.run(
        ["git", "show", f"{COMMIT_ORIGINAL}:{original}"],
        cwd=RAIZ, capture_output=True,
    )
    if en_git.returncode != 0:
        pytest.skip("el commit original no está disponible en este clon")
    assert (RAIZ / "respaldo_original" / copia).read_bytes() == en_git.stdout


def test_contenido_privado_ignorado_por_git():
    ignorados = (RAIZ / ".gitignore").read_text().splitlines()
    assert "contenido_privado/" in ignorados
