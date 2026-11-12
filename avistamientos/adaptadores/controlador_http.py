# Adaptador de entrada: el controlador HTTP.
#
# Traduce una petición (método, id, cuerpo ya convertido a dict) a una llamada
# a un caso de uso, y el resultado o el error del caso de uso a una
# RespuestaHttp (código de estado + cuerpo + encabezados).
# No importa Flask: la RespuestaHttp es una estructura de datos simple, y es
# el framework (círculo externo) quien la convierte en una respuesta real.
from dataclasses import dataclass, field

from avistamientos.casos_de_uso.errores import AvistamientoNoEncontrado, AvistamientoRepetido, DatosInvalidos

REPETIDO = {"error": "Ya existe un avistamiento con la misma especie, lugar, fecha y observador"}
NO_ENCONTRADO = {"error": "Avistamiento no encontrado"}


@dataclass
class RespuestaHttp:
    estado: int
    cuerpo: object = None
    encabezados: dict = field(default_factory=dict)


class ControladorDeAvistamientos:
    def __init__(self, listar, consultar, registrar, actualizar, eliminar, resumir):
        self._listar = listar
        self._consultar = consultar
        self._registrar = registrar
        self._actualizar = actualizar
        self._eliminar = eliminar
        self._resumir = resumir

    def listar(self):
        return RespuestaHttp(200, self._listar.ejecutar())

    def resumen(self):
        return RespuestaHttp(200, self._resumir.ejecutar())

    def ver(self, id):
        try:
            return RespuestaHttp(200, self._consultar.ejecutar(id))
        except AvistamientoNoEncontrado:
            return RespuestaHttp(404, NO_ENCONTRADO)

    def crear(self, cuerpo):
        try:
            creado = self._registrar.ejecutar(cuerpo)
        except DatosInvalidos as e:
            return _datos_invalidos(e)
        except AvistamientoRepetido:
            return RespuestaHttp(409, REPETIDO)
        return RespuestaHttp(201, creado, {"Location": f"/avistamientos/{creado['id']}"})

    def actualizar(self, id, cuerpo):
        try:
            return RespuestaHttp(200, self._actualizar.ejecutar(id, cuerpo))
        except AvistamientoNoEncontrado:
            return RespuestaHttp(404, NO_ENCONTRADO)
        except DatosInvalidos as e:
            return _datos_invalidos(e)
        except AvistamientoRepetido:
            return RespuestaHttp(409, REPETIDO)

    def eliminar(self, id):
        try:
            self._eliminar.ejecutar(id)
        except AvistamientoNoEncontrado:
            return RespuestaHttp(404, NO_ENCONTRADO)
        return RespuestaHttp(204)


def _datos_invalidos(error):
    return RespuestaHttp(400, {"error": "Datos inválidos", "detalles": error.errores})
