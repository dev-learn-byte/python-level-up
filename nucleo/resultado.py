"""Qué pasó al aplicar una acción, y el envoltorio común de las acciones."""
import copy
from dataclasses import dataclass, field
from functools import wraps

from .errores import AccionInvalida


@dataclass
class Resultado:
    xp: int = 0                 # XP ganados en esta acción
    puntos: int = 0             # puntos ganados
    puntos_gastados: int = 0
    vidas_perdidas: int = 0
    sucesos: list[str] = field(default_factory=list)  # p. ej. "nivel_reiniciado"
    duplicada: bool = False     # la acción ya se había aplicado antes

    def ocurrio(self, suceso: str) -> bool:
        return suceso in self.sucesos


def accion(funcion=None, *, durante_salto: bool = False):
    """Convierte `f(estado, catalogo, resultado, ...)` en una acción pura.

    La acción trabaja sobre una copia: devuelve `(estado_nuevo, resultado)` y
    nunca modifica el estado recibido. Si la regla no lo permite, lanza
    `AccionInvalida` y no cambia nada.

    Mientras hay un examen de salto empezado solo se admiten las acciones
    marcadas con `durante_salto=True`: el examen se termina antes de seguir.
    """

    def decorar(funcion):
        @wraps(funcion)
        def envoltura(estado, catalogo, *args, **kwargs):
            if estado.salto is not None and not durante_salto:
                raise AccionInvalida(
                    "salto_en_curso", "Termina primero tu examen de salto."
                )
            nuevo = copy.deepcopy(estado)
            resultado = Resultado()
            funcion(nuevo, catalogo, resultado, *args, **kwargs)
            return nuevo, resultado

        return envoltura

    return decorar(funcion) if funcion else decorar


def exigir_entero(nombre: str, valor, minimo: int = 0, maximo: int | None = None) -> None:
    """Rechaza datos que no sean enteros dentro del rango esperado."""
    valido = isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo
    if valido and maximo is not None:
        valido = valor <= maximo
    if not valido:
        raise AccionInvalida("dato_invalido", f"Valor no válido para {nombre}: {valor!r}.")
