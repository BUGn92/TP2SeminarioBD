# Anexo de Trazabilidad de Inteligencia Artificial (IA)
**Trabajo Práctico 2 — Seminario de Actualización 2026**  
**Equipo:** 6 | **Integrantes:** Agustin Bugnoni, Lorenzo Zárate  
**Variante:** 6 (Precios, recupero y rentabilidad del catálogo)

---

## 1. Bitácora de Prompts y Correcciones Manuales

Durante el desarrollo del Trabajo Práctico 2 se utilizaron asistentes de Inteligencia Artificial para acelerar tareas de exploración de sintaxis, estructuración de consultas complejas y generación de plantillas de visualización en Matplotlib/Seaborn.

### Interacciones Principales y Correcciones Realizadas

1. **Prompt 1: Generación de la consulta SQL del conjunto de trabajo**
   * *Prompt utilizado:* `"Escribí una consulta SQL Server para Sakila que una peliculas, inventario, alquileres y pagos y calcule la recaudacion total y cantidad de alquileres por pelicula."`
   * *Comportamiento de la IA:* La herramienta generó una consulta utilizando nombres canónicos en inglés (`film`, `inventory`, `rental`, `payment`) y aplicó `INNER JOIN`.
   * *Corrección manual indispensable:*
     * **Conflicto de nombres de tablas y columnas:** En nuestra base migrada en el TP1, las tablas y campos están traducidos al español (`pelicula`, `inventario`, `tarifa_alquiler`, etc.). La consulta arrojaba error inmediato de objeto no encontrado en SQL Server.
     * **Pérdida silenciosa de datos por `INNER JOIN`:** El modelo propuso `INNER JOIN`, lo cual eliminaba 42 películas del catálogo que no poseían copias en inventario. Se corrigió manualmente a `LEFT JOIN` para preservar las 1.000 películas del catálogo.
     * **Resolución arquitectónica:** Se diseñó el módulo `esquema.py` para mapear dinámicamente nombres canónicos a nombres en español de forma desacoplada y portable.

2. **Prompt 2: Cálculo de métricas derivadas en Pandas**
   * *Prompt utilizado:* `"Cómo calcular en pandas el ratio de recupero y el break even de alquileres para cada pelicula evitando division por cero si inventory_count es 0."`
   * *Comportamiento de la IA:* Sugirió una función aplicada con `.apply(lambda row: ...)` recorriendo fila por fila.
   * *Corrección manual:* Se reemplazó la propuesta por operaciones 100% vectorizadas con `np.where` y `np.ceil`, cumpliendo la restricción explícita de la cátedra que penaliza bucles y funciones fila por fila.

---

## 2. Crítica de Código: Código Propuesto por IA vs. Versión Propia Optimizada

A continuación se compara una porción crítica del pipeline: la transformación de datos y el cálculo del ratio de recupero de inversión.

### Versión Generada Inicialmente por IA (Iterativa / Poco Segura)
```python
# Propuesta inicial de la IA
def calcular_metricas_ia(df):
    ratios = []
    for idx, row in df.iterrows():
        if row['inventory_count'] > 0:
            costo = row['inventory_count'] * row['replacement_cost']
            ratio = row['total_revenue'] / costo
            ratios.append(round(ratio, 3))
        else:
            ratios.append(0.0)
    df['ratio_recupero'] = ratios
    return df
```

### Versión Definitiva Implementada por el Equipo (Vectorizada y Defensiva)
```python
# Versión propia implementada en pipeline/pipeline_tp2.py
def transformar(dataframe: pd.DataFrame, ruta_clasificacion: Path = DATA_PATH) -> pd.DataFrame:
    validar_calidad(dataframe)  # Validación defensiva previa
    resultado = dataframe.copy()
    sin_stock = resultado["inventory_count"].eq(0)

    resultado["costo_inventario_total"] = (
        resultado["inventory_count"] * resultado["replacement_cost"]
    ).round(2)

    resultado["ratio_recupero"] = np.where(
        resultado["costo_inventario_total"] > 0,
        (resultado["total_revenue"] / resultado["costo_inventario_total"]).round(3),
        0.0,
    )
    # Clasificación categórica vectorizada
    resultado["estado_recupero"] = np.select(
        [sin_stock, resultado["ratio_recupero"] >= 1.0],
        ["Sin inventario", "Recuperó inversión (≥ 1.0x)"],
        default="No recuperó (< 1.0x)",
    )
    return resultado
```

### Análisis Comparativo (Qué hace mejor cada una):
* **Rendimiento Algorítmico y Escalabilidad:** La versión de la IA utiliza `iterrows()`, penalizado por la cátedra por sobrecargar la memoria con la instanciación de objetos `pd.Series` por cada fila. La versión del equipo utiliza primitivas en C de NumPy (`np.where`), ejecutando en microsegundos y escalando a millones de filas.
* **Seguridad y Programación Defensiva:** La IA no incluía validaciones de precondición (`validar_calidad`). La versión del equipo verifica de antemano la unicidad de claves, tipos y valores no negativos, abortando con seguridad si el dataset de entrada está corrupto.
* **Manejo Semántico del Negocio:** La IA solo devolvía un número `0.0`. La versión del equipo etiqueta explícitamente el estado de recupero (`"Sin inventario"`, `"Recuperó inversión"`, `"No recuperó"`), enriqueciendo la capacidad analítica posterior.

---

## 3. Conclusiones Analíticas Erróneas Propuestas por la IA y su Detección

### Caso 1: Supuesta Elasticidad Continua y Recomendación de Precios Intermedios
* **Propuesta de la IA:** Tras calcular una correlación débil de Pearson ($r = -0.053$), la herramienta sugirió: *"Dado que el coeficiente es negativo, se observa una ligera pendiente descendente de la demanda; el videoclub debería optimizar ingresos testeando precios intermedios como \$1.99 o \$3.49 mediante una curva continua de demanda."*
* **Cómo se detectó el error:**  
  Al realizar el perfilado de datos de la Actividad 2 (cardinalidad de variables), el equipo constató que en Sakila `rental_rate` solo asume **3 valores fijos discretos** (\$0.99, \$2.99, \$4.99). La teoría estadística (Unidad 5) estipula claramente que no se puede derivar una curva continua ni afirmar elasticidad puntual ($\frac{\%\Delta Q}{\%\Delta P}$) con solo 3 niveles fijos. La aparente correlación negativa carece de significancia estadística ($p = 0.100 > 0.05$). Se rechazó la recomendación de la IA y se estructuró el análisis como una comparación entre tres estratos cualitativos fijos.

### Caso 2: Sugerencia de Descartar Películas con Recaudación Cero y Outliers Superiores
* **Propuesta de la IA:** La herramienta recomendó eliminar las 42 filas con `total_revenue = 0` bajo el argumento de que *"son datos incompletos que distorsionan la media de ingresos"*, y recomendó truncar o eliminar los 11 outliers superiores detectados por la regla de Tukey ($>\$181.80$) por considerarlos *"valores atípicos que sesgan la regresión"*.
* **Cómo se detectó el error:**  
  El equipo identificó que las 42 películas sin recaudación eran títulos legítimos del catálogo que carecían de copias físicas en inventario (`inventory_count = 0`), por lo que su eliminación violaría el principio de preservación del catálogo completo y ocultaría el costo de oportunidad del negocio. Asimismo, los outliers superiores eran títulos *blockbuster* de alta rotación legítima. Se sostuvo por escrito en el informe la decisión de conservar ambos grupos, demostrando criterio de analista sobre la automatización ciega.

---
**Equipo 6 — ISNSLBV 2026**
