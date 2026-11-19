# Diagnóstico de Calidad de Datos — Actividad 2
**Seminario de Bases de Datos 2026 — ISNSLBV** | **Equipo 6 — Variante 6:** Precios, recupero y rentabilidad del catálogo  
**Conjunto de trabajo:** `df_trabajo` (1.000 películas consolidadas desde `sakila_es` + auditoría transaccional en SQL Server)

---

## 1. Alcance y Checklist de Calidad de Datos (8 Puntos — Unidad 5)

Se auditaron las seis dimensiones formales (*Completitud, Unicidad, Validez, Consistencia, Exactitud y Oportunidad*) antes de calcular métricas derivadas:

| # | Control (Unidad 5) | Hallazgo en los Datos | Decisión / Transformación | Fundamento Técnico y de Negocio |
|---|---|---|---|---|
| **1** | **Volumen y dimensiones** | **1.000 filas × 9 columnas.** Reconciliación 15/15 tablas con diferencia = 0 (16.044 alquileres y 16.044 pagos). | **Conservar sin filtrar.** | Cobertura íntegra del catálogo sin pérdida ni multiplicación de entidades. |
| **2** | **Tipos de datos** | IDs y conteos en `int64`; montos `DECIMAL(4,2)`/`(5,2)` leídos en Pandas como `float64`; textos en `str`/`object`. | **Sin casteo.** | Sin números ni fechas infiltrados como texto; precisión validada (`0.000000` diff vs. T-SQL). |
| **3** | **Valores faltantes** | **0 nulos** en las 9 columnas de `df_trabajo`. En `alquiler`, 183 filas tienen `return_date IS NULL`. | **Sin imputación.** | `LEFT JOIN` + `ISNULL(..., 0)` absorbieron ausencias en origen; 183 alquileres abiertos son válidos. |
| **4** | **Duplicados por clave** | **0 duplicados** sobre `film_id` (`nunique() == 1000`). | **Sin transformación.** | Unicidad garantizada por película. |
| **5** | **Reglas de negocio propias** | 0 violaciones en 3 reglas independientes: (1) `replacement_cost > rental_rate` (ratio 2.0x–30.3x), (2) `return_date >= rental_date` (16.044 alq.) y (3) `payment_date >= rental_date` (16.044 pagos). | **Aceptado.** | Cumplimiento del 100% de restricciones lógicas de catálogo y cronología transaccional (sin superponerse con el control específico). |
| **6** | **Categorías normalizadas** | `rating` presenta 5 valores canónicos (`G`, `PG`, `PG-13`, `R`, `NC-17`). | **Sin limpieza de strings.** | Sin variantes ortográficas, espacios sucios ni inconsistencias de mayúsculas. |
| **7** | **Cardinalidad y constantes** | Sin columnas constantes. **`rental_rate` toma solo 3 valores discretos** (\$0.99, \$2.99, \$4.99). | **Segmentación discreta en Act. 3.** | *Hallazgo crítico:* invalida elasticidad continua; obliga a comparar 3 estratos fijos. |
| **8** | **Oportunidad / período** | **Serie histórica y discontinua (2005–2006):** actividad en may–ago 2005, **5 meses enteros sin movimientos** (sep 2005–ene 2006) y 182 registros el 14/02/2006. | **Apto con reserva explícita.** | Sirve para medir recupero acumulado en el período observado; impide inferir estacionalidad continua o vigencia actual. |

---

## 2. Valores Atípicos (Regla IQR de Tukey sobre `total_revenue`)

* **Cuartiles y límites:** $Q_1 = \$33.95$ | Mediana $= \$61.85$ | $Q_3 = \$93.09$ | $IQR = \$59.14$ | Límite inferior $= -\$54.77$ (piso físico $\$0.00$) | **Límite superior $= \$181.80$**.
* **11 outliers superiores ($>\$181.80$):** **NO SE ELIMINAN.** Corresponden a títulos legítimos de alta rotación (*blockbusters*, ej. *TELEGRAPH VOYAGE* con \$231.73). Eliminarlos sesgaría a la baja la rentabilidad real del catálogo.
* **42 títulos con ingreso \$0.00:** **SE CONSERVAN Y ETIQUETAN (`"Sin inventario"`).** Coinciden exactamente con los 42 títulos con `inventory_count = 0`. No son errores de carga sino ausencia de stock; se segregan con `sin_stock = True` para evitar divisiones por cero.

---

## 3. Control Específico de la Variante 6 y Réplica en SQL Server

* **Precios y costos de reposición:** 0 nulos, 0 valores $\le 0$, y `replacement_cost` dentro del rango $[\$9.99, \$29.99]$. `rental_rate` se reparte casi en tercios: **\$0.99** (341; 34.1%), **\$2.99** (323; 32.3%) y **\$4.99** (336; 33.6%), lo que descarta modelar una curva de elasticidad-precio continua.
* **Exactitud motor vs. Pandas (2 controles replicados en T-SQL):** Distribución de `rental_rate` (`341 / 323 / 336`) y conteo de películas sin ingreso (`42`) arrojaron **100% de coincidencia exacta** entre SQL Server y Pandas.

---

## 4. Síntesis de Transformaciones Propuestas para Actividad 3 y ETL

* **Filas descartadas / imputadas:** **0 filas (0%)**.
* **Transformaciones vectorizadas:** cálculo de `ingreso_por_copia`, `alquileres_por_copia`, `costo_inventario_total`, `ratio_recupero`, `breakeven_alquileres` y bandera `sin_stock` (sin bucles ni divisiones por cero).
