# Anexo de Trazabilidad de Inteligencia Artificial (IA)
**Trabajo Práctico 2 — Seminario de Actualización 2026**  
**Materia:** Seminario de Actualización | **Docente:** Jorge Insfran  
**Unidad 5:** Introducción a Data Analytics e Ingeniería de Datos  
**Equipo:** 6 | **Integrantes:** Agustín Bugnoni, Lorenzo Zárate  
**Variante:** 6 (Precios, recupero y rentabilidad del catálogo)  

---

## 1. Metodología de Trabajo: El Paradigma de IA Agente en Google Antigravity

A diferencia de un uso convencional de Inteligencia Artificial basado en consultas aisladas a un chatbot web (donde se solicita código fragmentado mediante copiar y pegar), el desarrollo de este Trabajo Práctico se llevó a cabo utilizando un **Agente de Inteligencia Artificial Autónomo integrado directamente en el entorno de desarrollo (Google Antigravity IDE)**.

### Características del Flujo Agéntico
* **Acceso Contextual al Repositorio:** El agente inspeccionó el árbol del proyecto, la documentación oficial (enunciado del TP2 y apunte de la Unidad 5), esquemas SQL y archivos de datos.
* **Supervisión Continua (*Human-in-the-Loop*):** Ningún cambio de código, script o refactorización fue ejecutado de manera desatendida. Asumimos un rol activo de **Dirección y Supervisión Técnica**, estableciendo restricciones de diseño, revisando cada modificación y sometiendo cada propuesta a repregunta y verificación empírica contra SQL Server.
* **Ciclo de Desarrollo en Cuatro Fases:**
  1. *Síntesis y Alineación Teórica:* Extracción de los conceptos rectores de la Unidad 5 (las 6 dimensiones de calidad, criterio de Tukey, diseño EDA y pipelines idempotentes).
  2. *Planificación Estructurada:* Definición previa del plan de implementación (`plan_implementacion_1.md`) y salvaguardas ante condiciones de desaprobación.
  3. *Ejecución Punto a Punto con Repreguntas:* Desarrollo secuencial de las Actividades 0 a 5 exigiendo justificación técnica en cada decisión.
  4. *Auditoría Defensiva y Testing:* Validación contra la base real `sakila_es` (idempotencia, reconciliación dinámica, parámetros `params` y coherencia entre código e informe).

---

## 2. Bitácora de Prompts, Repreguntas y Decisiones Supervisadas

### Hito 1: Marco Teórico y Síntesis de la Unidad 5
* **Interacción Inicial:**  
  *Prompt enviado:* *"Analizá el PDF de la Unidad 5 (`Seminario_2026_Unidad05.pdf`) junto con la consigna del TP2. Necesito un resumen ejecutivo de los conceptos teóricos obligatorios que debemos cumplir en el código y en el informe, especialmente en lo relativo a calidad de datos y arquitectura de pipelines."*  
  *Desvío del Agente:* Incluyó inicialmente un checklist genérico de analítica web que no correspondía a la bibliografía de la materia.
* **Intervención y Repregunta:**  
  *Nuestra corrección:* *"¿De dónde sacaste ese checklist? La Unidad 5 hace referencia estricta a lo dictado en clase y al apunte oficial. Releé el PDF de la Unidad 5 y estructurá el análisis según las 6 dimensiones de calidad formales y el checklist de 8 preguntas."*
* **Resultado Consolidado:** Se incorporaron las 6 dimensiones formales (Completitud, Unicidad, Validez, Consistencia, Exactitud y Oportunidad) y el checklist de 8 puntos en el notebook y en `informe/diagnostico_calidad.md`.

---

### Hito 2: Arquitectura de Portabilidad (`esquema.py`, `sql/` y `params`) (Actividad 0 y 1)
* **Interacción Inicial:**  
  *Prompt enviado:* *"Generá un plan de implementación detallado (`plan_implementacion_1.md`) para abordar el trabajo práctico. No modifiques código todavía; primero quiero revisar la viabilidad y las decisiones técnicas para blindar la aprobación."*  
  *Propuesta del Agente:* Planteó consultas T-SQL directas con nombres canónicos en inglés (`film`, `inventory`, `rental`, `payment`) y luego dejó scripts estáticos en español en `sql/` sin pasar filtros reales por `params`.
* **Intervención y Repregunta:**  
  *Nuestra corrección:* En el TP1 migramos las tablas al español (`pelicula`, `inventario`, `alquiler`, `pago`), y en la defensa el proyecto debe ejecutarse contra la base de otro equipo (incluso en un esquema distinto a `dbo`) cambiando únicamente `esquema.py` y `.env`. Además, exigimos que `t()`/`c()` fallen explícitamente ante claves inexistentes y que los filtros variables viajen realmente por `params`.
* **Decisión Técnica Adoptada:**  
  Se diseñó `esquema.py` con calificador de esquema (`"schema": "dbo"`), validación de identificadores y fallo explícito (`KeyError`) en `t()`, `c()` y `fqn()`. Los scripts `sql/conjunto_trabajo.sql` y `sql/reconciliacion.sql` quedaron libres de nombres en español y `USE [...]`, y los filtros (`tarifa_min`, `tarifa_max`, `clasificacion`, `esquema`) viajan estrictamente por `params` en `pd.read_sql`.

---

### Hito 3: Reparto de Cómputo y Preservación de Casos de Borde (Actividad 1)
* **Interacción Inicial:**  
  *Prompt enviado:* *"Escribí la consulta del conjunto de trabajo para la Variante 6 uniendo películas, inventario, alquileres y pagos, calculando la recaudación total y los alquileres por película. Mostrame cómo dividimos el trabajo entre SQL Server y Pandas."*  
  *Propuesta del Agente:* Propuso `INNER JOIN` entre las cuatro tablas y sugirió calcular ratios dentro de T-SQL.
* **Intervención y Repregunta:**  
  *Detección de falla:* Al contrastar contra las 1.000 películas de la Actividad 0, el `INNER JOIN` arrojaba solo **958 filas**, descartando silenciosamente las 42 películas sin inventario.
* **Decisión Técnica Adoptada:** Se corrigió a `LEFT JOIN` con `ISNULL(SUM(...), 0.0)` y `COUNT(DISTINCT id_alquiler)` para preservar el 100% del catálogo y prevenir multiplicación ante múltiples pagos, delegando a Pandas los ratios vectorizados y la integración multi-origen.

---

### Hito 4: Perfilado de Datos y Tratamiento de Outliers (Actividad 2)
* **Interacción Inicial:**  
  *Prompt enviado:* *"Ejecutemos el diagnóstico de calidad de datos sobre el DataFrame extraído. Aplicá el método de Tukey (IQR) sobre los ingresos acumulados y decime qué hacemos con los valores detectados."*  
  *Propuesta del Agente:* Sugirió eliminar los 11 outliers superiores ($>\$181.80$) y las 42 películas con ingreso cero calificándolos como "ruido estadístico" y "registros vacíos".
* **Intervención y Criterio Aplicado:** Rechazamos el descarte automático: los 42 títulos sin recaudación carecen de copias en inventario (dato legítimo del catálogo) y los 11 outliers superiores son los *blockbusters* que concentran el éxito comercial. Se conservaron las 1.000 filas y se etiquetó explícitamente `sin_stock`.

---

### Hito 5: Visualización Narrativa y Elección de Escalas (Actividad 3)
* **Interacción Inicial:**  
  *Prompt enviado:* *"Construyamos el gráfico obligatorio de la Variante 6: dispersión entre precio de alquiler y cantidad de alquileres, con tamaño de burbuja según recaudación."*  
  *Desvío del Agente:* Generó un scatter plot colapsado en tres columnas verticales superpuestas e incluyó afirmaciones de "inelasticidad perfecta" en la anotación.
* **Supervisión y Corrección:** Se aplicó *jitter* horizontal aleatorio para desagregar visualmente los 3 escalones discretos, se agregó el control por `alquileres_por_copia` (`inventory_count` como variable omitida en los propios datos) y se corrigió la anotación del gráfico para no afirmar causalidad ni elasticidad continua.

---

### Hito 6: Pipeline ETL Idempotente y Transaccional (Actividad 4)
* **Interacción Inicial:**  
  *Prompt enviado:* *"Estructurá `pipeline/pipeline_tp2.py` como script autónomo cumpliendo la Sección 7 del enunciado."*  
  *Propuesta del Agente:* Propuso `df.to_sql(..., if_exists='replace')`.
* **Intervención y Corrección:** Rechazamos `if_exists='replace'` porque destruye el DDL tipado (`DECIMAL`, `NVARCHAR`, `PRIMARY KEY`) y deja la tabla corrupta ante un fallo intermedio. Se implementó creación condicional con `PRIMARY KEY (film_id)`, verificación del esquema existente, `DELETE` + `to_sql(..., if_exists='append')` dentro de `with engine.begin()` y aserciones poscarga de `COUNT(*)` y `COUNT(DISTINCT film_id)`.

---

## 3. Crítica de Código: Implementación Inicial Propuesta vs. Versión Definitiva del Repositorio

A continuación se compara la propuesta inicial del asistente contra la función `transformar()` efectiva implementada en [`pipeline/pipeline_tp2.py`](../pipeline/pipeline_tp2.py).

### Versión A — Propuesta Inicial del Asistente (Imperativa, Vulnerable e Ineficiente)
```python
# Propuesta inicial generada por la IA
def procesar_recupero_ia(df):
    # La IA no valida precondiciones de calidad ni tipos
    ratios = []
    breakevens = []

    # Bucle fila por fila (anti-patrón en Pandas)
    for index, row in df.iterrows():
        costo_total = row['inventory_count'] * row['replacement_cost']
        if costo_total > 0:
            ratio = row['total_revenue'] / costo_total
        else:
            ratio = 0.0
        ratios.append(round(ratio, 3))

        # Cálculo de break-even incorrecto cuando la división es exacta (int + 1)
        be = row['replacement_cost'] / row['rental_rate']
        breakevens.append(int(be) + 1)

    df['ratio_recupero'] = ratios
    df['breakeven_alquileres'] = breakevens
    return df
```

### Versión B — Implementación Definitiva en `pipeline/pipeline_tp2.py` (Vectorizada, Defensiva y Tipada)
```python
def transformar(dataframe: pd.DataFrame, ruta_clasificacion: Path = DATA_PATH) -> pd.DataFrame:
    logger.info("Inicio de transformación: %d filas recibidas.", len(dataframe))
    validar_calidad(dataframe)
    resultado = dataframe.copy()
    resultado["rental_rate"] = resultado["rental_rate"].astype(float).round(2)
    resultado["replacement_cost"] = resultado["replacement_cost"].astype(float).round(2)
    resultado["total_revenue"] = resultado["total_revenue"].astype(float).round(2)
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
    clasificacion["rental_rate"] = clasificacion["rental_rate"].astype(float).round(2)
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
```

### Cuadro Comparativo de Arquitectura de Código

| Criterio de Evaluación | Versión Propuesta por IA (Versión A) | Versión Definitiva en `pipeline_tp2.py` (Versión B) | Justificación Técnica de la Mejora |
| :--- | :--- | :--- | :--- |
| **Eficiencia Algorítmica** | Bucle procedural con `iterrows()`. | 100% Vectorizado (`np.where`, `np.select`, `np.ceil`). | Cumple la consigna y opera en $O(N)$ sobre arrays contiguos en C sin sobrecarga por fila. |
| **Programación Defensiva** | Sin validaciones previas ni normalización de decimales. | `validar_calidad()` previo, `.round(2)` y validación exacta de conjuntos de tarifas. | Principio *Fail-Fast*: detiene la ejecución antes de cargar datos corruptos o mal tipados. |
| **Exactitud del Break-Even** | `int(be) + 1` (suma 1 de más si el cociente es entero exacto). | `np.ceil(replacement_cost / rental_rate).astype("int64")`. | Calcula el techo matemático exacto tras validar `rental_rate > 0` en `validar_calidad()`. |
| **Integración Multi-Fuente** | Ninguna. | `pd.merge(..., validate="many_to_one", indicator=True)` + verificación de cardinalidad final. | Audita integridad del cruce con `clasificacion_tarifaria.csv` y garantiza que no se pierdan ni multipliquen filas. |
| **Semántica del Dominio** | Solo calcula 2 columnas parciales. | Calcula todas las métricas obligatorias (`ingreso_por_copia`, `alquileres_por_copia`, `ratio_recupero`, `breakeven_alquileres`, `estado_recupero`, `sin_stock`, `nivel_precio`). | Entrega una tabla lista para consumo analítico con orden fijo (`DESTINATION_COLUMNS`). |

---

## 4. Conclusiones Analíticas Erróneas Sugeridas por la IA y Detección Crítica

### Caso 1: La Falacia de la Elasticidad Continua y Recomendación de Precios Intermedios
* **Conclusión Propuesta por la IA:**  
  > *"Dado que el coeficiente de Pearson presenta signo negativo ($r = -0.053$), se evidencia una ligera pendiente descendente en la curva de demanda. El videoclub debería optimizar sus ingresos mediante precios dinámicos continuos, testeando valores intermedios como \$1.99 o \$3.49."*
* **Cómo detectamos el error y criterio aplicado:**  
  1. *Falta de significancia:* $p = 0.100 > 0.05$; no existe correlación lineal estadísticamente significativa.
  2. *Solo 3 valores discretos:* `rental_rate` asume únicamente \$0.99 (341), \$2.99 (323) y \$4.99 (336), lo que invalida estimar una función de demanda continua o elasticidad puntual ($\epsilon = \frac{\%\Delta Q}{\%\Delta P}$).
  3. *Corrección aplicada:* Se reemplazó por una comparación descriptiva entre tres estratos discretos (*Económica*, *Estándar*, *Premium*) sin afirmar elasticidad continua ni causalidad.

---

### Caso 2: Supuesta Causalidad Directa y Sesgo de Variable Omitida
* **Conclusión Propuesta por la IA:**  
  > *"El precio fijado a una película determina de manera directa su rentabilidad y tasa de recupero, por lo que aumentar unilateralmente el precio de las películas de \$0.99 a \$4.99 triplicará la velocidad de amortización del catálogo."*
* **Cómo detectamos el error y criterio aplicado:**  
  1. *Correlación no implica causalidad:* Nunca se observó el contrafactual (qué ocurre con la demanda de un mismo título al modificar su tarifa).
  2. *Variables omitidas:* Tanto variables presentes en los propios datos (`inventory_count`, que explica ~86% de la varianza de `rental_count` con $r = 0.929$) como atributos comerciales no modelados (popularidad, género, elenco o criterio original de fijación de tarifa) confunden la relación.
  3. *Corrección aplicada:* Se reescribieron los hallazgos y decisiones del informe final en total coherencia con esta crítica: en lugar de eliminar unilateralmente el estrato de \$0.99 o proyectar ingresos sin evidencia sobre títulos sin stock, se proponen **experimentos controlados (pruebas piloto A/B)** y auditorías de reposición antes de cambios masivos de tarifario.

---

### Caso 3: Propuesta de Eliminar Casos de Borde (Outliers Superiores y Títulos con Ingreso Cero)
* **Conclusión Propuesta por la IA:**  
  > *"Para normalizar la distribución y mejorar $R^2$, se recomienda descartar las 42 películas con `total_revenue = 0` por constituir registros vacíos y truncar los 11 outliers superiores ($>\$181.80$) por considerarlos ruido estadístico."*
* **Cómo detectamos el error y criterio aplicado:**  
  1. Las 42 películas sin recaudación son títulos reales sin copias físicas (`inventory_count = 0`); eliminarlas ocultaría el 4.2% del catálogo.
  2. Los 11 outliers superiores son los *blockbusters* legítimos de mayor facturación (*TELEGRAPH VOYAGE*, \$231.73).
  3. *Corrección aplicada:* Se conservaron las 1.000 filas, segregando las 42 películas sin inventario mediante la bandera `sin_stock` y evitando proyectar demanda inobservada sobre ellas.

---

## 5. Reflexión Final sobre la Utilización de IA como Agente de Ingeniería

El uso de un agente integrado en el entorno aceleró la exploración y modularización del código, pero demostró que **la supervisión técnica humana es insustituible**: sin auditoría crítica sobre los archivos reales y los límites estadísticos de los datos, la IA tiende a introducir supuestos causales no sostenidos, consultas no portables o explicaciones plausibles pero falsas frente al esquema real.

---
**Equipo 6 — ISNSLBV 2026**  
Agustín Bugnoni — Lorenzo Zárate
