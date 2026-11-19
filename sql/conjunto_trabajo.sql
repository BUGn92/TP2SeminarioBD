-- =====================================================================
-- Trabajo Práctico 2 - Equipo 6
-- Actividad 1: Plantilla T-SQL del Conjunto de Trabajo Base (Portable)
-- Variante 6: Precios, recupero y rentabilidad del catálogo
-- =====================================================================
-- Diseño de portabilidad y seguridad:
-- 1. No contiene nombres propios en español ni instrucciones USE [...].
--    Los identificadores de esquema, tablas y columnas se resuelven
--    exclusivamente desde esquema.py (validados antes de renderizar).
-- 2. Todo valor variable de filtrado (tarifa_min, tarifa_max,
--    clasificacion) viaja estrictamente mediante el argumento params
--    de pandas.read_sql / SQLAlchemy (prevención de inyección SQL).
-- 3. Se utiliza LEFT JOIN para conservar el 100% del catálogo (incluidas
--    las 42 películas sin copias en inventario) y COUNT(DISTINCT ...) en
--    alquileres para evitar multiplicación ante múltiples pagos por alquiler.
-- =====================================================================

SELECT
    f.[{c_film_id}]                     AS film_id,
    f.[{c_film_title}]                  AS title,
    f.[{c_film_rate}]                   AS rental_rate,
    f.[{c_film_cost}]                   AS replacement_cost,
    f.[{c_film_duration}]               AS rental_duration,
    f.[{c_film_rating}]                 AS rating,
    COUNT(DISTINCT i.[{c_inv_id}])      AS inventory_count,
    COUNT(DISTINCT r.[{c_rent_id}])     AS rental_count,
    ISNULL(SUM(p.[{c_pay_amount}]), 0.0) AS total_revenue
FROM {fqn_film} f
LEFT JOIN {fqn_inventory} i
    ON f.[{c_film_id}] = i.[{c_inv_film_id}]
LEFT JOIN {fqn_rental} r
    ON i.[{c_inv_id}] = r.[{c_rent_inv_id}]
LEFT JOIN {fqn_payment} p
    ON r.[{c_rent_id}] = p.[{c_pay_rent_id}]
WHERE f.[{c_film_rate}] BETWEEN :tarifa_min AND :tarifa_max
  AND (:clasificacion IS NULL OR f.[{c_film_rating}] = :clasificacion)
GROUP BY
    f.[{c_film_id}],
    f.[{c_film_title}],
    f.[{c_film_rate}],
    f.[{c_film_cost}],
    f.[{c_film_duration}],
    f.[{c_film_rating}]
ORDER BY
    f.[{c_film_id}];
