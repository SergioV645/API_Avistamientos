import sqlite3
from datetime import date

from flask import Flask, jsonify, request

import db

CAMPOS = ["especie", "lugar", "fecha", "observador"]
REPETIDO = {"error": "Ya existe un avistamiento con la misma especie, lugar, fecha y observador"}


def validar(body):
    """Devuelve una lista de errores; vacía si el cuerpo es válido."""
    if not isinstance(body, dict):
        return ["El cuerpo debe ser un objeto JSON"]
    errores = []
    for campo in CAMPOS:
        valor = body.get(campo)
        if not isinstance(valor, str) or valor.strip() == "":
            errores.append(f'El campo "{campo}" es obligatorio y debe ser texto')
    fecha = body.get("fecha")
    if isinstance(fecha, str) and fecha.strip() and not fecha_valida(fecha):
        errores.append('El campo "fecha" debe tener el formato AAAA-MM-DD')
    return errores


def fecha_valida(texto):
    try:
        return date.fromisoformat(texto).isoformat() == texto  # descarta 2026-02-30
    except ValueError:
        return False


def limpiar(body):
    """Se queda solo con los 4 campos (ignora un "id" enviado por el cliente)."""
    return {campo: body[campo].strip() for campo in CAMPOS}


def crear_app(ruta_db=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    con = db.conectar(ruta_db)

    @app.get("/avistamientos")
    def listar():
        return jsonify(db.listar(con)), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        por_especie = db.resumen_por_especie(con)
        total = sum(f["cantidad"] for f in por_especie)
        return jsonify({"total": total, "porEspecie": por_especie}), 200

    @app.get("/avistamientos/<int:id>")
    def ver(id):
        avistamiento = db.buscar_por_id(con, id)
        if avistamiento is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        return jsonify(avistamiento), 200

    @app.post("/avistamientos")
    def crear():
        body = request.get_json(silent=True)
        errores = validar(body)
        if errores:
            return jsonify({"error": "Datos inválidos", "detalles": errores}), 400
        try:
            creado = db.crear(con, limpiar(body))
        except sqlite3.IntegrityError:  # la base rechazó el duplicado
            return jsonify(REPETIDO), 409
        return jsonify(creado), 201, {"Location": f"/avistamientos/{creado['id']}"}

    @app.put("/avistamientos/<int:id>")
    def actualizar(id):
        if db.buscar_por_id(con, id) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        body = request.get_json(silent=True)
        errores = validar(body)
        if errores:
            return jsonify({"error": "Datos inválidos", "detalles": errores}), 400
        try:
            actualizado = db.actualizar(con, id, limpiar(body))
        except sqlite3.IntegrityError:  # quedaría igual a otro avistamiento
            return jsonify(REPETIDO), 409
        return jsonify(actualizado), 200

    @app.delete("/avistamientos/<int:id>")
    def eliminar(id):
        if not db.eliminar(con, id):
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