"""Traduce los errores de Python a una explicación sencilla.

Cada explicación dice qué pasó, por qué suele ocurrir y hacia dónde mirar,
sin dar la solución.
"""
import traceback
from dataclasses import dataclass

ARCHIVO = "<tu código>"


class SinEntradas(Exception):
    """El programa pidió con input() más datos de los disponibles."""


class FaltaMarca(Exception):
    """El código ya no tiene la línea que separa los datos de la respuesta."""


@dataclass
class ErrorAlumno:
    tipo: str            # nombre del error de Python, p. ej. "NameError"
    detalle: str         # mensaje original de Python
    linea: int | None
    explicacion: str     # explicación sencilla

    def texto(self) -> str:
        donde = f" en la línea {self.linea}" if self.linea else ""
        return f"{self.tipo}{donde}: {self.explicacion}"


EXPLICACIONES = {
    "SyntaxError": (
        "Python no pudo leer esa línea porque no está escrita con sus reglas. "
        "Suele pasar por un nombre de variable no permitido (con espacios, guiones "
        "o que empieza por un número), comillas o paréntesis sin cerrar. "
        "Mira esa línea símbolo por símbolo."
    ),
    "NameError": (
        "Usaste un nombre que Python todavía no conoce. Pasa cuando la variable "
        "no se ha creado antes, cuando su nombre está escrito distinto, o cuando "
        "a un texto le faltan las comillas. Compara el nombre letra por letra."
    ),
    "TypeError": (
        "Mezclaste dos tipos de datos que no se pueden combinar así, por ejemplo "
        "un texto con un número. Recuerda que input() siempre entrega texto. "
        "Revisa de qué tipo es cada dato de esa línea."
    ),
    "ValueError": (
        "Intentaste convertir un dato que no tiene la forma correcta, por ejemplo "
        "pasar a número entero un texto con letras o con decimales. "
        "Mira qué texto exacto está recibiendo la conversión."
    ),
    "ZeroDivisionError": (
        "Dividiste entre cero, y eso no existe en matemáticas. "
        "Revisa qué valor tiene el número por el que divides."
    ),
    "IndexError": (
        "Pediste una posición que no existe en el texto. Las posiciones empiezan "
        "en 0, así que la última es la longitud menos 1. Cuenta las letras."
    ),
    "AttributeError": (
        "Le pediste a un dato algo que ese tipo no sabe hacer, por ejemplo "
        ".upper() a un número. Revisa el tipo del dato y cómo se escribe el método."
    ),
    "SinEntradas": (
        "Tu programa pidió con input() más datos de los que debía. "
        "Cuenta cuántas veces llamas a input()."
    ),
    "FaltaMarca": (
        "Falta la línea '# === TU CÓDIGO ===' que separa los datos de tu respuesta. "
        "No la borres: escribe tu código debajo de ella."
    ),
}
GENERICA = (
    "Tu código se detuvo por un error. Lee el mensaje de Python con calma: "
    "casi siempre señala la línea y la causa."
)


def explicar(error: BaseException) -> ErrorAlumno:
    tipo = type(error).__name__
    if isinstance(error, SyntaxError):
        linea = error.lineno
        detalle = error.msg or ""
    else:
        pasos = [p for p in traceback.extract_tb(error.__traceback__) if p.filename == ARCHIVO]
        linea = pasos[-1].lineno if pasos else None
        detalle = str(error)
    return ErrorAlumno(tipo, detalle, linea, EXPLICACIONES.get(tipo, GENERICA))
