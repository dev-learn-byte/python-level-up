"""Órdenes de consola de la versión local. Solo muestra; no decide nada."""
import argparse
import sys

from nucleo import AccionInvalida, EstadoNivel, jefe_disponible, niveles_pendientes

from .partida import NoDisponible, Partida

AYUDA = """\
PYTHON LEVEL UP - versión local

  Ver cómo vas
    py jugar.py estado                 vidas, XP, puntos, mapa y siguiente paso
    py jugar.py misiones [nivel]       lista de misiones de un nivel

  Estudiar
    py jugar.py teoria [nivel]         la lección del nivel
    py jugar.py ejemplos [nivel]       dónde están los ejemplos y cómo ejecutarlos

  Misiones (y la mazmorra)
    py jugar.py mision <nombre>        muestra la misión y crea tu archivo
    py jugar.py practicar <nombre>     gratis: prueba tu código y explica los errores
    py jugar.py entregar <nombre>      oficial: si falla, cuesta una vida
    py jugar.py pista <nombre>         la primera es gratis; las demás cuestan 10 puntos

  Nivel
    py jugar.py evaluacion [nivel]             crea los archivos de los retos
    py jugar.py evaluacion [nivel] entregar    oficial: cada fallo cuesta una vida
    py jugar.py repaso [nivel] [entregar]      si sale perfecto, recuperas una vida
    py jugar.py semilla [nivel]                Semilla del Ermitaño: +1 vida por 50 puntos
    py jugar.py entrar <nivel>                 empieza un nivel desbloqueado

  Jefe y extras
    py jugar.py jefe [practicar|entregar|pista]
    py jugar.py diaria [entregar]
    py jugar.py eventos

Escribes tu código en la carpeta mis_soluciones/ con tu editor.
"""


def barra(valor: int, maximo: int) -> str:
    return "[" + "#" * valor + "." * (maximo - valor) + f"] {valor}/{maximo}"


def titulo_nivel(partida: Partida, numero: int) -> str:
    datos = partida.niveles[numero]["datos"]
    return f"Nivel {numero}: {datos['titulo']} ({datos['subtitulo']})"


def mostrar_informe(informe) -> None:
    if informe.aprobado:
        print("  Todas las comprobaciones pasaron.")
        return
    for caso in informe.casos:
        print(f"  [{'OK' if caso.ok else 'X '}] {caso.nombre}")
        for fallo in caso.fallos:
            for linea in fallo.splitlines():
                print(f"        {linea}")


def mostrar_resultado(partida: Partida, resultado, vidas: int | None = None) -> None:
    """Explica las consecuencias que decidió el núcleo."""
    if resultado.xp or resultado.puntos:
        print(f"  Recompensa: +{resultado.xp} XP, +{resultado.puntos} puntos")
    if resultado.puntos_gastados:
        print(f"  Gastaste {resultado.puntos_gastados} puntos. Te quedan {partida.estado.puntos}.")
    if resultado.vidas_perdidas:
        resto = "" if vidas is None else f" Te quedan {vidas}."
        cuantas = "1 vida" if resultado.vidas_perdidas == 1 else f"{resultado.vidas_perdidas} vidas"
        print(f"  Perdiste {cuantas}.{resto}")
    mensajes = {
        "recompensa_repetida": "Ya habías cobrado esta recompensa: no se paga dos veces.",
        "bono_racha": "¡Racha! Tres misiones nuevas seguidas: bono de puntos.",
        "nivel_reiniciado": "Te quedaste sin vidas: el nivel empieza de nuevo. Conservas tus XP y puntos.\n"
                            "  Tus archivos anteriores están en mis_soluciones/intentos/.",
        "evaluacion_aprobada": "¡Evaluación aprobada!",
        "evaluacion_reprobada": "Evaluación no superada.",
        "jefe_vencido": "¡Venciste al jefe!",
        "jefe_resiste": "El jefe sigue en pie: faltan requisitos por cumplir.",
        "jefe_reiniciado": "Te quedaste sin vidas contra el jefe: el combate empieza de nuevo.",
        "vida_recuperada": "Recuperaste una vida.",
        "repaso_con_fallos": "El repaso no salió perfecto: no hay vida extra esta vez.",
        "diaria_completada": "¡Misión diaria completada!",
        "diaria_fallida": "No es correcto. Puedes volver a intentarlo hoy, sin castigo.",
        "evento_completado": "¡Evento completado!",
        "evento_fallido": "No es correcto. Los eventos no cuestan vidas: inténtalo de nuevo.",
        "penalizacion_cumplida": "¡Penalización cumplida! Recuperaste el acceso a los saltos.",
    }
    for suceso in resultado.sucesos:
        if suceso in mensajes:
            print(f"  {mensajes[suceso]}")
        elif suceso.startswith("nivel_desbloqueado:"):
            numero = suceso.split(":")[1]
            print(f"  Nivel {numero} desbloqueado. Empiézalo con: py jugar.py entrar {numero}")
        elif suceso.startswith("jefe_disponible:"):
            print("  El jefe de la saga te espera: py jugar.py jefe")
        elif suceso.startswith("transformacion:"):
            print(f"  ¡TRANSFORMACIÓN! Ahora eres: {suceso.split(':', 1)[1]}")
        elif suceso.startswith("logro:"):
            print(f"  Logro desbloqueado: {suceso.split(':', 1)[1]}")


def siguiente_paso(partida: Partida) -> str:
    estado, numero = partida.estado, partida.estado.nivel_actual
    progreso = estado.niveles[numero]
    if progreso.estado is EstadoNivel.ACTUAL:
        for mision in partida.niveles[numero]["misiones"]:
            if mision["id"] not in progreso.entregadas:
                return f"py jugar.py mision {mision['id']}"
        return f"py jugar.py evaluacion {numero}"
    desbloqueados = [n for n, p in estado.niveles.items() if p.estado is EstadoNivel.DESBLOQUEADO]
    if desbloqueados:
        return f"py jugar.py entrar {min(desbloqueados)}"
    saga = partida.niveles[numero]["saga"]
    vencido = saga in estado.jefes and estado.jefes[saga].vencido
    if partida.sagas[saga]["jefe"] and jefe_disponible(estado, partida.catalogo, saga) and not vencido:
        return "py jugar.py jefe"
    return "py jugar.py diaria   (no hay más niveles por ahora)"


def orden_estado(partida: Partida, _) -> None:
    estado, numero = partida.estado, partida.estado.nivel_actual
    saga = partida.sagas[partida.niveles[numero]["saga"]]["datos"]
    progreso = estado.niveles[numero]
    print("=" * 60)
    print(f"  PYTHON LEVEL UP   Saga {saga['numero']}: {saga['nombre']}")
    print("=" * 60)
    print(f"  {titulo_nivel(partida, numero)}  [{progreso.estado.value}]")
    print(f"  Vidas:  {barra(progreso.vidas, partida.catalogo.config.vidas_por_nivel)}")
    print(f"  XP:     {estado.xp}")
    print(f"  Puntos: {estado.puntos}")
    print(f"  Transformación: {estado.transformaciones[-1] if estado.transformaciones else 'ninguna todavía'}")
    if estado.logros:
        print(f"  Logros: {', '.join(estado.logros)}")
    if estado.penalizacion:
        print(f"  Penalización activa: faltan {estado.penalizacion.faltan} puntos nuevos.")
    pendientes = niveles_pendientes(estado, partida.catalogo)
    if pendientes:
        print(f"  Niveles pendientes: {pendientes}")
    mapa = " | ".join(f"{n}: {estado.estado_de(n).value}" for n in partida.niveles)
    print(f"  Mapa: {mapa}")
    print()
    orden_misiones(partida, argparse.Namespace(nivel=numero))
    print()
    print(f"  Siguiente paso: {siguiente_paso(partida)}")


def orden_misiones(partida: Partida, args) -> None:
    numero = partida._nivel(args.nivel)
    progreso = partida.estado.niveles.get(numero)
    print(f"  Misiones del {titulo_nivel(partida, numero)}")
    for mision in partida.niveles[numero]["misiones"]:
        hecha = progreso is not None and (
            mision["id"] in progreso.entregadas or progreso.estado is EstadoNivel.APROBADO
        )
        donde = "celular o PC" if mision["dispositivo"] == "celular" else "mejor en PC"
        print(f"   [{'OK' if hecha else '  '}] {mision['id']:<28} {mision['titulo']}  ({mision['anime']}, {donde})")


def orden_teoria(partida: Partida, args) -> None:
    print(partida.teoria(args.nivel))


def orden_ejemplos(partida: Partida, args) -> None:
    ruta = partida.ruta_ejemplos(args.nivel)
    print(f"  Los ejemplos están en:\n    {ruta}")
    print(f"  Ábrelos con tu editor y ejecútalos con:\n    py \"{ruta}\"")


def _mostrar_ejercicio(ejercicio: dict, ruta, creado: bool) -> None:
    print(f"  {ejercicio['titulo'].upper()}   ({ejercicio['anime']})")
    print(f"  Recompensa: {ejercicio['xp']} XP y {ejercicio['puntos']} puntos")
    print()
    print(ejercicio["enunciado"].strip())
    for indice, pregunta in enumerate(ejercicio.get("preguntas", []), start=1):
        print(f"\n  Pregunta {indice}: {pregunta['texto']}")
        for linea in pregunta["codigo"].strip().splitlines():
            print(f"      {linea}")
    print()
    print(f"  Tu archivo{' (recién creado)' if creado else ''}:\n    {ruta}")


def orden_mision(partida: Partida, args) -> None:
    ejercicio, ruta, creado = partida.abrir(args.nombre)
    _mostrar_ejercicio(ejercicio, ruta, creado)
    print(f"  Cuando lo tengas: py jugar.py practicar {args.nombre}")


def orden_practicar(partida: Partida, args) -> None:
    informe = partida.practicar(args.nombre)
    print("  PRÁCTICA (no cuenta ni cuesta vidas)")
    mostrar_informe(informe)
    if informe.aprobado:
        print(f"  Si ya estás seguro: py jugar.py entregar {args.nombre}")


def _vidas_de(partida: Partida, nombre: str) -> int | None:
    tipo, numero, _ = partida.ejercicio(nombre)
    return partida.estado.niveles[numero].vidas if tipo == "mision" else None


def orden_entregar(partida: Partida, args) -> None:
    entrega = partida.entregar(args.nombre)
    print("  ENTREGA OFICIAL")
    mostrar_informe(entrega.informe)
    mostrar_resultado(partida, entrega.resultado, _vidas_de(partida, args.nombre))


def orden_pista(partida: Partida, args) -> None:
    pistas, pagado = partida.pista(args.nombre)
    if pagado:
        print(f"  Pagaste {pagado} puntos. Te quedan {partida.estado.puntos}.")
    for indice, pista in enumerate(pistas, start=1):
        print(f"  Pista {indice}: {pista}")


def orden_semilla(partida: Partida, args) -> None:
    numero = partida._nivel(args.nivel)
    resultado = partida.semilla(numero)
    mostrar_resultado(partida, resultado)
    print(f"  Vidas: {barra(partida.estado.niveles[numero].vidas, 5)}")


def orden_entrar(partida: Partida, args) -> None:
    partida.entrar(args.nivel)
    print(f"  Comienza el {titulo_nivel(partida, args.nivel)}")
    print(f"  Lee la lección con: py jugar.py teoria {args.nivel}")


def orden_repaso(partida: Partida, args) -> None:
    numero = partida._nivel(args.nivel)
    if args.accion == "entregar":
        entrega = partida.repaso_entregar(numero)
        mostrar_informe(entrega.informe)
        mostrar_resultado(partida, entrega.resultado)
        return
    _, ruta = partida.repaso_abrir(numero)
    print(f"  Repaso del nivel {numero}: tres preguntas y un solo intento.")
    print(f"  Responde en:\n    {ruta}")
    print(f"  Después: py jugar.py repaso {numero} entregar")


def orden_evaluacion(partida: Partida, args) -> None:
    numero = partida._nivel(args.nivel)
    if args.accion != "entregar":
        carpeta, cantidad, _ = partida.evaluacion_abrir(numero)
        print(f"  EVALUACIÓN DEL NIVEL {numero}: {cantidad} retos.")
        print("  Se aprueba con 70 %. Cada reto fallado cuesta una vida.")
        print(f"  Vidas: {barra(partida.estado.niveles[numero].vidas, 5)}")
        print(f"  Resuelve los archivos reto_01.py a reto_{cantidad:02d}.py en:\n    {carpeta}")
        print(f"  Cuando termines: py jugar.py evaluacion {numero} entregar")
        return
    sin_resolver = partida.evaluacion_sin_resolver(numero)
    if sin_resolver and not args.igual:
        print(f"  Todavía hay retos sin resolver: {', '.join(sin_resolver)}")
        print("  Cada uno contaría como fallo y costaría una vida.")
        print(f"  Si quieres entregar igualmente: py jugar.py evaluacion {numero} entregar --igual")
        return
    informes, resultado = partida.evaluacion_entregar(numero)
    aciertos = sum(informe.aprobado for informe in informes)
    print(f"  RESULTADO: {aciertos} de {len(informes)} retos correctos")
    for indice, informe in enumerate(informes, start=1):
        print(f"  Reto {indice:02d}: {'correcto' if informe.aprobado else 'fallado'}")
        if not informe.aprobado:
            for caso in informe.casos:
                for fallo in caso.fallos:
                    print(f"        {fallo.splitlines()[0]}")
    mostrar_resultado(partida, resultado, partida.estado.niveles[numero].vidas)


def orden_jefe(partida: Partida, args) -> None:
    if args.accion == "practicar":
        print("  PRÁCTICA CONTRA EL JEFE (no cuesta vidas)")
        mostrar_informe(partida.jefe_practicar())
    elif args.accion == "entregar":
        saga, _ = partida.jefe()
        entrega = partida.jefe_entregar()
        print("  COMBATE OFICIAL")
        for caso in entrega.informe.casos:
            print(f"  [{'OK' if caso.ok else 'X '}] {caso.nombre}")
            for fallo in caso.fallos:
                print(f"        {fallo.splitlines()[0]}")
        mostrar_resultado(partida, entrega.resultado, partida.estado.jefes[saga].vidas)
    elif args.accion == "pista":
        for indice, pista in enumerate(partida.jefe_pista(), start=1):
            print(f"  Pista {indice}: {pista}")
    else:
        jefe, ruta, creado = partida.jefe_abrir()
        print(f"  JEFE: {jefe['nombre'].upper()} - {jefe['titulo']}")
        print(f"  Recompensa: {jefe['xp']} XP, {jefe['puntos']} puntos y la transformación {jefe['transformacion']}")
        print()
        print(jefe["enunciado"].strip())
        print()
        print(f"  Tu archivo{' (recién creado)' if creado else ''}:\n    {ruta}")
        print("  Practica gratis con: py jugar.py jefe practicar")


def orden_diaria(partida: Partida, args) -> None:
    if args.accion == "entregar":
        entrega = partida.diaria_entregar()
        mostrar_informe(entrega.informe)
        mostrar_resultado(partida, entrega.resultado)
        return
    pregunta, ruta = partida.diaria_abrir()
    print(f"  MISIÓN DIARIA (15 puntos y 5 XP)\n  {pregunta['texto']}")
    for linea in pregunta["codigo"].strip().splitlines():
        print(f"      {linea}")
    print(f"  Responde en:\n    {ruta}\n  Después: py jugar.py diaria entregar")


def orden_eventos(partida: Partida, _) -> None:
    for evento in partida.eventos.values():
        hecho = f"evento:{evento['id']}" in partida.estado.recompensas
        requisito = evento.get("requiere_nivel", 0)
        abierto = not requisito or partida.estado.estado_de(requisito) is EstadoNivel.APROBADO
        situacion = "completado" if hecho else "disponible" if abierto else f"se abre al aprobar el nivel {requisito}"
        print(f"  {evento['id']:<22} {evento['titulo']} ({evento['anime']}) - {situacion}")
    print("  Se juegan igual que una misión: py jugar.py mision <nombre>")


class Analizador(argparse.ArgumentParser):
    """No imprime los mensajes en inglés de argparse: `main` da el aviso."""

    def error(self, mensaje):
        raise SystemExit(2)


def _nivel_y_accion(args) -> None:
    """Acepta `evaluacion 1 entregar`, `evaluacion entregar` o `evaluacion`."""
    args.nivel, args.accion = None, None
    for palabra in args.palabras:
        if palabra.isdigit() and args.nivel is None:
            args.nivel = int(palabra)
        elif palabra == "entregar" and args.accion is None:
            args.accion = palabra
        else:
            raise SystemExit(2)


def crear_analizador() -> argparse.ArgumentParser:
    analizador = Analizador(prog="jugar.py", add_help=False)
    ordenes = analizador.add_subparsers(dest="orden")

    def orden(nombre, funcion, *argumentos):
        sub = ordenes.add_parser(nombre, add_help=False)
        for argumento in argumentos:
            argumento(sub)
        sub.set_defaults(funcion=funcion)

    nivel = lambda sub: sub.add_argument("nivel", nargs="?", type=int)
    nombre = lambda sub: sub.add_argument("nombre")
    accion = lambda *opciones: (lambda sub: sub.add_argument("accion", nargs="?", choices=opciones))

    orden("estado", orden_estado)
    orden("misiones", orden_misiones, nivel)
    orden("teoria", orden_teoria, nivel)
    orden("ejemplos", orden_ejemplos, nivel)
    orden("mision", orden_mision, nombre)
    orden("practicar", orden_practicar, nombre)
    orden("entregar", orden_entregar, nombre)
    orden("pista", orden_pista, nombre)
    orden("semilla", orden_semilla, nivel)
    orden("entrar", orden_entrar, lambda sub: sub.add_argument("nivel", type=int))
    palabras = lambda sub: sub.add_argument("palabras", nargs="*")
    orden("repaso", orden_repaso, palabras)
    orden("evaluacion", orden_evaluacion, palabras,
          lambda sub: sub.add_argument("--igual", action="store_true"))
    orden("jefe", orden_jefe, accion("practicar", "entregar", "pista"))
    orden("diaria", orden_diaria, accion("entregar"))
    orden("eventos", orden_eventos)
    return analizador


def main(argumentos: list[str] | None = None, partida: Partida | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    argumentos = sys.argv[1:] if argumentos is None else argumentos
    if not argumentos or argumentos[0] in ("ayuda", "-h", "--help"):
        print(AYUDA)
        return 0
    try:
        args = crear_analizador().parse_args(argumentos)
        if hasattr(args, "palabras"):
            _nivel_y_accion(args)
    except SystemExit:
        print("  No entendí esa orden. Mira las disponibles con: py jugar.py ayuda")
        return 2
    try:
        args.funcion(partida or Partida(), args)
    except NoDisponible as aviso:
        print(f"  {aviso}")
        return 1
    except AccionInvalida as aviso:
        print(f"  No se puede: {aviso.mensaje}")
        return 1
    return 0
