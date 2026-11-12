# Raíz de composición: el componente "Main" de Martin (2017, cap. 26).
# Es el único lugar que conoce todas las capas: crea los detalles concretos
# (conexión SQLite, reloj del sistema, Flask) y se los entrega a las capas
# internas, que solo conocen las abstracciones (Reloj, RepositorioDeAvistamientos).
from avistamientos.adaptadores.controlador_http import ControladorDeAvistamientos
from avistamientos.adaptadores.repositorio_sqlite import RepositorioSqliteDeAvistamientos
from avistamientos.casos_de_uso.avistamientos import (
    ActualizarAvistamiento,
    ConsultarAvistamiento,
    EliminarAvistamiento,
    ListarAvistamientos,
    RegistrarAvistamiento,
    ResumirPorEspecie,
)
from avistamientos.entidades.validador import ValidadorDeAvistamiento
from avistamientos.frameworks_y_drivers.reloj_del_sistema import RelojDelSistema
from avistamientos.frameworks_y_drivers.sqlite import abrir_conexion
from avistamientos.frameworks_y_drivers.web_flask import crear_app_flask


def crear_app(ruta_db=None, reloj=None):
    """Arma la API completa. ruta_db y reloj se pueden reemplazar en las pruebas."""
    repositorio = RepositorioSqliteDeAvistamientos(abrir_conexion(ruta_db))
    validador = ValidadorDeAvistamiento(reloj or RelojDelSistema())
    controlador = ControladorDeAvistamientos(
        listar=ListarAvistamientos(repositorio),
        consultar=ConsultarAvistamiento(repositorio),
        registrar=RegistrarAvistamiento(repositorio, validador),
        actualizar=ActualizarAvistamiento(repositorio, validador),
        eliminar=EliminarAvistamiento(repositorio),
        resumir=ResumirPorEspecie(repositorio),
    )
    return crear_app_flask(controlador)
