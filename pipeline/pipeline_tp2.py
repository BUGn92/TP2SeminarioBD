"""Pipeline ETL reproducible para el análisis de recupero del catálogo Sakila."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config_conexion
import esquema

DATA_PATH = Path(__file__).resolve().parent / "datos" / "clasificacion_tarifaria.csv"
LOG_PATH = Path(__file__).resolve().parent / "evidencia_ejecuciones.log"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "TP2_RecuperoPorPelicula"
SOURCE_COLUMNS = [
    "film_id",
    "title",
    "rental_rate",
    "replacement_cost",
    "rental_duration",
    "rating",
    "inventory_count",
    "rental_count",
    "total_revenue",
]
DERIVED_COLUMNS = [
    "ingreso_por_copia",
    "alquileres_por_copia",
    "costo_inventario_total",
    "ratio_recupero",
    "breakeven_alquileres",
    "estado_recupero",
    "sin_stock",
    "nivel_precio",
]
DESTINATION_COLUMNS = SOURCE_COLUMNS + DERIVED_COLUMNS

logger = logging.getLogger("pipeline_tp2")


def configurar_logging() -> None:
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def extraer(engine: Engine) -> pd.DataFrame:
    logger.info("Inicio de extracción desde SQL Server.")
    query = text(esquema.generar_query_conjunto_trabajo())
    dataframe = pd.read_sql_query(query, con=engine)
    logger.info("Fin de extracción: %d filas.", len(dataframe))
    return dataframe


def validar_calidad(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise ValueError("La extracción no devolvió filas; se cancela la carga.")
    if list(dataframe.columns) != SOURCE_COLUMNS:
        raise ValueError(
            "La extracción no coincide con las columnas esperadas: "
            f"{list(dataframe.columns)!r}"
        )
    if dataframe["film_id"].duplicated().any():
        raise ValueError("La extracción contiene film_id duplicados.")
    if dataframe.isna().any().any():
        raise ValueError("La extracción contiene valores nulos inesperados.")
    if (dataframe["rental_rate"] <= 0).any():
        raise ValueError("Hay tarifas de alquiler que no son positivas.")
    if (dataframe["replacement_cost"] <= dataframe["rental_rate"]).any():
        raise ValueError("Hay costos de reemplazo menores o iguales a la tarifa.")
    if (dataframe["total_revenue"] < 0).any():
        raise ValueError("Hay ingresos totales negativos.")
    if (dataframe[["inventory_count", "rental_count"]] < 0).any().any():
        raise ValueError("Hay conteos negativos de inventario o alquileres.")


def transformar(dataframe: pd.DataFrame, ruta_clasificacion: Path = DATA_PATH) -> pd.DataFrame:
    logger.info("Inicio de transformación: %d filas recibidas.", len(dataframe))
    validar_calidad(dataframe)
    resultado = dataframe.copy()
    sin_stock = resultado["inventory_count"].eq(0)

    resultado["ingreso_por_copia"] = np.where(
        ~sin_stock,
        (resultado["total_revenue"] / resultado["inventory_count"]).round(2),
        0.0,
    )
    resultado["alquileres_por_copia"] = np.where(
        ~sin_stock,
        (resultado["rental_count"] / resultado["inventory_count"]).round(2),
        0.0,
    )
    resultado["costo_inventario_total"] = (
        resultado["inventory_count"] * resultado["replacement_cost"]
    ).round(2)
    resultado["ratio_recupero"] = np.where(
        resultado["costo_inventario_total"] > 0,
        (
            resultado["total_revenue"] / resultado["costo_inventario_total"]
        ).round(3),
        0.0,
    )
    resultado["breakeven_alquileres"] = np.ceil(
        resultado["replacement_cost"] / resultado["rental_rate"]
    ).astype("int64")
    resultado["estado_recupero"] = np.select(
        [sin_stock, resultado["ratio_recupero"] >= 1.0],
        ["Sin inventario", "Recuperó inversión (≥ 1.0x)"],
        default="No recuperó (< 1.0x)",
    )
    resultado["sin_stock"] = sin_stock

    logger.info("Inicio de integración con el archivo plano: %d filas.", len(resultado))
    clasificacion = pd.read_csv(ruta_clasificacion)
    if list(clasificacion.columns) != ["rental_rate", "nivel_precio"]:
        raise ValueError(
            "El archivo complementario debe tener las columnas "
            "'rental_rate' y 'nivel_precio'."
        )
    if clasificacion["rental_rate"].duplicated().any():
        raise ValueError("El archivo complementario repite tarifas de alquiler.")
    if clasificacion[["rental_rate", "nivel_precio"]].isna().any().any():
        raise ValueError("El archivo complementario contiene valores nulos.")

    tarifas_origen = set(resultado["rental_rate"].unique())
    tarifas_archivo = set(clasificacion["rental_rate"].unique())
    if tarifas_origen != tarifas_archivo:
        raise ValueError(
            "Las tarifas del archivo complementario no coinciden con las del origen. "
            f"Sin clasificar: {sorted(tarifas_origen - tarifas_archivo)}; "
            f"sin correspondencia en origen: {sorted(tarifas_archivo - tarifas_origen)}."
        )

    resultado = resultado.merge(
        clasificacion,
        on="rental_rate",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    sin_clasificar = int(resultado["_merge"].ne("both").sum())
    if sin_clasificar:
        raise ValueError(
            f"Quedaron {sin_clasificar} filas sin clasificar tras el merge."
        )
    resultado = resultado.drop(columns="_merge")
    if len(resultado) != len(dataframe):
        raise RuntimeError("La integración modificó inesperadamente la cantidad de filas.")
    resultado = resultado[DESTINATION_COLUMNS]
    logger.info(
        "Fin de transformación e integración: %d filas; %d películas sin stock.",
        len(resultado),
        int(resultado["sin_stock"].sum()),
    )
    return resultado


def _crear_tabla_si_no_existe(connection) -> None:
    connection.execute(
        text(
            f"""
            IF OBJECT_ID(N'{TARGET_SCHEMA}.{TARGET_TABLE}', N'U') IS NULL
            BEGIN
                CREATE TABLE [{TARGET_SCHEMA}].[{TARGET_TABLE}] (
                    [film_id] INT NOT NULL,
                    [title] NVARCHAR(255) NOT NULL,
                    [rental_rate] DECIMAL(4, 2) NOT NULL,
                    [replacement_cost] DECIMAL(5, 2) NOT NULL,
                    [rental_duration] INT NOT NULL,
                    [rating] NVARCHAR(10) NOT NULL,
                    [inventory_count] INT NOT NULL,
                    [rental_count] INT NOT NULL,
                    [total_revenue] DECIMAL(18, 2) NOT NULL,
                    [ingreso_por_copia] DECIMAL(18, 2) NOT NULL,
                    [alquileres_por_copia] DECIMAL(18, 2) NOT NULL,
                    [costo_inventario_total] DECIMAL(18, 2) NOT NULL,
                    [ratio_recupero] DECIMAL(18, 3) NOT NULL,
                    [breakeven_alquileres] INT NOT NULL,
                    [estado_recupero] NVARCHAR(40) NOT NULL,
                    [sin_stock] BIT NOT NULL,
                    [nivel_precio] NVARCHAR(20) NOT NULL,
                    CONSTRAINT [PK_TP2_RecuperoPorPelicula]
                        PRIMARY KEY ([film_id])
                );
            END;
            """
        )
    )


def cargar(dataframe: pd.DataFrame, engine: Engine) -> int:
    logger.info("Inicio de carga en %s.%s: %d filas.", TARGET_SCHEMA, TARGET_TABLE, len(dataframe))
    with engine.begin() as connection:
        _crear_tabla_si_no_existe(connection)
        inspector = inspect(connection)
        columnas_actuales = [
            column["name"]
            for column in inspector.get_columns(TARGET_TABLE, schema=TARGET_SCHEMA)
        ]
        if columnas_actuales != DESTINATION_COLUMNS:
            raise RuntimeError(
                f"La tabla {TARGET_SCHEMA}.{TARGET_TABLE} ya existe con un esquema "
                "distinto al esperado; no se modificó."
            )
        clave_primaria = inspector.get_pk_constraint(
            TARGET_TABLE, schema=TARGET_SCHEMA
        ).get("constrained_columns", [])
        if clave_primaria != ["film_id"]:
            raise RuntimeError(
                f"La tabla {TARGET_SCHEMA}.{TARGET_TABLE} debe tener film_id como "
                "clave primaria; no se modificó."
            )

        connection.execute(
            text(f"DELETE FROM [{TARGET_SCHEMA}].[{TARGET_TABLE}]")
        )
        dataframe.to_sql(
            TARGET_TABLE,
            con=connection,
            schema=TARGET_SCHEMA,
            if_exists="append",
            index=False,
            chunksize=500,
        )
        conteo = connection.execute(
            text(f"SELECT COUNT(*) FROM [{TARGET_SCHEMA}].[{TARGET_TABLE}]")
        ).scalar_one()
        claves_distintas = connection.execute(
            text(
                f"SELECT COUNT(DISTINCT [film_id]) "
                f"FROM [{TARGET_SCHEMA}].[{TARGET_TABLE}]"
            )
        ).scalar_one()
        if conteo != len(dataframe) or claves_distintas != len(dataframe):
            raise RuntimeError(
                "La verificación de carga no coincide: "
                f"filas={conteo}, claves distintas={claves_distintas}, "
                f"esperadas={len(dataframe)}."
            )

    logger.info(
        "Fin de carga y verificación: SELECT COUNT(*) = %d; film_id distintos = %d.",
        conteo,
        claves_distintas,
    )
    return int(conteo)


def orquestar() -> None:
    configurar_logging()
    logger.info("Inicio del pipeline ETL.")
    engine = config_conexion.obtener_engine()
    try:
        extraido = extraer(engine)
        transformado = transformar(extraido)
        filas_cargadas = cargar(transformado, engine)
        logger.info(
            "Fin del pipeline ETL: %d filas en %s.%s.",
            filas_cargadas,
            TARGET_SCHEMA,
            TARGET_TABLE,
        )
    except Exception:
        logger.exception("Falló el pipeline ETL; la carga transaccional fue cancelada.")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    orquestar()
