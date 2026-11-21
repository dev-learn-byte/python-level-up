"""El progreso del jugador. Se guarda y se recupera como un diccionario JSON."""
from dataclasses import asdict, dataclass, field
from enum import Enum


class EstadoNivel(str, Enum):
    BLOQUEADO = "bloqueado"        # aún no se puede entrar
    DESBLOQUEADO = "desbloqueado"  # se puede entrar, pero no se ha empezado
    ACTUAL = "actual"              # el nivel que se está cursando
    APROBADO = "aprobado"          # evaluación superada
    PENDIENTE = "pendiente"        # saltado con puntos; hay que completarlo


@dataclass
class ProgresoNivel:
    estado: EstadoNivel
    vidas: int
    entregadas: set[str] = field(default_factory=set)  # misiones del intento actual
    intentos: int = 1
    semilla_usada: bool = False
    repaso_usado: bool = False
    version_evaluacion: str = "A"


@dataclass
class ProgresoJefe:
    vidas: int
    intentos: int = 1
    vencido: bool = False


@dataclass
class Penalizacion:
    """Bloqueo de saltos tras fracasar uno."""

    invertido: int
    meta: int           # puntos nuevos que hay que ganar
    acumulado: int = 0  # puntos nuevos ganados desde el fracaso

    @property
    def faltan(self) -> int:
        return max(0, self.meta - self.acumulado)


@dataclass
class SaltoEnCurso:
    origen: int
    destino: int
    costo: int
    retos: int


@dataclass
class Estado:
    xp: int = 0
    puntos: int = 0
    nivel_actual: int = 1
    niveles: dict[int, ProgresoNivel] = field(default_factory=dict)
    jefes: dict[str, ProgresoJefe] = field(default_factory=dict)
    recompensas: set[str] = field(default_factory=set)  # claves ya pagadas
    pistas: set[str] = field(default_factory=set)
    penalizacion: Penalizacion | None = None
    salto: SaltoEnCurso | None = None
    historial_saltos: list[dict] = field(default_factory=list)
    ultima_diaria: str | None = None  # fecha ISO de la última diaria cobrada
    racha_diaria: int = 0
    racha_entregas: int = 0
    logros: list[str] = field(default_factory=list)
    transformaciones: list[str] = field(default_factory=list)
    acciones: set[str] = field(default_factory=set)  # ids de acciones ya aplicadas

    @classmethod
    def nuevo(cls, catalogo) -> "Estado":
        """Partida nueva: nivel 1 en curso con todas las vidas."""
        inicio = ProgresoNivel(EstadoNivel.ACTUAL, catalogo.config.vidas_por_nivel)
        return cls(niveles={1: inicio})

    def estado_de(self, numero: int) -> EstadoNivel:
        progreso = self.niveles.get(numero)
        return progreso.estado if progreso else EstadoNivel.BLOQUEADO

    # --- Guardado ---
    def a_dict(self) -> dict:
        """Convierte el estado en datos compatibles con JSON."""
        return _a_json(asdict(self))

    @classmethod
    def desde_dict(cls, datos: dict) -> "Estado":
        datos = dict(datos)
        datos["niveles"] = {
            int(numero): ProgresoNivel(
                **{**p, "estado": EstadoNivel(p["estado"]), "entregadas": set(p["entregadas"])}
            )
            for numero, p in datos["niveles"].items()
        }
        datos["jefes"] = {saga: ProgresoJefe(**j) for saga, j in datos["jefes"].items()}
        for campo in ("recompensas", "pistas", "acciones"):
            datos[campo] = set(datos[campo])
        if datos["penalizacion"]:
            datos["penalizacion"] = Penalizacion(**datos["penalizacion"])
        if datos["salto"]:
            datos["salto"] = SaltoEnCurso(**datos["salto"])
        return cls(**datos)


def _a_json(valor):
    if isinstance(valor, Enum):
        return valor.value
    if isinstance(valor, dict):
        return {str(clave): _a_json(v) for clave, v in valor.items()}
    if isinstance(valor, (set, frozenset)):
        return sorted(valor)
    if isinstance(valor, (list, tuple)):
        return [_a_json(v) for v in valor]
    return valor
