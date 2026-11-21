"""Python Level Up, versión local para la consola.

Uso:  py jugar.py ayuda
"""
import sys

if sys.version_info < (3, 11):
    sys.exit("Python Level Up necesita Python 3.11 o superior. Tienes " + sys.version.split()[0])

from local.consola import main

if __name__ == "__main__":
    sys.exit(main())
