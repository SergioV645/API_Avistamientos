# Detalle: el reloj real del sistema operativo. Implementa la abstracción
# Reloj definida en la capa de entidades.
from datetime import date

from avistamientos.entidades.reloj import Reloj


class RelojDelSistema(Reloj):
    def hoy(self):
        return date.today()
