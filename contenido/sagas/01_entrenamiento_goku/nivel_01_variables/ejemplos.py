# Ejemplos del Nivel 1. Ejecútalos, cambia valores y mira qué pasa.

# --- Crear variables ---
nombre = "Goku"        # str: texto, siempre entre comillas
poder = 9001           # int: número entero
altura = 1.75          # float: número con decimales
es_saiyajin = True     # bool: verdadero o falso

# --- Mostrar ---
print(nombre)
print(nombre, "tiene", poder, "de poder")   # print puede mostrar varias cosas

# --- Preguntar el tipo ---
print(type(nombre))        # <class 'str'>
print(type(poder))         # <class 'int'>
print(type(altura))        # <class 'float'>
print(type(es_saiyajin))   # <class 'bool'>

# --- Cambiar el valor ---
esferas = 3
print("Tengo", esferas, "esferas")
esferas = esferas + 2      # usa el valor anterior para calcular el nuevo
print("Ahora tengo", esferas)

# --- Copiar un valor ---
poder_inicial = poder      # se copia el valor que hay en ese momento
poder = 150000             # cambiar `poder` no cambia `poder_inicial`
print(poder_inicial, poder)

# --- Un número y un texto que parece número no son lo mismo ---
numero = 9001
texto = "9001"
print(type(numero), type(texto))
