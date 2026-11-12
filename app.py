from flask import Flask, jsonify, request

from avistamientos.adaptadores.repositorio_sqlite import RepositorioSqliteDeAvistamientos
from avistamientos.casos_de_uso.errores import AvistamientoRepetido
from avistamientos.entidades.validador import ValidadorDeAvistamiento
from avistamientos.frameworks_y_drivers.reloj_del_sistema import RelojDelSistema
from avistamientos.frameworks_y_drivers.sqlite import abrir_conexion

CAMPOS = ["especie", "lugar", "fecha", "observador"]
REPETIDO = {"error": "Ya existe un avistamiento con la misma especie, lugar, fecha y observador"}


def limpiar(body):
    """Se queda solo con los 4 campos (ignora un "id" enviado por el cliente)."""
    return {campo: body[campo].strip() for campo in CAMPOS}


def crear_app(ruta_db=None, reloj=None):
    """Crea la API. ruta_db y reloj se pueden reemplazar en las pruebas."""
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    repo = RepositorioSqliteDeAvistamientos(abrir_conexion(ruta_db))
    validador = ValidadorDeAvistamiento(reloj or RelojDelSistema())

    def datos_invalidos(errores):
        return jsonify({"error": "Datos inválidos", "detalles": errores}), 400

    @app.get("/avistamientos")
    def listar():
        return jsonify(repo.listar()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        por_especie = repo.contar_por_especie()
        total = sum(f["cantidad"] for f in por_especie)
        return jsonify({"total": total, "porEspecie": por_especie}), 200

    @app.get("/avistamientos/<int:id>")
    def ver(id):
        avistamiento = repo.buscar_por_id(id)
        if avistamiento is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        return jsonify(avistamiento), 200

    @app.post("/avistamientos")
    def crear():
        body = request.get_json(silent=True)
        errores = validador.validar(body)
        if errores:
            return datos_invalidos(errores)
        try:
            creado = repo.agregar(limpiar(body))
        except AvistamientoRepetido:  # la base rechazó el duplicado
            return jsonify(REPETIDO), 409
        return jsonify(creado), 201, {"Location": f"/avistamientos/{creado['id']}"}

    @app.put("/avistamientos/<int:id>")
    def actualizar(id):
        if repo.buscar_por_id(id) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        body = request.get_json(silent=True)
        errores = validador.validar(body)
        if errores:
            return datos_invalidos(errores)
        try:
            actualizado = repo.actualizar(id, limpiar(body))
        except AvistamientoRepetido:  # quedaría igual a otro avistamiento
            return jsonify(REPETIDO), 409
        return jsonify(actualizado), 200

    @app.delete("/avistamientos/<int:id>")
    def eliminar(id):
        if not repo.eliminar(id):
            return jsonify({"error": "Avistamiento no encontrado"}), 404
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
