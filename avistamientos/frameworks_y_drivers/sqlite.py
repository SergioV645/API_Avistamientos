# Detalle: abrir la conexión con el motor SQLite.
import os
import sqlite3

RUTA_POR_DEFECTO = os.environ.get("DB_PATH", "avistamientos.db")


def abrir_conexion(ruta=None):
    return sqlite3.connect(ruta or RUTA_POR_DEFECTO, check_same_thread=False)
