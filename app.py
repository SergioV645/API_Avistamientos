# Punto de entrada: `python app.py` levanta la API en http://localhost:3000.
# Toda la construcción está en avistamientos/main.py (raíz de composición).
from avistamientos.main import crear_app

__all__ = ["crear_app"]

if __name__ == "__main__":
    crear_app().run(port=3000, debug=True)
