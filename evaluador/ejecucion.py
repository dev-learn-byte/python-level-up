"""Ejecuta el código de un ejercicio con datos y teclado simulados.

Este módulo NO aísla el código: lo ejecuta en el mismo proceso. El
aislamiento (navegador o entorno cerrado del servidor) se añade alrededor,
en las etapas 3 y 4. Aquí solo se decide qué significa "ejecutar un ejercicio".
"""
import builtins
import contextlib
import io
from dataclasses import dataclass

from .errores import ARCHIVO, ErrorAlumno, FaltaMarca, SinEntradas, explicar

MARCA_CODIGO = "# === TU CÓDIGO"


@dataclass
class Ejecucion:
    variables: dict          # variables que quedaron al terminar
    salida: list[str]        # líneas impresas con print()
    entradas_usadas: int     # veces que se llamó a input()
    error: ErrorAlumno | None = None


def ejecutar(codigo: str, datos: dict | None = None, entradas: list[str] | None = None) -> Ejecucion:
    """Ejecuta `codigo` y devuelve lo que pasó.

    - `datos`: valores que sustituyen a los de la sección DATOS del ejercicio.
      Así una respuesta escrita "a mano" falla cuando los datos cambian.
    - `entradas`: lo que el alumno "escribiría" en cada input().
    """
    pendientes = list(entradas or [])
    usadas = 0

    def entrada_simulada(mensaje=""):
        nonlocal usadas
        if not pendientes:
            raise SinEntradas()
        usadas += 1
        return pendientes.pop(0)

    integrados = dict(vars(builtins))
    integrados["input"] = entrada_simulada
    espacio = {"__builtins__": integrados, "__name__": "__main__"}
    impreso = io.StringIO()
    error = None
    try:
        compile(codigo, ARCHIVO, "exec")  # primero, que todo el código se pueda leer
        partes = _partir(codigo) if datos else [codigo]
        with contextlib.redirect_stdout(impreso):
            for numero, parte in enumerate(partes):
                exec(compile(parte, ARCHIVO, "exec"), espacio)
                if numero == 0 and datos:
                    espacio.update(datos)
    except (Exception, SystemExit) as problema:
        error = explicar(problema)

    variables = {n: v for n, v in espacio.items() if not n.startswith("__")}
    salida = [linea.rstrip() for linea in impreso.getvalue().splitlines()]
    return Ejecucion(variables, salida, usadas, error)


def _partir(codigo: str) -> list[str]:
    """Separa la sección DATOS de la respuesta, conservando los números de línea."""
    lineas = codigo.splitlines()
    for indice, linea in enumerate(lineas):
        if linea.strip().startswith(MARCA_CODIGO):
            antes = "\n".join(lineas[:indice])
            despues = "\n" * indice + "\n".join(lineas[indice:])
            return [antes, despues]
    raise FaltaMarca()


def codigo_del_alumno(codigo: str) -> str:
    """La parte escrita por el alumno, sin comentarios (para revisar qué usa)."""
    lineas = codigo.splitlines()
    for indice, linea in enumerate(lineas):
        if linea.strip().startswith(MARCA_CODIGO):
            lineas = lineas[indice + 1:]
            break
    return "\n".join(linea.split("#")[0] for linea in lineas)
