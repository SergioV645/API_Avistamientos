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


class RepositorioEnMemoria:
    """Fake del puerto RepositorioDeAvistamientos: guarda en un diccionario.

    Permite probar los casos de uso sin SQLite. Imita el comportamiento del
    adaptador real que importa a los casos de uso: asigna ids crecientes y
    lanza AvistamientoRepetido ante un duplicado (ignorando mayúsculas).
    """

    def __init__(self):
        self.datos = {}
        self.siguiente_id = 1

    def _clave(self, d):
        return (d["especie"].lower(), d["lugar"].lower(), d["fecha"], d["observador"].lower())

    def _hay_otro_igual(self, datos, excepto_id=None):
        return any(self._clave(a) == self._clave(datos) for i, a in self.datos.items() if i != excepto_id)

    def listar(self):
        return [dict(a) for _, a in sorted(self.datos.items())]

    def buscar_por_id(self, id):
        return dict(self.datos[id]) if id in self.datos else None

    def agregar(self, datos):
        from avistamientos.casos_de_uso.errores import AvistamientoRepetido
        if self._hay_otro_igual(datos):
            raise AvistamientoRepetido()
        nuevo = {"id": self.siguiente_id, **datos}
        self.datos[self.siguiente_id] = nuevo
        self.siguiente_id += 1
        return dict(nuevo)

    def actualizar(self, id, datos):
        from avistamientos.casos_de_uso.errores import AvistamientoRepetido
        if id not in self.datos:
            return None
        if self._hay_otro_igual(datos, excepto_id=id):
            raise AvistamientoRepetido()
        self.datos[id] = {"id": id, **datos}
        return dict(self.datos[id])

    def eliminar(self, id):
        return self.datos.pop(id, None) is not None

    def contar_por_especie(self):
        conteo = {}
        for a in self.datos.values():
            conteo[a["especie"]] = conteo.get(a["especie"], 0) + 1
        filas = [{"especie": e, "cantidad": c} for e, c in conteo.items()]
        return sorted(filas, key=lambda f: (-f["cantidad"], f["especie"]))
