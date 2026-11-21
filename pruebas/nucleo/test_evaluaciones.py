"""Evaluaciones de nivel: 70 % para aprobar y un fallo = una vida."""
import pytest

from nucleo import AccionInvalida, EstadoNivel, entrar_nivel, entregar_mision, rendir_evaluacion
from nucleo.progresion import aprueba

from .conftest import aprobar, entregar_todo


@pytest.mark.parametrize("aciertos, total, minimo, esperado", [
    (7, 10, 70, True), (6, 10, 70, False), (10, 10, 70, True), (0, 10, 70, False),
    (2, 3, 70, False), (3, 4, 70, True),
    (8, 10, 80, True), (7, 10, 80, False), (2, 2, 80, True), (1, 2, 80, False),
])
def test_porcentaje_de_aprobacion(aciertos, total, minimo, esperado):
    assert aprueba(aciertos, total, minimo) is esperado


def test_no_hay_evaluacion_sin_entregar_todas_las_misiones(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", True)
    with pytest.raises(AccionInvalida) as error:
        rendir_evaluacion(estado, cat, 1, 10)
    assert error.value.codigo == "misiones_pendientes"


def test_aprobar_con_el_minimo_de_siete_aciertos(nuevo, cat):
    estado = entregar_todo(nuevo, cat, 1)
    antes = estado.puntos
    estado, res = rendir_evaluacion(estado, cat, 1, 7)
    assert res.ocurrio("evaluacion_aprobada")
    assert res.vidas_perdidas == 3
    assert estado.niveles[1].estado is EstadoNivel.APROBADO
    assert res.xp == 50
    assert estado.puntos - antes == 30 + 2 * 5   # 30 + 5 por cada vida restante


def test_evaluacion_perfecta_da_bono_maximo_y_logro(nuevo, cat):
    estado = entregar_todo(nuevo, cat, 1)
    estado, res = rendir_evaluacion(estado, cat, 1, 10)
    assert res.puntos == 30 + 5 * 5
    assert "evaluacion_sin_perder_vidas" in estado.logros


def test_reprobar_con_vidas_repite_solo_la_evaluacion(nuevo, cat):
    estado = entregar_todo(nuevo, cat, 1)
    xp = estado.xp
    estado, res = rendir_evaluacion(estado, cat, 1, 6)  # 60 %: 4 fallos
    assert res.ocurrio("evaluacion_reprobada") and not res.ocurrio("nivel_reiniciado")
    progreso = estado.niveles[1]
    assert progreso.vidas == 1
    assert progreso.estado is EstadoNivel.ACTUAL
    assert len(progreso.entregadas) == 6          # las misiones se conservan
    assert progreso.version_evaluacion == "B"     # la repetición usa otros datos
    assert estado.xp == xp

    estado, res = rendir_evaluacion(estado, cat, 1, 10)
    assert res.ocurrio("evaluacion_aprobada")


def test_sin_vidas_en_la_evaluacion_se_reinicia_el_nivel_aunque_el_porcentaje_alcance(nuevo, cat):
    estado = entregar_todo(nuevo, cat, 1)
    estado.niveles[1].vidas = 2
    xp, puntos = estado.xp, estado.puntos
    estado, res = rendir_evaluacion(estado, cat, 1, 8)  # 80 %, pero 2 fallos y 2 vidas
    assert res.ocurrio("nivel_reiniciado")
    assert estado.niveles[1].estado is EstadoNivel.ACTUAL
    assert estado.niveles[1].entregadas == set()
    assert estado.niveles[1].vidas == 5
    assert (estado.xp, estado.puntos) == (xp, puntos)


def test_no_se_puede_avanzar_sin_aprobar(nuevo, cat):
    estado = entregar_todo(nuevo, cat, 1)
    estado, _ = rendir_evaluacion(estado, cat, 1, 6)
    assert estado.estado_de(2) is EstadoNivel.BLOQUEADO
    with pytest.raises(AccionInvalida) as error:
        entrar_nivel(estado, cat, 2)
    assert error.value.codigo == "nivel_no_desbloqueado"


def test_aprobar_desbloquea_el_siguiente_y_entrar_lo_vuelve_actual(nuevo, cat):
    estado = aprobar(nuevo, cat, 1)
    assert estado.estado_de(2) is EstadoNivel.DESBLOQUEADO
    assert estado.nivel_actual == 1
    estado, _ = entrar_nivel(estado, cat, 2)
    assert estado.estado_de(2) is EstadoNivel.ACTUAL
    assert estado.nivel_actual == 2
    assert estado.niveles[2].vidas == 5           # vidas nuevas en cada nivel


def test_nivel_aprobado_ya_no_admite_entregas_ni_evaluaciones(nuevo, cat):
    estado = aprobar(nuevo, cat, 1)
    with pytest.raises(AccionInvalida):
        rendir_evaluacion(estado, cat, 1, 10)
    with pytest.raises(AccionInvalida):
        entregar_mision(estado, cat, 1, "n1m1", True)


@pytest.mark.parametrize("aciertos", [-1, 11, 7.5, "10", True, None])
def test_aciertos_invalidos_se_rechazan(nuevo, cat, aciertos):
    estado = entregar_todo(nuevo, cat, 1)
    with pytest.raises(AccionInvalida) as error:
        rendir_evaluacion(estado, cat, 1, aciertos)
    assert error.value.codigo == "dato_invalido"
