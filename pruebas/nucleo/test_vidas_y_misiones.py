"""Vidas por nivel, entregas finales y recompensas únicas."""
import pytest

from nucleo import AccionInvalida, EstadoNivel, entregar_mision



def test_partida_nueva_empieza_en_nivel_1_con_cinco_vidas(nuevo):
    assert nuevo.nivel_actual == 1
    assert nuevo.niveles[1].estado is EstadoNivel.ACTUAL
    assert nuevo.niveles[1].vidas == 5
    assert (nuevo.xp, nuevo.puntos) == (0, 0)


def test_mision_correcta_da_xp_y_puntos(nuevo, cat):
    estado, res = entregar_mision(nuevo, cat, 1, "n1m1", True)
    assert (estado.xp, estado.puntos) == (10, 10)
    assert (res.xp, res.puntos, res.vidas_perdidas) == (10, 10, 0)
    assert estado.niveles[1].vidas == 5


def test_entrega_fallida_cuesta_una_vida_y_no_da_recompensa(nuevo, cat):
    estado, res = entregar_mision(nuevo, cat, 1, "n1m1", False)
    assert estado.niveles[1].vidas == 4
    assert res.vidas_perdidas == 1
    assert (estado.xp, estado.puntos) == (0, 0)
    assert "n1m1" not in estado.niveles[1].entregadas


def test_tras_fallar_se_puede_volver_a_entregar(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", False)
    estado, res = entregar_mision(estado, cat, 1, "n1m1", True)
    assert res.ocurrio("mision_superada")
    assert estado.xp == 10


def test_no_se_puede_entregar_dos_veces_la_misma_mision(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", True)
    with pytest.raises(AccionInvalida) as error:
        entregar_mision(estado, cat, 1, "n1m1", True)
    assert error.value.codigo == "mision_ya_entregada"


def test_quedarse_sin_vidas_reinicia_el_nivel_y_conserva_xp_y_puntos(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", True)
    estado, _ = entregar_mision(estado, cat, 1, "n1m2", True)
    xp, puntos = estado.xp, estado.puntos
    for _ in range(4):
        estado, res = entregar_mision(estado, cat, 1, "n1m3", False)
        assert not res.ocurrio("nivel_reiniciado")
    estado, res = entregar_mision(estado, cat, 1, "n1m3", False)

    assert res.ocurrio("nivel_reiniciado")
    progreso = estado.niveles[1]
    assert progreso.vidas == 5
    assert progreso.entregadas == set()      # hay que rehacer las misiones
    assert progreso.intentos == 2
    assert progreso.estado is EstadoNivel.ACTUAL
    assert (estado.xp, estado.puntos) == (xp, puntos)


def test_repetir_un_nivel_no_vuelve_a_pagar_las_misiones(nuevo, cat):
    estado = nuevo
    for mision in ("n1m1", "n1m2", "n1m3", "n1m4", "n1m5"):
        estado, _ = entregar_mision(estado, cat, 1, mision, True)
    xp, puntos = estado.xp, estado.puntos
    for _ in range(5):                       # pierde las 5 vidas en la sexta
        estado, _ = entregar_mision(estado, cat, 1, "n1m6", False)
    assert estado.niveles[1].entregadas == set()

    estado, res = entregar_mision(estado, cat, 1, "n1m2", True)
    assert res.ocurrio("recompensa_repetida")
    assert (res.xp, res.puntos) == (0, 0)
    for mision in ("n1m1", "n1m3", "n1m4", "n1m5"):
        estado, _ = entregar_mision(estado, cat, 1, mision, True)
    assert (estado.xp, estado.puntos) == (xp, puntos)     # repetir no paga

    estado, res = entregar_mision(estado, cat, 1, "n1m6", True)
    assert (res.xp, res.puntos) == (10, 10)               # la sexta era nueva


def test_tres_misiones_nuevas_seguidas_dan_bono_de_racha(nuevo, cat):
    estado = nuevo
    for mision in ("n1m1", "n1m2"):
        estado, res = entregar_mision(estado, cat, 1, mision, True)
        assert not res.ocurrio("bono_racha")
    estado, res = entregar_mision(estado, cat, 1, "n1m3", True)
    assert res.ocurrio("bono_racha")
    assert estado.puntos == 30 + 10


def test_un_fallo_corta_la_racha(nuevo, cat):
    estado, _ = entregar_mision(nuevo, cat, 1, "n1m1", True)
    estado, _ = entregar_mision(estado, cat, 1, "n1m2", True)
    estado, _ = entregar_mision(estado, cat, 1, "n1m3", False)
    estado, res = entregar_mision(estado, cat, 1, "n1m3", True)
    assert not res.ocurrio("bono_racha")


@pytest.mark.parametrize("nivel, mision, codigo", [
    (2, "n2m1", "nivel_no_jugable"),      # bloqueado
    (99, "x", "nivel_inexistente"),
    (1, "n2m1", "mision_inexistente"),    # misión de otro nivel
])
def test_entregas_invalidas(nuevo, cat, nivel, mision, codigo):
    with pytest.raises(AccionInvalida) as error:
        entregar_mision(nuevo, cat, nivel, mision, True)
    assert error.value.codigo == codigo
