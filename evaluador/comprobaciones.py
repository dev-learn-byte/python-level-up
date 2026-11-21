"""Decide si un ejercicio está bien resuelto y explica qué falló.

Se evalúa por comportamiento: se ejecuta el código y se mira qué variables
quedaron y qué se imprimió. Cualquier solución que funcione es válida.

Hay cuatro formas de evaluar:
- `evaluar_codigo`: misiones donde se escribe, completa o corrige código.
- `evaluar_prediccion`: misiones de "¿qué resultado da este código?".
- `evaluar_reto`: un reto de evaluación (de cualquiera de los dos tipos).
- `evaluar_jefe`: el proyecto de un jefe, requisito por requisito.
"""
from dataclasses import dataclass, field

from .ejecucion import Ejecucion, codigo_del_alumno, ejecutar

SIN_COMPLETAR = "Todavía no completaste `{nombre}`: cambia los tres puntos (...) por tu respuesta."


@dataclass
class ResultadoCaso:
    nombre: str
    fallos: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.fallos


@dataclass
class Informe:
    casos: list[ResultadoCaso]

    @property
    def aprobado(self) -> bool:
        return bool(self.casos) and all(caso.ok for caso in self.casos)

    @property
    def aciertos(self) -> int:
        return sum(caso.ok for caso in self.casos)

    def texto(self) -> str:
        """Explicación para mostrar al alumno."""
        if self.aprobado:
            return "¡Correcto! Todas las comprobaciones pasaron."
        lineas = []
        for caso in self.casos:
            for fallo in caso.fallos:
                lineas.append(f"[{caso.nombre}] {fallo}")
        return "\n".join(lineas)


def iguales(obtenido, esperado) -> bool:
    """Mismo valor y mismo tipo (5 y 5.0 no son iguales; True y 1 tampoco)."""
    if type(obtenido) is not type(esperado):
        return False
    if isinstance(esperado, float):
        return abs(obtenido - esperado) < 1e-9
    return obtenido == esperado


def _nombre_tipo(valor) -> str:
    return type(valor).__name__


def _comparar(ej: Ejecucion, esperado: dict, pista: str, mostrar_esperado: bool) -> list[str]:
    """Compara una ejecución con lo esperado y devuelve los fallos."""
    fallos = []
    cola = f" Pista: {pista}" if pista else ""

    def revisar(nombre):
        """Devuelve el valor de la variable, o anota por qué no se puede usar."""
        if nombre not in ej.variables:
            fallos.append(f"No encuentro la variable `{nombre}`. ¿La creaste con ese nombre exacto?")
        elif ej.variables[nombre] is ...:
            fallos.append(SIN_COMPLETAR.format(nombre=nombre))
        else:
            return True
        return False

    for nombre, valor in esperado.get("variables", {}).items():
        if not revisar(nombre):
            continue
        obtenido = ej.variables[nombre]
        if iguales(obtenido, valor):
            continue
        if type(obtenido) is not type(valor):
            fallos.append(
                f"`{nombre}` debería ser de tipo {_nombre_tipo(valor)}, "
                f"pero es de tipo {_nombre_tipo(obtenido)}.{cola}"
            )
        elif mostrar_esperado:
            fallos.append(f"`{nombre}` vale {obtenido!r}, pero se esperaba {valor!r}.{cola}")
        else:
            fallos.append(f"`{nombre}` no tiene el valor correcto (vale {obtenido!r}).{cola}")

    for nombre, tipo in esperado.get("tipos", {}).items():
        if revisar(nombre) and _nombre_tipo(ej.variables[nombre]) != tipo:
            fallos.append(
                f"`{nombre}` debería ser de tipo {tipo}, "
                f"pero es de tipo {_nombre_tipo(ej.variables[nombre])}.{cola}"
            )

    for nombre, clase in esperado.get("clases", {}).items():
        if revisar(nombre):
            valor = ej.variables[nombre]
            if not isinstance(valor, type) or valor.__name__ != clase:
                fallos.append(f"`{nombre}` no guarda el tipo correcto.{cola}")

    if "salida" in esperado:
        lineas = [str(linea).rstrip() for linea in esperado["salida"]]
        if ej.salida != lineas:
            if not ej.salida:
                fallos.append(f"Tu programa no imprimió nada. ¿Usaste print()?{cola}")
            elif mostrar_esperado:
                fallos.append(
                    "Lo que se imprime no coincide.\n"
                    f"   Se esperaba: {lineas}\n   Tu programa:  {ej.salida}{cola}"
                )
            else:
                fallos.append(f"Lo que se imprime no coincide (tu programa: {ej.salida}).{cola}")
    return fallos


def _esperado_de(caso: dict, referencia: str | None) -> dict:
    """Lo que debe cumplirse en un caso: escrito en él o calculado con la referencia."""
    esperado = {clave: caso[clave] for clave in ("variables", "tipos", "clases", "salida") if clave in caso}
    comparar = caso.get("comparar", [])
    if comparar or caso.get("comparar_salida"):
        if referencia is None:
            raise ValueError("este caso necesita la solución de referencia")
        modelo = ejecutar(referencia, caso.get("datos"), caso.get("entradas"))
        if modelo.error:
            raise ValueError(f"la solución de referencia falla: {modelo.error.texto()}")
        esperado.setdefault("variables", {}).update({n: modelo.variables[n] for n in comparar})
        if caso.get("comparar_salida"):
            esperado["salida"] = modelo.salida
    return esperado


def evaluar_codigo(codigo: str, casos: list[dict], referencia: str | None = None,
                   requiere: list[str] | tuple = (), mostrar_esperado: bool = True) -> Informe:
    """Ejecuta el código una vez por caso y comprueba el resultado de cada uno.

    Un caso puede traer `datos` y `entradas`, y lo esperado: `variables`,
    `tipos`, `clases`, `salida`, o bien `comparar` / `comparar_salida` para
    tomarlo de la solución de referencia.
    """
    resultados = []
    usado = codigo_del_alumno(codigo)
    faltan = [texto for texto in requiere if texto not in usado]
    for numero, caso in enumerate(casos or [{}], start=1):
        resultado = ResultadoCaso(caso.get("nombre", f"Prueba {numero}"))
        ej = ejecutar(codigo, caso.get("datos"), caso.get("entradas"))
        if ej.error:
            resultado.fallos.append(ej.error.texto())
        else:
            esperado = _esperado_de(caso, referencia)
            resultado.fallos += _comparar(ej, esperado, caso.get("pista", ""), mostrar_esperado)
            resultado.fallos += [f"Esta misión pide usar `{texto}` en tu código." for texto in faltan]
        resultados.append(resultado)
    return Informe(resultados)


def valor_mirado(pregunta: dict):
    """Ejecuta el código de una pregunta de predicción y devuelve la respuesta real."""
    ej = ejecutar(pregunta["codigo"], entradas=pregunta.get("entradas"))
    if ej.error:
        raise ValueError(f"el código de la pregunta falla: {ej.error.texto()}")
    mirar = pregunta["mirar"]
    if mirar == "salida":
        return "\n".join(ej.salida)
    if mirar.startswith("tipo:"):
        return _nombre_tipo(ej.variables[mirar[5:]])
    return ej.variables[mirar]


def evaluar_prediccion(codigo: str, preguntas: list[dict], nombres: list[str] | None = None) -> Informe:
    """Compara las respuestas del alumno con lo que el código realmente produce.

    El alumno guarda sus respuestas en `respuesta_1`, `respuesta_2`...
    La respuesta correcta no está escrita en ningún sitio: se calcula
    ejecutando el código de cada pregunta.
    """
    nombres = nombres or [f"respuesta_{n}" for n in range(1, len(preguntas) + 1)]
    ej = ejecutar(codigo)
    resultados = []
    for nombre, pregunta in zip(nombres, preguntas):
        resultado = ResultadoCaso(nombre)
        pista = pregunta.get("pista", "")
        cola = f" Pista: {pista}" if pista else ""
        if ej.error:
            resultado.fallos.append(ej.error.texto())
        elif nombre not in ej.variables:
            resultado.fallos.append(f"No encuentro la variable `{nombre}`.")
        elif ej.variables[nombre] is ...:
            resultado.fallos.append(SIN_COMPLETAR.format(nombre=nombre))
        else:
            correcta = valor_mirado(pregunta)
            obtenida = ej.variables[nombre]
            if isinstance(correcta, str) and isinstance(obtenida, str):
                obtenida = obtenida.strip()
            if not iguales(obtenida, correcta):
                if type(obtenida) is not type(correcta):
                    resultado.fallos.append(
                        f"La respuesta debería ser de tipo {_nombre_tipo(correcta)}, "
                        f"pero escribiste un dato de tipo {_nombre_tipo(obtenida)}.{cola}"
                    )
                else:
                    resultado.fallos.append(f"Esa no es la respuesta.{cola}")
        resultados.append(resultado)
    return Informe(resultados)


def evaluar_reto(reto: dict, codigo: str) -> Informe:
    """Evalúa un reto de evaluación. No muestra los valores esperados."""
    if reto["tipo"] == "predecir":
        return evaluar_prediccion(codigo, [reto], nombres=["respuesta"])
    casos = []
    for caso in reto.get("casos") or [{}]:
        casos.append({
            **caso,
            "comparar": reto.get("comparar", []),
            "comparar_salida": reto.get("salida", False),
        })
    return evaluar_codigo(codigo, casos, referencia=reto["solucion"],
                          requiere=reto.get("requiere", ()), mostrar_esperado=False)


def evaluar_jefe(codigo: str, casos: list[dict], requisitos: list[dict], referencia: str) -> Informe:
    """Evalúa el proyecto de un jefe: un resultado por requisito.

    Cada requisito se comprueba en todos los casos. Tipos de requisito:
    - `entradas = n`: el programa llama a input() exactamente n veces.
    - `lineas = n`: el programa imprime exactamente n líneas.
    - `linea = n`: la línea n de la salida coincide con la de referencia.
    """
    pares = []
    for caso in casos:
        alumno = ejecutar(codigo, caso.get("datos"), caso.get("entradas"))
        modelo = ejecutar(referencia, caso.get("datos"), caso.get("entradas"))
        if modelo.error:
            raise ValueError(f"la solución de referencia falla: {modelo.error.texto()}")
        pares.append((caso.get("nombre", "participante"), alumno, modelo))

    resultados = []
    for requisito in requisitos:
        resultado = ResultadoCaso(requisito["texto"])
        for nombre, alumno, modelo in pares:
            if alumno.error:
                resultado.fallos.append(f"Con {nombre}: {alumno.error.texto()}")
                break
            if not _cumple(requisito, alumno, modelo):
                resultado.fallos.append(f"No se cumple con {nombre}. Pista: {requisito['pista']}")
                break
        resultados.append(resultado)
    return Informe(resultados)


def _cumple(requisito: dict, alumno: Ejecucion, modelo: Ejecucion) -> bool:
    if "entradas" in requisito:
        return alumno.entradas_usadas == requisito["entradas"]
    if "lineas" in requisito:
        return len(alumno.salida) == requisito["lineas"]
    posicion = requisito["linea"] - 1
    if posicion >= len(alumno.salida):
        return False
    return alumno.salida[posicion] == modelo.salida[posicion]
