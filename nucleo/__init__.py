"""Núcleo de reglas de Python Level Up (Python puro, sin dependencias).

Uso típico desde el servidor:

    estado = Estado.nuevo(catalogo)
    estado, resultado = aplicar(estado, catalogo, {"tipo": "entregar_mision", ...})
"""
from .acciones import ACCIONES, aplicar
from .catalogo import Catalogo, Evento, Jefe, Mision, Nivel
from .config import Config
from .consultas import jefes_disponibles, mapa, niveles_pendientes, saltos_posibles
from .economia import comprar_pista, comprar_semilla, completar_repaso
from .errores import AccionInvalida
from .estado import Estado, EstadoNivel, Penalizacion
from .extras import completar_diaria, completar_evento
from .progresion import (
    entrar_nivel, entregar_jefe, entregar_mision, jefe_disponible, rendir_evaluacion,
)
from .resultado import Resultado
from .saltos import costo_salto, iniciar_salto, resolver_salto

__all__ = [
    "ACCIONES", "AccionInvalida", "Catalogo", "Config", "Estado", "EstadoNivel",
    "Evento", "Jefe", "Mision", "Nivel", "Penalizacion", "Resultado", "aplicar",
    "comprar_pista", "comprar_semilla", "completar_diaria", "completar_evento",
    "completar_repaso", "costo_salto", "entrar_nivel", "entregar_jefe",
    "entregar_mision", "iniciar_salto", "jefe_disponible", "jefes_disponibles",
    "mapa", "niveles_pendientes", "rendir_evaluacion", "resolver_salto",
    "saltos_posibles",
]
