"""Misión diaria y eventos especiales.

Son fuentes de puntos nuevos que no dependen de repetir niveles, para que
una penalización nunca quede sin forma de cumplirse. Fallar aquí no cuesta
vidas, y no hacer la diaria no tiene ningún castigo.
"""
from datetime import date, timedelta

from .economia import dar_logro, dar_puntos, dar_xp, recompensar
from .errores import AccionInvalida
from .estado import EstadoNivel
from .resultado import accion


@accion
def completar_diaria(estado, catalogo, res, fecha: date, correcta: bool):
    """Misión diaria: una recompensa por día. La fecha la pone el servidor."""
    if not isinstance(fecha, date):
        raise AccionInvalida("dato_invalido", "La fecha de la misión diaria no es válida.")
    hoy = fecha.isoformat()
    if estado.ultima_diaria is not None:
        if hoy == estado.ultima_diaria:
            raise AccionInvalida("diaria_ya_cobrada", "Ya cobraste la misión diaria de hoy.")
        if hoy < estado.ultima_diaria:
            raise AccionInvalida("dato_invalido", "Esa fecha es anterior a tu última diaria.")
    if not correcta:
        res.sucesos.append("diaria_fallida")  # se puede volver a intentar hoy
        return

    ayer = (fecha - timedelta(days=1)).isoformat()
    estado.racha_diaria = estado.racha_diaria + 1 if estado.ultima_diaria == ayer else 1
    estado.ultima_diaria = hoy
    dar_xp(estado, catalogo, res, catalogo.config.xp_diaria)
    dar_puntos(estado, res, catalogo.config.puntos_diaria)
    res.sucesos.append("diaria_completada")
    if estado.racha_diaria >= catalogo.config.racha_diaria_logro:
        dar_logro(estado, res, "racha_diaria")


@accion
def completar_evento(estado, catalogo, res, evento: str, correcta: bool):
    """Evento o mazmorra: paga una sola vez."""
    datos = catalogo.evento(evento)
    requerido = datos.requiere_nivel
    if requerido and estado.estado_de(requerido) is not EstadoNivel.APROBADO:
        raise AccionInvalida(
            "evento_bloqueado", f"Este evento se abre al aprobar el nivel {requerido}."
        )
    if not correcta:
        res.sucesos.append("evento_fallido")
        return
    res.sucesos.append("evento_completado")
    recompensar(estado, catalogo, res, f"evento:{evento}", datos.xp, datos.puntos)
