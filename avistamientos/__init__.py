"""API de avistamientos organizada según Clean Architecture (Martin, 2012/2017).

Capas, de adentro hacia afuera:
    entidades/            reglas de negocio del avistamiento
    casos_de_uso/         lo que la aplicación hace (registrar, listar, ...)
    adaptadores/          traducción entre los casos de uso y el exterior (HTTP, SQL)
    frameworks_y_drivers/ Flask, sqlite3 y el reloj del sistema
    main.py               arma todo (raíz de composición)

Regla de dependencia: los imports solo apuntan hacia adentro.
"""
