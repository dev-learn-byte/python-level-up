"""El contenido público está completo y bien formado."""
import pytest

from evaluador import ejecutar
from evaluador.contenido import PUBLICO, practicar_mision
from nucleo.cargador import archivos_de_misiones, cargar_catalogo, leer_toml

from .recoleccion import eventos, misiones, niveles

MISIONES = misiones()
IDS = [m["id"] for _, m in MISIONES]
ANIMES_ESPECIALES = {"KonoSuba", "Rompiendo el hielo", "My Hero Academia", "Solo Leveling"}
# Conceptos que todavía no se han enseñado en la Saga 1.
NO_ENSENADO = ["if ", "else", "def ", "return", "try:", "except", "for ", "while ", "lambda"]


def test_el_catalogo_se_carga_y_es_valido_para_las_reglas():
    catalogo = cargar_catalogo(PUBLICO)
    assert catalogo.numeros == [1, 2, 3]
    assert catalogo.sagas == ["goku"]
    assert len({m.id for n in catalogo.numeros for m in catalogo.nivel(n).misiones}) == 18
    assert catalogo.jefe("goku").transformacion == "Discípulo Tortuga"
    assert catalogo.jefe("goku").requisitos == 8
    assert catalogo.evento("mazmorra_rango_e").requiere_nivel == 3


@pytest.mark.parametrize("nivel", niveles(), ids=lambda n: n.name)
def test_cada_nivel_tiene_cuatro_misiones_de_dragon_ball_y_dos_especiales(nivel):
    animes = [leer_toml(a)["anime"] for a in archivos_de_misiones(nivel)]
    assert len(animes) == 6
    assert animes.count("Dragon Ball") == 4
    assert set(animes) - {"Dragon Ball"} <= ANIMES_ESPECIALES


@pytest.mark.parametrize("nivel", niveles(), ids=lambda n: n.name)
def test_la_teoria_tiene_sus_tres_partes_y_los_ejemplos_funcionan(nivel):
    teoria = (nivel / "teoria.md").read_text(encoding="utf-8")
    for seccion in ("## Para niños", "## Así lo dice un programador", "## Errores típicos"):
        assert seccion in teoria
    ejemplos = (nivel / "ejemplos.py").read_text(encoding="utf-8")
    resultado = ejecutar(ejemplos, entradas=["12", "Goku", "5", "3.5"] * 3)
    assert resultado.error is None, resultado.error.texto()
    assert resultado.salida


@pytest.mark.parametrize("mision", [m for _, m in MISIONES], ids=IDS)
def test_cada_mision_esta_completa(mision):
    assert mision["titulo"] and mision["enunciado"].strip() and mision["plantilla"].strip()
    assert mision["formato"] in {"escribir", "predecir", "corregir", "completar"}
    assert mision["dispositivo"] in {"celular", "pc"}
    assert len(mision["pistas"]) == 3 and all(mision["pistas"])
    especial = mision["anime"] != "Dragon Ball"
    assert (mision["xp"], mision["puntos"]) == ((15, 15) if especial else (10, 10))
    if mision["formato"] == "predecir":
        assert len(mision["preguntas"]) >= 3
    else:
        assert mision["casos"]


@pytest.mark.parametrize("mision", [m for _, m in MISIONES], ids=IDS)
def test_la_plantilla_sin_resolver_no_pasa_la_practica(mision):
    assert not practicar_mision(mision, mision["plantilla"]).aprobado


@pytest.mark.parametrize("mision", [m for _, m in MISIONES], ids=IDS)
def test_las_misiones_con_datos_se_prueban_con_mas_de_un_juego_de_datos(mision):
    if "# === DATOS" in mision["plantilla"]:
        assert sum("datos" in caso for caso in mision["casos"]) >= 1


@pytest.mark.parametrize("mision", [m for _, m in MISIONES], ids=IDS)
def test_las_misiones_no_usan_conceptos_que_aun_no_se_ensenan(mision):
    textos = [mision["plantilla"]] + [p["codigo"] for p in mision.get("preguntas", [])]
    for texto in textos:
        for concepto in NO_ENSENADO:
            assert concepto not in texto, f"usa {concepto!r} antes de tiempo"


@pytest.mark.parametrize("nivel", niveles(), ids=lambda n: n.name)
def test_los_ejemplos_no_usan_conceptos_que_aun_no_se_ensenan(nivel):
    ejemplos = (nivel / "ejemplos.py").read_text(encoding="utf-8")
    codigo = "\n".join(linea.split("#")[0] for linea in ejemplos.splitlines())
    for concepto in NO_ENSENADO:
        assert concepto not in codigo, f"usa {concepto!r} antes de tiempo"


def test_los_eventos_estan_completos():
    assert eventos()
    for evento in eventos():
        assert evento["enunciado"].strip() and evento["plantilla"].strip()
        assert len(evento["pistas"]) == 3
        assert not practicar_mision(evento, evento["plantilla"]).aprobado
