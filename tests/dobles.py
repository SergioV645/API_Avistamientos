# Dobles de prueba.
from datetime import date


class RelojFijo:
    """Stub del reloj: siempre responde la misma fecha.

    Reemplaza a RelojDelSistema para que las pruebas que dependen de "hoy"
    den el mismo resultado sin importar el día en que se corran.
    """

    def __init__(self, hoy):
        self._hoy = hoy

    def hoy(self):
        return self._hoy


# Fecha fija que usan todas las pruebas: el día del taller.
HOY = date(2026, 10, 21)
