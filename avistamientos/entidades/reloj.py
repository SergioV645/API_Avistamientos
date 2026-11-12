# La regla "la fecha no puede ser posterior a hoy" necesita saber qué día es hoy.
# La entidad no llama a date.today(): depende de esta abstracción, y la
# implementación concreta (RelojDelSistema) vive en el círculo externo.
# Es el principio de inversión de dependencias aplicado al reloj.
from abc import ABC, abstractmethod


class Reloj(ABC):
    @abstractmethod
    def hoy(self):
        """Devuelve la fecha de hoy (datetime.date)."""
