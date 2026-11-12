# Errores de la aplicación. Los lanzan los casos de uso y los adaptadores;
# el controlador HTTP los traduce a códigos de estado (400, 404, 409).


class DatosInvalidos(Exception):
    def __init__(self, errores):
        super().__init__("Datos inválidos")
        self.errores = errores


class AvistamientoNoEncontrado(Exception):
    pass


class AvistamientoRepetido(Exception):
    pass
