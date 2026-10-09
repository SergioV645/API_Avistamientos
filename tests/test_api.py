# Pruebas de integración con pytest. Usan una base de datos en memoria.
import pytest

from app import crear_app

EJEMPLO = {"especie": "colibrí", "lugar": "Parque Simón Bolívar", "fecha": "2026-09-29", "observador": "Sergio"}


@pytest.fixture
def cliente():
    app = crear_app(":memory:")
    return app.test_client()


def test_listar_devuelve_200_y_lista(cliente):
    r = cliente.get("/avistamientos")
    assert r.status_code == 200
    assert r.get_json() == []


def test_crear_devuelve_201_con_id(cliente):
    r = cliente.post("/avistamientos", json=EJEMPLO)
    assert r.status_code == 201
    creado = r.get_json()
    assert creado["id"] == 1
    assert creado["especie"] == "colibrí"


def test_crear_con_datos_faltantes_devuelve_400(cliente):
    r = cliente.post("/avistamientos", json={"especie": "garza"})
    assert r.status_code == 400
    assert len(r.get_json()["detalles"]) == 3


def test_crear_con_fecha_invalida_devuelve_400(cliente):
    assert cliente.post("/avistamientos", json={**EJEMPLO, "fecha": "29/09/2026"}).status_code == 400
    assert cliente.post("/avistamientos", json={**EJEMPLO, "fecha": "2026-02-30"}).status_code == 400


def test_crear_con_json_mal_formado_devuelve_400(cliente):
    r = cliente.post("/avistamientos", data="{ no es json", content_type="application/json")
    assert r.status_code == 400


def test_ver_uno_200_y_404(cliente):
    creado = cliente.post("/avistamientos", json=EJEMPLO).get_json()
    r = cliente.get(f"/avistamientos/{creado['id']}")
    assert r.status_code == 200
    assert r.get_json() == creado
    assert cliente.get("/avistamientos/999").status_code == 404
    assert cliente.get("/avistamientos/abc").status_code == 404


def test_actualizar_200_404_400(cliente):
    creado = cliente.post("/avistamientos", json=EJEMPLO).get_json()
    cambios = {**EJEMPLO, "especie": "tucán", "lugar": "Minca"}
    r = cliente.put(f"/avistamientos/{creado['id']}", json=cambios)
    assert r.status_code == 200
    assert r.get_json() == {"id": creado["id"], **cambios}
    assert cliente.put("/avistamientos/999", json=cambios).status_code == 404
    assert cliente.put(f"/avistamientos/{creado['id']}", json={"especie": "x"}).status_code == 400


def test_eliminar_204_y_luego_404(cliente):
    creado = cliente.post("/avistamientos", json=EJEMPLO).get_json()
    assert cliente.delete(f"/avistamientos/{creado['id']}").status_code == 204
    assert cliente.get(f"/avistamientos/{creado['id']}").status_code == 404
    assert cliente.delete(f"/avistamientos/{creado['id']}").status_code == 404


def test_resumen_por_especie(cliente):
    cliente.post("/avistamientos", json={**EJEMPLO, "especie": "cóndor"})
    cliente.post("/avistamientos", json={**EJEMPLO, "especie": "cóndor"})
    cliente.post("/avistamientos", json=EJEMPLO)
    r = cliente.get("/avistamientos/resumen")
    assert r.status_code == 200
    assert r.get_json() == {
        "total": 3,
        "porEspecie": [{"especie": "cóndor", "cantidad": 2}, {"especie": "colibrí", "cantidad": 1}],
    }
