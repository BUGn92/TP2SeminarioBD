-- =====================================================================
-- Trabajo Práctico 2 - Equipo 6
-- Actividad 0: Consulta de Reconciliación con el Origen
-- =====================================================================
-- Propósito: Comparar la cantidad de filas de la base migrada en SQL Server
-- contra el volcado original de Sakila MySQL.
-- El informe exige presentar una tabla de 4 columnas:
-- (tabla, filas en el origen, filas en SQL Server, diferencia).
-- =====================================================================

USE [sakila_es];
GO

SELECT 'actor' AS tabla, 200 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 200) AS diferencia FROM [actor]
UNION ALL
SELECT 'categoria' AS tabla, 16 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 16) AS diferencia FROM [categoria]
UNION ALL
SELECT 'idioma' AS tabla, 6 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 6) AS diferencia FROM [idioma]
UNION ALL
SELECT 'pais' AS tabla, 109 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 109) AS diferencia FROM [pais]
UNION ALL
SELECT 'ciudad' AS tabla, 600 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 600) AS diferencia FROM [ciudad]
UNION ALL
SELECT 'direccion' AS tabla, 603 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 603) AS diferencia FROM [direccion]
UNION ALL
SELECT 'pelicula' AS tabla, 1000 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 1000) AS diferencia FROM [pelicula]
UNION ALL
SELECT 'pelicula_actor' AS tabla, 5462 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 5462) AS diferencia FROM [pelicula_actor]
UNION ALL
SELECT 'pelicula_categoria' AS tabla, 1000 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 1000) AS diferencia FROM [pelicula_categoria]
UNION ALL
SELECT 'tienda' AS tabla, 2 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 2) AS diferencia FROM [tienda]
UNION ALL
SELECT 'personal' AS tabla, 2 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 2) AS diferencia FROM [personal]
UNION ALL
SELECT 'cliente' AS tabla, 599 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 599) AS diferencia FROM [cliente]
UNION ALL
SELECT 'inventario' AS tabla, 4581 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 4581) AS diferencia FROM [inventario]
UNION ALL
SELECT 'alquiler' AS tabla, 16044 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 16044) AS diferencia FROM [alquiler]
UNION ALL
SELECT 'pago' AS tabla, 16049 AS filas_origen, COUNT(*) AS filas_sql_server, (COUNT(*) - 16049) AS diferencia FROM [pago];
GO
