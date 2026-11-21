# Nivel 2: Operadores e input

*El caparazón de tortuga*

El Maestro Roshi te cuelga un caparazón de 20 kilos en la espalda. Hoy toca
hacer cuentas: cuánto corres, cuánto repartes y cuánto te falta.

## Para niños

### Los operadores son movimientos de entrenamiento

| Movimiento | Símbolo | Ejemplo | Resultado |
|---|---|---|---|
| Sumar | `+` | `5 + 2` | `7` |
| Restar | `-` | `5 - 2` | `3` |
| Multiplicar | `*` | `5 * 2` | `10` |
| Dividir | `/` | `5 / 2` | `2.5` |
| Repartir en partes iguales | `//` | `7 // 2` | `3` |
| Lo que sobra al repartir | `%` | `7 % 2` | `1` |
| Elevar (multiplicar varias veces) | `**` | `2 ** 3` | `8` |

Imagina que tienes 7 semillas del ermitaño para 2 guerreros:

```python
semillas = 7
guerreros = 2
print(semillas // guerreros)   # 3 para cada uno
print(semillas % guerreros)    # sobra 1
```

### Primero se multiplica, después se suma

Igual que en el colegio. Si quieres otro orden, usa paréntesis:

```python
print(2 + 3 * 4)     # 14: primero 3 * 4
print((2 + 3) * 4)   # 20: primero el paréntesis
```

### Comparar es hacer una pregunta de sí o no

La respuesta siempre es `True` (sí) o `False` (no):

```python
poder = 8000
print(poder > 9000)    # False
```

| Pregunta | Símbolo |
|---|---|
| ¿Es mayor? | `>` |
| ¿Es menor? | `<` |
| ¿Es mayor o igual? | `>=` |
| ¿Es menor o igual? | `<=` |
| ¿Es igual? | `==` |
| ¿Es distinto? | `!=` |

Cuidado: `=` **guarda** un valor y `==` **pregunta** si dos valores son iguales.

### Juntar preguntas: and, or, not

- `and` (y): es verdad solo si **las dos** cosas son verdad.
- `or` (o): es verdad si **al menos una** es verdad.
- `not` (no): le da la vuelta.

```python
poder = 12000
edad = 12
print(poder > 9000 and edad >= 18)   # False: la segunda no se cumple
print(poder > 9000 or edad >= 18)    # True: la primera sí se cumple
print(not poder > 9000)              # False
```

### input() es una pregunta del Maestro Roshi

`input()` detiene el programa y espera a que escribas algo:

```python
nombre = input("¿Cómo te llamas? ")
print("Bienvenido,", nombre)
```

Hay una regla que no falla nunca: **lo que llega de `input()` siempre es
texto**, aunque escribas un número. Para hacer cuentas hay que convertirlo:

```python
vueltas = int(input("¿Cuántas vueltas diste? "))
print(vueltas * 2)
```

## Así lo dice un programador

- **Operadores aritméticos**: `+ - * / // % **`.
  - `/` es la división real y **siempre** devuelve un `float`: `6 / 2` es `3.0`.
  - `//` es la división entera y `%` es el módulo (el resto).
- **Precedencia**: primero `**`, luego `* / // %`, y al final `+ -`. Los
  paréntesis cambian el orden.
- **Operadores de comparación**: `== != < > <= >=`. Devuelven un `bool`.
- **Operadores lógicos**: `and`, `or`, `not`. `not` se evalúa primero, luego
  `and` y al final `or`.
- **Conversión de tipos** (*casting*):

| Función | Convierte a | Ejemplo | Resultado |
|---|---|---|---|
| `int()` | Entero | `int("25")` | `25` |
| `float()` | Decimal | `float("2.5")` | `2.5` |
| `str()` | Texto | `str(25)` | `"25"` |

  `int()` aplicado a un decimal corta la parte decimal: `int(3.9)` es `3`.

- **Asignación aumentada**: `poder += 10` es una forma corta de
  `poder = poder + 10`. También existen `-=`, `*=` y `/=`.
- En esta etapa damos por hecho que el usuario escribe datos correctos. Más
  adelante aprenderás a comprobarlos.

## Errores típicos

**1. Hacer cuentas con lo que llega de input()**

```python
vueltas = input("Vueltas: ")
print(vueltas + 5)
```

`TypeError`. `vueltas` es un texto y no se puede sumar con un número. Falta
`int()`.

**2. Confundir `=` con `==`**

```python
gano = puntos = 10    # guarda 10 en las dos variables
gano = puntos == 10   # pregunta si puntos vale 10
```

**3. Olvidar los paréntesis**

```python
promedio = 8 + 6 / 2     # 11.0, no 7.0
promedio = (8 + 6) / 2   # 7.0
```

## Resumen

- `//` reparte y `%` dice lo que sobra.
- Las comparaciones responden `True` o `False`.
- `input()` siempre entrega texto: conviértelo con `int()` o `float()`.
- `=` guarda, `==` compara.
