# Casos de uso (interactores) de la API de avistamientos.
#
# Cada caso de uso recibe datos simples (dicts), usa la entidad
# ValidadorDeAvistamiento para aplicar la regla de negocio y el puerto
# RepositorioDeAvistamientos para guardar. No sabe nada de HTTP ni de SQL:
# comunica los fallos con los errores de errores.py.
from avistamientos.casos_de_uso.errores import AvistamientoNoEncontrado, DatosInvalidos

CAMPOS = ["especie", "lugar", "fecha", "observador"]


def _limpiar(datos):
    """Se queda solo con los 4 campos (ignora un "id" enviado por el cliente)."""
    return {campo: datos[campo].strip() for campo in CAMPOS}


class ListarAvistamientos:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self):
        return self.repositorio.listar()


class ConsultarAvistamiento:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id):
        avistamiento = self.repositorio.buscar_por_id(id)
        if avistamiento is None:
            raise AvistamientoNoEncontrado()
        return avistamiento


class RegistrarAvistamiento:
    def __init__(self, repositorio, validador):
        self.repositorio = repositorio
        self.validador = validador

    def ejecutar(self, datos):
        errores = self.validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
        return self.repositorio.agregar(_limpiar(datos))


class ActualizarAvistamiento:
    def __init__(self, repositorio, validador):
        self.repositorio = repositorio
        self.validador = validador

    def ejecutar(self, id, datos):
        # Primero se verifica que exista (404) y después los datos (400),
        # el mismo orden que tenía la API antes del refactor.
        if self.repositorio.buscar_por_id(id) is None:
            raise AvistamientoNoEncontrado()
        errores = self.validador.validar(datos)
        if errores:
            raise DatosInvalidos(errores)
        return self.repositorio.actualizar(id, _limpiar(datos))


class EliminarAvistamiento:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id):
        if not self.repositorio.eliminar(id):
            raise AvistamientoNoEncontrado()


class ResumirPorEspecie:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self):
        por_especie = self.repositorio.contar_por_especie()
        return {"total": sum(f["cantidad"] for f in por_especie), "porEspecie": por_especie}
