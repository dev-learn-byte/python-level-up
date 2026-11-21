"""Una partida real de la Saga 1: el evaluador decide y las reglas aplican.

Necesita el repositorio privado. Si no está, se omite.
"""
import re

import pytest

from evaluador import evaluar_reto, valor_mirado
from evaluador.contenido import PUBLICO, enfrentar_jefe, entregar_mision, practicar_mision
from nucleo import Estado, EstadoNivel, aplicar
from nucleo.cargador import cargar_catalogo, leer_toml

from .recoleccion import PRIVADO, espejo, eventos, misiones, niveles, sagas

pytestmark = pytest.mark.skipif(PRIVADO is None, reason="falta el contenido privado")


def respuesta(reto):
    return f"respuesta = {valor_mirado(reto)!r}" if reto["tipo"] == "predecir" else reto["solucion"]


def test_la_saga_1_se_completa_de_principio_a_fin():
    from .recoleccion import soluciones

    catalogo = cargar_catalogo(PUBLICO)
    estado = Estado.nuevo(catalogo)
    contador = 0

    def accion(**campos):
        nonlocal estado, contador
        contador += 1
        estado, resultado = aplicar(estado, catalogo, {"id": f"a{contador}", **campos})
        return resultado

    for carpeta in niveles():
        numero = leer_toml(carpeta / "nivel.toml")["numero"]
        if numero > 1:
            accion(tipo="entrar_nivel", nivel=numero)
        privados = soluciones(carpeta)
        for _, mision in [par for par in misiones() if par[0] == carpeta]:
            informe = entregar_mision(mision, privados[mision["id"]]["solucion"], privados[mision["id"]])
            accion(tipo="entregar_mision", nivel=numero, mision=mision["id"], correcta=informe.aprobado)
        retos = leer_toml(espejo(carpeta) / "evaluacion_A.toml")["retos"]
        aciertos = sum(evaluar_reto(reto, respuesta(reto)).aprobado for reto in retos)
        resultado = accion(tipo="rendir_evaluacion", nivel=numero, aciertos=aciertos)
        assert resultado.ocurrio("evaluacion_aprobada")

    saga = sagas()[0]
    jefe, privado = leer_toml(saga / "jefe.toml"), leer_toml(espejo(saga) / "jefe.toml")
    informe = enfrentar_jefe(jefe, privado["solucion"], privado)
    resultado = accion(tipo="entregar_jefe", saga="goku", requisitos_cumplidos=informe.aciertos)
    assert resultado.ocurrio("jefe_vencido")
    assert estado.transformaciones == ["Discípulo Tortuga"]

    mazmorra = eventos()[0]
    privado = leer_toml(PRIVADO / "eventos" / "soluciones.toml")[mazmorra["id"]]
    informe = entregar_mision(mazmorra, privado["solucion"], privado)
    accion(tipo="completar_evento", evento=mazmorra["id"], correcta=informe.aprobado)

    # Máximos de la saga anunciados en el diseño.
    assert (estado.xp, estado.puntos) == (550, 585)
    assert all(estado.estado_de(n) is EstadoNivel.APROBADO for n in (1, 2, 3))
    assert all(p.vidas == 5 for p in estado.niveles.values())


def test_entregar_una_mision_sin_resolver_cuesta_una_vida():
    catalogo = cargar_catalogo(PUBLICO)
    estado = Estado.nuevo(catalogo)
    _, mision = misiones()[0]
    informe = practicar_mision(mision, mision["plantilla"])
    estado, resultado = aplicar(estado, catalogo, {
        "tipo": "entregar_mision", "nivel": 1, "mision": mision["id"], "correcta": informe.aprobado,
    })
    assert resultado.vidas_perdidas == 1 and estado.xp == 0


def con_respuestas_fijas(mision: dict) -> str:
    """Rellena la plantilla con los valores del primer caso, escritos a mano."""
    codigo = mision["plantilla"]
    for nombre, valor in mision["casos"][0]["variables"].items():
        codigo = re.sub(rf"^{nombre} = \.\.\.$", f"{nombre} = {valor!r}", codigo, flags=re.M)
    return codigo


CON_DATOS = [m for _, m in misiones() + [(None, e) for e in eventos()]
             if "# === DATOS" in m["plantilla"] and "variables" in m["casos"][0]]


@pytest.mark.parametrize("mision", CON_DATOS, ids=[m["id"] for m in CON_DATOS])
def test_escribir_las_respuestas_a_mano_no_supera_la_practica(mision):
    trampa = con_respuestas_fijas(mision)
    assert "..." not in trampa.split("# === TU CÓDIGO")[1]
    informe = practicar_mision(mision, trampa)
    assert not informe.aprobado           # falla cuando los datos cambian
    if "salida" not in mision["casos"][0] and not mision.get("requiere"):
        assert informe.casos[0].ok        # aunque acierte con los datos visibles
