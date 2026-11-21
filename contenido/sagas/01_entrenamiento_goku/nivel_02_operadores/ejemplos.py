# Ejemplos del Nivel 2. Ejecútalos, cambia valores y mira qué pasa.

# --- Operadores aritméticos ---
poder = 3000
print(poder + 500)     # sumar
print(poder * 4)       # multiplicar, como el Kaioken x4
print(poder / 7)       # dividir: siempre da un decimal
print(2 ** 10)         # elevar: 2 multiplicado 10 veces

# --- Repartir y ver lo que sobra ---
semillas = 7
guerreros = 2
print(semillas // guerreros)   # 3 para cada uno
print(semillas % guerreros)    # sobra 1

# --- El orden de las operaciones ---
print(2 + 3 * 4)       # 14
print((2 + 3) * 4)     # 20

# --- Comparaciones: responden True o False ---
print(poder > 9000)
print(poder == 3000)
print(poder != 3000)

# --- Juntar preguntas ---
edad = 12
print(poder > 1000 and edad >= 18)   # las dos deben cumplirse
print(poder > 1000 or edad >= 18)    # basta con una
print(not edad >= 18)                # le da la vuelta

# --- Forma corta de actualizar ---
poder += 500           # igual que poder = poder + 500
print(poder)

# --- Preguntar con input() y convertir ---
vueltas = int(input("¿Cuántas vueltas diste? "))   # el texto pasa a entero
print("El doble sería", vueltas * 2)

# --- Conversiones ---
print(int("25") + 1)       # 26
print(float("2.5") * 2)    # 5.0
print(str(25) + " años")   # unir un número con un texto
print(int(3.9))            # 3: corta los decimales
