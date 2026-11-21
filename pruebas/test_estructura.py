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
    # Git no borra las cachés de Python (__pycache__), así que no cuentan.
    ruta = RAIZ / ruta
    restos = [ruta] if ruta.is_file() else ruta.rglob("*") if ruta.is_dir() else []
    restos = [r for r in restos if r.is_file() and "__pycache__" not in r.parts]
    assert restos == [], f"quedan archivos del sistema anterior: {restos}"


def test_contenido_privado_ignorado_por_git():
    ignorados = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "contenido_privado/" in ignorados
