# Ejemplos del Nivel 3. Ejecútalos, cambia valores y mira qué pasa.

ataque = "kamehameha"

# --- Posiciones (índices) ---
print(ataque[0])       # k: la primera
print(ataque[-1])      # a: la última
print(len(ataque))     # 10 letras

# --- Rebanadas ---
print(ataque[0:4])     # kame
print(ataque[:4])      # kame
print(ataque[4:])      # hameha
print(ataque[::-1])    # ahemahemak: al revés

# --- Métodos: devuelven un texto nuevo ---
print(ataque.upper())             # KAMEHAMEHA
print(ataque.capitalize())        # Kamehameha
print(ataque.replace("a", "4"))   # k4meh4meh4
print(ataque.count("a"))          # 3
print(ataque.startswith("kame"))  # True

# --- El texto original no cambia ---
ataque.upper()
print(ataque)                     # sigue en minúsculas
grito = ataque.upper()            # hay que guardar el resultado
print(grito)

# --- Limpiar un texto ---
lectura = "   Poder: 9001   "
print(lectura.strip())            # sin espacios a los lados
print(lectura.strip().lower())    # métodos encadenados

# --- Preguntar si un texto contiene otro ---
mensaje = "el radar detecta dos esferas"
print("radar" in mensaje)         # True
print("nave" in mensaje)          # False
print(len(mensaje.split()))       # 5 palabras

# --- f-strings ---
nombre = "Goku"
poder = 9001
altura = 1.756
print(f"{nombre} tiene {poder} de poder")
print(f"Poder con separador de miles: {poder:,}")
print(f"Altura con dos decimales: {altura:.2f}")
print(f"El doble de poder: {poder * 2}")
