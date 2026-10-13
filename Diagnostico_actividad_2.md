# Diagnóstico de Calidad de Datos — Actividad 2
**Seminario de Bases de Datos 2026 — ISNSLBV**  
**Equipo:** 6 | **Variante:** 6 (Precio de alquiler frente a costo de reposición y recupero de inversión)  
**Conjunto de trabajo:** `df_trabajo` (1 000 películas del catálogo consolidado)

---

## 1. Contexto y Alcance del Diagnóstico
El presente documento constituye el control previo de calidad de datos (*data profiling*) sobre el conjunto de trabajo extraído desde SQL Server, siguiendo los lineamientos teóricos y las 6 dimensiones de calidad de la **Unidad 5** (*Completitud, Unicidad, Validez, Consistencia, Exactitud y Oportunidad*).

El objetivo es determinar la confiabilidad del conjunto previo al cálculo de métricas derivadas y formalizar las decisiones de transformación o conservación de registros.

---

## 2. Checklist de Calidad de Datos (Unidad 5)

A continuación se detalla la evaluación sistemática sobre los 8 puntos del recorrido de rutina:

| # | Pregunta de Control (Unidad 5) | Hallazgo en los Datos | Decisión / Transformación Propuesta | Fundamento Técnico y de Negocio |
|---|---|---|---|---|
| **1** | **¿Volumen y dimensiones esperadas?** | **1 000 filas × 9 columnas.** Coincide con el universo de películas reconciliado contra SQL Server. | **Conservar sin filtrar.** | Se garantiza la totalidad del catálogo; no hay pérdida ni multiplicación de entidades. |
| **2** | **¿Tipos de datos correctos?** | Identificadores y contadores en `int64`; importes monetarios en `float64`; textos en `object`/`str`. | **Sin transformación de tipos.** | No hay campos numéricos o fechas infiltrados como texto (`str`). |
| **3** | **¿Valores faltantes y criterio adoptado?** | **0 celdas nulas** (`isna().sum() == 0` en todas las columnas). | **Sin imputación.** | La consulta base con `LEFT JOIN` e `ISNULL(..., 0)` resolvió las ausencias en origen. |
| **4** | **¿Duplicados por clave de negocio?** | **0 duplicados** sobre `film_id` (`film_id.nunique() == 1000`). | **Sin transformación.** | Cada película del catálogo está representada de forma unívoca. |
| **5** | **¿Rangos válidos y reglas de negocio?** | • `rental_rate > 0` (100% cumple)<br>• `replacement_cost > rental_rate` (100% cumple)<br>• `total_revenue >= 0` (100% cumple)<br>• `replacement_cost` en $[9.99, 29.99]$ | **Aceptado.** | Cumplimiento estricto de restricciones del dominio económico del videoclub. |
| **6** | **¿Variables categóricas normalizadas?** | `rating` presenta 5 categorías canónicas (`PG-13`, `NC-17`, `R`, `PG`, `G`) sin variantes ortográficas. | **Sin transformación de cadenas.** | No existen espacios sucios, sinónimos ni problemas de mayúsculas/minúsculas. |
| **7** | **¿Cardinalidad esperada / Columnas constantes?** | Sin columnas constantes (todas con varianza $> 0$). `rental_rate` presenta **cardinalidad 3** ($0.99, $2.99, $4.99). | **Segmentación discreta en Actividad 3.** | *Hallazgo crítico:* Invalida el modelado de elasticidad continua; exige comparar 3 estratos de precio. |
| **8** | **¿Período temporal adecuado?** | Consolida el histórico completo acumulado de transacciones de alquiler y recaudación. | **Apto para el análisis.** | Cobertura suficiente para evaluar el recupero histórico de la inversión por título. |

---

## 3. Análisis de Valores Atípicos (Regla IQR de Tukey)

Sobre la métrica principal (`total_revenue`), se calcularon los estadísticos de dispersión:
* **$Q_1$ (P25):** $33.95 | **Mediana (P50):** $61.85 | **$Q_3$ (P75):** $93.09 | **IQR:** $59.14
* **Límite Inferior ($Q_1 - 1.5 \times IQR$):** −$54.77 *(teórico)* $\rightarrow$ Umbral físico: $0.00
* **Límite Superior ($Q_3 + 1.5 \times IQR$):** $181.80

### Decisiones de Limpieza Justificadas:

1. **Outliers Superiores (11 películas con ingresos $> \$181.80$):**
   * **Decisión:** **NO SE ELIMINAN.**
   * **Fundamento:** Corresponden a los títulos de alta rotación (*blockbusters*, ej. *TELEGRAPH VOYAGE* con $231.73 y 27 alquileres a $4.99). El criterio de Tukey solo identifica candidatos estadísticos; eliminarlos eliminaría los casos comerciales más exitosos y sesgaría negativamente el análisis de rentabilidad.
2. **Películas con Ingreso Cero (42 películas con `total_revenue = $0.0`):**
   * **Decisión:** **SE CONSERVAN Y SE ETIQUETAN.**
   * **Fundamento:** Coinciden exactamente con las 42 películas sin copias físicas en inventario (`inventory_count = 0`). Su recaudación nula es una consecuencia directa de la falta de stock y no un error de registro. Se segregan para no distorsionar el análisis de rotación de copias activas.

---

## 4. Hallazgos Específicos de la Variante 6 y Réplica en Motor

1. **Estructura Discreta de Precios:**  
   `rental_rate` se distribuye de forma casi uniforme en solo 3 escalones: \$0.99 (34.1%), \$2.99 (32.3%) y \$4.99 (33.6%). Metodológicamente, esto impide calcular una función de elasticidad-precio continua ($\epsilon = \frac{\%\Delta Q}{\%\Delta P}$), orientando la Actividad 3 hacia el análisis comparativo entre los tres grupos tarifarios.
2. **Consistencia Motor SQL Server vs. Pandas (Exactitud):**  
   La réplica de controles de agregación en T-SQL arrojó una **coincidencia del 100%** frente al cliente Pandas (distribución de tarifas y conteo de películas sin ingreso = 42), validando la integridad del mapeo y la extracción.

---

## 5. Síntesis y Matriz de Transformaciones

* **Registros descartados:** **0 filas (0%)**.
* **Registros imputados:** **0 filas (0%)**.
* **Transformaciones a ejecutar en Actividad 3:**
  1. Cálculo vectorizado de métricas derivadas (ratio de recupero, break-even de alquileres e ingresos netos).
  2. Flag de segmentación para películas sin inventario (`sin_stock = True`).
