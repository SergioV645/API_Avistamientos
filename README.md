# API de avistamientos de aves

API REST para registrar avistamientos de aves.

* **Lenguaje:** Python 3.10+
* **Framework:** Flask 3
* **Base de datos:** SQLite embebida **Formato:** JSON para recibir y responder

## Instalación y ejecución

Requisito: [Python](https://www.python.org/) 3.10 o superior (`python --version`).



Activar el entorno virtual:

* Windows (cmd): `venv\\Scripts\\activate`
* macOS / Linux: `source venv/bin/activate`

Instalar dependencias y arrancar:

```bash
pip install -r requirements.txt
python app.py
```

La API queda en **http://localhost:3000**. La primera vez se crea automáticamente el archivo `avistamientos.db` con la tabla.

## Modelo: avistamiento

|Campo|Tipo|Descripción|
|-|-|-|
|`id`|número|Lo asigna el sistema (AUTOINCREMENT)|
|`especie`|texto|Nombre de la especie, ej. `"colibrí"`|
|`lugar`|texto|Dónde se observó|
|`fecha`|texto|Formato `AAAA-MM-DD`, ej. `"2026-10-08"`|
|`observador`|texto|Quién la registró|

Los cuatro campos de texto son obligatorios en `POST` y `PUT`. Si falta alguno, está vacío o la fecha no es válida, la API responde `400` con el detalle de los errores.

## Endpoints

|Método|Ruta|Respuesta|
|-|-|-|
|`GET`|`/avistamientos`|`200` con la lista|
|`GET`|`/avistamientos/{id}`|`200` con el avistamiento, `404` si no existe|
|`POST`|`/avistamientos`|`201` con el avistamiento creado, `400` si faltan datos|
|`PUT`|`/avistamientos/{id}`|`200` actualizado, `404` si no existe, `400` si faltan datos|
|`DELETE`|`/avistamientos/{id}`|`204` sin contenido, `404` si no existe|
|`GET`|`/avistamientos/resumen`|`200` con la cantidad de avistamientos por especie (**bonus**)|

## Ejemplos con curl

> En Windows usa \*\*Git Bash\*\* para copiar los ejemplos tal cual. En PowerShell escribe `curl.exe` en lugar de `curl`.

### Registrar un avistamiento — `POST /avistamientos`

```bash
curl -i -X POST http://localhost:3000/avistamientos \\
  -H "Content-Type: application/json" \\
  -d '{"especie":"colibrí","lugar":"Bogotá","fecha":"2026-10-08","observador":"Sergio"}'
```

Respuesta `201 Created`:

```json
{"id": 1, "especie": "colibrí", "lugar": "Bogotá", "fecha": "2026-10-08", "observador": "Sergio"}
```

Con datos faltantes responde `400 Bad Request`:

```bash
curl -i -X POST http://localhost:3000/avistamientos \\
  -H "Content-Type: application/json" \\
  -d '{"especie":"garza"}'
```

```json
{"error": "Datos inválidos", "detalles": \["El campo \\"lugar\\" es obligatorio y debe ser texto", "El campo \\"fecha\\" es obligatorio y debe ser texto", "El campo \\"observador\\" es obligatorio y debe ser texto"]}
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
curl -i -X PUT http://localhost:3000/avistamientos/1 \\
  -H "Content-Type: application/json" \\
  -d '{"especie":"tucán","lugar":"Minca","fecha":"2026-10-07","observador":"Sergio"}'
```

Respuesta `200 OK`:

```json
{"id": 1, "especie": "tucán", "lugar": "Minca", "fecha": "2026-10-07", "observador": "Sergio"}
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
{"total": 3, "porEspecie": \[{"especie": "cóndor", "cantidad": 2}, {"especie": "colibrí", "cantidad": 1}]}
```

## Pruebas (bonus)

Pruebas de integración con **pytest**. Usan una base de datos en memoria, así que no tocan `avistamientos.db`.

```bash
python -m pytest
```

Cubren los seis endpoints y los códigos 200, 201, 204, 400 (datos faltantes, fecha inválida, JSON mal formado) y 404.

## Estructura del proyecto

```
app.py               Rutas, validación y códigos de estado
db.py                Conexión a SQLite, creación de la tabla y consultas SQL
tests/test\_api.py    Pruebas de integración
requirements.txt     Dependencias (Flask, pytest)
```

## Uso de IA

Este proyecto se desarrolló con ayuda de Claude (Anthropic), modelo Claude Opus 5.5. 

Autor

Sergio Valderrama — ISW-2, 2026

