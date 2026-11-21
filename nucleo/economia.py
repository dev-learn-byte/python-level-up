"""XP, puntos, recompensas únicas y tienda.

Todo cambio de XP o puntos pasa por aquí, para que la penalización y los
logros se actualicen siempre igual.
"""
from .errores import AccionInvalida
from .estado import Estado, EstadoNivel
from .resultado import Resultado, accion


def dar_xp(estado: Estado, catalogo, res: Resultado, cantidad: int) -> None:
    """Suma XP. No existe ninguna función que los reste."""
    estado.xp += cantidad
    res.xp += cantidad
    if estado.xp >= catalogo.config.xp_logro_9000:
        dar_logro(estado, res, "mas_de_9000")


def dar_puntos(estado: Estado, res: Resultado, cantidad: int) -> None:
    """Suma puntos y, si hay penalización, los cuenta como puntos nuevos."""
    if cantidad <= 0:
        return
    estado.puntos += cantidad
    res.puntos += cantidad
    penalizacion = estado.penalizacion
    if penalizacion:
        penalizacion.acumulado += cantidad
        if penalizacion.acumulado >= penalizacion.meta:
            estado.penalizacion = None
            estado.historial_saltos.append(
                {"tipo": "penalizacion_cumplida", "meta": penalizacion.meta}
            )
            res.sucesos.append("penalizacion_cumplida")


def gastar(estado: Estado, res: Resultado, cantidad: int) -> None:
    """Resta puntos. Gastar no reduce el contador de la penalización."""
    if cantidad > estado.puntos:
        raise AccionInvalida(
            "puntos_insuficientes",
            f"Necesitas {cantidad} puntos y tienes {estado.puntos}.",
        )
    estado.puntos -= cantidad
    res.puntos_gastados += cantidad


def recompensar(estado, catalogo, res, clave: str, xp: int, puntos: int) -> bool:
    """Paga una recompensa solo la primera vez. Devuelve si se pagó."""
    if clave in estado.recompensas:
        res.sucesos.append("recompensa_repetida")
        return False
    estado.recompensas.add(clave)
    dar_xp(estado, catalogo, res, xp)
    dar_puntos(estado, res, puntos)
    return True


def dar_logro(estado: Estado, res: Resultado, logro: str) -> None:
    if logro not in estado.logros:
        estado.logros.append(logro)
        res.sucesos.append(f"logro:{logro}")


def nivel_jugable(estado: Estado, catalogo, numero: int):
    """Devuelve el progreso de un nivel en curso (actual o pendiente)."""
    catalogo.nivel(numero)
    progreso = estado.niveles.get(numero)
    if progreso is None or progreso.estado not in (EstadoNivel.ACTUAL, EstadoNivel.PENDIENTE):
        raise AccionInvalida(
            "nivel_no_jugable",
            f"El nivel {numero} está {estado.estado_de(numero).value}: no se puede jugar ahora.",
        )
    return progreso


# --- Tienda y recuperación de vidas ---

def _sumar_vida(progreso, catalogo) -> None:
    if progreso.vidas >= catalogo.config.vidas_por_nivel:
        raise AccionInvalida("vidas_completas", "Ya tienes todas las vidas.")
    progreso.vidas += 1


@accion
def comprar_semilla(estado, catalogo, res, nivel: int):
    """Semilla del Ermitaño: +1 vida por puntos, una vez por intento de nivel."""
    progreso = nivel_jugable(estado, catalogo, nivel)
    if progreso.semilla_usada:
        raise AccionInvalida("semilla_ya_usada", "Ya usaste la semilla de este nivel.")
    _sumar_vida(progreso, catalogo)
    gastar(estado, res, catalogo.config.costo_semilla)
    progreso.semilla_usada = True
    res.sucesos.append("vida_recuperada")


@accion
def completar_repaso(estado, catalogo, res, nivel: int, perfecto: bool):
    """Repaso de niveles anteriores: si sale perfecto, +1 vida (una vez por intento)."""
    progreso = nivel_jugable(estado, catalogo, nivel)
    if not perfecto:
        res.sucesos.append("repaso_con_fallos")
        return
    if progreso.repaso_usado:
        raise AccionInvalida("repaso_ya_usado", "Ya cobraste el repaso de este nivel.")
    _sumar_vida(progreso, catalogo)
    progreso.repaso_usado = True
    res.sucesos.append("vida_recuperada")


@accion
def comprar_pista(estado, catalogo, res, nivel: int, mision: str, numero: int):
    """Pista extra de una misión. Una vez comprada, volver a verla es gratis."""
    catalogo.mision(nivel, mision)
    clave = f"{mision}#{numero}"
    if clave in estado.pistas:
        res.sucesos.append("pista_ya_comprada")
        return
    gastar(estado, res, catalogo.config.costo_pista)
    estado.pistas.add(clave)
    res.sucesos.append("pista_comprada")
