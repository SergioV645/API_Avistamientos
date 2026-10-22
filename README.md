# API de avistamientos de aves

API REST para registrar avistamientos de aves. Ingeniería de Software 2 (ISW-2): construida en la Sesión 17 y probada en la Sesión 22.

- **Lenguaje:** Python 3.10+
- **Framework:** Flask 3
- **Base de datos:** SQLite embebida (módulo `sqlite3`, incluido en Python)
- **Formato:** JSON para recibir y responder
- **Pruebas:** pytest (unitarias e integración) y pytest-cov (cobertura)

## Instalación y ejecución

Requisito: Python 3.10 o superior (`python --version`).

```bash
git clone https://github.com/SergioV645/API_Avistamientos.git
cd API_Avistamientos
python -m venv venv
```

Activar el entorno virtual:

- Windows (cmd): `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`

Instalar dependencias y arrancar:

```bash
pip install -r requirements.txt
python app.py
```

La API queda en **http://localhost:3000**. La primera vez se crea automáticamente el archivo `avistamientos.db` con la tabla.

## Pruebas y cobertura

Con el entorno virtual activado:

| Qué | Comando |
|---|---|
| Correr todas las pruebas | `python -m pytest` |
| Solo las unitarias (validador) | `python -m pytest tests/test_validador.py` |
| Solo las de integración (API por HTTP) | `python -m pytest tests/test_api.py` |
| Generar la cobertura (en consola) | `python -m pytest --cov --cov-report=term-missing` |
| Generar la cobertura (en HTML, en `htmlcov/index.html`) | `python -m pytest --cov --cov-report=html` |

La justificación de las pruebas está en [`docs/justificacion-pruebas.md`](docs/justificacion-pruebas.md).

## Modelo: avistamiento

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | número | Lo asigna el sistema (AUTOINCREMENT) |
| `especie` | texto | Nombre de la especie, ej. `"Colibrí"` |
| `lugar` | texto | Dónde se observó |
| `fecha` | texto | Formato `AAAA-MM-DD`, ej. `"2026-10-08"` |
| `observador` | texto | Quién la registró |

### Regla de negocio

Un avistamiento es válido si:

- la **especie** tiene entre 3 y 50 caracteres (sin contar espacios al inicio y al final)
- la **fecha** tiene el formato `AAAA-MM-DD`, es una fecha real y **no es posterior a hoy**
- el **lugar** y el **observador** no están vacíos.

Si no es válido, `POST` y `PUT` responden `400` indicando qué campo falló. La regla vive en `validador.py` (`ValidadorDeAvistamiento`), separada de las rutas.

**No se permiten avistamientos repetidos:** si ya existe uno con la misma especie, lugar, fecha y observador (sin importar mayúsculas), la API responde `409 Conflict`. Lo garantiza un índice `UNIQUE` en la base de datos.

## Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| `GET` | `/avistamientos` | `200` con la lista |
| `GET` | `/avistamientos/{id}` | `200` con el avistamiento, `404` si no existe |
| `POST` | `/avistamientos` | `201` con el avistamiento creado, `400` si no cumple la regla, `409` si está repetido |
| `PUT` | `/avistamientos/{id}` | `200` actualizado, `404` si no existe, `400` si no cumple la regla, `409` si queda repetido |
| `DELETE` | `/avistamientos/{id}` | `204` sin contenido, `404` si no existe |
| `GET` | `/avistamientos/resumen` | `200` con la cantidad de avistamientos por especie (**bonus**) |

## Ejemplos con curl

> En Windows usa **Git Bash** para copiar los ejemplos tal cual. En PowerShell escribe `curl.exe` en lugar de `curl`.

### Registrar un avistamiento — `POST /avistamientos`

```bash
curl -i -X POST http://localhost:3000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"Colibrí","lugar":"Bogotá","fecha":"2026-10-08","observador":"Sergio"}'
```

Respuesta `201 Created`:

```json
{"id": 1, "especie": "Colibrí", "lugar": "Bogotá", "fecha": "2026-10-08", "observador": "Sergio"}
```

Si no cumple la regla responde `400 Bad Request` con el campo que falló:

```bash
curl -i -X POST http://localhost:3000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"ab","lugar":"","fecha":"2099-01-01","observador":"Sergio"}'
```

```json
{"error": "Datos inválidos", "detalles": [
  {"campo": "especie", "mensaje": "debe tener entre 3 y 50 caracteres (tiene 2)"},
  {"campo": "fecha", "mensaje": "no puede ser posterior a hoy"},
  {"campo": "lugar", "mensaje": "no puede estar vacío"}
]}
```

Si se envía el mismo avistamiento dos veces, la segunda vez responde `409 Conflict`:

```json
{"error": "Ya existe un avistamiento con la misma especie, lugar, fecha y observador"}
```

### Listar todos — `GET /avistamientos`

```bash
curl -i http://localhost:3000/avistamientos
```

Respuesta `200 OK` con un arreglo de avistamientos.

### Ver uno — `GET /avistamientos/{id}`

```bash
curl -i http://localhost:3000/avistamientos/1
```

Respuesta `200 OK` con el avistamiento, o `404 Not Found`:

```json
{"error": "Avistamiento no encontrado"}
```

### Actualizar — `PUT /avistamientos/{id}`

```bash
curl -i -X PUT http://localhost:3000/avistamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"especie":"Tucán","lugar":"Minca","fecha":"2026-10-07","observador":"Sergio"}'
```

Respuesta `200 OK`:

```json
{"id": 1, "especie": "Tucán", "lugar": "Minca", "fecha": "2026-10-07", "observador": "Sergio"}
```

`PUT` reemplaza el recurso completo, por eso pide los cuatro campos.

### Eliminar — `DELETE /avistamientos/{id}`

```bash
curl -i -X DELETE http://localhost:3000/avistamientos/1
```

Respuesta `204 No Content` (sin cuerpo), o `404 Not Found` si no existe.

### Resumen por especie (bonus) — `GET /avistamientos/resumen`

```bash
curl -i http://localhost:3000/avistamientos/resumen
```

Respuesta `200 OK`:

```json
{"total": 3, "porEspecie": [{"especie": "Colibrí", "cantidad": 2}, {"especie": "Tucán", "cantidad": 1}]}
```

## Estructura del proyecto

```
app.py                    Rutas (controlador) y códigos de estado
validador.py              Regla de negocio: ValidadorDeAvistamiento y RelojDelSistema
db.py                     Conexión a SQLite, creación de la tabla y consultas SQL
tests/test_validador.py   Pruebas unitarias del validador
tests/test_api.py         Pruebas de integración de la API por HTTP
tests/dobles.py           Dobles de prueba (RelojFijo, un stub del reloj)
tests/conftest.py         Fixture: API con base de datos en memoria nueva por prueba
docs/justificacion-pruebas.md   Justificación de las pruebas (Sesión 22)
requirements.txt          Dependencias (Flask, pytest, pytest-cov)
setup.cfg                 Configuración de la cobertura (incluye ramas)
```

## Uso de IA

Este proyecto se desarrolló con ayuda de **Claude con el modelo Claude Opus 5.5**. Revisé y entiendo el código publicado.

## Autor

Sergio Valderrama — ISW-2, 2026
