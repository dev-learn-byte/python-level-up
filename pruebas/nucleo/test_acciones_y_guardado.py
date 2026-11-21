"""Entrada del servidor, idempotencia, guardado y propiedades generales."""
import copy
import json
import random

import pytest

from nucleo import (
    ACCIONES, AccionInvalida, Catalogo, Estado, EstadoNivel, Jefe, Mision, Nivel,
    aplicar, entregar_mision, iniciar_salto, resolver_salto,
)

from .conftest import llegar_a


def entrega(identificador="a1", correcta=True):
    return {"tipo": "entregar_mision", "id": identificador,
            "nivel": 1, "mision": "n1m1", "correcta": correcta}


# --- Idempotencia ---

def test_la_misma_accion_enviada_dos_veces_no_duplica_la_recompensa(nuevo, cat):
    estado, res = aplicar(nuevo, cat, entrega())
    assert estado.puntos == 10 and not res.duplicada
    repetido, res = aplicar(estado, cat, entrega())
    assert res.duplicada
    assert repetido.a_dict() == estado.a_dict()


def test_la_misma_accion_enviada_dos_veces_no_duplica_el_castigo(nuevo, cat):
    estado, _ = aplicar(nuevo, cat, entrega(correcta=False))
    estado, res = aplicar(estado, cat, entrega(correcta=False))
    assert res.duplicada
    assert estado.niveles[1].vidas == 4


def test_dos_dispositivos_completan_la_misma_mision_y_cuenta_una_vez(nuevo, cat):
    estado, _ = aplicar(nuevo, cat, entrega("pc-1"))
    with pytest.raises(AccionInvalida) as error:
        aplicar(estado, cat, entrega("celular-1"))
    assert error.value.codigo == "mision_ya_entregada"
    assert estado.puntos == 10


# --- El servidor no acepta cantidades enviadas por el navegador ---

@pytest.mark.parametrize("campo", ["puntos", "xp", "vidas", "recompensa"])
def test_se_rechazan_acciones_que_intentan_fijar_puntos_xp_o_vidas(nuevo, cat, campo):
    with pytest.raises(AccionInvalida) as error:
        aplicar(nuevo, cat, {**entrega(), campo: 9999})
    assert error.value.codigo == "accion_mal_formada"


@pytest.mark.parametrize("accion, codigo", [
    ({"tipo": "regalar_puntos", "cantidad": 500}, "accion_desconocida"),
    ({}, "accion_desconocida"),
    ("entregar_mision", "accion_desconocida"),
    ({"tipo": "entregar_mision", "nivel": 1}, "accion_mal_formada"),
    ({"tipo": "entregar_mision", "nivel": "1", "mision": "n1m1", "correcta": True}, "dato_invalido"),
    ({"tipo": "entregar_mision", "nivel": 1, "mision": "n1m1", "correcta": "si"}, "dato_invalido"),
    ({"tipo": "rendir_evaluacion", "nivel": 1, "aciertos": True}, "dato_invalido"),
    ({"tipo": "completar_diaria", "fecha": "ayer", "correcta": True}, "dato_invalido"),
])
def test_acciones_mal_formadas(nuevo, cat, accion, codigo):
    with pytest.raises(AccionInvalida) as error:
        aplicar(nuevo, cat, accion)
    assert error.value.codigo == codigo


def test_la_fecha_de_la_diaria_llega_como_texto(nuevo, cat):
    estado, res = aplicar(nuevo, cat, {"tipo": "completar_diaria",
                                       "fecha": "2026-11-21", "correcta": True})
    assert estado.ultima_diaria == "2026-11-21" and res.puntos == 15


def test_todas_las_acciones_estan_registradas(cat):
    assert set(ACCIONES) == {
        "entrar_nivel", "entregar_mision", "rendir_evaluacion", "entregar_jefe",
        "iniciar_salto", "resolver_salto", "comprar_semilla", "comprar_pista",
        "completar_repaso", "completar_diaria", "completar_evento",
    }


# --- Las acciones no modifican el estado que reciben ---

def test_una_accion_valida_devuelve_un_estado_nuevo(nuevo, cat):
    original = copy.deepcopy(nuevo)
    entregar_mision(nuevo, cat, 1, "n1m1", True)
    assert nuevo == original


def test_una_accion_rechazada_no_cambia_nada(cat):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 499
    original = copy.deepcopy(estado)
    with pytest.raises(AccionInvalida):
        iniciar_salto(estado, cat, 10)       # no le alcanzan los puntos
    assert estado == original


# --- Guardado ---

def test_el_progreso_se_guarda_y_se_recupera_igual(cat):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 850
    estado, _ = iniciar_salto(estado, cat, 10)
    estado, _ = resolver_salto(estado, cat, 0)        # con penalización activa
    estado, _ = aplicar(estado, cat, {"tipo": "completar_diaria", "id": "d1",
                                      "fecha": "2026-11-21", "correcta": True})
    texto = json.dumps(estado.a_dict())
    recuperado = Estado.desde_dict(json.loads(texto))
    assert recuperado == estado
    assert recuperado.penalizacion.faltan == 985
    assert recuperado.estado_de(5) is EstadoNivel.APROBADO


def test_un_salto_a_medias_tambien_se_guarda(cat):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 850
    estado, _ = iniciar_salto(estado, cat, 10)
    recuperado = Estado.desde_dict(json.loads(json.dumps(estado.a_dict())))
    assert recuperado == estado
    recuperado, res = resolver_salto(recuperado, cat, 9)
    assert res.ocurrio("salto_superado")


# --- Catálogo ---

@pytest.mark.parametrize("niveles, jefes", [
    ([Nivel(1, "a", ()), Nivel(3, "a", ())], []),                      # hueco
    ([Nivel(1, "a", ()), Nivel(2, "b", ()), Nivel(3, "a", ())], []),   # saga partida
    ([Nivel(1, "a", (Mision("x"),)), Nivel(2, "a", (Mision("x"),))], []),
    ([Nivel(1, "a", ())], [Jefe("z", "t")]),
    ([Nivel(1, "a", ()), Nivel(2, "b", ())], [Jefe("a", "t", final=True)]),
])
def test_un_catalogo_incoherente_se_rechaza_al_cargarlo(niveles, jefes):
    with pytest.raises(ValueError):
        Catalogo(niveles, jefes)


def test_una_saga_sin_jefe_abre_la_siguiente_al_aprobar_su_ultimo_nivel():
    from nucleo import rendir_evaluacion
    cat = Catalogo([Nivel(1, "a", ()), Nivel(2, "b", ())])
    estado, _ = rendir_evaluacion(Estado.nuevo(cat), cat, 1, 10)
    assert estado.estado_de(2) is EstadoNivel.DESBLOQUEADO


# --- Propiedades que deben cumplirse siempre ---

def _accion_al_azar(azar, cat, estado):
    """Un jugador torpe pero insistente: suele hacer algo útil y a veces no."""
    jugables = [n for n, p in estado.niveles.items()
                if p.estado in (EstadoNivel.ACTUAL, EstadoNivel.PENDIENTE)]
    abiertos = [n for n, p in estado.niveles.items()
                if p.estado is EstadoNivel.DESBLOQUEADO]
    nivel = azar.choice(jugables) if jugables and azar.random() < 0.85 else azar.randint(1, 12)
    faltan = [m.id for m in cat.nivel(nivel).misiones
              if nivel not in estado.niveles or m.id not in estado.niveles[nivel].entregadas]
    mision = azar.choice(faltan) if faltan else f"n{nivel}m1"
    retos = estado.salto.retos if estado.salto else 10
    return azar.choice([
        {"tipo": "entrar_nivel", "nivel": azar.choice(abiertos) if abiertos else nivel},
        {"tipo": "entregar_mision", "nivel": nivel, "mision": mision,
         "correcta": azar.random() < 0.85},
        {"tipo": "entregar_mision", "nivel": nivel, "mision": mision, "correcta": True},
        {"tipo": "rendir_evaluacion", "nivel": nivel, "aciertos": azar.randint(5, 10)},
        {"tipo": "entregar_jefe", "saga": azar.choice(cat.sagas),
         "requisitos_cumplidos": azar.choice([8, 8, 5])},
        {"tipo": "iniciar_salto", "destino": estado.nivel_actual + azar.randint(1, 5)},
        {"tipo": "resolver_salto", "aciertos": azar.randint(retos // 2, retos)},
        {"tipo": "comprar_semilla", "nivel": nivel},
        {"tipo": "comprar_pista", "nivel": nivel, "mision": mision, "numero": azar.randint(1, 3)},
        {"tipo": "completar_repaso", "nivel": nivel, "perfecto": azar.random() < 0.5},
        {"tipo": "completar_evento", "evento": "mazmorra_1", "correcta": True},
    ])


@pytest.mark.parametrize("semilla", range(20))
def test_partidas_al_azar_respetan_las_reglas_basicas(cat, semilla):
    azar = random.Random(semilla)
    estado = Estado.nuevo(cat)
    aplicadas = 0
    for _ in range(800):
        accion = _accion_al_azar(azar, cat, estado)
        try:
            nuevo, res = aplicar(estado, cat, accion)
        except AccionInvalida:
            continue
        aplicadas += 1
        assert nuevo.xp >= estado.xp                      # los XP nunca bajan
        assert nuevo.puntos >= 0                          # nunca hay saldo negativo
        assert nuevo.puntos == estado.puntos + res.puntos - res.puntos_gastados
        assert all(1 <= p.vidas <= 5 for p in nuevo.niveles.values())
        assert all(1 <= j.vidas <= 5 for j in nuevo.jefes.values())
        actuales = [n for n, p in nuevo.niveles.items() if p.estado is EstadoNivel.ACTUAL]
        assert len(actuales) <= 1                         # un solo nivel actual
        aprobados_antes = {n for n, p in estado.niveles.items()
                           if p.estado is EstadoNivel.APROBADO}
        assert all(nuevo.estado_de(n) is EstadoNivel.APROBADO for n in aprobados_antes)
        if nuevo.penalizacion:
            assert 0 <= nuevo.penalizacion.acumulado < nuevo.penalizacion.meta
        estado = nuevo
    assert aplicadas > 100
    assert Estado.desde_dict(json.loads(json.dumps(estado.a_dict()))) == estado


def test_un_salto_aprobado_enviado_dos_veces_da_100_xp_una_sola_vez(cat):
    estado = llegar_a(cat, 5, aprobado=True)
    estado.puntos = 850
    estado, _ = aplicar(estado, cat, {"tipo": "iniciar_salto", "id": "s1", "destino": 10})
    xp = estado.xp
    estado, _ = aplicar(estado, cat, {"tipo": "resolver_salto", "id": "s2", "aciertos": 10})
    estado, res = aplicar(estado, cat, {"tipo": "resolver_salto", "id": "s2", "aciertos": 10})
    assert res.duplicada and estado.xp == xp + 100
