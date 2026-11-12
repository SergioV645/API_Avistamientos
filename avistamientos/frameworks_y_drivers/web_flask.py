# Detalle: Flask. Es "código pegamento" (Martin): declara las rutas, saca los
# datos de la petición y convierte la RespuestaHttp del controlador en una
# respuesta de Flask. No contiene reglas de negocio.
from flask import Flask, jsonify, request


def crear_app_flask(controlador):
    app = Flask(__name__)
    app.json.ensure_ascii = False  # muestra tildes tal cual: "Colibrí"
    app.json.sort_keys = False     # respeta el orden de los campos (id primero)

    def responder(respuesta):
        if respuesta.cuerpo is None:
            return "", respuesta.estado, respuesta.encabezados
        return jsonify(respuesta.cuerpo), respuesta.estado, respuesta.encabezados

    @app.get("/avistamientos")
    def listar():
        return responder(controlador.listar())

    @app.get("/avistamientos/resumen")
    def resumen():
        return responder(controlador.resumen())

    @app.get("/avistamientos/<int:id>")
    def ver(id):
        return responder(controlador.ver(id))

    @app.post("/avistamientos")
    def crear():
        return responder(controlador.crear(request.get_json(silent=True)))

    @app.put("/avistamientos/<int:id>")
    def actualizar(id):
        return responder(controlador.actualizar(id, request.get_json(silent=True)))

    @app.delete("/avistamientos/<int:id>")
    def eliminar(id):
        return responder(controlador.eliminar(id))

    @app.errorhandler(404)
    def ruta_no_encontrada(e):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(e):
        return jsonify({"error": "Método no permitido"}), 405

    return app
