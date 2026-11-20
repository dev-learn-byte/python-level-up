"""Ejemplos del Rango E. Ejecútalo y cambia valores para experimentar."""

nombre = "Goku"
poder = 3000
es_saiyajin = True

print(f"{nombre} tiene {poder} de poder. ¿Saiyajin? {es_saiyajin}")
print("Tipos:", type(nombre), type(poder), type(es_saiyajin))

# Kaioken x3
poder_kaioken = poder * 3
print(f"Con Kaioken x3: {poder_kaioken}")
print("¿Es más de 9000?", poder_kaioken > 9000)

# Repartir semillas del ermitaño
semillas, guerreros = 7, 2
print(f"Tocan {semillas // guerreros} a cada uno y sobra {semillas % guerreros}")

# El scouter entrega texto: hay que convertirlo para sumar
lectura = "9001"
print("Lectura + 1 =", int(lectura) + 1)

# Texto
print("  me alegra verte  ".strip().capitalize())
