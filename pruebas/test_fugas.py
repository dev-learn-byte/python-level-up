"""Ningún archivo privado puede acabar en el repositorio público.

Se revisa todo lo que Git tiene registrado para publicar.
"""
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).parent.parent
MARCA = "# PRIVADO" + "-PLU"   # primera línea de todo archivo privado
NOMBRES_PRIVADOS = ("soluciones.toml", "solucion.py", "evaluacion_A.toml", "evaluacion_B.toml")
CLAVES_PRIVADAS = ("solucion =", "[[retos]]")


def archivos_publicados() -> list[Path]:
    salida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True,
    )
    if salida.returncode != 0:
        pytest.skip("no es un repositorio de Git")
    return [RAIZ / linea for linea in salida.stdout.splitlines() if (RAIZ / linea).is_file()]


def test_hay_archivos_que_revisar():
    assert len(archivos_publicados()) > 30


def test_ningun_archivo_publicado_tiene_nombre_de_archivo_privado():
    culpables = [a for a in archivos_publicados() if a.name in NOMBRES_PRIVADOS]
    assert culpables == []


def test_ningun_archivo_publicado_lleva_la_marca_de_privado():
    culpables = []
    for archivo in archivos_publicados():
        try:
            primera = archivo.read_text(encoding="utf-8").split("\n", 1)[0]
        except UnicodeDecodeError:
            continue
        if primera.startswith(MARCA):
            culpables.append(archivo)
    assert culpables == []


def test_el_contenido_publico_no_incluye_soluciones_ni_retos_de_evaluacion():
    culpables = []
    for archivo in (RAIZ / "contenido").rglob("*.toml"):
        texto = archivo.read_text(encoding="utf-8")
        if any(linea.startswith(CLAVES_PRIVADAS) for linea in texto.splitlines()):
            culpables.append(archivo)
    assert culpables == []


@pytest.mark.parametrize("ruta", ["contenido_privado/", "contenido_privado", ".env", "progreso.json"])
def test_git_ignora_lo_privado(ruta):
    assert ruta in (RAIZ / ".gitignore").read_text().splitlines()


def test_la_carpeta_privada_no_esta_registrada_en_git():
    registrados = subprocess.run(
        ["git", "ls-files", "contenido_privado"], cwd=RAIZ, capture_output=True, text=True,
    ).stdout
    assert registrados == ""
