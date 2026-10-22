# Pruebas UNITARIAS de la regla de negocio (ValidadorDeAvistamiento).
# No levantan la API ni tocan la base de datos: prueban la lógica aislada.
# El reloj se reemplaza por un stub (RelojFijo) con hoy = 2026-10-21.
from datetime import timedelta

import pytest

from tests.dobles import HOY, RelojFijo
from validador import ValidadorDeAvistamiento

VALIDO = {"especie": "Colibrí", "lugar": "Bogotá", "fecha": "2026-10-01", "observador": "Sergio"}


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def campos_con_error(errores):
    return [e["campo"] for e in errores]


# ---------- Caso representativo ----------

def test_avistamiento_con_todos_los_campos_validos_no_tiene_errores(validador):
    # Arrange
    datos = dict(VALIDO)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == []


# ---------- Especie: partición y valores límite (3 a 50 caracteres) ----------

def test_especie_de_2_caracteres_es_invalida_por_estar_bajo_el_minimo(validador):
    # Arrange
    datos = {**VALIDO, "especie": "ab"}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["especie"]
    assert "entre 3 y 50" in errores[0]["mensaje"]


def test_especie_de_3_caracteres_es_valida_por_ser_el_minimo(validador):
    # Arrange
    datos = {**VALIDO, "especie": "abc"}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == []


def test_especie_de_50_caracteres_es_valida_por_ser_el_maximo(validador):
    # Arrange
    datos = {**VALIDO, "especie": "a" * 50}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == []


def test_especie_de_51_caracteres_es_invalida_por_superar_el_maximo(validador):
    # Arrange
    datos = {**VALIDO, "especie": "a" * 51}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["especie"]
    assert "(tiene 51)" in errores[0]["mensaje"]


def test_especie_con_espacios_alrededor_se_mide_sin_los_espacios(validador):
    # Arrange: "  ab  " tiene 6 caracteres, pero solo 2 son de la especie
    datos = {**VALIDO, "especie": "  ab  "}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["especie"]


def test_especie_ausente_es_invalida(validador):
    # Arrange
    datos = {k: v for k, v in VALIDO.items() if k != "especie"}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["especie"]


# ---------- Fecha: formato y valores límite alrededor de hoy ----------

def test_fecha_de_hoy_es_valida_por_ser_el_limite_permitido(validador):
    # Arrange
    datos = {**VALIDO, "fecha": HOY.isoformat()}  # 2026-10-21
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == []


def test_fecha_de_manana_es_invalida_por_ser_posterior_a_hoy(validador):
    # Arrange
    datos = {**VALIDO, "fecha": (HOY + timedelta(days=1)).isoformat()}  # 2026-10-22
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == [{"campo": "fecha", "mensaje": "no puede ser posterior a hoy"}]


@pytest.mark.parametrize("fecha", ["21/10/2026", "2026-10-1", "20261021", "hoy"])
def test_fecha_con_formato_distinto_a_aaaa_mm_dd_es_invalida(validador, fecha):
    # Arrange
    datos = {**VALIDO, "fecha": fecha}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == [{"campo": "fecha", "mensaje": "debe tener el formato AAAA-MM-DD"}]


@pytest.mark.parametrize("fecha", ["", "   ", None, 20261021])
def test_fecha_vacia_o_que_no_es_texto_es_invalida(validador, fecha):
    # Arrange (agregada después de leer la cobertura: esta rama no estaba cubierta)
    datos = {**VALIDO, "fecha": fecha}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == [{"campo": "fecha", "mensaje": "es obligatoria y debe ser texto"}]


def test_fecha_con_formato_correcto_pero_dia_inexistente_es_invalida(validador):
    # Arrange: 2025 no es bisiesto, el 29 de febrero no existe
    datos = {**VALIDO, "fecha": "2025-02-29"}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["fecha"]


# ---------- Lugar y observador: no vacíos ----------

@pytest.mark.parametrize("campo", ["lugar", "observador"])
@pytest.mark.parametrize("valor", ["", "   "])
def test_lugar_u_observador_vacio_o_solo_espacios_es_invalido(validador, campo, valor):
    # Arrange
    datos = {**VALIDO, campo: valor}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == [{"campo": campo, "mensaje": "no puede estar vacío"}]


# ---------- Varios errores y cuerpo inválido ----------

def test_cuando_fallan_varios_campos_se_reportan_todos(validador):
    # Arrange
    datos = {"especie": "ab", "lugar": "", "fecha": "2026-12-31", "observador": ""}
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["especie", "fecha", "lugar", "observador"]


def test_cuerpo_que_no_es_un_objeto_es_invalido(validador):
    # Arrange
    datos = ["no", "es", "un", "objeto"]
    # Act
    errores = validador.validar(datos)
    # Assert
    assert campos_con_error(errores) == ["cuerpo"]
