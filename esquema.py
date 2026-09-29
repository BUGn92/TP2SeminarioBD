"""
Módulo de Diccionario de Esquema y Portabilidad
Trabajo Práctico 2 - Equipo 6

Permite desacoplar el código de análisis y del pipeline de los nombres en español
elegidos por el equipo en el TP1.

Prueba de portabilidad (evaluada en la defensa oral):
Cambiando únicamente este archivo por el de otro equipo, el proyecto completo
debe poder ejecutarse contra la base de dicho equipo.
"""

from typing import Dict, Any
import pandas as pd

# Diccionario canónico de Sakila -> Nombres específicos de la base del equipo
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
        "category": {
            "category_id": "id_categoria",
            "name": "nombre",
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
