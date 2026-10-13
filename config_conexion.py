"""
Módulo de Configuración de Conexión a la Base de Datos
Trabajo Práctico 2 - Equipo 6

"""

import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno desde .env si existe
load_dotenv()


def obtener_cadena_conexion() -> str:
    """
    Cadena de conexión ODBC a partir de las variables de entorno.
    """
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME", "sakila_es")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "no").lower() == "yes"
    trust_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    # Formato de servidor con puerto
    servidor_completo = (
        f"{server},{port}"
        if port and "," not in server and "\\" not in server
        else server
    )

    if trusted_connection:
        params = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor_completo};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate={trust_cert};"
        )
    else:
        user = os.getenv("DB_USER", "sa")
        password = os.getenv("DB_PASSWORD", "")
        params = (
            f"DRIVER={{{driver}}};"
            f"SERVER={servidor_completo};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate={trust_cert};"
        )

    # Codificar los parámetros ODBC para SQLAlchemy
    params_codificados = urllib.parse.quote_plus(params)
    return f"mssql+pyodbc:///?odbc_connect={params_codificados}"


def obtener_engine(echo: bool = False):
    """
    Creación del motor de SQLAlchemy para interactuar con SQL Server.
    """
    connection_url = obtener_cadena_conexion()
    return create_engine(connection_url, echo=echo, fast_executemany=True)


def probar_conexion() -> bool:
    """
    Prueba de conexión ejecutando un SELECT 1 simple y muestra el estado.
    """
    try:
        engine = obtener_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION AS version, DB_NAME() AS db_actual")).fetchone()
            print(" Conexión exitosa a SQL Server:")
            print(f"  - Base actual: {result.db_actual}")
            print(f"  - Versión del motor: {result.version[:80]}...")
            return True
    except Exception as e:
        print(f" Error al conectar con SQL Server: {e}")
        print("\nVerifique que:")
        print(" 1. El servicio de SQL Server esté corriendo.")
        print(" 2. El archivo .env tenga las credenciales y el puerto correctos.")
        print(" 3. El driver especificado en DB_DRIVER esté instalado en su sistema.")
        return False


if __name__ == "__main__":
    probar_conexion()
