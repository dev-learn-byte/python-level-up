"""Números del juego. Cambiar una regla es cambiar un valor aquí."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Vidas
    vidas_por_nivel: int = 5
    vidas_por_jefe: int = 5
    # Porcentaje mínimo de aciertos para aprobar
    aprobacion_evaluacion: int = 70
    aprobacion_salto: int = 80
    # Saltos de nivel
    costo_salto_por_nivel: int = 100
    salto_maximo: int = 5
    retos_salto_por_nivel: int = 2
    retos_salto_minimo: int = 5
    multiplicador_penalizacion: int = 2
    xp_salto_superado: int = 100
    # Tienda
    costo_semilla: int = 50
    costo_pista: int = 10
    # Bonos
    puntos_por_vida_restante: int = 5
    racha_para_bono: int = 3
    bono_racha: int = 10
    # Misión diaria
    puntos_diaria: int = 15
    xp_diaria: int = 5
    racha_diaria_logro: int = 7
    # Logros
    xp_logro_9000: int = 9000
