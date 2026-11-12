from flask import Flask, jsonify, request

from avistamientos.adaptadores.repositorio_sqlite import RepositorioSqliteDeAvistamientos
from avistamientos.casos_de_uso.avistamientos import (
    ActualizarAvistamiento,
    ConsultarAvistamiento,
    EliminarAvistamiento,
    ListarAvistamientos,
    RegistrarAvistamiento,
    ResumirPorEspecie,
)
from avistamientos.casos_de_uso.errores import AvistamientoNoEncontrado, AvistamientoRepetido, DatosInvalidos
from avistamientos.entidades.validador import ValidadorDeAvistamiento
from avistamientos.frameworks_y_drivers.reloj_del_sistema import RelojDelSistema
from avistamientos.frameworks_y_drivers.sqlite import abrir_conexion

REPETIDO = {"error": "Ya existe un avistamiento con la misma especie, lugar, fecha y observador"}
NO_ENCONTRADO = {"error": "Avistamiento no encontrado"}


def crear_app(ruta_db=None, reloj=None):
    """Crea la API. ruta_db y reloj se pueden reemplazar en las pruebas."""
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    repo = RepositorioSqliteDeAvistamientos(abrir_conexion(ruta_db))
    validador = ValidadorDeAvistamiento(reloj or RelojDelSistema())

    @app.get("/avistamientos")
    def listar():
        return jsonify(ListarAvistamientos(repo).ejecutar()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify(ResumirPorEspecie(repo).ejecutar()), 200

    @app.get("/avistamientos/<int:id>")
    def ver(id):
        try:
            return jsonify(ConsultarAvistamiento(repo).ejecutar(id)), 200
        except AvistamientoNoEncontrado:
            return jsonify(NO_ENCONTRADO), 404

    @app.post("/avistamientos")
    def crear():
        try:
            creado = RegistrarAvistamiento(repo, validador).ejecutar(request.get_json(silent=True))
        except DatosInvalidos as e:
            return jsonify({"error": "Datos inválidos", "detalles": e.errores}), 400
        except AvistamientoRepetido:
            return jsonify(REPETIDO), 409
        return jsonify(creado), 201, {"Location": f"/avistamientos/{creado['id']}"}

    @app.put("/avistamientos/<int:id>")
    def actualizar(id):
        try:
            actualizado = ActualizarAvistamiento(repo, validador).ejecutar(id, request.get_json(silent=True))
        except AvistamientoNoEncontrado:
            return jsonify(NO_ENCONTRADO), 404
        except DatosInvalidos as e:
            return jsonify({"error": "Datos inválidos", "detalles": e.errores}), 400
        except AvistamientoRepetido:
            return jsonify(REPETIDO), 409
        return jsonify(actualizado), 200

    @app.delete("/avistamientos/<int:id>")
    def eliminar(id):
        try:
            EliminarAvistamiento(repo).ejecutar(id)
        except AvistamientoNoEncontrado:
            return jsonify(NO_ENCONTRADO), 404
        return "", 204

    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(e):
        return jsonify({"error": "Método no permitido"}), 405

    return app


if __name__ == "__main__":
    crear_app().run(port=3000, debug=True)
