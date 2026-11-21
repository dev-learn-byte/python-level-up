"""Catálogo de prueba y atajos para llegar rápido a una situación."""
import pytest

from nucleo import (
    Catalogo, Estado, Evento, Jefe, Mision, Nivel, entrar_nivel, entregar_jefe,
    entregar_mision, rendir_evaluacion,
)

SAGAS = ["goku", "torneo", "saiyajin", "freezer"]  # 3 niveles cada una


def crear_catalogo() -> Catalogo:
    niveles = [
        Nivel(n, SAGAS[(n - 1) // 3], tuple(Mision(f"n{n}m{i}") for i in range(1, 7)))
        for n in range(1, 13)
    ]
    jefes = [
        Jefe(saga, f"transformacion_{saga}", final=(saga == SAGAS[-1])) for saga in SAGAS
    ]
    eventos = [Evento("mazmorra_1"), Evento("evento_ua", requiere_nivel=2)]
    return Catalogo(niveles, jefes, eventos)


@pytest.fixture
def cat():
    return crear_catalogo()


@pytest.fixture
def nuevo(cat):
    return Estado.nuevo(cat)


def entregar_todo(estado, cat, nivel):
    for mision in cat.nivel(nivel).misiones:
        if mision.id not in estado.niveles[nivel].entregadas:
            estado, _ = entregar_mision(estado, cat, nivel, mision.id, True)
    return estado


def aprobar(estado, cat, nivel, aciertos=10):
    """Entrega todas las misiones del nivel y aprueba su evaluación."""
    estado = entregar_todo(estado, cat, nivel)
    estado, resultado = rendir_evaluacion(estado, cat, nivel, aciertos)
    assert resultado.ocurrio("evaluacion_aprobada")
    return estado


def vencer_jefe(estado, cat, saga):
    estado, resultado = entregar_jefe(estado, cat, saga, cat.jefe(saga).requisitos)
    assert resultado.ocurrio("jefe_vencido")
    return estado


def llegar_a(cat, nivel, aprobado=False):
    """Partida que avanzó sin saltos hasta `nivel` (en curso o ya aprobado)."""
    estado = Estado.nuevo(cat)
    for n in range(1, nivel + 1):
        if n > 1:
            estado, _ = entrar_nivel(estado, cat, n)
        if n == nivel and not aprobado:
            break
        estado = aprobar(estado, cat, n)
        saga = cat.nivel(n).saga
        if cat.es_ultimo_de_saga(n) and n != nivel:
            estado = vencer_jefe(estado, cat, saga)
    return estado
