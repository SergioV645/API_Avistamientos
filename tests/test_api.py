# Pruebas de INTEGRACIÓN: recorren la API completa por HTTP (rutas + validador
# + SQLite) con el test_client() de Flask. Cada prueba usa una base en memoria
# nueva (fixture "cliente" en conftest.py) y prepara sus propios datos.
from datetime import date, timedelta

from app import crear_app

EJEMPLO = {"especie": "Colibrí", "lugar": "Parque Simón Bolívar", "fecha": "2026-09-29", "observador": "Sergio"}
OTRO = {"especie": "Tucán", "lugar": "Minca", "fecha": "2026-09-20", "observador": "Laura"}


def crear(cliente, datos):
    """Helper de preparación (Arrange): crea un avistamiento y devuelve el JSON."""
    respuesta = cliente.post("/avistamientos", json=datos)
    assert respuesta.status_code == 201
    return respuesta.get_json()


# ---------- GET /avistamientos ----------

def test_listar_sin_avistamientos_devuelve_200_y_lista_vacia(cliente):
    # Act
    r = cliente.get("/avistamientos")
    # Assert
    assert r.status_code == 200
    assert r.get_json() == []


def test_listar_devuelve_todos_los_avistamientos_con_sus_campos(cliente):
    # Arrange
    crear(cliente, EJEMPLO)
    crear(cliente, OTRO)
    # Act
    r = cliente.get("/avistamientos")
    # Assert
    assert r.status_code == 200
    assert r.get_json() == [{"id": 1, **EJEMPLO}, {"id": 2, **OTRO}]


# ---------- POST /avistamientos ----------

def test_crear_valido_devuelve_201_con_el_avistamiento_y_queda_guardado(cliente):
    # Act
    r = cliente.post("/avistamientos", json=EJEMPLO)
    # Assert: respuesta completa
    assert r.status_code == 201
    creado = r.get_json()
    assert creado == {"id": 1, **EJEMPLO}
    assert r.headers["Location"] == "/avistamientos/1"
    # Assert: efecto, un GET al nuevo id lo devuelve
    assert cliente.get("/avistamientos/1").get_json() == creado


def test_crear_ignora_el_id_enviado_por_el_cliente(cliente):
    # Act
    r = cliente.post("/avistamientos", json={**EJEMPLO, "id": 99})
    # Assert
    assert r.get_json()["id"] == 1
    assert cliente.get("/avistamientos/99").status_code == 404


def test_crear_con_especie_corta_devuelve_400_indicando_el_campo_y_no_guarda(cliente):
    # Act
    r = cliente.post("/avistamientos", json={**EJEMPLO, "especie": "ab"})
    # Assert
    assert r.status_code == 400
    cuerpo = r.get_json()
    assert cuerpo["error"] == "Datos inválidos"
    assert [d["campo"] for d in cuerpo["detalles"]] == ["especie"]
    assert cliente.get("/avistamientos").get_json() == []


def test_crear_con_fecha_futura_devuelve_400_indicando_la_fecha(cliente):
    # Arrange: el reloj de la API está fijo en 2026-10-21
    datos = {**EJEMPLO, "fecha": "2026-10-22"}
    # Act
    r = cliente.post("/avistamientos", json=datos)
    # Assert
    assert r.status_code == 400
    assert r.get_json()["detalles"] == [{"campo": "fecha", "mensaje": "no puede ser posterior a hoy"}]


def test_crear_sin_reloj_inyectado_usa_la_fecha_real_del_sistema():
    # Arrange: API con el reloj real (sin stub)
    cliente_real = crear_app(":memory:").test_client()
    manana = (date.today() + timedelta(days=1)).isoformat()
    # Act
    r = cliente_real.post("/avistamientos", json={**EJEMPLO, "fecha": manana})
    # Assert
    assert r.status_code == 400


def test_crear_con_json_mal_formado_devuelve_400(cliente):
    # Act
    r = cliente.post("/avistamientos", data="{ no es json", content_type="application/json")
    # Assert
    assert r.status_code == 400
    assert r.get_json()["detalles"][0]["campo"] == "cuerpo"


def test_crear_un_avistamiento_repetido_devuelve_409_y_no_lo_duplica(cliente):
    # Arrange
    crear(cliente, EJEMPLO)
    # Act: mismo avistamiento, con otras mayúsculas
    r = cliente.post("/avistamientos", json={**EJEMPLO, "lugar": "parque simón bolívar"})
    # Assert
    assert r.status_code == 409
    assert "Ya existe" in r.get_json()["error"]
    assert len(cliente.get("/avistamientos").get_json()) == 1


# ---------- GET /avistamientos/{id} ----------

def test_ver_un_avistamiento_existente_devuelve_200_con_sus_datos(cliente):
    # Arrange
    creado = crear(cliente, EJEMPLO)
    # Act
    r = cliente.get(f"/avistamientos/{creado['id']}")
    # Assert
    assert r.status_code == 200
    assert r.get_json() == {"id": creado["id"], **EJEMPLO}


def test_ver_un_id_que_no_existe_devuelve_404_con_mensaje(cliente):
    # Act
    r = cliente.get("/avistamientos/999")
    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


# ---------- PUT /avistamientos/{id} ----------

def test_actualizar_devuelve_200_y_el_cambio_queda_guardado(cliente):
    # Arrange
    creado = crear(cliente, EJEMPLO)
    # Act
    r = cliente.put(f"/avistamientos/{creado['id']}", json=OTRO)
    # Assert: respuesta y efecto
    assert r.status_code == 200
    assert r.get_json() == {"id": creado["id"], **OTRO}
    assert cliente.get(f"/avistamientos/{creado['id']}").get_json() == {"id": creado["id"], **OTRO}


def test_actualizar_un_id_que_no_existe_devuelve_404(cliente):
    # Act
    r = cliente.put("/avistamientos/999", json=EJEMPLO)
    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


def test_actualizar_con_especie_de_51_caracteres_devuelve_400_y_no_cambia_nada(cliente):
    # Arrange
    creado = crear(cliente, EJEMPLO)
    # Act
    r = cliente.put(f"/avistamientos/{creado['id']}", json={**EJEMPLO, "especie": "a" * 51})
    # Assert
    assert r.status_code == 400
    assert r.get_json()["detalles"][0]["campo"] == "especie"
    assert cliente.get(f"/avistamientos/{creado['id']}").get_json() == creado


def test_actualizar_para_que_quede_igual_a_otro_devuelve_409(cliente):
    # Arrange
    crear(cliente, EJEMPLO)
    otro = crear(cliente, OTRO)
    # Act
    r = cliente.put(f"/avistamientos/{otro['id']}", json=EJEMPLO)
    # Assert
    assert r.status_code == 409
    assert cliente.get(f"/avistamientos/{otro['id']}").get_json() == otro


# ---------- DELETE /avistamientos/{id} ----------

def test_eliminar_devuelve_204_y_despues_el_avistamiento_ya_no_existe(cliente):
    # Arrange
    creado = crear(cliente, EJEMPLO)
    # Act
    r = cliente.delete(f"/avistamientos/{creado['id']}")
    # Assert: respuesta sin cuerpo y efecto
    assert r.status_code == 204
    assert r.data == b""
    assert cliente.get(f"/avistamientos/{creado['id']}").status_code == 404
    assert cliente.get("/avistamientos").get_json() == []


def test_eliminar_un_id_que_no_existe_devuelve_404(cliente):
    # Act
    r = cliente.delete("/avistamientos/999")
    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


# ---------- GET /avistamientos/resumen (bonus) ----------

def test_resumen_cuenta_los_avistamientos_por_especie(cliente):
    # Arrange
    crear(cliente, EJEMPLO)
    crear(cliente, {**EJEMPLO, "fecha": "2026-09-30"})
    crear(cliente, OTRO)
    # Act
    r = cliente.get("/avistamientos/resumen")
    # Assert
    assert r.status_code == 200
    assert r.get_json() == {
        "total": 3,
        "porEspecie": [{"especie": "Colibrí", "cantidad": 2}, {"especie": "Tucán", "cantidad": 1}],
    }
