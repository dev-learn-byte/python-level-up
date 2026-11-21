"""La misión diaria varía de verdad y los repasos están bien formados."""
from datetime import date, timedelta

import pytest

from evaluador import evaluar_prediccion, valor_mirado
from evaluador.contenido import PUBLICO
from evaluador.diaria import elegir_repaso, mision_diaria, variantes
from nucleo.cargador import leer_toml

from .recoleccion import niveles

PLANTILLAS = leer_toml(PUBLICO / "diarias" / "plantillas.toml")["plantillas"]
INICIO = date(2026, 11, 21)
DIAS = [INICIO + timedelta(days=n) for n in range(120)]


def test_hay_tres_familias_y_cada_nivel_tiene_plantillas():
    assert len({p["familia"] for p in PLANTILLAS}) == 3
    assert {p["nivel"] for p in PLANTILLAS} == {1, 2, 3}
    assert sum(variantes(p) for p in PLANTILLAS) > 300


@pytest.mark.parametrize("plantilla", PLANTILLAS, ids=lambda p: p["texto"][:25] + str(id(p) % 97))
def test_todas_las_combinaciones_de_una_plantilla_se_pueden_ejecutar(plantilla):
    import itertools
    nombres = sorted(plantilla["valores"])
    for combinacion in itertools.product(*(plantilla["valores"][n] for n in nombres)):
        codigo = plantilla["codigo"]
        for nombre, valor in zip(nombres, combinacion):
            codigo = codigo.replace(f"<<{nombre}>>", str(valor))
        assert "<<" not in codigo
        valor_mirado({"codigo": codigo, "mirar": plantilla["mirar"]})   # no debe fallar


def test_sin_niveles_aprobados_no_hay_mision_diaria():
    assert mision_diaria(INICIO, PLANTILLAS, set()) is None


def test_la_diaria_solo_usa_niveles_aprobados():
    assert all(mision_diaria(dia, PLANTILLAS, {1})["nivel"] == 1 for dia in DIAS)
    assert {mision_diaria(dia, PLANTILLAS, {1, 2, 3})["nivel"] for dia in DIAS} == {1, 2, 3}


def test_la_misma_fecha_da_la_misma_mision_en_cualquier_dispositivo():
    assert mision_diaria(INICIO, PLANTILLAS, {1, 2}) == mision_diaria(INICIO, PLANTILLAS, {1, 2})


def test_la_diaria_varia_de_un_dia_a_otro():
    codigos = [mision_diaria(dia, PLANTILLAS, {1, 2, 3})["codigo"] for dia in DIAS]
    assert len(set(codigos)) > 80                      # de 120 días, casi todos distintos
    repetidos_seguidos = sum(a == b for a, b in zip(codigos, codigos[1:]))
    assert repetidos_seguidos <= 2


def test_la_diaria_se_puede_responder_y_evaluar():
    for dia in DIAS[:30]:
        pregunta = mision_diaria(dia, PLANTILLAS, {1, 2, 3})
        correcta = valor_mirado(pregunta)
        assert evaluar_prediccion(f"respuesta = {correcta!r}", [pregunta], ["respuesta"]).aprobado
        assert not evaluar_prediccion("respuesta = ...", [pregunta], ["respuesta"]).aprobado


# --- Repasos ---

REPASOS = [(n.name, leer_toml(n / "repaso.toml")) for n in niveles() if (n / "repaso.toml").exists()]


def test_los_niveles_2_y_3_tienen_repaso():
    assert [nombre for nombre, _ in REPASOS] == ["nivel_02_operadores", "nivel_03_cadenas"]


@pytest.mark.parametrize("nombre, repaso", REPASOS, ids=[r[0] for r in REPASOS])
def test_el_repaso_elige_tres_preguntas_que_se_pueden_evaluar(nombre, repaso):
    assert len(repaso["preguntas"]) > repaso["preguntas_por_repaso"] == 3
    for pregunta in repaso["preguntas"]:
        valor_mirado(pregunta)
    elegidas = elegir_repaso(repaso, semilla=1)
    assert len(elegidas) == 3
    assert elegir_repaso(repaso, semilla=1) == elegidas
    assert any(elegir_repaso(repaso, semilla=s) != elegidas for s in range(2, 8))
    respuestas = "\n".join(f"respuesta_{n} = {valor_mirado(p)!r}" for n, p in enumerate(elegidas, 1))
    assert evaluar_prediccion(respuestas, elegidas).aprobado
