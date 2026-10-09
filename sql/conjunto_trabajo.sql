-- =====================================================================
-- Trabajo Práctico 2 - Equipo 6
-- Actividad 1: Consulta del Conjunto de Trabajo Base
-- Variante 6: Precios, recupero y rentabilidad del catálogo
-- =====================================================================
-- Justificación de diseño del reparto de trabajo:
-- 1. En SQL Server se resuelven los JOINs relacionales y las agregaciones
--    pesadas (COUNT, SUM) para evitar transferir más de 32.000 filas de
--    transacciones crudas (alquileres y pagos) hacia Python.
-- 2. Se utiliza LEFT JOIN para preservar las 1.000 películas del catálogo,
--    incluyendo las 42 que no poseen inventario físico registrado.
-- 3. Los cálculos analíticos derivados (ratios, break-even) y visualizaciones
--    se delegan a Pandas para procesamiento vectorizado.
-- =====================================================================

USE [sakila_es];
GO

-- ---------------------------------------------------------------------
-- Consulta Principal: Conjunto de Trabajo Agregado a Nivel Película
-- ---------------------------------------------------------------------
-- Nota sobre parametrización: Desde Python, todo filtro por variable
-- (ej. rango de tarifas o clasificación) se pasa mediante 'params' en
-- pandas.read_sql(..., params={"tarifa_min": 0.0}).
-- ---------------------------------------------------------------------

SELECT 
    p.[id_pelicula]                     AS film_id,
    p.[titulo]                          AS title,
    p.[tarifa_alquiler]                 AS rental_rate,
    p.[costo_reemplazo]                 AS replacement_cost,
    p.[duracion_alquiler]               AS rental_duration,
    p.[duracion]                        AS length,
    p.[clasificacion]                   AS rating,
    COUNT(DISTINCT i.[id_inventario])   AS inventory_count,
    COUNT(a.[id_alquiler])              AS rental_count,
    ISNULL(SUM(pg.[monto]), 0.0)        AS total_revenue
FROM [pelicula] p
LEFT JOIN [inventario] i 
    ON p.[id_pelicula] = i.[id_pelicula]
LEFT JOIN [alquiler] a 
    ON i.[id_inventario] = a.[id_inventario]
LEFT JOIN [pago] pg 
    ON a.[id_alquiler] = pg.[id_alquiler]
GROUP BY 
    p.[id_pelicula],
    p.[titulo],
    p.[tarifa_alquiler],
    p.[costo_reemplazo],
    p.[duracion_alquiler],
    p.[duracion],
    p.[clasificacion];
GO

-- ---------------------------------------------------------------------
-- Consulta de Contraste (Benchmark SQL vs Pandas):
-- Cálculo del ingreso total por película íntegramente en el motor
-- ---------------------------------------------------------------------
SELECT 
    p.[id_pelicula]              AS film_id,
    ISNULL(SUM(pg.[monto]), 0.0) AS total_revenue_sql
FROM [pelicula] p
LEFT JOIN [inventario] i 
    ON p.[id_pelicula] = i.[id_pelicula]
LEFT JOIN [alquiler] a 
    ON i.[id_inventario] = a.[id_inventario]
LEFT JOIN [pago] pg 
    ON a.[id_alquiler] = pg.[id_alquiler]
GROUP BY 
    p.[id_pelicula];
GO
