"""La partida local: une núcleo, evaluador y contenido.

Aquí no hay reglas del juego. Las reglas las aplica `nucleo`, los ejercicios
los juzga `evaluador` y los textos salen de `contenido/`. Esta clase solo
coordina: lee tus archivos, pide la evaluación, envía la acción al núcleo y
guarda el progreso.
"""
import json
import shutil
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from evaluador.comprobaciones import Informe
from evaluador.contenido import PUBLICO, ruta_privada
from evaluador.diaria import elegir_repaso, mision_diaria
from nucleo import Estado, EstadoNivel, aplicar, jefe_disponible
from nucleo.cargador import (
    archivos_de_eventos, archivos_de_misiones, cargar_catalogo, carpetas_de_niveles,
    carpetas_de_sagas, leer_toml,
)
from nucleo.resultado import Resultado

from . import aislado

RAIZ = Path(__file__).parent.parent
SIN_PRIVADO = (
    "Las entregas oficiales necesitan el contenido privado, y no lo encuentro.\n"
    "Puedes seguir practicando. Para activarlas, clona el repositorio privado\n"
    "dentro de esta carpeta con el nombre `contenido_privado`."
)


class NoDisponible(Exception):
    """Algo que el jugador pidió y ahora no se puede hacer. El mensaje es para él."""


@dataclass
class Entrega:
    informe: Informe
    resultado: Resultado


class Partida:
    def __init__(self, datos: Path | None = None, privado: Path | None | str = "auto",
                 hoy=date.today, evaluar=aislado.evaluar):
        """`datos` es la carpeta donde se guardan el progreso y tus soluciones."""
        datos = Path(datos or RAIZ)
        self.archivo = datos / "progreso.json"
        self.trabajo = datos / "mis_soluciones"
        self.privado = ruta_privada() if privado == "auto" else privado
        self.hoy = hoy
        self._evaluar = evaluar
        self.catalogo = cargar_catalogo(PUBLICO)
        self._indexar()
        self._cargar()

    # ------------------------------------------------------------------ contenido

    def _indexar(self) -> None:
        self.sagas, self.niveles, self.misiones = {}, {}, {}
        for carpeta in carpetas_de_sagas(PUBLICO):
            saga = leer_toml(carpeta / "saga.toml")
            jefe = leer_toml(carpeta / "jefe.toml") if (carpeta / "jefe.toml").exists() else None
            self.sagas[saga["id"]] = {"carpeta": carpeta, "datos": saga, "jefe": jefe}
            for carpeta_nivel in carpetas_de_niveles(carpeta):
                datos = leer_toml(carpeta_nivel / "nivel.toml")
                misiones = [leer_toml(a) for a in archivos_de_misiones(carpeta_nivel)]
                self.niveles[datos["numero"]] = {
                    "carpeta": carpeta_nivel, "datos": datos, "misiones": misiones, "saga": saga["id"],
                }
                for mision in misiones:
                    self.misiones[mision["id"]] = (datos["numero"], mision)
        self.eventos = {e["id"]: e for e in map(leer_toml, archivos_de_eventos(PUBLICO))}
        self.plantillas_diarias = leer_toml(PUBLICO / "diarias" / "plantillas.toml")["plantillas"]

    def ejercicio(self, identificador: str) -> tuple[str, int | None, dict]:
        """Devuelve ("mision", nivel, datos) o ("evento", None, datos)."""
        if identificador in self.misiones:
            numero, mision = self.misiones[identificador]
            return "mision", numero, mision
        if identificador in self.eventos:
            return "evento", None, self.eventos[identificador]
        raise NoDisponible(
            f"No conozco ninguna misión llamada '{identificador}'. "
            "Mira los nombres con: py jugar.py misiones"
        )

    def _nivel(self, numero: int | None) -> int:
        numero = self.estado.nivel_actual if numero is None else numero
        if numero not in self.niveles:
            raise NoDisponible(f"No existe el nivel {numero}.")
        return numero

    def _privado(self, relativa: Path) -> dict:
        if self.privado is None:
            raise NoDisponible(SIN_PRIVADO)
        archivo = self.privado / relativa
        if not archivo.exists():
            raise NoDisponible(SIN_PRIVADO)
        return leer_toml(archivo)

    def _privado_de(self, tipo: str, numero: int | None, identificador: str) -> dict:
        if tipo == "evento":
            return self._privado(Path("eventos") / "soluciones.toml")[identificador]
        carpeta = self.niveles[numero]["carpeta"].relative_to(PUBLICO)
        return self._privado(carpeta / "soluciones.toml")[identificador]

    # ------------------------------------------------------------------ guardado

    def _cargar(self) -> None:
        if self.archivo.exists():
            guardado = json.loads(self.archivo.read_text(encoding="utf-8"))
            self.estado = Estado.desde_dict(guardado["estado"])
            self.local = guardado["local"]
        else:
            self.estado = Estado.nuevo(self.catalogo)
            self.local = {"entregas": [], "pistas": {}, "repasos": [], "evaluaciones": {}}

    def guardar(self) -> None:
        """Guarda de forma segura: escribe aparte y conserva la copia anterior."""
        contenido = json.dumps(
            {"formato": 1, "estado": self.estado.a_dict(), "local": self.local},
            ensure_ascii=False, indent=1,
        )
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.archivo.with_suffix(".json.tmp")
        temporal.write_text(contenido, encoding="utf-8")
        if self.archivo.exists():
            shutil.copyfile(self.archivo, self.archivo.with_suffix(".json.bak"))
        temporal.replace(self.archivo)

    def _aplicar(self, **campos) -> Resultado:
        """Envía una acción al núcleo y guarda el progreso."""
        accion = {"id": uuid.uuid4().hex, **campos}
        self.estado, resultado = aplicar(self.estado, self.catalogo, accion)
        self.guardar()
        return resultado

    def _permitida(self, **campos) -> None:
        """Comprueba que el núcleo aceptaría la acción, sin aplicarla."""
        aplicar(self.estado, self.catalogo, campos)

    # ------------------------------------------------------------------ archivos

    def ruta(self, nombre: str) -> Path:
        return self.trabajo / nombre

    def _crear(self, ruta: Path, contenido: str) -> bool:
        if ruta.exists():
            return False
        ruta.parent.mkdir(parents=True, exist_ok=True)
        contenido = contenido.replace("\r\n", "\n").strip("\n") + "\n"
        ruta.write_text(contenido, encoding="utf-8")
        return True

    def _leer(self, ruta: Path, orden: str) -> str:
        if not ruta.exists():
            raise NoDisponible(f"Todavía no existe {ruta.name}. Créalo con: py jugar.py {orden}")
        try:
            # utf-8-sig acepta también los archivos que el Bloc de notas guarda con marca inicial.
            return ruta.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            raise NoDisponible(
                f"No puedo leer {ruta.name}: no está guardado como UTF-8. "
                "En tu editor, usa 'Guardar con codificación' y elige UTF-8."
            ) from None

    def _archivar(self, rutas: list[Path], etiqueta: str) -> Path | None:
        """Mueve archivos de trabajo a `mis_soluciones/intentos/`."""
        rutas = [ruta for ruta in rutas if ruta.exists()]
        if not rutas:
            return None
        destino = self.trabajo / "intentos" / f"{etiqueta}_{datetime.now():%Y%m%d_%H%M%S_%f}"
        destino.mkdir(parents=True)
        for ruta in rutas:
            shutil.move(str(ruta), str(destino / ruta.name))
        return destino

    def _archivar_nivel(self, numero: int) -> None:
        """Nivel reiniciado: las misiones vuelven a empezar desde su plantilla."""
        rutas = [self.ruta(f"{m['id']}.py") for m in self.niveles[numero]["misiones"]]
        rutas += [self.carpeta_evaluacion(numero), self.ruta(f"repaso_nivel_{numero}.py")]
        self._archivar(rutas, f"nivel_{numero}")
        self.local["evaluaciones"].pop(str(numero), None)
        for mision in self.niveles[numero]["misiones"]:
            self.local["pistas"].pop(mision["id"], None)
        self.guardar()

    # ------------------------------------------------------------------ misiones

    def abrir(self, identificador: str) -> tuple[dict, Path, bool]:
        """Crea tu archivo de trabajo desde la plantilla, si aún no existe."""
        _, _, ejercicio = self.ejercicio(identificador)
        ruta = self.ruta(f"{identificador}.py")
        return ejercicio, ruta, self._crear(ruta, ejercicio["plantilla"])

    def practicar(self, identificador: str) -> Informe:
        """Gratis: no cambia el progreso."""
        _, _, ejercicio = self.ejercicio(identificador)
        codigo = self._leer(self.ruta(f"{identificador}.py"), f"mision {identificador}")
        return self._evaluar("practicar_mision", mision=ejercicio, codigo=codigo)

    def entregar(self, identificador: str) -> Entrega:
        """Entrega oficial: si falla una misión, cuesta una vida."""
        tipo, numero, ejercicio = self.ejercicio(identificador)
        codigo = self._leer(self.ruta(f"{identificador}.py"), f"mision {identificador}")
        if tipo == "mision":
            campos = {"tipo": "entregar_mision", "nivel": numero, "mision": identificador}
        else:
            campos = {"tipo": "completar_evento", "evento": identificador}
        self._permitida(**campos, correcta=True)
        privado = self._privado_de(tipo, numero, identificador)
        informe = self._evaluar("entregar_mision", mision=ejercicio, codigo=codigo, privado=privado)
        resultado = self._aplicar(**campos, correcta=informe.aprobado)
        self._registrar(identificador, codigo, informe.aprobado)
        if resultado.ocurrio("nivel_reiniciado"):
            self._archivar_nivel(numero)
        return Entrega(informe, resultado)

    def _registrar(self, identificador: str, codigo: str, aprobado: bool) -> None:
        """Guarda el código entregado, para poder reevaluarlo más adelante."""
        self.local["entregas"].append({
            "ejercicio": identificador, "codigo": codigo, "aprobado": aprobado,
            "fecha": datetime.now().isoformat(timespec="seconds"),
        })
        self.guardar()

    def pista(self, identificador: str) -> tuple[list[str], int]:
        """Desbloquea la siguiente pista. Devuelve (pistas visibles, puntos pagados)."""
        tipo, numero, ejercicio = self.ejercicio(identificador)
        return self._siguiente_pista(identificador, ejercicio["pistas"], numero if tipo == "mision" else None)

    def _siguiente_pista(self, clave: str, pistas: list[str], nivel: int | None) -> tuple[list[str], int]:
        vistas = self.local["pistas"].get(clave, 0)
        pagado = 0
        if vistas < len(pistas):
            # La primera pista es gratis. Las siguientes de una misión cuestan puntos.
            if vistas >= 1 and nivel is not None:
                resultado = self._aplicar(
                    tipo="comprar_pista", nivel=nivel, mision=clave, numero=vistas + 1,
                )
                pagado = resultado.puntos_gastados
            vistas += 1
            self.local["pistas"][clave] = vistas
            self.guardar()
        return pistas[:vistas], pagado

    # ------------------------------------------------------------------ niveles

    def entrar(self, numero: int) -> Resultado:
        return self._aplicar(tipo="entrar_nivel", nivel=numero)

    def semilla(self, numero: int | None = None) -> Resultado:
        return self._aplicar(tipo="comprar_semilla", nivel=self._nivel(numero))

    def teoria(self, numero: int | None = None) -> str:
        carpeta = self.niveles[self._nivel(numero)]["carpeta"]
        return (carpeta / "teoria.md").read_text(encoding="utf-8")

    def ruta_ejemplos(self, numero: int | None = None) -> Path:
        return self.niveles[self._nivel(numero)]["carpeta"] / "ejemplos.py"

    def _exigir_jugable(self, numero: int) -> None:
        if self.estado.estado_de(numero) not in (EstadoNivel.ACTUAL, EstadoNivel.PENDIENTE):
            raise NoDisponible(
                f"El nivel {numero} está {self.estado.estado_de(numero).value}: ahora no se puede jugar."
            )

    # ------------------------------------------------------------------ repaso

    def repaso_abrir(self, numero: int | None = None) -> tuple[list[dict], Path]:
        numero = self._nivel(numero)
        self._exigir_jugable(numero)
        archivo = self.niveles[numero]["carpeta"] / "repaso.toml"
        if not archivo.exists():
            raise NoDisponible(f"El nivel {numero} no tiene repaso: no hay niveles anteriores.")
        progreso = self.estado.niveles[numero]
        if progreso.vidas >= self.catalogo.config.vidas_por_nivel:
            raise NoDisponible("Ya tienes todas las vidas: no necesitas el repaso.")
        if f"{numero}-{progreso.intentos}" in self.local["repasos"]:
            raise NoDisponible("Ya hiciste el repaso de este intento de nivel.")
        preguntas = elegir_repaso(leer_toml(archivo), semilla=numero * 1000 + progreso.intentos)
        ruta = self.ruta(f"repaso_nivel_{numero}.py")
        lineas = [f"# Repaso del nivel {numero}. Un solo intento: si aciertas las tres, recuperas una vida.", ""]
        for indice, pregunta in enumerate(preguntas, start=1):
            lineas += _pregunta_comentada(indice, pregunta) + [f"respuesta_{indice} = ...", ""]
        self._crear(ruta, "\n".join(lineas))
        return preguntas, ruta

    def repaso_entregar(self, numero: int | None = None) -> Entrega:
        numero = self._nivel(numero)
        if not self.ruta(f"repaso_nivel_{numero}.py").exists():
            raise NoDisponible(f"Primero abre el repaso con: py jugar.py repaso {numero}")
        preguntas, ruta = self.repaso_abrir(numero)
        informe = self._evaluar(
            "evaluar_prediccion", codigo=self._leer(ruta, f"repaso {numero}"), preguntas=preguntas,
        )
        self.local["repasos"].append(f"{numero}-{self.estado.niveles[numero].intentos}")
        resultado = self._aplicar(tipo="completar_repaso", nivel=numero, perfecto=informe.aprobado)
        self._archivar([ruta], f"repaso_nivel_{numero}")
        return Entrega(informe, resultado)

    # ------------------------------------------------------------------ evaluación

    def carpeta_evaluacion(self, numero: int) -> Path:
        return self.ruta(f"evaluacion_nivel_{numero}")

    def _retos(self, numero: int) -> list[dict]:
        version = self.estado.niveles[numero].version_evaluacion
        carpeta = self.niveles[numero]["carpeta"].relative_to(PUBLICO)
        return self._privado(carpeta / f"evaluacion_{version}.toml")["retos"]

    def evaluacion_abrir(self, numero: int | None = None) -> tuple[Path, int, bool]:
        """Crea un archivo por reto. Devuelve (carpeta, cantidad de retos, si es nueva)."""
        numero = self._nivel(numero)
        self._exigir_jugable(numero)
        retos = self._retos(numero)
        self._permitida(tipo="rendir_evaluacion", nivel=numero, aciertos=len(retos))
        version = self.estado.niveles[numero].version_evaluacion
        carpeta = self.carpeta_evaluacion(numero)
        if self.local["evaluaciones"].get(str(numero)) != version:
            self._archivar([carpeta], f"evaluacion_nivel_{numero}")
        nueva = not carpeta.exists()
        for indice, reto in enumerate(retos, start=1):
            self._crear(carpeta / f"reto_{indice:02d}.py", _archivo_de_reto(indice, len(retos), numero, reto))
        self.local["evaluaciones"][str(numero)] = version
        self.guardar()
        return carpeta, len(retos), nueva

    def evaluacion_sin_resolver(self, numero: int | None = None) -> list[str]:
        """Retos cuyo archivo sigue igual que cuando se creó."""
        numero = self._nivel(numero)
        carpeta = self.carpeta_evaluacion(numero)
        retos = self._retos(numero)
        pendientes = []
        for indice, reto in enumerate(retos, start=1):
            archivo = carpeta / f"reto_{indice:02d}.py"
            original = _archivo_de_reto(indice, len(retos), numero, reto).strip()
            if not archivo.exists() or archivo.read_text(encoding="utf-8").strip() == original:
                pendientes.append(archivo.name)
        return pendientes

    def evaluacion_entregar(self, numero: int | None = None) -> tuple[list[Informe], Resultado]:
        """Evaluación oficial: cada reto fallado cuesta una vida."""
        numero = self._nivel(numero)
        carpeta = self.carpeta_evaluacion(numero)
        if not carpeta.exists() or self.local["evaluaciones"].get(str(numero)) is None:
            raise NoDisponible(f"Primero abre la evaluación con: py jugar.py evaluacion {numero}")
        retos = self._retos(numero)
        self._permitida(tipo="rendir_evaluacion", nivel=numero, aciertos=len(retos))
        informes = []
        for indice, reto in enumerate(retos, start=1):
            codigo = self._leer(carpeta / f"reto_{indice:02d}.py", f"evaluacion {numero}")
            informes.append(self._evaluar("evaluar_reto", reto=reto, codigo=codigo))
            self._registrar(f"evaluacion:{numero}:{reto.get('formato', reto['tipo'])}:{indice}", codigo, informes[-1].aprobado)
        aciertos = sum(informe.aprobado for informe in informes)
        resultado = self._aplicar(tipo="rendir_evaluacion", nivel=numero, aciertos=aciertos)
        self._archivar([carpeta], f"evaluacion_nivel_{numero}")
        self.local["evaluaciones"].pop(str(numero), None)
        self.guardar()
        if resultado.ocurrio("nivel_reiniciado"):
            self._archivar_nivel(numero)
        return informes, resultado

    # ------------------------------------------------------------------ jefe

    def _saga_actual(self) -> str:
        return self.niveles[self.estado.nivel_actual]["saga"]

    def jefe(self, saga: str | None = None) -> tuple[str, dict]:
        saga = saga or self._saga_actual()
        jefe = self.sagas[saga]["jefe"]
        if jefe is None:
            raise NoDisponible("Esta saga todavía no tiene jefe.")
        return saga, jefe

    def jefe_abrir(self, saga: str | None = None) -> tuple[dict, Path, bool]:
        saga, jefe = self.jefe(saga)
        if not jefe_disponible(self.estado, self.catalogo, saga):
            raise NoDisponible(
                f"{jefe['nombre']} solo te recibirá cuando apruebes todos los niveles de la saga."
            )
        ruta = self.ruta(f"jefe_{jefe['id']}.py")
        return jefe, ruta, self._crear(ruta, jefe["plantilla"])

    def jefe_practicar(self, saga: str | None = None) -> Informe:
        jefe, ruta, _ = self.jefe_abrir(saga)
        return self._evaluar("practicar_jefe", jefe=jefe, codigo=self._leer(ruta, "jefe"))

    def jefe_entregar(self, saga: str | None = None) -> Entrega:
        saga, jefe = self.jefe(saga)
        _, ruta, _ = self.jefe_abrir(saga)
        codigo = self._leer(ruta, "jefe")
        self._permitida(tipo="entregar_jefe", saga=saga, requisitos_cumplidos=len(jefe["requisitos"]))
        carpeta = self.sagas[saga]["carpeta"].relative_to(PUBLICO)
        privado = self._privado(carpeta / "jefe.toml")
        informe = self._evaluar("enfrentar_jefe", jefe=jefe, codigo=codigo, privado=privado)
        resultado = self._aplicar(tipo="entregar_jefe", saga=saga, requisitos_cumplidos=informe.aciertos)
        self._registrar(f"jefe:{saga}", codigo, informe.aprobado)
        return Entrega(informe, resultado)

    def jefe_pista(self, saga: str | None = None) -> list[str]:
        _, jefe = self.jefe(saga)
        return self._siguiente_pista(f"jefe:{jefe['id']}", jefe["pistas"], None)[0]

    # ------------------------------------------------------------------ diaria

    def _aprobados(self) -> set[int]:
        return {n for n in self.niveles if self.estado.estado_de(n) is EstadoNivel.APROBADO}

    def diaria_abrir(self) -> tuple[dict, Path]:
        hoy = self.hoy()
        if self.estado.ultima_diaria == hoy.isoformat():
            raise NoDisponible("Ya completaste la misión diaria de hoy. Vuelve mañana.")
        pregunta = mision_diaria(hoy, self.plantillas_diarias, self._aprobados())
        if pregunta is None:
            raise NoDisponible("La misión diaria se abre cuando apruebes tu primer nivel.")
        ruta = self.ruta("diaria.py")
        if self.local.get("diaria") != hoy.isoformat():
            self._archivar([ruta], "diaria")   # era la de otro día
            self.local["diaria"] = hoy.isoformat()
            self.guardar()
        cabecera = f"# Misión diaria del {hoy.isoformat()}"
        self._crear(ruta, "\n".join([cabecera, ""] + _pregunta_comentada(0, pregunta) + ["respuesta = ..."]))
        return pregunta, ruta

    def diaria_entregar(self) -> Entrega:
        if not self.ruta("diaria.py").exists():
            raise NoDisponible("Primero abre la misión diaria con: py jugar.py diaria")
        pregunta, ruta = self.diaria_abrir()
        informe = self._evaluar(
            "evaluar_prediccion", codigo=self._leer(ruta, "diaria"),
            preguntas=[pregunta], nombres=["respuesta"],
        )
        resultado = self._aplicar(
            tipo="completar_diaria", fecha=self.hoy().isoformat(), correcta=informe.aprobado,
        )
        if informe.aprobado:
            self._archivar([ruta], "diaria")
        return Entrega(informe, resultado)


def _pregunta_comentada(indice: int, pregunta: dict) -> list[str]:
    """Una pregunta de predicción escrita como comentarios."""
    titulo = f"# Pregunta {indice}: " if indice else "# "
    lineas = [titulo + pregunta.get("texto", pregunta.get("enunciado", "")).strip().replace("\n", "\n# ")]
    lineas.append("# Código (no lo ejecutes, piénsalo):")
    lineas += [f"#     {linea}" for linea in pregunta["codigo"].strip().splitlines()]
    return lineas


def _archivo_de_reto(indice: int, total: int, nivel: int, reto: dict) -> str:
    cabecera = [f"# RETO {indice} de {total} - Evaluación del nivel {nivel}", "#"]
    if reto["tipo"] == "predecir":
        return "\n".join(cabecera + _pregunta_comentada(0, reto) + ["", "respuesta = ..."])
    enunciado = ["# " + linea if linea else "#" for linea in reto["enunciado"].strip().splitlines()]
    return "\n".join(cabecera + enunciado + [""]) + "\n" + reto["plantilla"].strip("\n")
