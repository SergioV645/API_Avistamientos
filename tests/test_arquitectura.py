# Prueba de la REGLA DE DEPENDENCIA (Martin, 2012): los imports solo pueden
# apuntar hacia adentro. Lee el código fuente de cada capa y falla si una capa
# interna importa algo de una externa o un framework (flask, sqlite3).
import ast
from pathlib import Path

import pytest

PAQUETE = Path(__file__).resolve().parent.parent / "avistamientos"

# Para cada capa: qué capas del proyecto puede importar (ella misma y las internas)
PERMITIDAS = {
    "entidades": {"entidades"},
    "casos_de_uso": {"entidades", "casos_de_uso"},
    "adaptadores": {"entidades", "casos_de_uso", "adaptadores"},
}
FRAMEWORKS = {"flask", "sqlite3", "werkzeug"}


def imports_de(archivo):
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            yield from (a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.module


@pytest.mark.parametrize("capa", sorted(PERMITIDAS))
def test_cada_capa_solo_importa_capas_mas_internas(capa):
    violaciones = []
    for archivo in (PAQUETE / capa).glob("*.py"):
        for modulo in imports_de(archivo):
            partes = modulo.split(".")
            if partes[0] == "avistamientos" and len(partes) > 1 and partes[1] not in PERMITIDAS[capa]:
                violaciones.append(f"{archivo.name} importa {modulo}")
    assert violaciones == []


@pytest.mark.parametrize("capa", ["entidades", "casos_de_uso"])
def test_entidades_y_casos_de_uso_no_conocen_frameworks(capa):
    violaciones = [
        f"{archivo.name} importa {modulo}"
        for archivo in (PAQUETE / capa).glob("*.py")
        for modulo in imports_de(archivo)
        if modulo.split(".")[0] in FRAMEWORKS
    ]
    assert violaciones == []


def test_los_adaptadores_no_conocen_flask():
    violaciones = [
        f"{archivo.name} importa {modulo}"
        for archivo in (PAQUETE / "adaptadores").glob("*.py")
        for modulo in imports_de(archivo)
        if modulo.split(".")[0] in {"flask", "werkzeug"}
    ]
    assert violaciones == []
