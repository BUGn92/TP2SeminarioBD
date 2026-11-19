"""
Módulo de Diccionario de Esquema y Portabilidad
Trabajo Práctico 2 - Equipo 6

Único lugar del proyecto donde figuran el esquema SQL Server y los nombres
físicos de tablas y columnas de la base migrada. Para ejecutar el proyecto
contra la base de otro equipo, basta actualizar el diccionario ESQUEMA
(y las variables de conexión en .env).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parent
SQL_DIR = PROJECT_ROOT / "sql"
DEFAULT_DUMP_PATH = PROJECT_ROOT / "sakila-dataSQLserver.sql"

_IDENTIFICADOR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Diccionario canónico de Sakila -> Esquema y nombres físicos de la base local
ESQUEMA: Dict[str, Any] = {
    "schema": "dbo",
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
        "address": "direccion",
        # "film_text": None  # No migrada por diseño en sakila_es (15 tablas)
    },
    "columnas": {
        "actor": {
            "actor_id": "id_actor",
            "first_name": "nombre",
            "last_name": "apellido",
            "last_update": "ultima_actualizacion",
        },
        "category": {
            "category_id": "id_categoria",
            "name": "nombre",
            "last_update": "ultima_actualizacion",
        },
        "language": {
            "language_id": "id_idioma",
            "name": "nombre",
            "last_update": "ultima_actualizacion",
        },
        "country": {
            "country_id": "id_pais",
            "country": "pais",
            "last_update": "ultima_actualizacion",
        },
        "city": {
            "city_id": "id_ciudad",
            "city": "ciudad",
            "country_id": "id_pais",
            "last_update": "ultima_actualizacion",
        },
        "address": {
            "address_id": "id_direccion",
            "address": "direccion",
            "address2": "direccion2",
            "district": "distrito",
            "city_id": "id_ciudad",
            "postal_code": "codigo_postal",
            "phone": "telefono",
            "last_update": "ultima_actualizacion",
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
            "last_update": "ultima_actualizacion",
        },
        "store": {
            "store_id": "id_tienda",
            "manager_staff_id": "id_gerente_personal",
            "address_id": "id_direccion",
            "last_update": "ultima_actualizacion",
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
            "picture": "foto",
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
            "last_update": "ultima_actualizacion",
        },
        "inventory": {
            "inventory_id": "id_inventario",
            "film_id": "id_pelicula",
            "store_id": "id_tienda",
            "last_update": "ultima_actualizacion",
        },
        "rental": {
            "rental_id": "id_alquiler",
            "rental_date": "fecha_alquiler",
            "inventory_id": "id_inventario",
            "customer_id": "id_cliente",
            "return_date": "fecha_devolucion",
            "staff_id": "id_personal",
            "last_update": "ultima_actualizacion",
        },
        "payment": {
            "payment_id": "id_pago",
            "customer_id": "id_cliente",
            "staff_id": "id_personal",
            "rental_id": "id_alquiler",
            "amount": "monto",
            "payment_date": "fecha_pago",
            "last_update": "ultima_actualizacion",
        },
        "film_actor": {
            "actor_id": "id_actor",
            "film_id": "id_pelicula",
            "last_update": "ultima_actualizacion",
        },
        "film_category": {
            "film_id": "id_pelicula",
            "category_id": "id_categoria",
            "last_update": "ultima_actualizacion",
        },
    },
}


def _validar_identificador(nombre: str, contexto: str) -> str:
    """Valida que un identificador SQL proveniente de ESQUEMA sea seguro."""
    if not isinstance(nombre, str) or not _IDENTIFICADOR_RE.match(nombre):
        raise ValueError(
            f"Identificador SQL inválido para {contexto}: {nombre!r}. "
            "Verifique el diccionario en esquema.py."
        )
    return nombre


def schema() -> str:
    """Devuelve el nombre del esquema SQL Server configurado (ej. 'dbo' o 'sakila')."""
    if "schema" not in ESQUEMA or not ESQUEMA["schema"]:
        raise KeyError(
            "Falta la clave 'schema' en ESQUEMA dentro de esquema.py "
            "(ejemplo: 'dbo')."
        )
    return _validar_identificador(ESQUEMA["schema"], "schema")


def t(tabla_canonica: str) -> str:
    """
    Devuelve el nombre físico de la tabla en la base de datos a partir del
    nombre canónico de Sakila. Falla explícitamente si la tabla no está mapeada.
    """
    tablas = ESQUEMA.get("tablas", {})
    if tabla_canonica not in tablas or not tablas[tabla_canonica]:
        disponibles = ", ".join(sorted(tablas.keys()))
        raise KeyError(
            f"Tabla canónica '{tabla_canonica}' no encontrada en esquema.py. "
            f"Tablas mapeadas: [{disponibles}]."
        )
    return _validar_identificador(tablas[tabla_canonica], f"tabla '{tabla_canonica}'")


def c(tabla_canonica: str, columna_canonica: str) -> str:
    """
    Devuelve el nombre físico de la columna a partir de los nombres canónicos
    de tabla y columna. Falla explícitamente si falta la tabla o la columna.
    """
    columnas_por_tabla = ESQUEMA.get("columnas", {})
    if tabla_canonica not in columnas_por_tabla:
        raise KeyError(
            f"Tabla canónica '{tabla_canonica}' sin diccionario de columnas "
            "en esquema.py."
        )
    cols = columnas_por_tabla[tabla_canonica]
    if columna_canonica not in cols or not cols[columna_canonica]:
        disponibles = ", ".join(sorted(cols.keys()))
        raise KeyError(
            f"Columna canónica '{columna_canonica}' no encontrada para la tabla "
            f"'{tabla_canonica}' en esquema.py. Columnas disponibles: [{disponibles}]."
        )
    return _validar_identificador(
        cols[columna_canonica], f"columna '{tabla_canonica}.{columna_canonica}'"
    )


def fqn(tabla_canonica: str) -> str:
    """Devuelve el nombre completamente calificado [esquema].[tabla] en SQL Server."""
    return f"[{schema()}].[{t(tabla_canonica)}]"


def renombrar_a_canonico(df: pd.DataFrame, tabla_canonica: str) -> pd.DataFrame:
    """
    Renombra las columnas de un DataFrame extraído desde SQL Server a sus
    nombres canónicos de Sakila.
    """
    if tabla_canonica not in ESQUEMA.get("columnas", {}):
        raise KeyError(
            f"Tabla canónica '{tabla_canonica}' no encontrada en ESQUEMA['columnas']."
        )
    mapa_inverso = {v: k for k, v in ESQUEMA["columnas"][tabla_canonica].items()}
    return df.rename(columns=mapa_inverso)


def generar_query_conjunto_trabajo(
    ruta_template: Path = SQL_DIR / "conjunto_trabajo.sql",
) -> str:
    """
    Lee la plantilla portable sql/conjunto_trabajo.sql e inyecta únicamente los
    identificadores validados desde ESQUEMA. Los valores de filtro (:tarifa_min,
    :tarifa_max, :clasificacion) permanecen como placeholders para ser enviados
    estrictamente vía params en pandas.read_sql.
    """
    plantilla = ruta_template.read_text(encoding="utf-8")
    mapeo = {
        "fqn_film": fqn("film"),
        "fqn_inventory": fqn("inventory"),
        "fqn_rental": fqn("rental"),
        "fqn_payment": fqn("payment"),
        "c_film_id": c("film", "film_id"),
        "c_film_title": c("film", "title"),
        "c_film_rate": c("film", "rental_rate"),
        "c_film_cost": c("film", "replacement_cost"),
        "c_film_duration": c("film", "rental_duration"),
        "c_film_rating": c("film", "rating"),
        "c_inv_id": c("inventory", "inventory_id"),
        "c_inv_film_id": c("inventory", "film_id"),
        "c_rent_id": c("rental", "rental_id"),
        "c_rent_inv_id": c("rental", "inventory_id"),
        "c_pay_rent_id": c("payment", "rental_id"),
        "c_pay_amount": c("payment", "amount"),
    }
    return plantilla.format(**mapeo)


def generar_query_ingresos_por_pelicula() -> str:
    """Genera la consulta de contraste T-SQL usando nombres calificados del esquema."""
    return f"""
    SELECT
        f.[{c("film", "film_id")}] AS film_id,
        ISNULL(SUM(p.[{c("payment", "amount")}]), 0.0) AS total_revenue
    FROM {fqn("film")} f
    LEFT JOIN {fqn("inventory")} i
        ON f.[{c("film", "film_id")}] = i.[{c("inventory", "film_id")}]
    LEFT JOIN {fqn("rental")} r
        ON i.[{c("inventory", "inventory_id")}] = r.[{c("rental", "inventory_id")}]
    LEFT JOIN {fqn("payment")} p
        ON r.[{c("rental", "rental_id")}] = p.[{c("payment", "rental_id")}]
    GROUP BY f.[{c("film", "film_id")}]
    ORDER BY f.[{c("film", "film_id")}];
    """


def contar_filas_origen_volcado(ruta_volcado: Path = DEFAULT_DUMP_PATH) -> Dict[str, int]:
    """
    Cuenta dinámicamente la cantidad real de filas por tabla directamente desde
    el script SQL de volcado de datos (sin escribir cifras a mano).
    Devuelve un diccionario indexado por nombre canónico de Sakila.
    """
    ruta = Path(ruta_volcado)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de volcado de origen en: {ruta}"
        )

    mapa_fisico_a_canonico = {
        nombre_fisico.lower(): nombre_canonico
        for nombre_canonico, nombre_fisico in ESQUEMA["tablas"].items()
        if nombre_fisico
    }
    # Acepta también volcados con nombres canónicos originales de MySQL Sakila
    for nombre_canonico in ESQUEMA["tablas"]:
        mapa_fisico_a_canonico.setdefault(nombre_canonico.lower(), nombre_canonico)

    conteos_crudos: Dict[str, int] = {}
    tabla_actual: str | None = None
    patron_insert = re.compile(
        r"^\s*INSERT\s+(?:INTO\s+)?(?:\[?\w+\]?\.)?\[?(\w+)\]?", re.IGNORECASE
    )

    with ruta.open("r", encoding="utf-8", errors="ignore") as fh:
        for linea in fh:
            match = patron_insert.match(linea)
            if match:
                tabla_actual = match.group(1).lower()
                conteos_crudos.setdefault(tabla_actual, 0)
                if "VALUES" in linea.upper():
                    resto = linea.split("VALUES", 1)[1] if "VALUES" in linea else linea.split("values", 1)[1]
                    if "(" in resto:
                        # Cuenta tuplas en la misma línea (formato MySQL multi-row o single-row)
                        conteos_crudos[tabla_actual] += len(re.findall(r"\([^)]*\)", resto))
                continue

            if tabla_actual:
                limpia = linea.strip()
                upper = limpia.upper()
                if not limpia or limpia.startswith("--"):
                    continue
                if upper.startswith(("GO", "SET ", "PRINT", "ALTER", "UNLOCK", "LOCK")):
                    if "IDENTITY_INSERT" in upper and "OFF" in upper:
                        tabla_actual = None
                    elif upper.startswith(("UNLOCK", "LOCK", "GO")):
                        tabla_actual = None
                    continue
                if limpia.startswith("("):
                    conteos_crudos[tabla_actual] += 1

    conteos_canonicos: Dict[str, int] = {}
    for tabla_cruda, cantidad in conteos_crudos.items():
        if tabla_cruda in mapa_fisico_a_canonico:
            canon = mapa_fisico_a_canonico[tabla_cruda]
            conteos_canonicos[canon] = conteos_canonicos.get(canon, 0) + cantidad
    return conteos_canonicos


def generar_query_reconciliacion(
    ruta_sql: Path = SQL_DIR / "reconciliacion.sql",
) -> str:
    """Devuelve la consulta portable sql/reconciliacion.sql (espera params={'esquema': schema()})."""
    return ruta_sql.read_text(encoding="utf-8")


def reconciliar_con_origen(
    engine: Engine,
    ruta_volcado: Path = DEFAULT_DUMP_PATH,
    ruta_sql: Path = SQL_DIR / "reconciliacion.sql",
) -> pd.DataFrame:
    """
    Ejecuta la reconciliación de 4 columnas (tabla, filas_origen, filas_sql_server,
    diferencia) contando dinámicamente tanto el volcado de origen como SQL Server.
    """
    conteos_origen = contar_filas_origen_volcado(ruta_volcado)
    query = text(generar_query_reconciliacion(ruta_sql))
    df_motor = pd.read_sql(query, engine, params={"esquema": schema()})

    conteos_motor = {
        str(row["tabla_fisica"]).lower(): int(row["filas_sql_server"])
        for _, row in df_motor.iterrows()
    }

    orden_tablas = [
        "actor", "category", "language", "country", "city", "address",
        "film", "film_actor", "film_category", "store", "staff",
        "customer", "inventory", "rental", "payment",
    ]
    # Incorporar cualquier tabla adicional presente en el mapeo (ej. film_text)
    for canon in ESQUEMA["tablas"]:
        if canon not in orden_tablas:
            orden_tablas.append(canon)

    filas = []
    for canon in orden_tablas:
        if canon not in ESQUEMA["tablas"] or not ESQUEMA["tablas"][canon]:
            continue
        fisica = t(canon).lower()
        n_origen = conteos_origen.get(canon, 0)
        n_sql = conteos_motor.get(fisica, 0)
        filas.append(
            {
                "tabla": canon,
                "filas_origen": n_origen,
                "filas_sql_server": n_sql,
                "diferencia": n_sql - n_origen,
            }
        )
    return pd.DataFrame(filas)


def generar_query_reglas_negocio_transaccionales() -> Dict[str, str]:
    """
    Consultas portables para verificar reglas de negocio transaccionales
    en SQL Server (sin superponerse con el control específico de la variante).
    """
    return {
        "devolucion_anterior_alquiler": f"""
        SELECT
            COUNT(*) AS total_alquileres,
            SUM(CASE WHEN [{c("rental", "return_date")}] IS NULL THEN 1 ELSE 0 END) AS alquileres_sin_devolucion,
            SUM(
                CASE
                    WHEN [{c("rental", "return_date")}] IS NOT NULL
                     AND [{c("rental", "return_date")}] < [{c("rental", "rental_date")}]
                    THEN 1 ELSE 0
                END
            ) AS violaciones_devolucion_anterior
        FROM {fqn("rental")};
        """,
        "pago_anterior_alquiler": f"""
        SELECT
            COUNT(*) AS total_pagos,
            SUM(CASE WHEN pg.[{c("payment", "rental_id")}] IS NULL THEN 1 ELSE 0 END) AS pagos_sin_alquiler,
            SUM(
                CASE
                    WHEN a.[{c("rental", "rental_id")}] IS NOT NULL
                     AND pg.[{c("payment", "payment_date")}] < a.[{c("rental", "rental_date")}]
                    THEN 1 ELSE 0
                END
            ) AS violaciones_pago_anterior
        FROM {fqn("payment")} pg
        LEFT JOIN {fqn("rental")} a
            ON pg.[{c("payment", "rental_id")}] = a.[{c("rental", "rental_id")}];
        """,
    }


def generar_query_cobertura_temporal() -> str:
    """Genera la consulta portable de distribución mensual de alquileres (Oportunidad)."""
    col_fecha = c("rental", "rental_date")
    return f"""
    SELECT
        YEAR([{col_fecha}])  AS anio,
        MONTH([{col_fecha}]) AS mes,
        COUNT(*)             AS alquileres,
        MIN([{col_fecha}])   AS primera_fecha,
        MAX([{col_fecha}])   AS ultima_fecha
    FROM {fqn("rental")}
    GROUP BY YEAR([{col_fecha}]), MONTH([{col_fecha}])
    ORDER BY anio, mes;
    """
