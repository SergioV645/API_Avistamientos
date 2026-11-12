# Puerto de salida (en Martin, una "data access interface" o gateway).
# Los casos de uso necesitan guardar datos pero no pueden depender de la base
# de datos. Por eso la interfaz se declara AQUÍ, en la capa de casos de uso,
# y la implementa un adaptador de la capa externa (RepositorioSqlite).
# Los datos que cruzan son diccionarios simples, no filas de SQLite.
from abc import ABC, abstractmethod


class RepositorioDeAvistamientos(ABC):
    @abstractmethod
    def listar(self):
        """Lista de todos los avistamientos (dicts con id), ordenados por id."""

    @abstractmethod
    def buscar_por_id(self, id):
        """El avistamiento con ese id, o None si no existe."""

    @abstractmethod
    def agregar(self, datos):
        """Guarda un avistamiento nuevo y lo devuelve con su id.
        Lanza AvistamientoRepetido si ya existe uno igual."""

    @abstractmethod
    def actualizar(self, id, datos):
        """Reemplaza los datos; devuelve el avistamiento o None si no existe.
        Lanza AvistamientoRepetido si queda igual a otro."""

    @abstractmethod
    def eliminar(self, id):
        """Elimina; devuelve True si existía."""

    @abstractmethod
    def contar_por_especie(self):
        """Lista de {"especie", "cantidad"} de mayor a menor cantidad."""
