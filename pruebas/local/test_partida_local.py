"""La versión local: jugar la Saga 1 desde archivos y guardar el progreso.

Casi todas las pruebas necesitan el repositorio privado; sin él se omiten.
"""
from datetime import date

import pytest

from evaluador import valor_mirado
from evaluador.contenido import PUBLICO, ruta_privada
from local import aislado
from local.consola import main
from local.partida import NoDisponible, Partida
from local.trabajador import TRABAJOS
from nucleo import AccionInvalida, EstadoNivel
from nucleo.cargador import leer_toml

PRIVADO = ruta_privada()
con_privado = pytest.mark.skipif(PRIVADO is None, reason="falta el contenido privado")
HOY = date(2026, 11, 21)


def directo(tipo, **datos):
    """Evalúa en el mismo proceso: más rápido para las pruebas."""
    return TRABAJOS[tipo](**datos)


@pytest.fixture
def partida(tmp_path):
    return Partida(datos=tmp_path, privado=PRIVADO, hoy=lambda: HOY, evaluar=directo)


def solucion(partida, identificador):
    tipo, numero, _ = partida.ejercicio(identificador)
    return partida._privado_de(tipo, numero, identificador)["solucion"]


def resolver(partida, identificador):
    """Escribe la solución de referencia en el archivo de trabajo y la entrega."""
    _, ruta, _ = partida.abrir(identificador)
    ruta.write_text(solucion(partida, identificador), encoding="utf-8")
    return partida.entregar(identificador)


def resolver_evaluacion(partida, numero, fallar=0):
    carpeta, cantidad, _ = partida.evaluacion_abrir(numero)
    retos = partida._retos(numero)
    for indice, reto in enumerate(retos, start=1):
        if indice <= fallar:
            continue   # se queda con la plantilla sin resolver
        codigo = f"respuesta = {valor_mirado(reto)!r}" if reto["tipo"] == "predecir" else reto["solucion"]
        (carpeta / f"reto_{indice:02d}.py").write_text(codigo, encoding="utf-8")
    return partida.evaluacion_entregar(numero)


def aprobar_nivel(partida, numero):
    if partida.estado.estado_de(numero) is EstadoNivel.DESBLOQUEADO:
        partida.entrar(numero)
    for mision in partida.niveles[numero]["misiones"]:
        resolver(partida, mision["id"])
    return resolver_evaluacion(partida, numero)


# --- Misiones ---

def test_abrir_una_mision_crea_el_archivo_y_no_pisa_tu_trabajo(partida):
    mision, ruta, creado = partida.abrir("n1_ficha_goku")
    assert creado and ruta.read_text(encoding="utf-8").strip() == mision["plantilla"].strip()
    ruta.write_text("nombre = 'mi avance'", encoding="utf-8")
    _, _, creado = partida.abrir("n1_ficha_goku")
    assert not creado and "mi avance" in ruta.read_text(encoding="utf-8")


def test_practicar_es_gratis_y_no_guarda_nada(partida):
    partida.abrir("n1_ficha_goku")
    informe = partida.practicar("n1_ficha_goku")
    assert not informe.aprobado
    assert partida.estado.niveles[1].vidas == 5
    assert not partida.archivo.exists()


def test_practicar_sin_haber_abierto_la_mision_lo_explica(partida):
    with pytest.raises(NoDisponible, match="py jugar.py mision n1_ficha_goku"):
        partida.practicar("n1_ficha_goku")


def test_una_mision_que_no_existe_lo_explica(partida):
    with pytest.raises(NoDisponible, match="No conozco"):
        partida.abrir("n9_inventada")


@con_privado
def test_entregar_mal_cuesta_una_vida_y_entregar_bien_da_recompensa(partida):
    partida.abrir("n1_ficha_goku")
    entrega = partida.entregar("n1_ficha_goku")
    assert not entrega.informe.aprobado and entrega.resultado.vidas_perdidas == 1
    assert partida.estado.niveles[1].vidas == 4

    entrega = resolver(partida, "n1_ficha_goku")
    assert entrega.informe.aprobado
    assert (partida.estado.xp, partida.estado.puntos) == (10, 10)


@con_privado
def test_no_se_puede_entregar_dos_veces_ni_un_nivel_bloqueado(partida):
    resolver(partida, "n1_ficha_goku")
    with pytest.raises(AccionInvalida) as error:
        partida.entregar("n1_ficha_goku")
    assert error.value.codigo == "mision_ya_entregada"
    partida.abrir("n2_kaioken")
    with pytest.raises(AccionInvalida) as error:
        partida.entregar("n2_kaioken")
    assert error.value.codigo == "nivel_no_jugable"
    assert (partida.estado.xp, partida.estado.niveles[1].vidas) == (10, 5)


@con_privado
def test_cada_entrega_guarda_el_codigo_para_poder_reevaluarlo(partida):
    partida.abrir("n1_ficha_goku")
    partida.entregar("n1_ficha_goku")
    resolver(partida, "n1_ficha_goku")
    entregas = partida.local["entregas"]
    assert [e["aprobado"] for e in entregas] == [False, True]
    assert entregas[1]["codigo"] == solucion(partida, "n1_ficha_goku")
    assert all(e["ejercicio"] == "n1_ficha_goku" and e["fecha"] for e in entregas)


# --- Sin contenido privado ---

def test_sin_contenido_privado_se_practica_pero_no_se_entrega(tmp_path):
    partida = Partida(datos=tmp_path, privado=None, evaluar=directo)
    partida.abrir("n1_ficha_goku")
    assert not partida.practicar("n1_ficha_goku").aprobado          # la práctica funciona
    with pytest.raises(NoDisponible, match="contenido privado"):
        partida.entregar("n1_ficha_goku")
    with pytest.raises(NoDisponible, match="contenido privado"):
        partida.evaluacion_abrir(1)
    assert partida.estado.niveles[1].vidas == 5 and partida.estado.xp == 0


def test_el_evaluador_rechaza_una_entrega_oficial_sin_datos_privados():
    from evaluador.contenido import EntregaOficialNoDisponible, enfrentar_jefe, entregar_mision
    mision = leer_toml(PUBLICO / "sagas/01_entrenamiento_goku/nivel_02_operadores/misiones/m1_kaioken.toml")
    for privado in (None, {}, {"solucion": "x = 1"}):       # el último no trae casos oficiales
        with pytest.raises(EntregaOficialNoDisponible):
            entregar_mision(mision, mision["plantilla"], privado)
    with pytest.raises(EntregaOficialNoDisponible):
        enfrentar_jefe({"id": "roshi", "requisitos": []}, "", None)


# --- Guardado ---

@con_privado
def test_el_progreso_se_guarda_y_se_recupera_otro_dia(partida, tmp_path):
    resolver(partida, "n1_ficha_goku")
    partida.abrir("n1_nombre_prohibido")
    partida.entregar("n1_nombre_prohibido")           # falla: una vida menos
    partida.pista("n1_radar_del_dragon")

    otra = Partida(datos=tmp_path, privado=PRIVADO, evaluar=directo)
    assert otra.estado == partida.estado
    assert (otra.estado.xp, otra.estado.niveles[1].vidas) == (10, 4)
    assert otra.local == partida.local
    assert (tmp_path / "progreso.json.bak").exists()   # copia de la versión anterior
    assert not (tmp_path / "progreso.json.tmp").exists()


# --- Pistas y semilla ---

@con_privado
def test_la_primera_pista_es_gratis_y_las_siguientes_cuestan_puntos(partida):
    resolver(partida, "n1_ficha_goku")                 # 10 puntos
    pistas, pagado = partida.pista("n1_radar_del_dragon")
    assert (len(pistas), pagado, partida.estado.puntos) == (1, 0, 10)
    pistas, pagado = partida.pista("n1_radar_del_dragon")
    assert (len(pistas), pagado, partida.estado.puntos) == (2, 10, 0)
    with pytest.raises(AccionInvalida) as error:        # no alcanza para la tercera
        partida.pista("n1_radar_del_dragon")
    assert error.value.codigo == "puntos_insuficientes"
    assert partida.local["pistas"]["n1_radar_del_dragon"] == 2


@con_privado
def test_la_semilla_del_ermitano_devuelve_una_vida(partida):
    for nombre in ("n1_ficha_goku", "n1_radar_del_dragon", "n1_nombre_prohibido",
                   "n1_almacen_capsulas", "n1_tarjeta_de_aqua"):
        resolver(partida, nombre)
    partida.abrir("n1_agenda_de_la_cita")
    partida.entregar("n1_agenda_de_la_cita")
    puntos = partida.estado.puntos
    partida.semilla()
    assert partida.estado.niveles[1].vidas == 5 and partida.estado.puntos == puntos - 50


# --- Quedarse sin vidas ---

@con_privado
def test_sin_vidas_el_nivel_se_reinicia_y_los_archivos_se_archivan(partida):
    resolver(partida, "n1_ficha_goku")
    _, ruta, _ = partida.abrir("n1_nombre_prohibido")
    for _ in range(5):
        entrega = partida.entregar("n1_nombre_prohibido")
    assert entrega.resultado.ocurrio("nivel_reiniciado")
    assert partida.estado.niveles[1].vidas == 5
    assert partida.estado.niveles[1].entregadas == set()
    assert partida.estado.xp == 10                               # los XP se conservan
    assert not ruta.exists() and not partida.ruta("n1_ficha_goku.py").exists()
    archivados = list((partida.trabajo / "intentos").rglob("*.py"))
    assert {a.name for a in archivados} == {"n1_ficha_goku.py", "n1_nombre_prohibido.py"}

    entrega = resolver(partida, "n1_ficha_goku")                 # repetir no vuelve a pagar
    assert entrega.resultado.ocurrio("recompensa_repetida") and partida.estado.xp == 10


# --- Evaluación ---

@con_privado
def test_la_evaluacion_exige_las_misiones_y_se_aprueba_con_los_retos(partida):
    with pytest.raises(AccionInvalida) as error:
        partida.evaluacion_abrir(1)
    assert error.value.codigo == "misiones_pendientes"

    for mision in partida.niveles[1]["misiones"]:
        resolver(partida, mision["id"])
    carpeta, cantidad, nueva = partida.evaluacion_abrir(1)
    assert (cantidad, nueva) == (10, True)
    assert len(list(carpeta.glob("reto_*.py"))) == 10
    assert len(partida.evaluacion_sin_resolver(1)) == 10
    primero = (carpeta / "reto_01.py").read_text(encoding="utf-8")
    assert "RETO 1 de 10" in primero and "respuesta = ..." in primero

    informes, resultado = resolver_evaluacion(partida, 1)
    assert sum(i.aprobado for i in informes) == 10
    assert resultado.ocurrio("evaluacion_aprobada")
    assert partida.estado.estado_de(1) is EstadoNivel.APROBADO
    assert partida.estado.estado_de(2) is EstadoNivel.DESBLOQUEADO
    assert not carpeta.exists()                                   # queda archivada


@con_privado
def test_reprobar_la_evaluacion_cuesta_vidas_y_cambia_a_la_version_b(partida):
    for mision in partida.niveles[1]["misiones"]:
        resolver(partida, mision["id"])
    carpeta, _, _ = partida.evaluacion_abrir(1)
    version_a = (carpeta / "reto_01.py").read_text(encoding="utf-8")
    informes, resultado = resolver_evaluacion(partida, 1, fallar=4)   # 6 de 10
    assert resultado.ocurrio("evaluacion_reprobada") and not resultado.ocurrio("nivel_reiniciado")
    assert partida.estado.niveles[1].vidas == 1
    assert len(partida.estado.niveles[1].entregadas) == 6            # las misiones se conservan

    carpeta, _, nueva = partida.evaluacion_abrir(1)
    assert nueva and (carpeta / "reto_01.py").read_text(encoding="utf-8") != version_a
    informes, resultado = resolver_evaluacion(partida, 1)
    assert resultado.ocurrio("evaluacion_aprobada")


@con_privado
def test_entregar_la_evaluacion_sin_abrirla_lo_explica(partida):
    with pytest.raises(NoDisponible, match="py jugar.py evaluacion 1"):
        partida.evaluacion_entregar(1)


# --- Repaso ---

@con_privado
def test_el_repaso_perfecto_recupera_una_vida_y_solo_hay_un_intento(partida):
    aprobar_nivel(partida, 1)
    partida.entrar(2)
    with pytest.raises(NoDisponible, match="todas las vidas"):
        partida.repaso_abrir(2)
    with pytest.raises(NoDisponible, match="ahora no se puede jugar"):
        partida.repaso_abrir(1)                                   # el nivel 1 ya está aprobado

    partida.abrir("n2_kaioken")
    partida.entregar("n2_kaioken")                                # 4 vidas
    with pytest.raises(NoDisponible, match="Primero abre el repaso"):
        partida.repaso_entregar(2)
    preguntas, ruta = partida.repaso_abrir(2)
    assert len(preguntas) == 3
    respuestas = "\n".join(f"respuesta_{n} = {valor_mirado(p)!r}" for n, p in enumerate(preguntas, 1))
    ruta.write_text(respuestas, encoding="utf-8")
    entrega = partida.repaso_entregar(2)
    assert entrega.informe.aprobado and partida.estado.niveles[2].vidas == 5

    partida.entregar("n2_kaioken")                                # otra vez 4 vidas
    with pytest.raises(NoDisponible, match="Ya hiciste el repaso"):
        partida.repaso_abrir(2)


# --- Diaria ---

@con_privado
def test_la_mision_diaria_se_abre_tras_el_primer_nivel_y_paga_una_vez_al_dia(tmp_path):
    hoy = [HOY]
    partida = Partida(datos=tmp_path, privado=PRIVADO, hoy=lambda: hoy[0], evaluar=directo)
    with pytest.raises(NoDisponible, match="primer nivel"):
        partida.diaria_abrir()
    aprobar_nivel(partida, 1)
    with pytest.raises(NoDisponible, match="Primero abre la misión diaria"):
        partida.diaria_entregar()

    pregunta, ruta = partida.diaria_abrir()
    assert pregunta["nivel"] == 1 and "2026-11-21" in ruta.read_text(encoding="utf-8")
    entrega = partida.diaria_entregar()                           # sin responder: no castiga
    assert not entrega.informe.aprobado and entrega.resultado.puntos == 0
    puntos = partida.estado.puntos
    ruta.write_text(f"respuesta = {valor_mirado(pregunta)!r}", encoding="utf-8")
    entrega = partida.diaria_entregar()
    assert (entrega.resultado.puntos, entrega.resultado.xp) == (15, 5)
    with pytest.raises(NoDisponible, match="Vuelve mañana"):
        partida.diaria_abrir()

    hoy[0] = date(2026, 11, 22)
    otra, ruta = partida.diaria_abrir()
    assert "2026-11-22" in ruta.read_text(encoding="utf-8")
    assert partida.estado.puntos == puntos + 15


# --- Jefe, mazmorra y partida completa ---

@con_privado
def test_la_saga_completa_se_juega_desde_archivos(partida):
    with pytest.raises(NoDisponible, match="Maestro Roshi"):
        partida.jefe_abrir()
    partida.abrir("mazmorra_rango_e")
    with pytest.raises(AccionInvalida) as error:
        partida.entregar("mazmorra_rango_e")
    assert error.value.codigo == "evento_bloqueado"

    for numero in (1, 2, 3):
        _, resultado = aprobar_nivel(partida, numero)
        assert resultado.ocurrio("evaluacion_aprobada")

    jefe, ruta, creado = partida.jefe_abrir()
    assert creado and jefe["nombre"] == "Maestro Roshi"
    entrega = partida.jefe_entregar()                             # sin resolver
    assert entrega.informe.aciertos == 0 and partida.estado.jefes["goku"].vidas == 4
    assert len(partida.jefe_pista()) == 1 and len(partida.jefe_pista()) == 2

    privado = leer_toml(PRIVADO / "sagas/01_entrenamiento_goku/jefe.toml")
    ruta.write_text(privado["solucion"], encoding="utf-8")
    assert partida.jefe_practicar().aprobado
    entrega = partida.jefe_entregar()
    assert entrega.resultado.ocurrio("jefe_vencido")
    assert partida.estado.transformaciones == ["Discípulo Tortuga"]

    entrega = resolver(partida, "mazmorra_rango_e")
    assert entrega.resultado.ocurrio("evento_completado")
    assert (partida.estado.xp, partida.estado.puntos) == (550, 585)


# --- Proceso aparte ---

@con_privado
def test_la_evaluacion_real_corre_en_un_proceso_aparte(tmp_path):
    partida = Partida(datos=tmp_path, privado=PRIVADO)             # evaluador real
    entrega = resolver(partida, "n1_ficha_goku")
    assert entrega.informe.aprobado and partida.estado.xp == 10
    _, ruta, _ = partida.abrir("n1_nombre_prohibido")
    informe = partida.practicar("n1_nombre_prohibido")
    assert "SyntaxError" in informe.texto()


def test_un_bucle_infinito_se_corta_y_no_cuelga_el_juego(tmp_path, monkeypatch):
    monkeypatch.setattr(aislado, "SEGUNDOS", 2)
    partida = Partida(datos=tmp_path, privado=None)
    _, ruta, _ = partida.abrir("n1_ficha_goku")
    ruta.write_text("# === TU CÓDIGO ===\nwhile True:\n    pass\n", encoding="utf-8")
    informe = partida.practicar("n1_ficha_goku")
    assert not informe.aprobado and "tardó más de 2 segundos" in informe.texto()


def test_los_archivos_que_cree_tu_codigo_no_ensucian_el_proyecto(tmp_path):
    partida = Partida(datos=tmp_path, privado=None)
    _, ruta, _ = partida.abrir("n1_ficha_goku")
    ruta.write_text('# === TU CÓDIGO ===\nopen("rastro_de_prueba.txt", "w").write("x")\n', encoding="utf-8")
    partida.practicar("n1_ficha_goku")
    assert not (aislado.RAIZ / "rastro_de_prueba.txt").exists()
    assert not list(tmp_path.rglob("rastro_de_prueba.txt"))


# --- Consola ---

def test_la_consola_muestra_el_estado_y_la_ayuda(partida, capsys):
    assert main(["estado"], partida) == 0
    salida = capsys.readouterr().out
    assert "Vidas:  [#####] 5/5" in salida and "Entrenamiento de Goku" in salida
    assert "Siguiente paso: py jugar.py mision n1_ficha_goku" in salida
    assert main([], partida) == 0 and "versión local" in capsys.readouterr().out


@pytest.mark.parametrize("orden", [["volar"], ["mision"], ["evaluacion", "saltar"], ["entrar"]])
def test_una_orden_mal_escrita_se_explica_en_espanol(partida, capsys, orden):
    assert main(orden, partida) == 2
    capturado = capsys.readouterr()
    assert "No entendí esa orden" in capturado.out and "usage" not in capturado.out + capturado.err


@con_privado
def test_la_consola_recorre_un_nivel_sin_mostrar_nunca_las_soluciones(partida, capsys):
    ordenes = [["misiones"], ["teoria"], ["ejemplos"], ["eventos"], ["evaluacion"], ["jefe"], ["diaria"]]
    for mision in partida.niveles[1]["misiones"]:
        nombre = mision["id"]
        ordenes += [["mision", nombre], ["practicar", nombre], ["entregar", nombre], ["pista", nombre]]
    for orden in ordenes:
        assert main(orden, partida) in (0, 1)
    main(["estado"], partida)
    salida = capsys.readouterr().out
    assert "ENTREGA OFICIAL" in salida and "Perdiste 1 vida." in salida
    assert "PRIVADO" not in salida
    for mision in partida.niveles[1]["misiones"]:
        propias = [
            linea.strip() for linea in solucion(partida, mision["id"]).splitlines()
            if linea.strip() and linea.strip() not in mision["plantilla"] and len(linea.strip()) > 14
        ]
        assert propias, mision["id"]
        assert not [linea for linea in propias if linea in salida], mision["id"]


@con_privado
def test_la_consola_juega_la_evaluacion_y_avisa_de_retos_sin_resolver(partida, capsys):
    for mision in partida.niveles[1]["misiones"]:
        resolver(partida, mision["id"])
    assert main(["evaluacion"], partida) == 0
    assert main(["evaluacion", "entregar"], partida) == 0
    salida = capsys.readouterr().out
    assert "Todavía hay retos sin resolver" in salida and "--igual" in salida
    assert partida.estado.niveles[1].vidas == 5                    # no se entregó nada

    carpeta = partida.carpeta_evaluacion(1)
    for indice, reto in enumerate(partida._retos(1), start=1):
        codigo = f"respuesta = {valor_mirado(reto)!r}" if reto["tipo"] == "predecir" else reto["solucion"]
        (carpeta / f"reto_{indice:02d}.py").write_text(codigo, encoding="utf-8")
    assert main(["evaluacion", "1", "entregar"], partida) == 0
    salida = capsys.readouterr().out
    assert "10 de 10 retos correctos" in salida and "py jugar.py entrar 2" in salida
    assert main(["entrar", "2"], partida) == 0


# --- Windows ---

def test_un_archivo_guardado_con_marca_inicial_del_bloc_de_notas_se_lee_bien(partida):
    _, ruta, _ = partida.abrir("n1_ficha_goku")
    codigo = '# === TU CÓDIGO ===\nnombre = "Goku"\npoder = 9001\naltura = 1.75\nes_saiyajin = True\n'
    ruta.write_bytes(b"\xef\xbb\xbf" + codigo.replace("\n", "\r\n").encode("utf-8"))
    assert partida.practicar("n1_ficha_goku").aprobado


def test_un_archivo_que_no_es_utf8_se_explica_en_vez_de_fallar(partida):
    _, ruta, _ = partida.abrir("n1_ficha_goku")
    ruta.write_bytes('nombre = "Gokú"'.encode("utf-16"))
    with pytest.raises(NoDisponible, match="UTF-8"):
        partida.practicar("n1_ficha_goku")


def test_los_finales_de_linea_de_windows_no_rompen_la_evaluacion(partida):
    from evaluador import evaluar_codigo
    _, _, mision = partida.ejercicio("n2_kaioken")
    codigo = mision["plantilla"].replace("...", "poder_base * multiplicador", 1).replace("...", "poder_base ** 2")
    assert evaluar_codigo(codigo.replace("\n", "\r\n"), mision["casos"]).aprobado
    ruta = partida.ruta("prueba_crlf.py")
    partida._crear(ruta, "a = 1\r\nb = 2\r\n")
    assert ruta.read_bytes().count(b"\r\r") == 0
