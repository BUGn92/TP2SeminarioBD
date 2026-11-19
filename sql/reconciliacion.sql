-- =====================================================================
-- Trabajo Práctico 2 - Equipo 6
-- Actividad 0: Consulta Portable de Reconciliación en SQL Server
-- =====================================================================
-- Propósito:
--   Obtener el conteo de filas por tabla del esquema activo en SQL Server
--   directamente desde el catálogo del sistema (sys.tables / sys.partitions),
--   sin hardcodear nombres de tablas propios ni instrucciones USE [...].
--
-- Uso:
--   Se ejecuta desde Python pasando params={"esquema": esquema.schema()}.
--   Luego Python traduce los nombres físicos a nombres canónicos de Sakila
--   usando esquema.py y los contrasta contra el conteo dinámico del volcado
--   de origen (sin escribir cifras a mano).
-- =====================================================================

SELECT
    t.name              AS tabla_fisica,
    SUM(p.[rows])       AS filas_sql_server
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON t.schema_id = s.schema_id
INNER JOIN sys.partitions AS p
    ON t.object_id = p.object_id
WHERE s.name = :esquema
  AND p.index_id IN (0, 1)
GROUP BY
    t.name
ORDER BY
    t.name;
