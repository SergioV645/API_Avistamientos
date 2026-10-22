# Justificación de las pruebas — API de avistamientos

Sergio Valderrama · Ingeniería de Software 2 · Sesión 22 (21 de octubre de 2026)

Repositorio: https://github.com/SergioV645/API_Avistamientos

Resumen: **42 casos de prueba** (24 unitarios sobre el validador y 18 de integración sobre la API por HTTP), todos en verde, con **cobertura de ramas del 98 %**. Comandos en el README.

---

## 1. Qué cambió en el código

| Cambio | Antes | Después | Por qué hace la API más testeable |
|---|---|---|---|
| **Validación extraída** | La función `validar()` estaba en `app.py`, junto a las rutas. Solo revisaba que los campos no estuvieran vacíos y el formato de la fecha. | Nueva clase `ValidadorDeAvistamiento` en `validador.py`, con la regla de negocio completa (especie de 3 a 50 caracteres, fecha no posterior a hoy, lugar y observador no vacíos). Devuelve una lista de errores `{"campo", "mensaje"}`. | Se prueba llamando a `validar(datos)` directamente, **sin levantar Flask ni crear la base de datos**. Las pruebas unitarias corren en milisegundos y, si fallan, el error está en la regla y no en otra capa. |
| **Reloj inyectado** | Para saber "hoy" habría que llamar a `date.today()` dentro de la validación. | El validador recibe un objeto *reloj* con un método `hoy()`. En producción es `RelojDelSistema`; en las pruebas, el stub `RelojFijo`. `crear_app(ruta_db, reloj)` permite pasarlo también a la API. | "Hoy" pasa a ser una **dependencia controlable**. Sin esto, la prueba de "fecha de mañana" escrita hoy con una fecha fija fallaría dentro de un mes (cuando esa fecha ya sea pasado). |
| **Base de datos configurable** | Ya existía `crear_app(ruta_db)`. | Se usa `":memory:"` en cada prueba (fixture `cliente` en `tests/conftest.py`). | Cada prueba de integración arranca con una base vacía: son **independientes** y no dependen del orden ni ensucian `avistamientos.db`. |
| **Errores con campo** | `"detalles": ["El campo \"lugar\" es obligatorio..."]` (texto libre). | `"detalles": [{"campo": "lugar", "mensaje": "no puede estar vacío"}]`. | El cliente sabe qué campo falló, como pide el enunciado, y la prueba puede verificar el campo exacto sin comparar textos largos. |

El controlador (`app.py`) quedó solo con su responsabilidad: leer la petición, delegar en el validador y en `db.py`, y traducir el resultado a un código HTTP.

---

## 2. Tabla de casos de la Parte A (pruebas unitarias del validador)

Técnicas: **partición de equivalencia** (dividir las entradas en clases que el sistema trata igual y tomar un representante de cada una) y **análisis de valores límite** (probar justo en la frontera y justo al lado, porque ahí se cometen los errores de `<` contra `<=`).

### Especie (válida si tiene de 3 a 50 caracteres)

Particiones: `< 3` (inválida) · `3..50` (válida) · `> 50` (inválida) · ausente o no texto (inválida).

| Valor | Tipo de caso | Esperado | Por qué este valor |
|---|---|---|---|
| `"Colibrí"` (7) | Representativo de la partición válida | Válido | Un valor típico del medio de `3..50`. |
| `"ab"` (2) | Límite inválido inferior | 400 en `especie` | Justo debajo de la frontera 3. Detecta un `>= 2` en vez de `>= 3`. |
| `"abc"` (3) | Límite válido inferior | Válido | La frontera exacta. Detecta un `> 3` en vez de `>= 3`. |
| `"a" * 50` | Límite válido superior | Válido | La frontera exacta superior. |
| `"a" * 51` | Límite inválido superior | 400 en `especie` | Justo encima de 50. Detecta un `<= 51`. |
| `"  ab  "` (6 con espacios, 2 sin ellos) | Inválido (partición "corta" disfrazada) | 400 en `especie` | Verifica que se mide sin los espacios: si no, pasaría como 6 caracteres. |
| ausente | Inválido (sin valor) | 400 en `especie` | Otra partición: el campo no viene. |

No probé 0, 1, 25 ni 100 caracteres: pertenecen a particiones que ya tienen representante y no son frontera, así que no aportan información nueva.

### Fecha (formato `AAAA-MM-DD`, fecha real, no posterior a hoy). Hoy fijo = `2026-10-21`

Particiones: pasado (válida) · hoy (válida) · futuro (inválida) · formato incorrecto (inválida) · formato correcto pero día inexistente (inválida) · vacía o no texto (inválida).

| Valor | Tipo de caso | Esperado | Por qué este valor |
|---|---|---|---|
| `"2026-10-01"` | Representativo del pasado | Válido | Fecha típica ya ocurrida. |
| `"2026-10-21"` (hoy) | Límite válido | Válido | La frontera exacta: "no posterior a hoy" incluye hoy. Detecta un `>=` en vez de `>`. |
| `"2026-10-22"` (mañana) | Límite inválido | 400 `no puede ser posterior a hoy` | El primer día inválido, justo después de la frontera. |
| `"21/10/2026"`, `"2026-10-1"`, `"20261021"`, `"hoy"` | Inválidos de formato | 400 `debe tener el formato AAAA-MM-DD` | Cada uno es un error de formato distinto (orden, cero faltante, sin guiones, texto). `"20261021"` importa porque `date.fromisoformat` de Python **sí lo acepta**: sin esta prueba no sabría que mi chequeo extra hace falta. |
| `"2025-02-29"` | Inválido: formato bien, día inexistente | 400 en `fecha` | 2025 no es bisiesto. Separa "tiene la forma correcta" de "es una fecha real". |
| `""`, `"   "`, `null`, `20261021` (número) | Inválidos: vacía o no texto | 400 `es obligatoria y debe ser texto` | Agregada **después de leer la cobertura** (sección 6). |

### Lugar y observador (no vacíos)

| Valor | Tipo de caso | Esperado | Por qué |
|---|---|---|---|
| `"Bogotá"` / `"Sergio"` | Representativo válido | Válido | Valor típico. |
| `""` | Límite inválido (longitud 0) | 400 en ese campo | El caso más obvio de vacío. |
| `"   "` | Inválido | 400 en ese campo | Solo espacios: parece no vacío pero no tiene contenido. |

Además: un caso con **varios campos inválidos a la vez** (se reportan todos, no solo el primero) y un **cuerpo que no es objeto JSON**.

---

## 3. Por qué cada nivel

- **"Especie de 51 caracteres es inválida" → unitaria.** Es lógica pura: entra un diccionario y sale una lista de errores. No necesita HTTP ni base de datos, así que levantarlos solo la haría más lenta y, si fallara, no sabría si el problema es la regla o la infraestructura. Los valores límite se prueban aquí porque es barato probar muchos.

- **"Crear un avistamiento válido devuelve 201 y queda guardado" → integración.** Lo que verifica no existe dentro de una sola unidad: que la ruta `POST` lea el JSON, llame al validador, guarde en SQLite, responda **201** con el `id` asignado por la base y el header `Location`, y que **un `GET` posterior lo devuelva**. Es una prueba de la **frontera** entre capas.

- **¿Qué detecta la prueba de integración del POST que la unitaria del validador no puede detectar?** Que el validador **esté conectado** a la ruta (si alguien borra la llamada a `validador.validar`, las 24 unitarias siguen en verde y solo fallan las de integración); que los errores se traduzcan a **400** y no a 500; que un dato inválido **no quede guardado**; que el JSON mal formado se maneje; que el **409** de repetidos funcione (lo garantiza el índice `UNIQUE` de SQLite, que una unitaria no ve); y que la respuesta salga bien serializada (con tildes y el `id` primero).

- **"Sin reloj inyectado se usa la fecha real" → integración.** Es la única prueba que usa `RelojDelSistema`. Comprueba el **cableado de producción** (que `crear_app()` sin argumentos use el reloj real), algo que las pruebas con el stub no pueden comprobar. Usa `date.today() + 1 día`, así que no depende de en qué fecha se corra.

---

## 4. Los dobles

**Doble usado: `RelojFijo` (en `tests/dobles.py`). Tipo: stub.**

Un **stub** devuelve respuestas preparadas de antemano para que el código bajo prueba pueda ejecutarse en condiciones controladas. `RelojFijo(date(2026, 10, 21)).hoy()` siempre responde `2026-10-21`. Lo uso en las 24 unitarias y en el fixture de integración.

**Por qué stub y no otro tipo:**
- No es un **mock** porque no me interesa verificar *cómo* el validador usa el reloj (cuántas veces llama a `hoy()`). Me interesa el **resultado** de la validación dada cierta fecha. Verificar llamadas acoplaría la prueba a la implementación.
- No es un **spy** por la misma razón: no registro llamadas.
- No es un **fake** porque no tiene comportamiento propio simplificado; solo devuelve un valor fijo.

**¿Qué habría pasado sin el doble?** Hay dos opciones y las dos son malas:
1. Escribir `"2026-10-22"` como "mañana" con el reloj real: la prueba pasa el 21 de octubre y **falla desde el 22**, sin que el código haya cambiado. Es una prueba frágil (*flaky* por fecha).
2. Calcular `date.today() + 1`: la prueba funciona, pero no puedo probar fronteras exactas reproducibles, y el mensaje de error no se puede comparar contra una fecha conocida.

**La base en memoria (`":memory:"`) no es un doble:** es el mismo motor SQLite de producción, solo que sin archivo. Por eso las pruebas de integración siguen probando el SQL real (incluido el índice `UNIQUE`).

**Repositorio:** la API no tiene capa de servicio separada; `db.py` son funciones SQL delgadas. No creé un *fake* del repositorio porque no hay lógica en un servicio que aislar de él: la única lógica de negocio está en el validador, que ya no depende de la base.

---

## 5. Lo que no probé (y por qué)

1. **Pruebas unitarias de `db.py` con un mock de `sqlite3`.** Un mock del cursor solo comprobaría que llamo a `execute` con cierto texto; no detectaría un SQL mal escrito ni el comportamiento del índice `UNIQUE`. Esas funciones ya se ejecutan de verdad en las pruebas de integración (100 % de cobertura en `db.py`). Mockearlas sería probar el mock.
2. **Los manejadores de error genéricos de Flask** (ruta inexistente → 404 JSON, método no permitido → 405 JSON). Solo cambian el formato del mensaje de errores que produce el framework; no contienen lógica de negocio y el riesgo de que fallen es bajo.
3. **Mayúsculas con tilde en los repetidos (limitación conocida).** El índice usa `COLLATE NOCASE`, que en SQLite solo ignora mayúsculas en letras ASCII. Lo verifiqué a mano: `"Ñandú"` y `"ñandú"` se aceptan como distintos (201 y 201). No escribí una prueba que falle a propósito porque arreglarlo (normalizar con `casefold()` antes de guardar) cambia datos guardados y está fuera del alcance del taller. Queda documentado.
4. **Concurrencia y rendimiento.** La API usa una sola conexión SQLite y el servidor de desarrollo de Flask; no es un requisito del enunciado.
5. **El arranque del servidor** (`if __name__ == "__main__"`). Se verifica a mano corriendo `python app.py`; probarlo automáticamente exigiría abrir un puerto real en cada corrida.

---

## 6. Lectura de la cobertura

Herramienta: `pytest-cov`, con **criterio de cobertura de sentencias y de ramas** (`branch = true` en `setup.cfg`). Las ramas importan porque un `if` puede ejecutarse siempre por el mismo lado.

**Primer reporte** (con 38 casos):

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
app.py            68      3     12      1    95%   79, 83, 89
db.py             31      0      0      0   100%
validador.py      43      2     14      1    95%   58-59
----------------------------------------------------------
TOTAL            142      5     26      2    96%
```

Qué quedó sin cubrir y qué decidí:

| Líneas | Qué es | Decisión |
|---|---|---|
| `validador.py` 58-59 | La rama "fecha vacía, ausente o que no es texto". | **Sí hacía falta una prueba.** Es parte de la regla de negocio y una partición de equivalencia que se me había quedado por fuera de la tabla. Agregué `test_fecha_vacia_o_que_no_es_texto_es_invalida` con `""`, `"   "`, `null` y un número. |
| `app.py` 79 y 83 | Manejadores de Flask para ruta inexistente (404) y método no permitido (405). | **No vale la pena** (sección 5, punto 2). |
| `app.py` 89 | `crear_app().run(...)`, el arranque del servidor. | **No vale la pena** (sección 5, punto 5). |

**Reporte final** (42 casos):

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
app.py            68      3     12      1    95%   79, 83, 89
db.py             31      0      0      0   100%
validador.py      43      0     14      0   100%
----------------------------------------------------------
TOTAL            142      3     26      1    98%
```

**Conclusión.** La cobertura dice qué líneas se *ejecutaron*, no si las pruebas *verifican* algo. Para comprobar que las pruebas detectan errores reales, introduje a propósito cinco defectos en `validador.py` y corrí las unitarias:

| Defecto introducido | ¿Lo detectaron? |
|---|---|
| Mínimo de especie 3 → 2 | Sí (3 pruebas fallaron) |
| Máximo de especie 50 → 51 | Sí (2 fallaron) |
| `fecha > hoy` → `fecha >= hoy` | Sí (falló la prueba de la fecha de hoy) |
| Medir la especie sin quitar espacios | Sí (falló la de `"  ab  "`) |
| Aceptar `"20261021"` sin guiones | Sí (falló la de formato) |

Cada defecto lo atrapó justamente una prueba de valor límite o de partición, lo que confirma que esos casos se eligieron por la técnica y no al azar.
