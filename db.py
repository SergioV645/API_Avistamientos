import os
import sqlite3

RUTA_DB = os.environ.get("DB_PATH", "avistamientos.db")


def conectar(ruta=None):
    conexion = sqlite3.connect(ruta or RUTA_DB, check_same_thread=False)
    conexion.row_factory = sqlite3.Row  # permite convertir cada fila en diccionario

    # 1. Primero se crea la tabla
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS avistamientos (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            especie    TEXT NOT NULL,
            lugar      TEXT NOT NULL,
            fecha      TEXT NOT NULL,
            observador TEXT NOT NULL
        )
    """)

    # 2. Después el índice que impide avistamientos repetidos.
    conexion.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_avistamiento_unico ON avistamientos (
            especie COLLATE NOCASE,
            lugar COLLATE NOCASE,
            fecha,
            observador COLLATE NOCASE
        )
    """)
    conexion.commit()
    return conexion


def listar(con):
    filas = con.execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
    return [dict(f) for f in filas]


def buscar_por_id(con, id):
    fila = con.execute("SELECT * FROM avistamientos WHERE id = ?", (id,)).fetchone()
    return dict(fila) if fila else None


def crear(con, datos):
    cursor = con.execute(
        "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
        (datos["especie"], datos["lugar"], datos["fecha"], datos["observador"]),
    )
    con.commit()
    return buscar_por_id(con, cursor.lastrowid)


def actualizar(con, id, datos):
    cursor = con.execute(
        "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
        (datos["especie"], datos["lugar"], datos["fecha"], datos["observador"], id),
    )
    con.commit()
    return buscar_por_id(con, id) if cursor.rowcount > 0 else None


def eliminar(con, id):
    cursor = con.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
    con.commit()
    return cursor.rowcount > 0


def resumen_por_especie(con):
    filas = con.execute("""
        SELECT especie, COUNT(*) AS cantidad
        FROM avistamientos
        GROUP BY especie
        ORDER BY cantidad DESC, especie
    """).fetchall()
    return [dict(f) for f in filas]