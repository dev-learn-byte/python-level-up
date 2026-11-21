"""MISIONES DEL RANGO E.

Cambia cada `pass` por tu código. Usa `return` para devolver la respuesta
(no `print`). Luego ejecuta desde la carpeta sistema_leveling:

    python sistema.py
"""


def presentar_guerrero(nombre, poder):
    """Misión 1 (10 XP). Devuelve el texto de presentación.

    presentar_guerrero("Goku", 9001) -> "Soy Goku y mi poder es 9001"
    """
    pass


def poder_del_equipo(poder_goku, poder_vegeta):
    """Misión 2 (10 XP). Devuelve la suma de los dos poderes.

    poder_del_equipo(9000, 8500) -> 17500
    """
    pass


def kaioken(poder, multiplicador):
    """Misión 3 (10 XP). Devuelve el poder multiplicado.

    kaioken(3000, 4) -> 12000
    """
    pass


def repartir_semillas(semillas, guerreros):
    """Misión 4 (10 XP). Devuelve DOS valores: cuántas semillas le tocan
    a cada guerrero y cuántas sobran.

    repartir_semillas(7, 2) -> (3, 1)
    Pista: return a, b
    """
    pass


def supera_los_9000(poder):
    """Misión 5 (10 XP). Devuelve True si el poder es MAYOR que 9000.

    supera_los_9000(9001) -> True
    supera_los_9000(9000) -> False
    """
    pass


def leer_scouter(lectura):
    """Misión 6 (10 XP). El scouter entrega el poder como TEXTO.
    Devuélvelo como número entero.

    leer_scouter("9001") -> 9001
    """
    pass


def limpiar_mensaje(mensaje):
    """Misión 7 (10 XP). Himuro escribió su mensaje nervioso y con espacios
    de más. Quita los espacios de los lados y pon la primera letra en mayúscula.

    limpiar_mensaje("   gracias por tu ayuda  ") -> "Gracias por tu ayuda"
    """
    pass


def ficha_de_combate(nombre, lectura_scouter, multiplicador):
    """JEFE FINAL (30 XP). Junta todo lo aprendido.

    - nombre llega con espacios y en minúsculas: límpialo y ponlo en MAYÚSCULAS.
    - lectura_scouter es TEXTO: conviértelo a entero.
    - El poder final es la lectura por el multiplicador.
    - Devuelve exactamente este formato:

    ficha_de_combate("  goku ", "3000", 4)
        -> "GOKU | Poder: 12000 | ¿Supera 9000?: True"
    """
    pass
