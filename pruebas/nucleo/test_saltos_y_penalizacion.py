"""Saltos con puntos, niveles pendientes y penalización del doble."""
import pytest

from nucleo import (
    AccionInvalida, EstadoNivel, comprar_semilla, completar_evento, costo_salto,
    entrar_nivel, entregar_jefe, entregar_mision, iniciar_salto, mapa,
    niveles_pendientes, rendir_evaluacion, resolver_salto, saltos_posibles,
)

from .conftest import aprobar, llegar_a, vencer_jefe

E = EstadoNivel


def en_nivel_5(cat, puntos=850, aprobado=True):
    estado = llegar_a(cat, 5, aprobado=aprobado)
    estado.puntos = puntos
    return estado


def fracasar_salto(cat, puntos=850):
    """El ejemplo de la especificación: 850 puntos, salto de 5 a 10, fracaso."""
    estado, _ = iniciar_salto(en_nivel_5(cat, puntos), cat, 10)
    return resolver_salto(estado, cat, 0)


# --- Requisitos y costo ---

def test_el_salto_cuesta_100_puntos_por_nivel(cat):
    estado = en_nivel_5(cat)
    assert costo_salto(estado, cat, 10) == 500
    assert costo_salto(estado, cat, 7) == 200
    assert saltos_posibles(estado, cat) == {7: 200, 8: 300, 9: 400, 10: 500}


def test_los_puntos_se_descuentan_al_iniciar_el_examen(cat):
    estado, res = iniciar_salto(en_nivel_5(cat), cat, 10)
    assert estado.puntos == 350
    assert res.puntos_gastados == 500
    assert estado.salto.retos == 10
    assert estado.nivel_actual == 5               # todavía no se mueve


@pytest.mark.parametrize("puntos, destino, codigo", [
    (499, 10, "puntos_insuficientes"),   # gastar más de lo disponible
    (0, 7, "puntos_insuficientes"),
    (9999, 11, "salto_demasiado_largo"),
    (9999, 5, "destino_invalido"),       # el propio nivel
    (9999, 3, "destino_invalido"),       # hacia atrás
    (9999, 6, "destino_invalido"),       # ya desbloqueado
    (9999, 13, "nivel_inexistente"),
])
def test_saltos_que_no_se_permiten(cat, puntos, destino, codigo):
    estado = en_nivel_5(cat, puntos)
    with pytest.raises(AccionInvalida) as error:
        iniciar_salto(estado, cat, destino)
    assert error.value.codigo == codigo
    assert estado.puntos == puntos                # no se cobró nada


@pytest.mark.parametrize("destino, retos", [(6, 5), (7, 5), (8, 6), (9, 8), (10, 10)])
def test_el_examen_tiene_minimo_5_retos_y_crece_con_la_distancia(cat, destino, retos):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 5000
    estado.niveles.pop(6)                     # el 6 bloqueado, para poder saltar 1 nivel
    estado, _ = iniciar_salto(estado, cat, destino)
    assert estado.salto.retos == retos


@pytest.mark.parametrize("aciertos, superado", [(4, True), (3, False)])
def test_salto_corto_exige_4_de_5(cat, aciertos, superado):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 5000
    estado.niveles.pop(6)
    estado, _ = iniciar_salto(estado, cat, 6)
    estado, res = resolver_salto(estado, cat, aciertos)
    assert res.ocurrio("salto_superado") is superado


def test_no_se_pueden_tener_dos_examenes_de_salto_a_la_vez(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat, 2000), cat, 8)
    with pytest.raises(AccionInvalida) as error:
        iniciar_salto(estado, cat, 9)
    assert error.value.codigo == "salto_en_curso"


@pytest.mark.parametrize("accion", [
    lambda e, c: entrar_nivel(e, c, 6),
    lambda e, c: entregar_mision(e, c, 5, "n5m1", True),
    lambda e, c: rendir_evaluacion(e, c, 5, 10),
    lambda e, c: comprar_semilla(e, c, 5),
    lambda e, c: completar_evento(e, c, "mazmorra_1", True),
])
def test_durante_el_examen_de_salto_no_se_puede_hacer_otra_cosa(cat, accion):
    estado, _ = iniciar_salto(en_nivel_5(cat, aprobado=False), cat, 10)
    with pytest.raises(AccionInvalida) as error:
        accion(estado, cat)
    assert error.value.codigo == "salto_en_curso"


def test_resolver_sin_examen_empezado_es_un_error(cat):
    with pytest.raises(AccionInvalida) as error:
        resolver_salto(en_nivel_5(cat), cat, 10)
    assert error.value.codigo == "sin_salto_en_curso"


# --- Salto superado y niveles pendientes ---

def test_salto_superado_con_el_minimo_de_80_por_ciento(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    xp = estado.xp
    estado, res = resolver_salto(estado, cat, 8)
    assert res.ocurrio("salto_superado")
    assert estado.nivel_actual == 10
    assert estado.puntos == 350                   # se descuentan los puntos usados
    assert estado.xp == xp + 100                  # recompensa por superarlo
    assert estado.penalizacion is None and estado.salto is None
    assert "salto_superado" in estado.logros
    assert estado.historial_saltos[-1]["superado"] is True


def test_con_el_nivel_5_aprobado_los_pendientes_son_del_6_al_9(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat, aprobado=True), cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    assert niveles_pendientes(estado, cat) == [6, 7, 8, 9]
    assert mapa(estado, cat) == {
        1: E.APROBADO, 2: E.APROBADO, 3: E.APROBADO, 4: E.APROBADO, 5: E.APROBADO,
        6: E.PENDIENTE, 7: E.PENDIENTE, 8: E.PENDIENTE, 9: E.PENDIENTE,
        10: E.ACTUAL, 11: E.BLOQUEADO, 12: E.BLOQUEADO,
    }


def test_si_el_nivel_actual_no_estaba_aprobado_tambien_queda_pendiente(cat):
    estado = en_nivel_5(cat, aprobado=False)
    estado, _ = entregar_mision(estado, cat, 5, "n5m1", True)
    estado, _ = iniciar_salto(estado, cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    assert niveles_pendientes(estado, cat) == [5, 6, 7, 8, 9]
    assert estado.niveles[5].entregadas == {"n5m1"}   # conserva lo avanzado


def test_siete_de_diez_no_alcanza_para_el_salto(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    _, res = resolver_salto(estado, cat, 7)
    assert res.ocurrio("salto_fracasado")


def test_un_nivel_pendiente_se_juega_con_las_reglas_normales(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    xp = estado.xp
    estado = aprobar(estado, cat, 6)
    assert estado.estado_de(6) is E.APROBADO
    assert estado.xp > xp                          # paga como primera vez
    assert estado.nivel_actual == 10               # la posición no cambia
    assert niveles_pendientes(estado, cat) == [7, 8, 9]


def test_perder_las_vidas_en_un_pendiente_reinicia_solo_ese_nivel(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    for _ in range(5):
        estado, res = entregar_mision(estado, cat, 7, "n7m1", False)
    assert res.ocurrio("nivel_reiniciado")
    assert estado.estado_de(7) is E.PENDIENTE
    assert estado.nivel_actual == 10
    assert estado.niveles[10].vidas == 5


def test_no_se_puede_saltar_de_nuevo_con_niveles_pendientes_detras(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat, 5000), cat, 8)
    estado, _ = resolver_salto(estado, cat, 6)
    with pytest.raises(AccionInvalida) as error:
        iniciar_salto(estado, cat, 10)
    assert error.value.codigo == "niveles_anteriores_sin_aprobar"


def test_la_transformacion_de_una_saga_saltada_exige_vencer_al_jefe_real(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    assert estado.transformaciones == ["transformacion_goku"]
    with pytest.raises(AccionInvalida) as error:
        entregar_jefe(estado, cat, "torneo", 8)
    assert error.value.codigo == "saga_incompleta"


def test_el_jefe_final_exige_no_tener_niveles_pendientes(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    estado, _ = resolver_salto(estado, cat, 10)
    for nivel in (10, 11, 12):
        if nivel > 10:
            estado, _ = entrar_nivel(estado, cat, nivel)
        estado = aprobar(estado, cat, nivel)
    with pytest.raises(AccionInvalida) as error:
        entregar_jefe(estado, cat, "freezer", 8)
    assert error.value.codigo == "niveles_pendientes"

    for nivel in (6, 7, 8, 9):
        estado = aprobar(estado, cat, nivel)
    with pytest.raises(AccionInvalida) as error:   # faltan los jefes saltados
        entregar_jefe(estado, cat, "freezer", 8)
    assert error.value.codigo == "jefes_pendientes"

    estado = vencer_jefe(estado, cat, "torneo")
    estado = vencer_jefe(estado, cat, "saiyajin")
    estado = vencer_jefe(estado, cat, "freezer")
    assert estado.transformaciones[-1] == "transformacion_freezer"
    assert niveles_pendientes(estado, cat) == []


# --- Fracaso y penalización ---

def test_ejemplo_de_la_especificacion_850_menos_500_quedan_350(cat):
    estado, res = fracasar_salto(cat)
    assert res.ocurrio("salto_fracasado") and res.ocurrio("penalizacion_activada")
    assert estado.puntos == 350                    # pierde los 500 invertidos
    assert estado.nivel_actual == 5                # regresa a su nivel
    assert estado.estado_de(10) is E.BLOQUEADO     # no desbloquea el avanzado
    assert estado.estado_de(5) is E.APROBADO       # su progreso sigue intacto
    assert estado.penalizacion.meta == 1000        # el doble de lo invertido
    assert estado.penalizacion.acumulado == 0      # los 350 no cuentan
    assert estado.penalizacion.faltan == 1000
    assert estado.historial_saltos[-1] == {
        "tipo": "salto", "origen": 5, "destino": 10, "costo": 500,
        "aciertos": 0, "retos": 10, "superado": False,
    }


def test_fracasar_no_quita_xp(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 10)
    xp = estado.xp
    estado, _ = resolver_salto(estado, cat, 0)
    assert estado.xp == xp


def test_con_penalizacion_no_se_puede_saltar_aunque_sobren_puntos(cat):
    estado, _ = fracasar_salto(cat, puntos=5000)
    assert estado.puntos == 4500
    with pytest.raises(AccionInvalida) as error:
        iniciar_salto(estado, cat, 7)
    assert error.value.codigo == "saltos_bloqueados"
    assert saltos_posibles(estado, cat) == {}


def test_con_penalizacion_se_sigue_estudiando_y_ganando_xp_y_puntos(cat):
    estado, _ = fracasar_salto(cat)
    xp, puntos = estado.xp, estado.puntos
    estado, _ = entrar_nivel(estado, cat, 6)
    estado, res = entregar_mision(estado, cat, 6, "n6m1", True)
    assert (estado.xp, estado.puntos) == (xp + 10, puntos + 10)
    assert estado.penalizacion.acumulado == 10     # solo cuentan los puntos nuevos
    assert estado.penalizacion.faltan == 990


def test_gastar_puntos_no_reduce_el_contador_de_la_penalizacion(cat):
    estado, _ = fracasar_salto(cat)
    estado, _ = entrar_nivel(estado, cat, 6)
    estado, _ = entregar_mision(estado, cat, 6, "n6m1", True)
    estado, _ = entregar_mision(estado, cat, 6, "n6m2", False)
    estado, _ = comprar_semilla(estado, cat, 6)
    assert estado.puntos == 350 + 10 - 50
    assert estado.penalizacion.acumulado == 10


def test_la_penalizacion_se_levanta_sola_al_llegar_al_doble(cat):
    estado, _ = fracasar_salto(cat)
    estado.penalizacion.acumulado = 949            # como si hubiera ganado 949 nuevos
    estado, res = completar_evento(estado, cat, "mazmorra_1", True)   # +50
    assert estado.penalizacion.acumulado == 999
    assert not res.ocurrio("penalizacion_cumplida")
    with pytest.raises(AccionInvalida):
        iniciar_salto(estado, cat, 7)

    estado, _ = entrar_nivel(estado, cat, 6)
    estado, res = entregar_mision(estado, cat, 6, "n6m1", True)       # +10 -> 1009
    assert res.ocurrio("penalizacion_cumplida")
    assert estado.penalizacion is None
    assert estado.historial_saltos[-1] == {"tipo": "penalizacion_cumplida", "meta": 1000}
    assert costo_salto(estado, cat, 8) == 200      # recupera el acceso a los saltos


def test_abandonar_el_examen_equivale_a_fracasar(cat):
    estado, _ = iniciar_salto(en_nivel_5(cat), cat, 7)
    estado, res = resolver_salto(estado, cat, 0)
    assert estado.penalizacion.meta == 400         # el doble de 200
    assert res.ocurrio("salto_fracasado")
