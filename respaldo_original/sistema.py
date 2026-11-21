"""EL SISTEMA: revisa tus misiones y te dice tu rango.

Uso (desde la carpeta sistema_leveling):
    python sistema.py
"""
import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).parent

# (XP necesaria, rango) de menor a mayor
RANGOS = [
    (0, "E - Novato"),
    (100, "D - Guerrero Z"),
    (200, "C - Estudiante de la U.A."),
    (300, "B - Aventurero"),
    (400, "A - Héroe profesional"),
    (500, "S - Super Saiyajin"),
    (600, "Monarca - Ultra Instinto"),
]


def cargar(ruta):
    """Importa un archivo .py a partir de su ruta."""
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def rango_actual(xp):
    nombre = RANGOS[0][1]
    for minimo, rango in RANGOS:
        if xp >= minimo:
            nombre = rango
    return nombre


def revisar_carpeta(carpeta):
    """Devuelve (xp_ganada, xp_posible) de una carpeta de rango."""
    print(f"\n=== {carpeta.name} ===")
    try:
        misiones = cargar(carpeta / "misiones.py")
    except Exception as error:  # error de sintaxis, etc.
        print(f"  [!] Tu misiones.py tiene un error: {type(error).__name__}: {error}")
        misiones = None
    pruebas = cargar(carpeta / "pruebas.py")

    ganada = posible = 0
    for titulo, xp, prueba in pruebas.MISIONES:
        posible += xp
        if misiones is None:
            continue
        try:
            prueba(misiones)
        except AssertionError as fallo:
            print(f"  [ ] {titulo}  ->  {fallo}")
        except Exception as error:
            print(f"  [x] {titulo}  ->  {type(error).__name__}: {error}")
        else:
            ganada += xp
            print(f"  [OK] {titulo}  +{xp} XP")
    return ganada, posible


def main():
    carpetas = sorted(c for c in AQUI.glob("rango_*") if (c / "pruebas.py").exists())
    total = posible = 0
    for carpeta in carpetas:
        ganada, maximo = revisar_carpeta(carpeta)
        total += ganada
        posible += maximo

    llenos = 20 * total // posible if posible else 0
    print("\n" + "=" * 44)
    print(f"  XP: [{'#' * llenos}{'.' * (20 - llenos)}] {total}/{posible}")
    print(f"  RANGO ACTUAL: {rango_actual(total)}")
    print("=" * 44)
    if total == posible:
        print("  ¡Has subido de nivel! Pide el siguiente rango.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
