"""Puerta de entrada para el servidor: aplica acciones descritas con datos.

El navegador nunca envía cantidades de puntos, XP ni vidas. Envía qué hizo
(por ejemplo, "entregué la misión X y pasó las pruebas") y las reglas
calculan las consecuencias.
"""
from datetime import date

from . import economia, extras, progresion, saltos
from .errores import AccionInvalida
from .resultado import Resultado

# tipo de acción -> (función, campos obligatorios)
ACCIONES = {
    "entrar_nivel": (progresion.entrar_nivel, ("nivel",)),
    "entregar_mision": (progresion.entregar_mision, ("nivel", "mision", "correcta")),
    "rendir_evaluacion": (progresion.rendir_evaluacion, ("nivel", "aciertos")),
    "entregar_jefe": (progresion.entregar_jefe, ("saga", "requisitos_cumplidos")),
    "iniciar_salto": (saltos.iniciar_salto, ("destino",)),
    "resolver_salto": (saltos.resolver_salto, ("aciertos",)),
    "comprar_semilla": (economia.comprar_semilla, ("nivel",)),
    "comprar_pista": (economia.comprar_pista, ("nivel", "mision", "numero")),
    "completar_repaso": (economia.completar_repaso, ("nivel", "perfecto")),
    "completar_diaria": (extras.completar_diaria, ("fecha", "correcta")),
    "completar_evento": (extras.completar_evento, ("evento", "correcta")),
}
_TIPOS = {
    "nivel": int, "aciertos": int, "requisitos_cumplidos": int, "destino": int,
    "numero": int, "mision": str, "saga": str, "evento": str,
    "correcta": bool, "perfecto": bool,
}


def aplicar(estado, catalogo, accion: dict):
    """Aplica `{"tipo": ..., "id": ..., ...campos}` y devuelve (estado, resultado).

    Si el `id` ya se aplicó antes, no hace nada: así un envío repetido (por
    mala conexión o por dos dispositivos) nunca duplica recompensas ni castigos.
    """
    if not isinstance(accion, dict) or accion.get("tipo") not in ACCIONES:
        raise AccionInvalida("accion_desconocida", "No reconozco esa acción.")
    identificador = accion.get("id")
    if identificador is not None and identificador in estado.acciones:
        return estado, Resultado(duplicada=True)

    funcion, campos = ACCIONES[accion["tipo"]]
    extra = set(accion) - set(campos) - {"tipo", "id"}
    if extra:  # p. ej. alguien intenta enviar "puntos": 9999
        raise AccionInvalida("accion_mal_formada", f"Campos no permitidos: {sorted(extra)}.")
    argumentos = {}
    for campo in campos:
        if campo not in accion:
            raise AccionInvalida("accion_mal_formada", f"Falta el campo {campo!r}.")
        argumentos[campo] = _convertir(campo, accion[campo])

    nuevo, resultado = funcion(estado, catalogo, **argumentos)
    if identificador is not None:
        nuevo.acciones.add(identificador)
    return nuevo, resultado


def _convertir(campo: str, valor):
    if campo == "fecha":
        try:
            return date.fromisoformat(valor)
        except (TypeError, ValueError):
            raise AccionInvalida("dato_invalido", "La fecha no es válida.") from None
    esperado = _TIPOS[campo]
    if type(valor) is not esperado:
        raise AccionInvalida("dato_invalido", f"Valor no válido para {campo!r}: {valor!r}.")
    return valor
