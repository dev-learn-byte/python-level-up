"""Las soluciones de referencia resuelven cada ejercicio y cada evaluación.

Estas pruebas necesitan el repositorio privado. Si no está, se omiten.
"""
import pytest

from evaluador import evaluar_reto, valor_mirado
from evaluador.contenido import (
    enfrentar_jefe, entregar_mision, practicar_jefe, practicar_mision,
)
from nucleo.cargador import leer_toml

from .recoleccion import PRIVADO, espejo, eventos, misiones, sagas

pytestmark = pytest.mark.skipif(PRIVADO is None, reason="falta el contenido privado")

MISIONES = misiones()
IDS = [m["id"] for _, m in MISIONES]
NO_ENSENADO = ["if ", "else", "def ", "return", "try:", "except", "for ", "while ", "lambda"]

if PRIVADO is not None:
    from .recoleccion import evaluaciones, retos, soluciones
    EVALUACIONES = evaluaciones()
    RETOS = retos()
else:
    EVALUACIONES, RETOS = [], []


def respuesta_correcta(reto: dict) -> str:
    """El código que resuelve un reto."""
    if reto["tipo"] == "predecir":
        return f"respuesta = {valor_mirado(reto)!r}"
    return reto["solucion"]


def sin_resolver(reto: dict) -> str:
    return "respuesta = ..." if reto["tipo"] == "predecir" else reto["plantilla"]


# --- Misiones ---

@pytest.mark.parametrize("nivel, mision", MISIONES, ids=IDS)
def test_la_solucion_de_referencia_supera_la_mision(nivel, mision):
    privado = soluciones(nivel)[mision["id"]]
    assert privado["solucion"].startswith("# === ") or "# === TU CÓDIGO" in privado["solucion"]
    assert practicar_mision(mision, privado["solucion"]).aprobado
    informe = entregar_mision(mision, privado["solucion"], privado)
    assert informe.aprobado, informe.texto()


@pytest.mark.parametrize("nivel, mision", MISIONES, ids=IDS)
def test_la_plantilla_sin_resolver_no_supera_la_entrega(nivel, mision):
    privado = soluciones(nivel)[mision["id"]]
    assert not entregar_mision(mision, mision["plantilla"], privado).aprobado


@pytest.mark.parametrize("nivel, mision", MISIONES, ids=IDS)
def test_las_misiones_con_datos_tienen_casos_oficiales_distintos(nivel, mision):
    if "# === DATOS" not in mision["plantilla"]:
        return
    oficiales = soluciones(nivel)[mision["id"]]["casos"]
    assert len(oficiales) >= 2
    publicos = [caso.get("datos") for caso in mision["casos"]]
    assert all(caso["datos"] not in publicos for caso in oficiales)


@pytest.mark.parametrize("nivel, mision", MISIONES, ids=IDS)
def test_las_soluciones_no_usan_conceptos_que_aun_no_se_ensenan(nivel, mision):
    solucion = soluciones(nivel)[mision["id"]]["solucion"]
    for concepto in NO_ENSENADO:
        assert concepto not in solucion, f"usa {concepto!r} antes de tiempo"


# --- Evaluaciones ---

@pytest.mark.parametrize("nombre, nivel, evaluacion", EVALUACIONES, ids=[e[0] for e in EVALUACIONES])
def test_cada_evaluacion_tiene_los_retos_que_indica_el_nivel(nombre, nivel, evaluacion):
    assert len(evaluacion["retos"]) == nivel["retos_evaluacion"]
    assert all(reto["enunciado"].strip() for reto in evaluacion["retos"])


def test_las_versiones_a_y_b_tienen_la_misma_estructura_y_distinto_contenido():
    por_nivel = {}
    for nombre, _, evaluacion in EVALUACIONES:
        por_nivel.setdefault(nombre[:-2], []).append(evaluacion["retos"])
    assert por_nivel
    for a, b in por_nivel.values():
        assert [r["tipo"] for r in a] == [r["tipo"] for r in b]
        for reto_a, reto_b in zip(a, b):
            assert reto_a.get("codigo", reto_a.get("solucion")) != reto_b.get("codigo", reto_b.get("solucion"))


@pytest.mark.parametrize("nombre, reto", RETOS, ids=[r[0] for r in RETOS])
def test_cada_reto_se_supera_con_su_respuesta_y_no_con_la_plantilla(nombre, reto):
    informe = evaluar_reto(reto, respuesta_correcta(reto))
    assert informe.aprobado, informe.texto()
    assert not evaluar_reto(reto, sin_resolver(reto)).aprobado


@pytest.mark.parametrize("nombre, reto", RETOS, ids=[r[0] for r in RETOS])
def test_los_retos_no_usan_conceptos_que_aun_no_se_ensenan(nombre, reto):
    for texto in (reto.get("codigo", ""), reto.get("solucion", ""), reto.get("plantilla", "")):
        for concepto in NO_ENSENADO:
            assert concepto not in texto, f"usa {concepto!r} antes de tiempo"


# --- Jefes ---

@pytest.mark.parametrize("saga", sagas(), ids=lambda s: s.name)
def test_el_jefe_se_vence_con_la_solucion_y_no_con_la_plantilla(saga):
    jefe = leer_toml(saga / "jefe.toml")
    privado = leer_toml(espejo(saga) / "jefe.toml")
    assert practicar_jefe(jefe, privado["solucion"]).aprobado
    informe = enfrentar_jefe(jefe, privado["solucion"], privado)
    assert informe.aprobado, informe.texto()
    assert len(informe.casos) == len(jefe["requisitos"])
    assert len(privado["casos"]) >= 3
    sin_hacer = enfrentar_jefe(jefe, jefe["plantilla"], privado)
    assert sin_hacer.aciertos == 0
    for concepto in NO_ENSENADO:
        assert concepto not in privado["solucion"]


# --- Eventos ---

def test_los_eventos_se_superan_con_su_solucion():
    privados = leer_toml(PRIVADO / "eventos" / "soluciones.toml")
    for evento in eventos():
        privado = privados[evento["id"]]
        informe = entregar_mision(evento, privado["solucion"], privado)
        assert informe.aprobado, informe.texto()
        assert not entregar_mision(evento, evento["plantilla"], privado).aprobado
