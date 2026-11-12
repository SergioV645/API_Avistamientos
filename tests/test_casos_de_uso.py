# Pruebas UNITARIAS de los casos de uso (Taller 5).
# Usan un fake del repositorio (RepositorioEnMemoria) en lugar de SQLite y el
# stub RelojFijo: prueban la orquestación sin Flask ni base de datos.
# Antes del refactor no se podían escribir: la lógica estaba dentro de las
# rutas de Flask y llamaba directamente a SQLite.
import pytest

from avistamientos.casos_de_uso.avistamientos import (
    ActualizarAvistamiento,
    ConsultarAvistamiento,
    EliminarAvistamiento,
    RegistrarAvistamiento,
    ResumirPorEspecie,
)
from avistamientos.casos_de_uso.errores import AvistamientoNoEncontrado, AvistamientoRepetido, DatosInvalidos
from avistamientos.entidades.validador import ValidadorDeAvistamiento
from tests.dobles import HOY, RelojFijo, RepositorioEnMemoria

VALIDO = {"especie": "Colibrí", "lugar": "Bogotá", "fecha": "2026-10-01", "observador": "Sergio"}


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def test_registrar_valido_lo_guarda_limpio_y_devuelve_el_id(repo, validador):
    # Arrange
    datos = {**VALIDO, "especie": "  Colibrí  ", "id": 99}
    # Act
    creado = RegistrarAvistamiento(repo, validador).ejecutar(datos)
    # Assert: espacios quitados, id del sistema (no el del cliente), guardado
    assert creado == {"id": 1, **VALIDO}
    assert repo.listar() == [creado]


def test_registrar_invalido_lanza_datos_invalidos_y_no_guarda_nada(repo, validador):
    # Arrange
    datos = {**VALIDO, "especie": "ab"}
    # Act
    with pytest.raises(DatosInvalidos) as error:
        RegistrarAvistamiento(repo, validador).ejecutar(datos)
    # Assert
    assert [e["campo"] for e in error.value.errores] == ["especie"]
    assert repo.listar() == []


def test_registrar_repetido_propaga_avistamiento_repetido(repo, validador):
    # Arrange
    RegistrarAvistamiento(repo, validador).ejecutar(VALIDO)
    # Act / Assert
    with pytest.raises(AvistamientoRepetido):
        RegistrarAvistamiento(repo, validador).ejecutar({**VALIDO, "especie": "colibrí"})


def test_consultar_un_id_que_no_existe_lanza_no_encontrado(repo):
    # Act / Assert
    with pytest.raises(AvistamientoNoEncontrado):
        ConsultarAvistamiento(repo).ejecutar(7)


def test_actualizar_un_id_inexistente_da_no_encontrado_antes_de_validar(repo, validador):
    # Arrange: datos inválidos Y id inexistente; debe ganar "no encontrado" (404),
    # como en la API antes del refactor.
    datos = {**VALIDO, "especie": "ab"}
    # Act / Assert
    with pytest.raises(AvistamientoNoEncontrado):
        ActualizarAvistamiento(repo, validador).ejecutar(7, datos)


def test_eliminar_un_id_inexistente_lanza_no_encontrado(repo):
    # Act / Assert
    with pytest.raises(AvistamientoNoEncontrado):
        EliminarAvistamiento(repo).ejecutar(7)


def test_resumir_suma_el_total_de_todas_las_especies(repo, validador):
    # Arrange
    registrar = RegistrarAvistamiento(repo, validador)
    registrar.ejecutar(VALIDO)
    registrar.ejecutar({**VALIDO, "fecha": "2026-09-30"})
    registrar.ejecutar({**VALIDO, "especie": "Tucán"})
    # Act
    resumen = ResumirPorEspecie(repo).ejecutar()
    # Assert
    assert resumen == {
        "total": 3,
        "porEspecie": [{"especie": "Colibrí", "cantidad": 2}, {"especie": "Tucán", "cantidad": 1}],
    }
