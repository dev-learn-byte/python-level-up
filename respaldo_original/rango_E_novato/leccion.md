# Rango E: Novato — Variables, tipos y operadores

Anime del rango: **Dragon Ball** (con un cameo de *Rompiendo el hielo*).

## 1. Una variable es una cápsula con etiqueta

Bulma guarda cosas en cápsulas y les pone un nombre. Una variable es eso: una caja con nombre.

```python
nombre = "Goku"      # texto            -> str
poder = 9001         # número entero    -> int
altura = 1.75        # número decimal   -> float
es_saiyajin = True   # verdadero/falso  -> bool
```

`type(poder)` te dice qué tipo de cosa hay dentro de la cápsula.

## 2. Hablar y escuchar: `print` e `input`

```python
print("¡Kame Hame Ha!")
print(f"{nombre} tiene {poder} de poder")   # f-string: mete variables en el texto
```

`input()` **siempre** devuelve texto. El scouter lee `"9001"`, no `9001`.
Para hacer cuentas hay que convertirlo:

```python
poder = int("9001")     # texto -> entero
texto = str(9001)       # entero -> texto
```

## 3. Operadores: las técnicas básicas

| Operador | Qué hace | Ejemplo | Resultado |
|---|---|---|---|
| `+` `-` `*` | sumar, restar, multiplicar | `3000 * 3` | `9000` |
| `/` | dividir (da decimal) | `7 / 2` | `3.5` |
| `//` | dividir sin decimales | `7 // 2` | `3` |
| `%` | lo que sobra | `7 % 2` | `1` |
| `**` | potencia | `2 ** 3` | `8` |
| `>` `<` `>=` `<=` `==` `!=` | comparar (da `True`/`False`) | `9001 > 9000` | `True` |

Si hay 7 semillas del ermitaño y 2 guerreros: a cada uno le tocan `7 // 2 = 3` y sobra `7 % 2 = 1`.

## 4. Trucos con texto

```python
"  hola  ".strip()      # "hola"   (quita espacios de los lados)
"goku".upper()          # "GOKU"
"goku".capitalize()     # "Goku"
len("Vegeta")           # 6
```

## Tu turno

1. Ejecuta `python rango_E_novato/ejemplos.py` y juega con los valores.
2. Abre `misiones.py` y completa cada función (cambia el `pass` por tu código).
3. Ejecuta `python sistema.py` para que el Sistema te dé tu XP.
