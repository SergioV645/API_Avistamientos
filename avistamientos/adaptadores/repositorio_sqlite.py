# Adaptador: implementa el puerto RepositorioDeAvistamientos con SQLite.
# Todo el SQL de la aplicación está aquí y en ningún otro lugar.
import sqlite3

from avistamientos.casos_de_uso.errores import AvistamientoRepetido
from avistamientos.casos_de_uso.repositorio import RepositorioDeAvistamientos


class RepositorioSqliteDeAvistamientos(RepositorioDeAvistamientos):
    def __init__(self, conexion):
        self.con = conexion
        self.con.row_factory = sqlite3.Row
        self._crear_esquema()

    def _crear_esquema(self):
        # 1. Primero se crea la tabla
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS avistamientos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                especie    TEXT NOT NULL,
                lugar      TEXT NOT NULL,
                fecha      TEXT NOT NULL,
                observador TEXT NOT NULL
            )
        """)
        # 2. Después el índice que impide avistamientos repetidos.
        # COLLATE NOCASE hace que "Colibrí" y "colibrí" cuenten como iguales.
        self.con.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_avistamiento_unico ON avistamientos (
                especie COLLATE NOCASE,
                lugar COLLATE NOCASE,
                fecha,
                observador COLLATE NOCASE
            )
        """)
        self.con.commit()

    def listar(self):
        filas = self.con.execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
        return [dict(f) for f in filas]

    def buscar_por_id(self, id):
        fila = self.con.execute("SELECT * FROM avistamientos WHERE id = ?", (id,)).fetchone()
        return dict(fila) if fila else None

    def agregar(self, datos):
        try:
            cursor = self.con.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
                (datos["especie"], datos["lugar"], datos["fecha"], datos["observador"]),
            )
        except sqlite3.IntegrityError:
            # La traducción del error de SQLite a un error de la aplicación
            # ocurre aquí, para que nadie hacia adentro conozca sqlite3.
            raise AvistamientoRepetido()
        self.con.commit()
        return self.buscar_por_id(cursor.lastrowid)

    def actualizar(self, id, datos):
        try:
            cursor = self.con.execute(
                "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
                (datos["especie"], datos["lugar"], datos["fecha"], datos["observador"], id),
            )
        except sqlite3.IntegrityError:
            raise AvistamientoRepetido()
        self.con.commit()
        return self.buscar_por_id(id) if cursor.rowcount > 0 else None

    def eliminar(self, id):
        cursor = self.con.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
        self.con.commit()
        return cursor.rowcount > 0

    def contar_por_especie(self):
        filas = self.con.execute("""
            SELECT especie, COUNT(*) AS cantidad
            FROM avistamientos
            GROUP BY especie
            ORDER BY cantidad DESC, especie
        """).fetchall()
        return [dict(f) for f in filas]
