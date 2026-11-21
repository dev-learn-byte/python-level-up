"""Lo que las reglas necesitan saber del contenido: niveles, jefes y eventos.

El catálogo no contiene enunciados ni código; solo identificadores y
recompensas. Agregar una saga es agregar entradas aquí, sin tocar las reglas.
"""
from dataclasses import dataclass

from .config import Config
from .errores import AccionInvalida


@dataclass(frozen=True)
class Mision:
    id: str
    xp: int = 10
    puntos: int = 10


@dataclass(frozen=True)
class Nivel:
    numero: int
    saga: str
    misiones: tuple[Mision, ...]
    retos_evaluacion: int = 10
    xp_evaluacion: int = 50
    puntos_evaluacion: int = 30


@dataclass(frozen=True)
class Jefe:
    saga: str
    transformacion: str
    requisitos: int = 8
    xp: int = 150
    puntos: int = 100
    final: bool = False  # el jefe final exige haber completado todo


@dataclass(frozen=True)
class Evento:
    """Misión especial (evento o mazmorra). Paga una sola vez."""

    id: str
    xp: int = 40
    puntos: int = 50
    requiere_nivel: int = 0  # nivel que debe estar aprobado (0 = ninguno)


class Catalogo:
    def __init__(self, niveles, jefes=(), eventos=(), config: Config | None = None):
        self.config = config or Config()
        self._niveles = {n.numero: n for n in niveles}
        self._jefes = {j.saga: j for j in jefes}
        self._eventos = {e.id: e for e in eventos}
        self.sagas: list[str] = list(dict.fromkeys(n.saga for n in niveles))
        self._validar(list(niveles), list(jefes), list(eventos))

    def _validar(self, niveles, jefes, eventos):
        numeros = [n.numero for n in niveles]
        if numeros != list(range(1, len(niveles) + 1)):
            raise ValueError("los niveles deben numerarse 1, 2, 3... sin huecos")
        vistas = []
        for nivel in niveles:  # cada saga ocupa niveles seguidos
            if nivel.saga not in vistas:
                vistas.append(nivel.saga)
            elif vistas[-1] != nivel.saga:
                raise ValueError(f"la saga {nivel.saga!r} tiene niveles separados")
        ids = [m.id for n in niveles for m in n.misiones]
        if len(ids) != len(set(ids)):
            raise ValueError("hay identificadores de misión repetidos")
        if len(self._eventos) != len(eventos):
            raise ValueError("hay identificadores de evento repetidos")
        if len(self._jefes) != len(jefes):
            raise ValueError("una saga tiene más de un jefe")
        for jefe in jefes:
            if jefe.saga not in self.sagas:
                raise ValueError(f"jefe de una saga inexistente: {jefe.saga!r}")
            if jefe.final and jefe.saga != self.sagas[-1]:
                raise ValueError("el jefe final debe estar en la última saga")

    # --- Consultas ---
    @property
    def numeros(self) -> list[int]:
        return list(self._niveles)

    def existe(self, numero: int) -> bool:
        return numero in self._niveles

    def nivel(self, numero: int) -> Nivel:
        if numero not in self._niveles:
            raise AccionInvalida("nivel_inexistente", f"No existe el nivel {numero}.")
        return self._niveles[numero]

    def mision(self, numero: int, mision_id: str) -> Mision:
        for mision in self.nivel(numero).misiones:
            if mision.id == mision_id:
                return mision
        raise AccionInvalida(
            "mision_inexistente", f"El nivel {numero} no tiene la misión {mision_id!r}."
        )

    def niveles_de(self, saga: str) -> list[int]:
        return [n.numero for n in self._niveles.values() if n.saga == saga]

    def jefe(self, saga: str) -> Jefe | None:
        return self._jefes.get(saga)

    def jefes(self) -> list[Jefe]:
        return list(self._jefes.values())

    def evento(self, evento_id: str) -> Evento:
        if evento_id not in self._eventos:
            raise AccionInvalida("evento_inexistente", f"No existe el evento {evento_id!r}.")
        return self._eventos[evento_id]

    def es_ultimo_de_saga(self, numero: int) -> bool:
        return self.niveles_de(self.nivel(numero).saga)[-1] == numero

    def primer_nivel_de_saga_siguiente(self, saga: str) -> int | None:
        posicion = self.sagas.index(saga)
        if posicion + 1 == len(self.sagas):
            return None
        return self.niveles_de(self.sagas[posicion + 1])[0]
