#!/bin/bash
# Arranca la API con una base nueva, hace una secuencia fija de peticiones
# y escribe "MÉTODO RUTA -> código + cuerpo" para comparar antes/después.
cd "$1"; rm -f /tmp/muestra.db
DB_PATH=/tmp/muestra.db python3 app.py >/tmp/srv.log 2>&1 & PID=$!
for i in $(seq 1 30); do curl -s localhost:3000/avistamientos >/dev/null && break; sleep 0.3; done
B=http://localhost:3000; H="Content-Type: application/json"
p(){ printf '%s %s -> ' "$1" "$2"; shift 2; curl -s -w ' [%{http_code}]' "$@" | tr -d '\n' | sed 's/  */ /g'; echo; }
p POST /avistamientos -X POST $B/avistamientos -H "$H" -d '{"especie":"Colibrí","lugar":"Bogotá","fecha":"2026-10-01","observador":"Sergio"}'
p POST /avistamientos -X POST $B/avistamientos -H "$H" -d '{"especie":"Tucán","lugar":"Minca","fecha":"2026-09-20","observador":"Laura"}'
p "POST (repetido)" /avistamientos -X POST $B/avistamientos -H "$H" -d '{"especie":"colibrí","lugar":"bogotá","fecha":"2026-10-01","observador":"Sergio"}'
p "POST (inválido)" /avistamientos -X POST $B/avistamientos -H "$H" -d '{"especie":"ab","lugar":"","fecha":"2099-01-01","observador":"Sergio"}'
p "POST (JSON malo)" /avistamientos -X POST $B/avistamientos -H "$H" -d '{ no es json'
p GET /avistamientos $B/avistamientos
p GET /avistamientos/1 $B/avistamientos/1
p GET /avistamientos/99 $B/avistamientos/99
p PUT /avistamientos/1 -X PUT $B/avistamientos/1 -H "$H" -d '{"especie":"Barranquero","lugar":"Parque Arví","fecha":"2026-09-28","observador":"Sergio"}'
p "PUT (inválido)" /avistamientos/1 -X PUT $B/avistamientos/1 -H "$H" -d '{"especie":"Barranquero","lugar":"Parque Arví","fecha":"28/09/2026","observador":"Sergio"}'
p "PUT (repetido)" /avistamientos/2 -X PUT $B/avistamientos/2 -H "$H" -d '{"especie":"Barranquero","lugar":"Parque Arví","fecha":"2026-09-28","observador":"Sergio"}'
p PUT /avistamientos/99 -X PUT $B/avistamientos/99 -H "$H" -d '{"especie":"Barranquero","lugar":"Parque Arví","fecha":"2026-09-28","observador":"Sergio"}'
p GET /avistamientos/resumen $B/avistamientos/resumen
p DELETE /avistamientos/2 -X DELETE $B/avistamientos/2
p DELETE /avistamientos/2 -X DELETE $B/avistamientos/2
p "PATCH (no existe)" /avistamientos/1 -X PATCH $B/avistamientos/1
p GET /no-existe $B/no-existe
kill $PID; wait $PID 2>/dev/null; rm -f /tmp/muestra.db
