# Nivel 3: Cadenas de texto

*Los mensajes del Gran Patriarca*

Los mensajes que llegan de otros planetas vienen con ruido, al revés o con
letras de más. Hoy aprendes a trabajar con textos.

## Para niños

### Un texto es un collar de perlas

Cada letra es una perla, y cada perla tiene un número. Se empieza a contar
**desde 0**:

```
 G   o   k   u
 0   1   2   3
```

Para mirar una perla, escribes su número entre corchetes:

```python
nombre = "Goku"
print(nombre[0])    # G
print(nombre[3])    # u
```

También puedes contar desde el final con números negativos:

```python
print(nombre[-1])   # u  (la última)
print(nombre[-2])   # k  (la penúltima)
```

### Cortar un trozo del collar

Con dos números separados por dos puntos sacas un trozo. Empieza en el
primero y **se detiene justo antes** del segundo:

```python
ataque = "kamehameha"
print(ataque[0:4])   # kame
print(ataque[:4])    # kame  (si falta el primero, empieza al principio)
print(ataque[4:])    # hameha  (si falta el segundo, llega hasta el final)
```

### ¿Cuántas perlas hay?

```python
print(len("Goku"))   # 4
```

### Las técnicas que los textos ya saben

Un texto sabe hacer cosas solo. Se le piden con un punto:

| Técnica | Qué hace | Ejemplo | Resultado |
|---|---|---|---|
| `.upper()` | Todo en mayúsculas | `"goku".upper()` | `"GOKU"` |
| `.lower()` | Todo en minúsculas | `"GOKU".lower()` | `"goku"` |
| `.capitalize()` | Solo la primera en mayúscula | `"gOKU".capitalize()` | `"Goku"` |
| `.title()` | Cada palabra con mayúscula inicial | `"son goku".title()` | `"Son Goku"` |
| `.strip()` | Quita los espacios de los lados | `"  hola  ".strip()` | `"hola"` |
| `.replace(a, b)` | Cambia un trozo por otro | `"na-mek".replace("-", "")` | `"namek"` |
| `.count(x)` | Cuenta cuántas veces aparece | `"banana".count("a")` | `3` |

### Mezclar texto y variables

Pon una `f` delante de las comillas y mete las variables entre llaves:

```python
nombre = "Goku"
poder = 9001
print(f"{nombre} tiene {poder} de poder")
```

A esto se le llama **f-string**, y es la forma más cómoda de armar mensajes.

## Así lo dice un programador

- **Cadena** (`str`): una secuencia ordenada de caracteres.
- **Índice**: la posición de un carácter. El primero es `0` y el último es
  `len(texto) - 1`, o también `-1`.
- **Rebanada** (*slice*): `texto[inicio:fin:paso]`. Incluye `inicio` y
  excluye `fin`. Con paso `-1` se recorre al revés: `texto[::-1]` invierte
  el texto.
- **Método**: una función que pertenece a un tipo de dato y se llama con un
  punto: `texto.upper()`.
- **Inmutabilidad**: una cadena no se puede modificar. Los métodos
  **devuelven una cadena nueva** y dejan intacta la original:

```python
nombre = "goku"
nombre.upper()            # crea "GOKU", pero nadie lo guarda
print(nombre)             # goku
nombre = nombre.upper()   # ahora sí se guarda
```

- Los métodos se pueden **encadenar**: `texto.strip().lower()` primero quita
  los espacios y después pasa a minúsculas.
- **Pertenencia**: `"radar" in mensaje` responde `True` o `False`.
- Otros métodos útiles: `.startswith(x)` y `.endswith(x)` preguntan cómo
  empieza o termina un texto. `.split()` separa un texto en palabras, así que
  `len(frase.split())` cuenta las palabras.
- **Formato dentro de una f-string**: después de dos puntos se indica cómo
  mostrar el valor.

| Formato | Qué hace | Ejemplo | Resultado |
|---|---|---|---|
| `:.1f` | Un decimal | `f"{3.14159:.1f}"` | `3.1` |
| `:.2f` | Dos decimales | `f"{3.14159:.2f}"` | `3.14` |
| `:,` | Separador de miles | `f"{9001:,}"` | `9,001` |

- Dentro de las llaves puede ir cualquier expresión: `f"{poder * 2}"` o
  `f"{nombre.upper()}"`.

## Errores típicos

**1. Pedir una posición que no existe**

```python
palabra = "radar"
print(palabra[5])
```

`IndexError`. Tiene 5 letras, así que las posiciones van de 0 a 4.

**2. Creer que el método cambia la variable**

```python
nombre = "goku"
nombre.upper()
print(nombre)   # sigue siendo goku
```

Hay que guardar el resultado: `nombre = nombre.upper()`.

**3. Olvidar la `f` de la f-string**

```python
print("Hola {nombre}")    # muestra las llaves tal cual
print(f"Hola {nombre}")   # muestra el valor
```

## Resumen

- Las posiciones empiezan en 0 y `-1` es la última.
- `texto[a:b]` corta desde `a` hasta justo antes de `b`.
- Los métodos devuelven un texto nuevo: guarda el resultado.
- Las f-strings mezclan texto y variables: `f"{nombre}: {poder:,}"`.
