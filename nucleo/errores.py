"""Error único del núcleo."""


class AccionInvalida(Exception):
    """La acción no está permitida por las reglas.

    `codigo` es un texto corto y estable (para el servidor y las pruebas);
    `mensaje` es la explicación para la persona.
    """

    def __init__(self, codigo: str, mensaje: str):
        super().__init__(f"{codigo}: {mensaje}")
        self.codigo = codigo
        self.mensaje = mensaje
