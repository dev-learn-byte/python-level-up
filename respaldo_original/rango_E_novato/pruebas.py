"""Pruebas del Rango E. No hace falta modificar este archivo."""


def igual(obtenido, esperado):
    if obtenido is None:
        raise AssertionError("pendiente (la función aún no devuelve nada)")
    assert obtenido == esperado and type(obtenido) is type(esperado), (
        f"esperaba {esperado!r} pero obtuve {obtenido!r}"
    )


def m1(m):
    igual(m.presentar_guerrero("Goku", 9001), "Soy Goku y mi poder es 9001")
    igual(m.presentar_guerrero("Krilin", 75), "Soy Krilin y mi poder es 75")


def m2(m):
    igual(m.poder_del_equipo(9000, 8500), 17500)
    igual(m.poder_del_equipo(1, 2), 3)


def m3(m):
    igual(m.kaioken(3000, 4), 12000)
    igual(m.kaioken(500, 10), 5000)


def m4(m):
    igual(m.repartir_semillas(7, 2), (3, 1))
    igual(m.repartir_semillas(10, 5), (2, 0))


def m5(m):
    igual(m.supera_los_9000(9001), True)
    igual(m.supera_los_9000(9000), False)
    igual(m.supera_los_9000(5), False)


def m6(m):
    igual(m.leer_scouter("9001"), 9001)
    igual(m.leer_scouter("42"), 42)


def m7(m):
    igual(m.limpiar_mensaje("   gracias por tu ayuda  "), "Gracias por tu ayuda")
    igual(m.limpiar_mensaje("hola"), "Hola")


def jefe(m):
    igual(m.ficha_de_combate("  goku ", "3000", 4), "GOKU | Poder: 12000 | ¿Supera 9000?: True")
    igual(m.ficha_de_combate("krilin", "75", 2), "KRILIN | Poder: 150 | ¿Supera 9000?: False")


MISIONES = [
    ("Misión 1: Presentación", 10, m1),
    ("Misión 2: Poder del equipo", 10, m2),
    ("Misión 3: Kaioken", 10, m3),
    ("Misión 4: Semillas del ermitaño", 10, m4),
    ("Misión 5: ¡Más de 9000!", 10, m5),
    ("Misión 6: El scouter", 10, m6),
    ("Misión 7: El mensaje de Himuro", 10, m7),
    ("JEFE FINAL: Ficha de combate", 30, jefe),
]
