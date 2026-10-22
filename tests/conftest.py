# Configuración compartida de pytest.
import pytest

from app import crear_app
from tests.dobles import HOY, RelojFijo


@pytest.fixture
def cliente():
    """Cliente HTTP de Flask sobre una API nueva en cada prueba.

    Cada prueba recibe una base de datos en memoria vacía, así que ninguna
    depende de los datos ni del orden de las otras.
    """
    app = crear_app(":memory:", reloj=RelojFijo(HOY))
    return app.test_client()
