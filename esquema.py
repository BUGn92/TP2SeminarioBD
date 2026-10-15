"""
Módulo de Diccionario de Esquema y Portabilidad
Trabajo Práctico 2 - Equipo 6
"""

from typing import Dict, Any
import pandas as pd

# Diccionario canónico de Sakila -> Nombres específicos de la base sakila_es
ESQUEMA: Dict[str, Any] = {
    "tablas": {
        "film": "pelicula",
        "inventory": "inventario",
        "rental": "alquiler",
        "payment": "pago",
        "category": "categoria",
        "film_category": "pelicula_categoria",
        "customer": "cliente",
        "staff": "personal",
        "store": "tienda",
        "actor": "actor",
        "film_actor": "pelicula_actor",
        "language": "idioma",
        "country": "pais",
        "city": "ciudad",
        "address": "direccion"
    },
    "columnas": {
        "actor": {
            "actor_id": "id_actor",
            "first_name": "nombre",
            "last_name": "apellido",
            "last_update": "ultima_actualizacion"
        },
        "category": {
            "category_id": "id_categoria",
            "name": "nombre",
            "last_update": "ultima_actualizacion"
        },
        "language": {
            "language_id": "id_idioma",
            "name": "nombre",
            "last_update": "ultima_actualizacion"
        },
        "country": {
            "country_id": "id_pais",
            "country": "pais",
            "last_update": "ultima_actualizacion"
        },
        "city": {
            "city_id": "id_ciudad",
            "city": "ciudad",
            "country_id": "id_pais",
            "last_update": "ultima_actualizacion"
        },
        "address": {
            "address_id": "id_direccion",
            "address": "direccion",
            "address2": "direccion2",
            "district": "distrito",
            "city_id": "id_ciudad",
            "postal_code": "codigo_postal",
            "phone": "telefono",
            "last_update": "ultima_actualizacion"
        },
        "film": {
            "film_id": "id_pelicula",
            "title": "titulo",
            "description": "descripcion",
            "release_year": "anio_lanzamiento",
            "language_id": "id_idioma",
            "original_language_id": "id_idioma_original",
            "rental_duration": "duracion_alquiler",
            "rental_rate": "tarifa_alquiler",
            "length": "duracion",
            "replacement_cost": "costo_reemplazo",
            "rating": "clasificacion",
            "special_features": "caracteristicas_especiales",
            "last_update": "ultima_actualizacion"
        },
        "store": {
            "store_id": "id_tienda",
            "manager_staff_id": "id_gerente_personal",
            "address_id": "id_direccion",
            "last_update": "ultima_actualizacion"
        },
        "staff": {
            "staff_id": "id_personal",
            "first_name": "nombre",
            "last_name": "apellido",
            "address_id": "id_direccion",
            "email": "correo_electronico",
            "store_id": "id_tienda",
            "active": "activo",
            "username": "nombre_usuario",
            "password": "contrasena",
            "last_update": "ultima_actualizacion",
            "picture": "foto"
        },
        "customer": {
            "customer_id": "id_cliente",
            "store_id": "id_tienda",
            "first_name": "nombre",
            "last_name": "apellido",
            "email": "correo_electronico",
            "address_id": "id_direccion",
            "active": "activo",
            "create_date": "fecha_creacion",
            "last_update": "ultima_actualizacion"
        },
        "inventory": {
            "inventory_id": "id_inventario",
            "film_id": "id_pelicula",
            "store_id": "id_tienda",
            "last_update": "ultima_actualizacion"
        },
        "rental": {
            "rental_id": "id_alquiler",
            "rental_date": "fecha_alquiler",
            "inventory_id": "id_inventario",
            "customer_id": "id_cliente",
            "return_date": "fecha_devolucion",
            "staff_id": "id_personal",
            "last_update": "ultima_actualizacion"
        },
        "payment": {
            "payment_id": "id_pago",
            "customer_id": "id_cliente",
            "staff_id": "id_personal",
            "rental_id": "id_alquiler",
            "amount": "monto",
            "payment_date": "fecha_pago",
            "last_update": "ultima_actualizacion"
        },
        "film_actor": {
            "actor_id": "id_actor",
            "film_id": "id_pelicula",
            "last_update": "ultima_actualizacion"
        },
        "film_category": {
            "film_id": "id_pelicula",
            "category_id": "id_categoria",
            "last_update": "ultima_actualizacion"
        }
    }
}


def t(tabla_canonica: str) -> str:
    """Devuelve el nombre de la tabla en la base de datos a partir del nombre canónico."""
    return ESQUEMA["tablas"].get(tabla_canonica, tabla_canonica)


def c(tabla_canonica: str, columna_canonica: str) -> str:
    """Devuelve el nombre de la columna en la base de datos a partir de su nombre canónico."""
    return ESQUEMA["columnas"].get(tabla_canonica, {}).get(columna_canonica, columna_canonica)


def renombrar_a_canonico(df: pd.DataFrame, tabla_canonica: str) -> pd.DataFrame:
    """
    Renombra las columnas del DataFrame traído de la base a sus nombres canónicos de Sakila.
    Permite que todo el código posterior use siempre nombres canónicos estándar.
    """
    mapa_inverso = {v: k for k, v in ESQUEMA["columnas"].get(tabla_canonica, {}).items()}
    return df.rename(columns=mapa_inverso)


def generar_query_conjunto_trabajo() -> str:
    """
    Construye dinámicamente la consulta T-SQL del conjunto de trabajo del Equipo 6
    (pelicula -> inventario -> alquiler -> pago) utilizando las tablas y columnas mapeadas.
    
    Garantiza que cambiando únicamente este archivo, la consulta se ejecute sobre
    la base de datos de cualquier otro equipo sin errores.
    """
    # Tablas
    t_film = t("film")
    t_inv = t("inventory")
    t_rent = t("rental")
    t_pay = t("payment")

    # Columnas film
    f_id = c("film", "film_id")
    f_title = c("film", "title")
    f_rate = c("film", "rental_rate")
    f_cost = c("film", "replacement_cost")
    f_duration = c("film", "rental_duration")
    f_rating = c("film", "rating")

    # Columnas inventory
    i_id = c("inventory", "inventory_id")
    i_film_id = c("inventory", "film_id")

    # Columnas rental
    r_id = c("rental", "rental_id")
    r_inv_id = c("rental", "inventory_id")

    # Columnas payment
    p_rent_id = c("payment", "rental_id")
    p_amount = c("payment", "amount")

    query = f"""
    SELECT 
        f.[{f_id}] AS film_id,
        f.[{f_title}] AS title,
        f.[{f_rate}] AS rental_rate,
        f.[{f_cost}] AS replacement_cost,
        f.[{f_duration}] AS rental_duration,
        f.[{f_rating}] AS rating,
        COUNT(DISTINCT i.[{i_id}]) AS inventory_count,
        COUNT(r.[{r_id}]) AS rental_count,
        ISNULL(SUM(p.[{p_amount}]), 0.0) AS total_revenue
    FROM [{t_film}] f
    LEFT JOIN [{t_inv}] i 
        ON f.[{f_id}] = i.[{i_film_id}]
    LEFT JOIN [{t_rent}] r 
        ON i.[{i_id}] = r.[{r_inv_id}]
    LEFT JOIN [{t_pay}] p 
        ON r.[{r_id}] = p.[{p_rent_id}]
    GROUP BY 
        f.[{f_id}],
        f.[{f_title}],
        f.[{f_rate}],
        f.[{f_cost}],
        f.[{f_duration}],
        f.[{f_rating}];
    """
    return query


def generar_query_ingresos_por_pelicula() -> str:
    """Genera la consulta de contraste SQL usando el esquema configurado."""
    return f"""
    SELECT
        f.[{c("film", "film_id")}] AS film_id,
        ISNULL(SUM(p.[{c("payment", "amount")}]), 0.0) AS total_revenue
    FROM [{t("film")}] f
    LEFT JOIN [{t("inventory")}] i
        ON f.[{c("film", "film_id")}] = i.[{c("inventory", "film_id")}]
    LEFT JOIN [{t("rental")}] r
        ON i.[{c("inventory", "inventory_id")}] = r.[{c("rental", "inventory_id")}]
    LEFT JOIN [{t("payment")}] p
        ON r.[{c("rental", "rental_id")}] = p.[{c("payment", "rental_id")}]
    GROUP BY f.[{c("film", "film_id")}]
    ORDER BY f.[{c("film", "film_id")}];
    """


def generar_query_reconciliacion() -> str:
    """Genera el conteo de filas por tabla, aplicando los nombres del esquema."""
    filas_origen = {
        "actor": 200,
        "category": 16,
        "language": 6,
        "country": 109,
        "city": 600,
        "address": 603,
        "film": 1000,
        "film_actor": 5462,
        "film_category": 1000,
        "store": 2,
        "staff": 2,
        "customer": 599,
        "inventory": 4581,
        "rental": 16044,
        "payment": 16049,
    }
    consultas = [
        (
            f"SELECT '{tabla}' AS tabla, {cantidad} AS filas_origen, "
            f"COUNT(*) AS filas_sql_server, COUNT(*) - {cantidad} AS diferencia "
            f"FROM [{t(tabla)}]"
        )
        for tabla, cantidad in filas_origen.items()
    ]
    return "\nUNION ALL\n".join(consultas) + ";"
