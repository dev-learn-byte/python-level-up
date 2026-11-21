"""Niveles, entregas, evaluaciones y jefes.

Practicar no aparece aquí a propósito: es gratis y no cambia el progreso.
Las vidas solo se pierden en entregas finales, evaluaciones y jefes.
"""
from .economia import dar_logro, dar_puntos, nivel_jugable, recompensar
from .errores import AccionInvalida
from .estado import EstadoNivel, ProgresoJefe, ProgresoNivel
from .resultado import accion, exigir_entero


def aprueba(aciertos: int, total: int, porcentaje_minimo: int) -> bool:
    """¿Los aciertos alcanzan el porcentaje? (con enteros, sin redondeos)."""
    return aciertos * 100 >= porcentaje_minimo * total


def _desbloquear(estado, catalogo, res, numero) -> None:
    if numero is not None and catalogo.existe(numero):
        if estado.estado_de(numero) is EstadoNivel.BLOQUEADO:
            estado.niveles[numero] = ProgresoNivel(
                EstadoNivel.DESBLOQUEADO, catalogo.config.vidas_por_nivel
            )
            res.sucesos.append(f"nivel_desbloqueado:{numero}")


def _perder_vidas(progreso, res, cantidad: int) -> None:
    perdidas = min(cantidad, progreso.vidas)
    progreso.vidas -= perdidas
    res.vidas_perdidas += perdidas


def _reiniciar_nivel(progreso, catalogo, res) -> None:
    """Sin vidas: el nivel empieza de cero. XP y puntos no se tocan."""
    progreso.entregadas.clear()
    progreso.vidas = catalogo.config.vidas_por_nivel
    progreso.intentos += 1
    progreso.semilla_usada = False
    progreso.repaso_usado = False
    _alternar_version(progreso)
    res.sucesos.append("nivel_reiniciado")


def _alternar_version(progreso) -> None:
    progreso.version_evaluacion = "B" if progreso.version_evaluacion == "A" else "A"


@accion
def entrar_nivel(estado, catalogo, res, nivel: int):
    """Empieza un nivel desbloqueado: pasa a ser el nivel actual."""
    catalogo.nivel(nivel)
    if estado.estado_de(nivel) is not EstadoNivel.DESBLOQUEADO:
        raise AccionInvalida(
            "nivel_no_desbloqueado",
            f"El nivel {nivel} está {estado.estado_de(nivel).value}.",
        )
    estado.niveles[nivel].estado = EstadoNivel.ACTUAL
    estado.nivel_actual = nivel
    res.sucesos.append("nivel_iniciado")


@accion
def entregar_mision(estado, catalogo, res, nivel: int, mision: str, correcta: bool):
    """Entrega final de una misión. Si falla, cuesta una vida."""
    progreso = nivel_jugable(estado, catalogo, nivel)
    datos = catalogo.mision(nivel, mision)
    if mision in progreso.entregadas:
        raise AccionInvalida("mision_ya_entregada", "Esa misión ya está entregada.")

    if not correcta:
        estado.racha_entregas = 0
        _perder_vidas(progreso, res, 1)
        res.sucesos.append("mision_fallida")
        if progreso.vidas == 0:
            _reiniciar_nivel(progreso, catalogo, res)
        return

    progreso.entregadas.add(mision)
    res.sucesos.append("mision_superada")
    if recompensar(estado, catalogo, res, f"mision:{mision}", datos.xp, datos.puntos):
        # La racha solo cuenta misiones nuevas, para que repetir no dé bonos.
        estado.racha_entregas += 1
        if estado.racha_entregas % catalogo.config.racha_para_bono == 0:
            dar_puntos(estado, res, catalogo.config.bono_racha)
            res.sucesos.append("bono_racha")


@accion
def rendir_evaluacion(estado, catalogo, res, nivel: int, aciertos: int):
    """Evaluación del nivel: cada fallo cuesta una vida; se aprueba con 70 %."""
    progreso = nivel_jugable(estado, catalogo, nivel)
    datos = catalogo.nivel(nivel)
    exigir_entero("aciertos", aciertos, maximo=datos.retos_evaluacion)
    faltantes = {m.id for m in datos.misiones} - progreso.entregadas
    if faltantes:
        raise AccionInvalida(
            "misiones_pendientes",
            f"Antes de la evaluación faltan {len(faltantes)} misiones por entregar.",
        )

    _perder_vidas(progreso, res, datos.retos_evaluacion - aciertos)
    if progreso.vidas == 0:
        res.sucesos.append("evaluacion_reprobada")
        _reiniciar_nivel(progreso, catalogo, res)
        return
    if not aprueba(aciertos, datos.retos_evaluacion, catalogo.config.aprobacion_evaluacion):
        _alternar_version(progreso)  # se repite solo la evaluación, con otros datos
        res.sucesos.append("evaluacion_reprobada")
        return

    progreso.estado = EstadoNivel.APROBADO
    res.sucesos.append("evaluacion_aprobada")
    bono = progreso.vidas * catalogo.config.puntos_por_vida_restante
    recompensar(
        estado, catalogo, res, f"evaluacion:{nivel}",
        datos.xp_evaluacion, datos.puntos_evaluacion + bono,
    )
    if progreso.vidas == catalogo.config.vidas_por_nivel:
        dar_logro(estado, res, "evaluacion_sin_perder_vidas")

    if catalogo.es_ultimo_de_saga(nivel) and catalogo.jefe(datos.saga):
        if jefe_disponible(estado, catalogo, datos.saga):
            res.sucesos.append(f"jefe_disponible:{datos.saga}")
    elif catalogo.es_ultimo_de_saga(nivel):
        _desbloquear(estado, catalogo, res, catalogo.primer_nivel_de_saga_siguiente(datos.saga))
    else:
        _desbloquear(estado, catalogo, res, nivel + 1)


# --- Jefes ---

def motivo_jefe_bloqueado(estado, catalogo, saga: str) -> str | None:
    """Devuelve por qué no se puede enfrentar al jefe, o None si se puede."""
    jefe = catalogo.jefe(saga)
    if jefe is None:
        return "jefe_inexistente"
    aprobado = lambda n: estado.estado_de(n) is EstadoNivel.APROBADO
    if not all(aprobado(n) for n in catalogo.niveles_de(saga)):
        return "saga_incompleta"
    if jefe.final:
        if not all(aprobado(n) for n in catalogo.numeros):
            return "niveles_pendientes"
        otros = [j for j in catalogo.jefes() if j.saga != saga]
        if not all(j.saga in estado.jefes and estado.jefes[j.saga].vencido for j in otros):
            return "jefes_pendientes"
    return None


def jefe_disponible(estado, catalogo, saga: str) -> bool:
    return motivo_jefe_bloqueado(estado, catalogo, saga) is None


@accion
def entregar_jefe(estado, catalogo, res, saga: str, requisitos_cumplidos: int):
    """Entrega del proyecto del jefe. Si falta algún requisito, cuesta una vida."""
    motivo = motivo_jefe_bloqueado(estado, catalogo, saga)
    if motivo:
        raise AccionInvalida(motivo, f"Aún no puedes enfrentar al jefe de {saga!r}.")
    jefe = catalogo.jefe(saga)
    exigir_entero("requisitos_cumplidos", requisitos_cumplidos, maximo=jefe.requisitos)
    progreso = estado.jefes.setdefault(saga, ProgresoJefe(catalogo.config.vidas_por_jefe))
    if progreso.vencido:
        raise AccionInvalida("jefe_ya_vencido", "Ya venciste a este jefe.")

    if requisitos_cumplidos < jefe.requisitos:
        _perder_vidas(progreso, res, 1)
        res.sucesos.append("jefe_resiste")
        if progreso.vidas == 0:  # se repite solo el jefe, no la saga
            progreso.vidas = catalogo.config.vidas_por_jefe
            progreso.intentos += 1
            res.sucesos.append("jefe_reiniciado")
        return

    progreso.vencido = True
    res.sucesos.append("jefe_vencido")
    recompensar(estado, catalogo, res, f"jefe:{saga}", jefe.xp, jefe.puntos)
    estado.transformaciones.append(jefe.transformacion)
    res.sucesos.append(f"transformacion:{jefe.transformacion}")
    dar_logro(estado, res, f"saga_completa:{saga}")
    if progreso.vidas == catalogo.config.vidas_por_jefe and progreso.intentos == 1:
        dar_logro(estado, res, "jefe_sin_perder_vidas")
    _desbloquear(estado, catalogo, res, catalogo.primer_nivel_de_saga_siguiente(saga))
