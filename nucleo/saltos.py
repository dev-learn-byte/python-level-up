"""Saltos de nivel con puntos ("Habitación del Tiempo") y su penalización.

El examen tiene un único intento y no usa vidas: se supera con 80 %.
Si se fracasa, se pierden los puntos invertidos y los saltos quedan
bloqueados hasta ganar el doble en puntos nuevos.
"""
from .economia import dar_logro, dar_xp, gastar
from .errores import AccionInvalida
from .estado import EstadoNivel, Penalizacion, ProgresoNivel, SaltoEnCurso
from .progresion import aprueba
from .resultado import accion, exigir_entero


def costo_salto(estado, catalogo, destino: int) -> int:
    """Valida un salto y devuelve su costo. Lanza AccionInvalida si no procede."""
    config = catalogo.config
    if estado.penalizacion:
        raise AccionInvalida(
            "saltos_bloqueados",
            f"Tienes una penalización: faltan {estado.penalizacion.faltan} puntos nuevos.",
        )
    catalogo.nivel(destino)
    origen = estado.nivel_actual
    distancia = destino - origen
    if distancia < 1:
        raise AccionInvalida("destino_invalido", "Solo se puede saltar hacia adelante.")
    if distancia > config.salto_maximo:
        raise AccionInvalida(
            "salto_demasiado_largo", f"El salto máximo es de {config.salto_maximo} niveles."
        )
    if estado.estado_de(destino) is not EstadoNivel.BLOQUEADO:
        raise AccionInvalida("destino_invalido", f"El nivel {destino} ya es accesible.")
    if any(estado.estado_de(n) is not EstadoNivel.APROBADO for n in range(1, origen)):
        raise AccionInvalida(
            "niveles_anteriores_sin_aprobar",
            "Antes de saltar debes aprobar todos los niveles anteriores al actual.",
        )
    costo = distancia * config.costo_salto_por_nivel
    if costo > estado.puntos:
        raise AccionInvalida(
            "puntos_insuficientes", f"El salto cuesta {costo} puntos y tienes {estado.puntos}."
        )
    return costo


@accion
def iniciar_salto(estado, catalogo, res, destino: int):
    """Empieza el examen de salto. Los puntos se descuentan en este momento."""
    exigir_entero("destino", destino, minimo=1)
    costo = costo_salto(estado, catalogo, destino)
    gastar(estado, res, costo)
    distancia = destino - estado.nivel_actual
    estado.salto = SaltoEnCurso(
        origen=estado.nivel_actual, destino=destino, costo=costo,
        retos=distancia * catalogo.config.retos_salto_por_nivel,
    )
    res.sucesos.append("salto_iniciado")


@accion(durante_salto=True)
def resolver_salto(estado, catalogo, res, aciertos: int):
    """Cierra el examen de salto. Abandonarlo equivale a resolverlo con 0 aciertos."""
    salto = estado.salto
    if salto is None:
        raise AccionInvalida("sin_salto_en_curso", "No hay ningún examen de salto empezado.")
    exigir_entero("aciertos", aciertos, maximo=salto.retos)
    estado.salto = None
    registro = {
        "tipo": "salto", "origen": salto.origen, "destino": salto.destino,
        "costo": salto.costo, "aciertos": aciertos, "retos": salto.retos,
    }

    if not aprueba(aciertos, salto.retos, catalogo.config.aprobacion_salto):
        # Los puntos ya se descontaron; el nivel actual y su progreso no cambian.
        meta = salto.costo * catalogo.config.multiplicador_penalizacion
        estado.penalizacion = Penalizacion(invertido=salto.costo, meta=meta)
        estado.historial_saltos.append({**registro, "superado": False})
        res.sucesos += ["salto_fracasado", "penalizacion_activada"]
        return

    vidas = catalogo.config.vidas_por_nivel
    saltados = list(range(salto.origen + 1, salto.destino))
    if estado.estado_de(salto.origen) is not EstadoNivel.APROBADO:
        saltados.insert(0, salto.origen)  # el nivel actual sin aprobar también queda pendiente
    for numero in saltados:
        progreso = estado.niveles.setdefault(numero, ProgresoNivel(EstadoNivel.PENDIENTE, vidas))
        progreso.estado = EstadoNivel.PENDIENTE
    estado.niveles[salto.destino] = ProgresoNivel(EstadoNivel.ACTUAL, vidas)
    estado.nivel_actual = salto.destino
    estado.historial_saltos.append({**registro, "superado": True, "pendientes": saltados})
    dar_xp(estado, catalogo, res, catalogo.config.xp_salto_superado)
    dar_logro(estado, res, "salto_superado")
    res.sucesos.append("salto_superado")
