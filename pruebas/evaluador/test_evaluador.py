"""El evaluador ejecuta el código, compara resultados y explica los errores."""
import pytest

from evaluador import (
    ejecutar, evaluar_codigo, evaluar_jefe, evaluar_prediccion, evaluar_reto, iguales,
)

CON_DATOS = '''
# === DATOS (no los cambies) ===
ataque = "kamehameha"

# === TU CÓDIGO ===
grito = ataque.upper()
'''


# --- Ejecución ---

def test_devuelve_las_variables_y_lo_que_se_imprime():
    resultado = ejecutar('poder = 9001\nprint("Poder:", poder)\nprint("fin")')
    assert resultado.error is None
    assert resultado.variables["poder"] == 9001
    assert resultado.salida == ["Poder: 9001", "fin"]


def test_los_datos_del_caso_sustituyen_a_los_de_la_plantilla():
    assert ejecutar(CON_DATOS).variables["grito"] == "KAMEHAMEHA"
    assert ejecutar(CON_DATOS, datos={"ataque": "masenko"}).variables["grito"] == "MASENKO"


def test_input_se_simula_y_no_ensucia_la_salida():
    codigo = 'a = input("Nombre: ")\nb = int(input("Edad: "))\nprint(a, b + 1)'
    resultado = ejecutar(codigo, entradas=["Goku", "12"])
    assert resultado.salida == ["Goku 13"]
    assert resultado.entradas_usadas == 2


def test_pedir_mas_entradas_de_las_previstas_es_un_error_explicado():
    resultado = ejecutar("a = input()\nb = input()", entradas=["1"])
    assert resultado.error.tipo == "SinEntradas"
    assert "input()" in resultado.error.explicacion


def test_borrar_la_marca_de_codigo_se_explica():
    resultado = ejecutar('ataque = "x"\ngrito = ataque', datos={"ataque": "y"})
    assert resultado.error.tipo == "FaltaMarca"


@pytest.mark.parametrize("codigo, tipo, linea", [
    ("nombre = Goku", "NameError", 1),
    ("a = 1\n2do = 3", "SyntaxError", 2),
    ('a = "5"\nb = 1\nc = a + b', "TypeError", 3),
    ('n = int("doce")', "ValueError", 1),
    ("a = 1\n\nb = a / 0", "ZeroDivisionError", 3),
    ('p = "radar"\nx = p[5]', "IndexError", 2),
    ("n = 5\nn.upper()", "AttributeError", 2),
])
def test_cada_error_se_explica_con_su_linea(codigo, tipo, linea):
    error = ejecutar(codigo).error
    assert (error.tipo, error.linea) == (tipo, linea)
    assert len(error.explicacion) > 40
    assert tipo in error.texto() and f"línea {linea}" in error.texto()


def test_el_numero_de_linea_es_correcto_tambien_con_seccion_de_datos():
    codigo = "# === DATOS ===\nx = 1\n\n# === TU CÓDIGO ===\ny = x\nz = y / 0"
    assert ejecutar(codigo, datos={"x": 5}).error.linea == 6


def test_exit_no_detiene_al_evaluador():
    assert ejecutar("exit()").error.tipo == "SystemExit"


# --- Comparación ---

@pytest.mark.parametrize("a, b, esperado", [
    (5, 5, True), (5, 5.0, False), (True, 1, False), ("5", 5, False),
    (0.1 + 0.2, 0.3, True), ("Goku", "goku", False), (4.0, 4.0, True),
])
def test_iguales_exige_mismo_valor_y_mismo_tipo(a, b, esperado):
    assert iguales(a, b) is esperado


# --- Misiones de código ---

CASOS = [
    {"nombre": "kamehameha", "variables": {"grito": "KAMEHAMEHA"}},
    {"nombre": "masenko", "datos": {"ataque": "masenko"}, "variables": {"grito": "MASENKO"}, "pista": "Usa la variable."},
]


def test_una_solucion_correcta_aprueba():
    informe = evaluar_codigo(CON_DATOS, CASOS)
    assert informe.aprobado and informe.aciertos == 2
    assert "Correcto" in informe.texto()


def test_una_respuesta_escrita_a_mano_falla_con_otros_datos():
    trampa = CON_DATOS.replace("ataque.upper()", '"KAMEHAMEHA"')
    informe = evaluar_codigo(trampa, CASOS)
    assert not informe.aprobado
    assert informe.casos[0].ok and not informe.casos[1].ok
    assert "Usa la variable." in informe.texto()


def test_dejar_los_tres_puntos_se_explica():
    informe = evaluar_codigo(CON_DATOS.replace("ataque.upper()", "..."), CASOS)
    assert "Todavía no completaste `grito`" in informe.texto()


def test_falta_la_variable_o_el_tipo_es_otro():
    casos = [{"variables": {"poder": 9001}}]
    assert "No encuentro la variable `poder`" in evaluar_codigo("x = 1", casos).texto()
    texto = evaluar_codigo('poder = "9001"', casos).texto()
    assert "debería ser de tipo int" in texto and "es de tipo str" in texto


def test_se_comprueba_la_salida_y_los_tipos():
    casos = [{"salida": ["Hola Goku"], "tipos": {"n": "float"}}]
    assert evaluar_codigo('n = 1.5\nprint("Hola", "Goku")', casos).aprobado
    assert "no imprimió nada" in evaluar_codigo("n = 1.5", casos).texto()
    assert not evaluar_codigo('n = 1\nprint("Hola Goku")', casos).aprobado


def test_una_mision_puede_exigir_el_uso_de_algo():
    casos = [{"clases": {"t": "int"}}]
    assert evaluar_codigo("# === TU CÓDIGO ===\nt = type(5)", casos, requiere=["type("]).aprobado
    informe = evaluar_codigo("# === TU CÓDIGO ===\nt = int", casos, requiere=["type("])
    assert "pide usar `type(`" in informe.texto()


def test_los_casos_oficiales_se_comparan_con_la_referencia_sin_mostrar_lo_esperado():
    casos = [{"datos": {"ataque": "genkidama"}, "comparar": ["grito"]}]
    assert evaluar_codigo(CON_DATOS, casos, referencia=CON_DATOS).aprobado
    trampa = CON_DATOS.replace("ataque.upper()", "ataque")
    informe = evaluar_codigo(trampa, casos, referencia=CON_DATOS, mostrar_esperado=False)
    assert not informe.aprobado
    assert "GENKIDAMA" not in informe.texto()


def test_un_error_del_alumno_aparece_explicado_en_el_informe():
    informe = evaluar_codigo("# === DATOS ===\nataque = 1\n# === TU CÓDIGO ===\ngrito = atake", CASOS)
    assert "NameError en la línea 4" in informe.texto()


# --- Predicción ---

PREGUNTAS = [
    {"codigo": "x = 3\nx = x + 2", "mirar": "x", "pista": "Suma."},
    {"codigo": "x = 7.0", "mirar": "tipo:x"},
    {"codigo": 'print("Hola", 4 + 3)', "mirar": "salida"},
]


def test_prediccion_correcta():
    codigo = 'respuesta_1 = 5\nrespuesta_2 = "float"\nrespuesta_3 = "Hola 7"'
    assert evaluar_prediccion(codigo, PREGUNTAS).aprobado


def test_prediccion_equivocada_no_revela_la_respuesta():
    codigo = 'respuesta_1 = 6\nrespuesta_2 = "float"\nrespuesta_3 = ...'
    informe = evaluar_prediccion(codigo, PREGUNTAS)
    assert [caso.ok for caso in informe.casos] == [False, True, False]
    assert informe.aciertos == 1
    assert "Suma." in informe.texto()
    assert "5" not in informe.casos[0].fallos[0]
    assert "Hola 7" not in informe.texto()


def test_prediccion_con_el_tipo_equivocado_avisa_del_tipo():
    informe = evaluar_prediccion('respuesta_1 = "5"\nrespuesta_2 = "float"\nrespuesta_3 = "Hola 7"', PREGUNTAS)
    assert "debería ser de tipo int" in informe.texto()


# --- Retos de evaluación ---

def test_reto_de_prediccion_y_reto_de_codigo():
    predecir = {"tipo": "predecir", "codigo": "r = 17 % 5", "mirar": "r"}
    assert evaluar_reto(predecir, "respuesta = 2").aprobado
    assert not evaluar_reto(predecir, "respuesta = 3").aprobado

    solucion = "# === DATOS ===\nm = 135\n# === TU CÓDIGO ===\nh = m // 60"
    codigo = {"tipo": "codigo", "solucion": solucion, "comparar": ["h"],
              "casos": [{"datos": {"m": 135}}, {"datos": {"m": 59}}]}
    assert evaluar_reto(codigo, solucion).aprobado
    assert not evaluar_reto(codigo, solucion.replace("m // 60", "2")).aprobado


# --- Jefe ---

REFERENCIA = 'n = input().strip().capitalize()\ne = int(input())\nprint("Torneo")\nprint(f"Nombre: {n}")\nprint(f"Edad: {e}")'
REQUISITOS = [
    {"texto": "Pide dos datos", "entradas": 2, "pista": "Cuenta los input()."},
    {"texto": "Título", "linea": 1, "pista": "Copia el título."},
    {"texto": "Nombre limpio", "linea": 2, "pista": "Limpia el nombre."},
    {"texto": "Edad", "linea": 3, "pista": "Convierte la edad."},
]
PARTICIPANTES = [{"nombre": "Goku", "entradas": ["goku", "12"]}, {"nombre": "Krilin", "entradas": [" kRILIN ", "13"]}]


def test_el_jefe_se_evalua_requisito_por_requisito():
    assert evaluar_jefe(REFERENCIA, PARTICIPANTES, REQUISITOS, REFERENCIA).aciertos == 4

    sin_limpiar = REFERENCIA.replace(".strip().capitalize()", ".capitalize()")
    informe = evaluar_jefe(sin_limpiar, PARTICIPANTES, REQUISITOS, REFERENCIA)
    assert [caso.ok for caso in informe.casos] == [True, True, False, True]
    assert "Limpia el nombre." in informe.texto()


def test_un_programa_del_jefe_que_falla_no_cumple_ningun_requisito():
    informe = evaluar_jefe('n = input()\ne = input() + 1', PARTICIPANTES, REQUISITOS, REFERENCIA)
    assert informe.aciertos == 0
    assert "TypeError" in informe.texto()
