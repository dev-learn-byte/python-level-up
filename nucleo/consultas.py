"""Preguntas sobre el progreso que no lo modifican (para mostrar en pantalla)."""
from .errores import AccionInvalida
from .estado import EstadoNivel
from .progresion import jefe_disponible
from .saltos import costo_salto


def mapa(estado, catalogo) -> dict[int, EstadoNivel]:
    """El estado de cada nivel del catálogo."""
    return {numero: estado.estado_de(numero) for numero in catalogo.numeros}


def niveles_pendientes(estado, catalogo) -> list[int]:
    return [n for n, e in mapa(estado, catalogo).items() if e is EstadoNivel.PENDIENTE]


def saltos_posibles(estado, catalogo) -> dict[int, int]:
    """Destinos a los que se puede saltar ahora mismo, con su costo."""
    posibles = {}
    for destino in catalogo.numeros:
        try:
            posibles[destino] = costo_salto(estado, catalogo, destino)
        except AccionInvalida:
            pass
    return posibles


def jefes_disponibles(estado, catalogo) -> list[str]:
    return [
        j.saga for j in catalogo.jefes()
        if jefe_disponible(estado, catalogo, j.saga)
        and not (j.saga in estado.jefes and estado.jefes[j.saga].vencido)
    ]
