# Versión local (consola)

Una forma provisional de jugar la Saga 1 en tu computadora mientras se
construye la aplicación web. Usa el mismo núcleo de reglas, el mismo
evaluador y el mismo contenido: no duplica ninguna regla.

## Qué necesitas

- Windows con PowerShell (también funciona en macOS y Linux).
- Python 3.11 o superior. Compruébalo con `py --version`.
- Git. Compruébalo con `git --version`.
- Un editor de código, por ejemplo Visual Studio Code.

No hay que instalar ninguna biblioteca.

## Instalación

```powershell
cd $HOME\Documents
git clone -b motor-y-saga-1 https://github.com/dev-learn-byte/python-level-up
cd python-level-up
git clone https://github.com/dev-learn-byte/python-level-up-privado contenido_privado
py jugar.py estado
```

El segundo `git clone` descarga el contenido privado (soluciones y
evaluaciones). Git te pedirá iniciar sesión en GitHub porque ese repositorio
es privado. Sin él puedes practicar, pero no entregar ni presentar
evaluaciones.

**No abras la carpeta `contenido_privado`: contiene las respuestas.** Si
usas Visual Studio Code, el proyecto ya la oculta del explorador y del
buscador.

## Cómo se juega

Todo se hace con `py jugar.py <orden>` desde la carpeta del proyecto. La
lista completa está en `py jugar.py ayuda`.

Una sesión típica:

```powershell
py jugar.py estado                    # cómo vas y cuál es el siguiente paso
py jugar.py teoria                    # la lección del nivel actual
py jugar.py mision n1_ficha_goku      # muestra la misión y crea tu archivo
# ...editas mis_soluciones\n1_ficha_goku.py con tu editor...
py jugar.py practicar n1_ficha_goku   # gratis: te explica los errores
py jugar.py entregar n1_ficha_goku    # oficial: si falla, cuesta una vida
```

Cuando entregues las seis misiones de un nivel:

```powershell
py jugar.py evaluacion                # crea diez archivos, uno por reto
# ...resuelves mis_soluciones\evaluacion_nivel_1\reto_01.py a reto_10.py...
py jugar.py evaluacion entregar       # se aprueba con 7 de 10
py jugar.py entrar 2                  # empieza el nivel siguiente
```

| Qué quieres hacer | Orden |
|---|---|
| Ver vidas, XP, puntos y mapa | `estado` |
| Leer la lección o ver los ejemplos | `teoria`, `ejemplos` |
| Trabajar una misión | `mision`, `practicar`, `entregar` |
| Pedir una pista (la primera es gratis; después, 10 puntos) | `pista <nombre>` |
| Recuperar una vida por 50 puntos | `semilla` |
| Recuperar una vida con un repaso perfecto | `repaso`, `repaso entregar` |
| Presentar la evaluación del nivel | `evaluacion`, `evaluacion entregar` |
| Enfrentar al Maestro Roshi | `jefe`, `jefe practicar`, `jefe entregar` |
| Misión diaria | `diaria`, `diaria entregar` |
| Ver la mazmorra y otros eventos | `eventos` |

## Dónde queda cada cosa

| Ruta | Contenido | ¿Se sube a GitHub? |
|---|---|---|
| `mis_soluciones/` | Tus archivos de trabajo | No |
| `mis_soluciones/intentos/` | Archivos de intentos anteriores | No |
| `progreso.json` | Tu progreso | No |
| `progreso.json.bak` | La versión anterior del progreso | No |
| `contenido_privado/` | Soluciones y evaluaciones | No |

Para hacer una copia de seguridad, copia `progreso.json` y `mis_soluciones/`
a otro sitio.

Para actualizar el juego:

```powershell
git pull
git -C contenido_privado pull
```

## Restricciones de esta versión

**No es un entorno aislado.** Tu código se ejecuta en un proceso aparte con
un límite de 10 segundos, y eso basta para que un bucle infinito no cuelgue
el juego. Pero ese proceso tiene los mismos permisos que tú: puede leer y
borrar archivos y usar la red. Por eso:

- Ejecuta solo código escrito por ti.
- No pegues código de otras personas ni de internet sin entenderlo.
- Esta versión no debe usarse para evaluar código de terceros ni ponerse en
  un servidor.

**Es provisional y el progreso es solo local.**

- El progreso vive en esta computadora y no se sincroniza con ningún otro
  dispositivo.
- No está garantizado que pase a la aplicación web como progreso oficial. El
  juego guarda el código de cada entrega para que el servidor pueda
  reevaluarlo en el futuro, pero esa importación aún no está diseñada.
- `progreso.json` es un archivo que se puede editar a mano. Es un sistema de
  honor.

**Diferencias con el diseño final.**

- La fecha de la misión diaria sale del reloj de tu computadora.
- Las evaluaciones no tienen límite de tiempo.
- Las pistas del jefe y de los eventos son gratis.
- Los saltos de nivel con puntos no están disponibles: solo existe la Saga 1
  y sus exámenes de salto aún no están escritos.
- Las respuestas están en tu disco, dentro de `contenido_privado/`.

## Problemas frecuentes

| Mensaje | Qué hacer |
|---|---|
| `py` no se reconoce | Instala Python desde python.org y marca "Add python.exe to PATH" |
| "necesita Python 3.11 o superior" | Instala una versión más reciente de Python |
| "necesitan el contenido privado" | Falta el segundo `git clone` de la instalación |
| "no está guardado como UTF-8" | En tu editor, guarda el archivo con codificación UTF-8 |
| "Tiempo agotado" | Tu código se quedó repitiendo algo sin parar |
