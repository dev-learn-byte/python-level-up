# Nivel 1: Variables y tipos

*El primer día en Kame House*

El Maestro Roshi no te deja lanzar un Kamehameha el primer día. Primero hay
que aprender a guardar las cosas en su sitio.

## Para niños

### Una variable es una cápsula con etiqueta

Bulma guarda todo en cápsulas Hoi-Poi. Cada cápsula tiene una **etiqueta**
por fuera y **una cosa** por dentro.

En Python, esa cápsula se llama **variable**:

```python
poder = 9001
```

- `poder` es la etiqueta (el nombre).
- `=` significa "guarda esto aquí dentro".
- `9001` es lo que queda guardado.

Cuando escribes el nombre, Python abre la cápsula y te da lo que hay dentro:

```python
print(poder)    # muestra 9001
```

`print()` sirve para **mostrar** cosas en la pantalla.

### Puedes cambiar lo que hay dentro

Si guardas otra cosa en la misma cápsula, lo anterior desaparece:

```python
esferas = 3
esferas = 5
print(esferas)  # muestra 5
```

También puedes usar lo que ya había para calcular lo nuevo:

```python
esferas = 3
esferas = esferas + 2   # toma el 3, le suma 2 y guarda 5
```

### Hay cuatro clases de cosas

| Clase | Qué guarda | Ejemplo |
|---|---|---|
| Número entero | Números sin decimales | `9001` |
| Número decimal | Números con punto | `1.75` |
| Texto | Letras, siempre entre comillas | `"Goku"` |
| Verdadero o falso | Solo dos valores | `True`, `False` |

Las **comillas** son muy importantes: `"Goku"` es un texto, pero `Goku` sin
comillas es el nombre de una cápsula que Python va a buscar.

### Los comentarios son notas para ti

Todo lo que va después de `#` es una nota. Python no la lee:

```python
poder = 9001   # el poder de Goku al llegar Vegeta
```

## Así lo dice un programador

- **Variable**: un nombre que apunta a un valor guardado en la memoria.
- **Asignación**: la instrucción `nombre = valor`. Primero se calcula lo de
  la derecha y luego se guarda con el nombre de la izquierda.
- **Tipo de dato**: la clase de un valor. Los cuatro básicos son:

| Tipo | Nombre en Python | Ejemplo |
|---|---|---|
| Entero | `int` | `9001` |
| Decimal (coma flotante) | `float` | `1.75` |
| Cadena de texto | `str` | `"Goku"` |
| Booleano | `bool` | `True` |

- `type(valor)` te dice de qué tipo es un valor:

```python
altura = 1.75
print(type(altura))   # <class 'float'>
```

- Python tiene **tipado dinámico**: una misma variable puede guardar primero
  un número y después un texto. El tipo pertenece al valor, no al nombre.
- `True` y `False` se escriben con la primera letra en mayúscula.

### Reglas para nombrar variables

1. Solo letras, números y guion bajo (`_`).
2. No pueden empezar por un número.
3. No pueden tener espacios ni guiones (`-`).
4. Mayúsculas y minúsculas cuentan: `poder` y `Poder` son distintas.

Por costumbre, en Python se escriben en minúsculas y separando las palabras
con guion bajo: `poder_maximo`. A ese estilo se le llama *snake_case*.

## Errores típicos

**1. Olvidar las comillas de un texto**

```python
nombre = Goku
```

`NameError: name 'Goku' is not defined`. Python cree que `Goku` es otra
variable y no la encuentra.

**2. Un nombre que no cumple las reglas**

```python
2do_guerrero = "Vegeta"
```

`SyntaxError`. Un nombre no puede empezar por un número.

**3. Confundir un número con un texto que parece número**

```python
poder = "9001"   # esto es un texto, no un número
```

Se ve igual en pantalla, pero con un texto no puedes hacer cuentas. Si
dudas, pregunta con `type(poder)`.

## Resumen

- Una variable guarda un valor con un nombre: `nombre = valor`.
- Los tipos básicos son `int`, `float`, `str` y `bool`.
- `print()` muestra y `type()` dice el tipo.
- Los textos siempre van entre comillas.
