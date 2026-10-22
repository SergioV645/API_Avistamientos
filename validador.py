# Regla de negocio del avistamiento, separada del controlador (app.py)
# para poder probarla sin levantar la API ni tocar la base de datos.
from datetime import date


class RelojDelSistema:
    """Reloj real: devuelve la fecha de hoy según el sistema.

    El validador no llama a date.today() directamente, sino a un reloj que
    recibe por el constructor. Así, en las pruebas se puede reemplazar por un
    reloj fijo (un stub) y la prueba de "fecha de mañana" no depende del día
    en que se corra.
    """

    def hoy(self):
        return date.today()


class ValidadorDeAvistamiento:
    """Un avistamiento es válido si:
    - la especie tiene entre 3 y 50 caracteres,
    - la fecha tiene el formato AAAA-MM-DD y no es posterior a hoy,
    - el lugar y el observador no están vacíos.
    """

    LONGITUD_MINIMA_ESPECIE = 3
    LONGITUD_MAXIMA_ESPECIE = 50

    def __init__(self, reloj):
        self.reloj = reloj

    def validar(self, datos):
        """Devuelve la lista de errores ({"campo", "mensaje"}); vacía si es válido."""
        if not isinstance(datos, dict):
            return [{"campo": "cuerpo", "mensaje": "El cuerpo debe ser un objeto JSON"}]

        errores = []
        self._validar_especie(datos.get("especie"), errores)
        self._validar_fecha(datos.get("fecha"), errores)
        self._validar_no_vacio("lugar", datos.get("lugar"), errores)
        self._validar_no_vacio("observador", datos.get("observador"), errores)
        return errores

    def _validar_especie(self, valor, errores):
        if not isinstance(valor, str):
            errores.append({"campo": "especie", "mensaje": "es obligatoria y debe ser texto"})
            return
        largo = len(valor.strip())
        if not self.LONGITUD_MINIMA_ESPECIE <= largo <= self.LONGITUD_MAXIMA_ESPECIE:
            errores.append({
                "campo": "especie",
                "mensaje": f"debe tener entre {self.LONGITUD_MINIMA_ESPECIE} y "
                           f"{self.LONGITUD_MAXIMA_ESPECIE} caracteres (tiene {largo})",
            })

    def _validar_fecha(self, valor, errores):
        if not isinstance(valor, str) or valor.strip() == "":
            errores.append({"campo": "fecha", "mensaje": "es obligatoria y debe ser texto"})
            return
        fecha = _convertir_fecha(valor.strip())
        if fecha is None:
            errores.append({"campo": "fecha", "mensaje": "debe tener el formato AAAA-MM-DD"})
        elif fecha > self.reloj.hoy():
            errores.append({"campo": "fecha", "mensaje": "no puede ser posterior a hoy"})

    def _validar_no_vacio(self, campo, valor, errores):
        if not isinstance(valor, str) or valor.strip() == "":
            errores.append({"campo": campo, "mensaje": "no puede estar vacío"})


def _convertir_fecha(texto):
    """Convierte 'AAAA-MM-DD' en date; None si el formato o la fecha no son válidos."""
    try:
        fecha = date.fromisoformat(texto)
    except ValueError:
        return None
    # fromisoformat también acepta '20261008'; exigimos exactamente AAAA-MM-DD
    return fecha if fecha.isoformat() == texto else None
