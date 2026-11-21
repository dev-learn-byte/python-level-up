"""La estructura base del proyecto existe y el sistema anterior no reaparece."""
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
CARPETAS = ["nucleo", "contenido/sagas", "contenido/eventos", "contenido/diarias",
            "servidor", "web", "pruebas", "docs"]
SISTEMA_ANTERIOR = ["sistema.py", "rango_E_novato", "respaldo_original"]


@pytest.mark.parametrize("carpeta", CARPETAS)
def test_carpeta_existe(carpeta):
    assert (RAIZ / carpeta).is_dir()


@pytest.mark.parametrize("ruta", SISTEMA_ANTERIOR)
def test_el_sistema_anterior_fue_retirado(ruta):
    assert not (RAIZ / ruta).exists()


def test_contenido_privado_ignorado_por_git():
    ignorados = (RAIZ / ".gitignore").read_text().splitlines()
    assert "contenido_privado/" in ignorados
