"""Recuperar vidas, pistas, misión diaria y eventos especiales."""
from datetime import date

import pytest

from nucleo import (
    AccionInvalida, comprar_pista, comprar_semilla, completar_diaria, completar_evento,
    completar_repaso, entrar_nivel, entregar_mision,
)

from .conftest import aprobar

HOY = date(2026, 11, 21)


def con_una_vida_menos(estado, cat, puntos=100):
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    estado.puntos = puntos
    return estado


# --- Vidas ---

def test_la_semilla_devuelve_una_vida_por_50_puntos(nuevo, cat):
    estado, res = comprar_semilla(con_una_vida_menos(nuevo, cat), cat, 1)
    assert estado.niveles[1].vidas == 5
    assert estado.puntos == 50
    assert res.puntos_gastados == 50


def test_solo_una_semilla_por_intento_de_nivel(nuevo, cat):
    estado = con_una_vida_menos(nuevo, cat, puntos=500)
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)   # 3 vidas
    estado, _ = comprar_semilla(estado, cat, 1)
    with pytest.raises(AccionInvalida) as error:
        comprar_semilla(estado, cat, 1)
    assert error.value.codigo == "semilla_ya_usada"


def test_no_se_puede_comprar_la_semilla_sin_puntos_suficientes(nuevo, cat):
    estado = con_una_vida_menos(nuevo, cat, puntos=49)
    with pytest.raises(AccionInvalida) as error:
        comprar_semilla(estado, cat, 1)
    assert error.value.codigo == "puntos_insuficientes"
    assert estado.puntos == 49 and estado.niveles[1].vidas == 4


def test_nunca_se_superan_las_cinco_vidas(nuevo, cat):
    nuevo.puntos = 500
    with pytest.raises(AccionInvalida) as error:
        comprar_semilla(nuevo, cat, 1)
    assert error.value.codigo == "vidas_completas"
    assert nuevo.puntos == 500


def test_repaso_perfecto_da_una_vida_una_sola_vez(nuevo, cat):
    estado = con_una_vida_menos(nuevo, cat)
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)   # 3 vidas
    estado, res = completar_repaso(estado, cat, 1, False)
    assert estado.niveles[1].vidas == 3
    estado, _ = completar_repaso(estado, cat, 1, True)
    assert estado.niveles[1].vidas == 4
    with pytest.raises(AccionInvalida) as error:
        completar_repaso(estado, cat, 1, True)
    assert error.value.codigo == "repaso_ya_usado"


def test_al_reiniciar_el_nivel_la_semilla_vuelve_a_estar_disponible(nuevo, cat):
    estado = con_una_vida_menos(nuevo, cat, puntos=500)
    estado, _ = comprar_semilla(estado, cat, 1)
    for _ in range(5):
        estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    estado, _ = comprar_semilla(estado, cat, 1)
    assert estado.niveles[1].vidas == 5


# --- Pistas ---

def test_una_pista_cuesta_10_puntos_y_volver_a_verla_es_gratis(nuevo, cat):
    nuevo.puntos = 25
    estado, _ = comprar_pista(nuevo, cat, 1, "n1m1", 1)
    assert estado.puntos == 15
    estado, res = comprar_pista(estado, cat, 1, "n1m1", 1)
    assert estado.puntos == 15 and res.ocurrio("pista_ya_comprada")
    estado, _ = comprar_pista(estado, cat, 1, "n1m1", 2)
    with pytest.raises(AccionInvalida) as error:
        comprar_pista(estado, cat, 1, "n1m2", 1)
    assert error.value.codigo == "puntos_insuficientes"


# --- Misión diaria ---

def test_la_diaria_paga_15_puntos_una_sola_vez_al_dia(nuevo, cat):
    estado, res = completar_diaria(nuevo, cat, HOY, True)
    assert (res.puntos, res.xp) == (15, 5)
    with pytest.raises(AccionInvalida) as error:
        completar_diaria(estado, cat, HOY, True)
    assert error.value.codigo == "diaria_ya_cobrada"
    assert estado.puntos == 15


def test_fallar_la_diaria_no_cuesta_nada_y_se_puede_reintentar(nuevo, cat):
    estado, res = completar_diaria(nuevo, cat, HOY, False)
    assert (estado.puntos, estado.xp, estado.niveles[1].vidas) == (0, 0, 5)
    estado, res = completar_diaria(estado, cat, HOY, True)
    assert res.ocurrio("diaria_completada")


def test_perder_dias_no_castiga_solo_reinicia_la_racha(nuevo, cat):
    estado, _ = completar_diaria(nuevo, cat, date(2026, 11, 21), True)
    estado, _ = completar_diaria(estado, cat, date(2026, 11, 22), True)
    assert estado.racha_diaria == 2
    antes = (estado.xp, estado.puntos, estado.niveles[1].vidas)
    estado, _ = completar_diaria(estado, cat, date(2026, 12, 5), True)   # dos semanas después
    assert estado.racha_diaria == 1
    assert estado.xp == antes[0] + 5 and estado.puntos == antes[1] + 15
    assert estado.niveles[1].vidas == antes[2]


def test_siete_dias_seguidos_dan_un_logro(nuevo, cat):
    estado = nuevo
    for dia in range(1, 8):
        estado, _ = completar_diaria(estado, cat, date(2026, 12, dia), True)
    assert "racha_diaria" in estado.logros
    assert estado.puntos == 7 * 15


def test_no_se_acepta_una_fecha_anterior_a_la_ultima_diaria(nuevo, cat):
    estado, _ = completar_diaria(nuevo, cat, HOY, True)
    with pytest.raises(AccionInvalida) as error:
        completar_diaria(estado, cat, date(2026, 11, 20), True)
    assert error.value.codigo == "dato_invalido"


# --- Eventos ---

def test_un_evento_paga_una_sola_vez(nuevo, cat):
    estado, res = completar_evento(nuevo, cat, "mazmorra_1", True)
    assert (res.xp, res.puntos) == (40, 50)
    estado, res = completar_evento(estado, cat, "mazmorra_1", True)
    assert res.ocurrio("recompensa_repetida")
    assert (estado.xp, estado.puntos) == (40, 50)


def test_fallar_un_evento_no_cuesta_vidas(nuevo, cat):
    estado, res = completar_evento(nuevo, cat, "mazmorra_1", False)
    assert estado.niveles[1].vidas == 5 and estado.puntos == 0
    estado, res = completar_evento(estado, cat, "mazmorra_1", True)
    assert res.puntos == 50


def test_evento_que_exige_un_nivel_aprobado(nuevo, cat):
    with pytest.raises(AccionInvalida) as error:
        completar_evento(nuevo, cat, "evento_ua", True)
    assert error.value.codigo == "evento_bloqueado"

    estado = aprobar(nuevo, cat, 1)
    estado, _ = entrar_nivel(estado, cat, 2)
    estado = aprobar(estado, cat, 2)
    estado, res = completar_evento(estado, cat, "evento_ua", True)
    assert res.ocurrio("evento_completado")


def test_evento_inexistente(nuevo, cat):
    with pytest.raises(AccionInvalida) as error:
        completar_evento(nuevo, cat, "no_existe", True)
    assert error.value.codigo == "evento_inexistente"


def test_al_reiniciar_el_nivel_el_repaso_vuelve_a_estar_disponible_una_vez(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", False)
    estado, _ = completar_repaso(estado, cat, 1, True)
    for _ in range(5):
        estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    assert estado.niveles[1].intentos == 2
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    estado, _ = completar_repaso(estado, cat, 1, True)
    assert estado.niveles[1].vidas == 5
    estado, _ = entregar_mision(estado, cat, 1, "n1m1", False)
    with pytest.raises(AccionInvalida):
        completar_repaso(estado, cat, 1, True)
