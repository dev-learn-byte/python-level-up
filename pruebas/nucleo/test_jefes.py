"""Jefes de saga: cinco vidas propias y se repite solo el jefe."""
import pytest

from nucleo import AccionInvalida, EstadoNivel, entregar_jefe, jefes_disponibles

from .conftest import llegar_a, vencer_jefe


def test_el_jefe_no_esta_disponible_con_la_saga_incompleta(cat):
    estado = llegar_a(cat, 3)  # nivel 3 en curso
    assert jefes_disponibles(estado, cat) == []
    with pytest.raises(AccionInvalida) as error:
        entregar_jefe(estado, cat, "goku", 8)
    assert error.value.codigo == "saga_incompleta"


def test_el_ultimo_nivel_de_la_saga_no_abre_la_siguiente_sin_vencer_al_jefe(cat):
    estado = llegar_a(cat, 3, aprobado=True)
    assert estado.estado_de(4) is EstadoNivel.BLOQUEADO
    assert jefes_disponibles(estado, cat) == ["goku"]


def test_vencer_al_jefe_da_recompensa_transformacion_y_abre_la_saga_siguiente(cat):
    estado = llegar_a(cat, 3, aprobado=True)
    xp, puntos = estado.xp, estado.puntos
    estado, res = entregar_jefe(estado, cat, "goku", 8)
    assert res.ocurrio("jefe_vencido")
    assert (estado.xp - xp, estado.puntos - puntos) == (150, 100)
    assert estado.transformaciones == ["transformacion_goku"]
    assert "saga_completa:goku" in estado.logros
    assert "jefe_sin_perder_vidas" in estado.logros
    assert estado.estado_de(4) is EstadoNivel.DESBLOQUEADO


def test_entrega_incompleta_cuesta_una_vida_del_jefe_no_del_nivel(cat):
    estado = llegar_a(cat, 3, aprobado=True)
    estado, res = entregar_jefe(estado, cat, "goku", 7)
    assert res.vidas_perdidas == 1
    assert estado.jefes["goku"].vidas == 4
    assert not estado.jefes["goku"].vencido


def test_sin_vidas_se_repite_solo_el_jefe_y_no_la_saga(cat):
    estado = llegar_a(cat, 3, aprobado=True)
    xp, puntos = estado.xp, estado.puntos
    for _ in range(5):
        estado, res = entregar_jefe(estado, cat, "goku", 0)
    assert res.ocurrio("jefe_reiniciado")
    assert estado.jefes["goku"].vidas == 5
    assert estado.jefes["goku"].intentos == 2
    assert all(estado.estado_de(n) is EstadoNivel.APROBADO for n in (1, 2, 3))
    assert (estado.xp, estado.puntos) == (xp, puntos)

    estado, res = entregar_jefe(estado, cat, "goku", 8)   # se puede volver a intentar
    assert res.ocurrio("jefe_vencido")
    assert "jefe_sin_perder_vidas" not in estado.logros


def test_un_jefe_vencido_no_se_cobra_dos_veces(cat):
    estado = vencer_jefe(llegar_a(cat, 3, aprobado=True), cat, "goku")
    with pytest.raises(AccionInvalida) as error:
        entregar_jefe(estado, cat, "goku", 8)
    assert error.value.codigo == "jefe_ya_vencido"


@pytest.mark.parametrize("saga, cumplidos, codigo", [
    ("goku", 9, "dato_invalido"), ("goku", -1, "dato_invalido"),
    ("nadie", 8, "jefe_inexistente"),
])
def test_entregas_de_jefe_invalidas(cat, saga, cumplidos, codigo):
    estado = llegar_a(cat, 3, aprobado=True)
    with pytest.raises(AccionInvalida) as error:
        entregar_jefe(estado, cat, saga, cumplidos)
    assert error.value.codigo == codigo
