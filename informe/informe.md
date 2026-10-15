# Informe Final de Conclusiones — Trabajo Práctico 2
**Materia:** Seminario de Actualización | **Docente:** Jorge Insfran  
**Unidad 5:** Introducción a Data Analytics e Ingeniería de Datos  
**Equipo:** 6 | **Integrantes:** Agustin Bugnoni, Lorenzo Zárate  
**Variante Asignada:** Variante 6 — Precios, recupero y rentabilidad del catálogo  

---

## 1. Pregunta de Negocio y Abordaje Metodológico

### Pregunta de Negocio Asignada
> *¿Cada película recupera lo que costó reponerla? ¿El precio de alquiler tiene relación con la demanda?*

### Abordaje Metodológico
Para responder a esta pregunta, se articuló un flujo de trabajo integral entre **Microsoft SQL Server** y **Python (Pandas, NumPy, Matplotlib, Seaborn)**, dividido en tres ejes analíticos fundamentales:

1. **Evaluación de la Elasticidad y Sensibilidad Precio-Demanda:**
   Se analizó la relación entre la tarifa unitaria de alquiler (`rental_rate`) y el volumen físico de demanda (`rental_count`). Mediante el cálculo del coeficiente de correlación lineal de Pearson y Spearman, complementado con diagramas de dispersión de burbujas ponderados por recaudación acumulada (`total_revenue`), se contrastó la hipótesis económica tradicional de demanda decreciente frente a las particularidades de consumo del videoclub.
2. **Análisis Financiero de Recupero Unitario y Amortización por Título:**
   Se modeló la rentabilidad a nivel lote de inventario por título cinematográfico, contrastando el ingreso bruto generado contra el costo total de reposición de las copias físicas adquiridas:
   $$\text{costo\_inventario\_total} = \text{inventory\_count} \times \text{replacement\_cost}$$
   $$\text{ratio\_recupero} = \frac{\text{total\_revenue}}{\text{costo\_inventario\_total}}$$
   Se definió el umbral crítico de **Break-Even** en $1.0\times$ (amortización completa de la inversión). Adicionalmente, se calculó la exigencia física de rotación para cada película:
   $$\text{breakeven\_alquileres} = \left\lceil \frac{\text{replacement\_cost}}{\text{rental\_rate}} \right\rceil$$
3. **Costo de Oportunidad y Eficiencia del Catálogo:**
   Se identificó el impacto comercial de los títulos presentes en el catálogo pero desprovistos de stock físico (`inventory_count = 0`), evaluando su potencial de monetización desaprovechado.

---

## 2. Decisiones de Diseño Técnico

### 2.1 Reparto de Trabajo entre SQL Server y Python
Siguiendo las buenas prácticas de arquitectura de datos (Unidad 5), se delimitó estrictamente qué resuelve el motor de base de datos y qué resuelve el cliente de análisis:

* **En el Motor de Base de Datos (SQL Server):**
  * **Resolución de Joins Complejos:** Se procesó la cadena relacional canónica `pelicula` $\rightarrow$ `inventario` $\rightarrow$ `alquiler` $\rightarrow$ `pago`.
  * **Preservación Exhaustiva del Catálogo (`LEFT JOIN`):** Se evitó terminantemente el uso de `INNER JOIN`. En Sakila existen 42 títulos sin copias en inventario; un `INNER JOIN` los habría descartado silenciosamente. El `LEFT JOIN` preserva las 1.000 películas del universo catalogado.
  * **Agregaciones Pesadas en Origen:** Conteo de inventario (`COUNT(DISTINCT inventory_id)`), conteo de transacciones (`COUNT(rental_id)`) y suma de recaudación (`ISNULL(SUM(amount), 0.0)`). Esto evitó traficar más de 32.000 registros crudos por la red hacia la memoria de Python.
* **En el Cliente de Análisis (Python / Pandas):**
  * **Cálculo de Métricas Derivadas Vectorizadas:** Operaciones de ratios y umbrales con NumPy (`np.where`, `np.select`, `np.ceil`). Quedó prohibido el uso de iteraciones con bucles `for` o `iterrows()`, penalizadas por ineficiencia algorítmica.
  * **Manejo Seguro de Casos de Borde:** Tratamiento condicional de divisiones por cero para las películas sin copias (`inventory_count = 0`), asignándoles ingreso por copia de $0.00 y ratio de recupero de $0.00$.
  * **Enriquecimiento Multi-Fuente:** Cruce mediante `merge` con archivos planos de clasificación comercial.

### 2.2 Elección del Controlador de Conexión (`pyodbc`)
Se seleccionó **`pyodbc`** sobre SQLAlchemy en lugar de conectores alternativos por tres motivos:
1. **Estándar Corporativo y Compatibilidad ODBC:** Interactúa de forma nativa con el controlador oficial *Microsoft ODBC Driver 18 for SQL Server*, asegurando máxima fidelidad en tipos de datos migrados (`DATETIME2`, `DECIMAL(5,2)` monetario exacto).
2. **Soporte de Inserción Masiva Optimizada:** Habilita el parámetro `fast_executemany=True` para acelerar drásticamente los tiempos de carga en el pipeline ETL.
3. **Seguridad y Cero Credenciales en Código:** La conexión se establece parametrizada consumiendo variables de entorno locales protegidas (`.env`), garantizando que ninguna contraseña ni host quede expuesto en el repositorio.

### 2.3 Portabilidad Total mediante `esquema.py`
Para cumplir la exigencia de desacoplamiento (evaluada en la defensa oral), no se escribieron nombres de tablas ni columnas en español de forma rígida en el código. El módulo `esquema.py` actúa como diccionario de traducción canónico bidireccional. La consulta de extracción se construye mediante `generar_query_conjunto_trabajo()`, garantizando que cambiando únicamente `esquema.py`, el proyecto se ejecuta sin modificaciones contra la base migrada por cualquier otro equipo.

### 2.4 Criterios de Limpieza y Estrategia de Carga Idempotente (ETL)
* **Criterios de Limpieza:** Se aplicaron aserciones estrictas de calidad (`validar_calidad`) previas a la transformación.
* **Estrategia de Carga Idempotente:** En el pipeline ETL (`pipeline_tp2.py`), se implementó la estrategia transaccional *Truncate-and-Load* atómica dentro de `with engine.begin() as connection:`. Previo a la inserción masiva (`to_sql` con `if_exists='append'`), se ejecuta un `DELETE FROM dbo.TP2_RecuperoPorPelicula`. Si ocurre cualquier error, la transacción revierte automáticamente (`ROLLBACK`). Ejecutar el pipeline consecutivas veces garantiza exactamente 1.000 filas finales verificadas con `SELECT COUNT(*)`, erradicando el riesgo de duplicación.

---

## 3. Síntesis del Diagnóstico de Calidad de Datos

El perfilado sistemático sobre el conjunto de trabajo de 1.000 películas evaluó las 6 dimensiones de calidad de la Unidad 5:

| Dimensión | Evaluación en el Dataset | Impacto sobre las Conclusiones |
| :--- | :--- | :--- |
| **Completitud** | 100% completo (0 valores faltantes en todas las columnas). | Las ausencias transaccionales fueron absorbidas en origen con `ISNULL(..., 0.0)`. |
| **Unicidad** | 1.000 registros únicos sobre la clave primaria de negocio `film_id`. | Garantiza que ninguna película esté duplicada ni subrepresentada. |
| **Validez** | Cumplimiento total de reglas de negocio: `rental_rate > 0`, `replacement_cost > rental_rate`. | No existen anomalías de formato ni inconsistencias lógicas en el dominio. |
| **Consistencia** | La variable categórica `rating` presenta exactamente 5 categorías canónicas. | No se requirió limpieza ortográfica ni unificación de texto. |
| **Exactitud** | Reconciliación al 100% entre agregaciones T-SQL en el motor y Pandas en Python. | Certeza matemática plena sobre la veracidad de los datos analizados. |
| **Oportunidad** | Cobertura temporal histórica completa de la actividad transaccional del videoclub. | Apto para evaluar la amortización histórica del catálogo. |

### Hallazgo Crítico de Calidad: Cardinalidad de Precios
La variable `rental_rate` solo asume **3 valores discretos**: **\$0.99 (34.1%)**, **\$2.99 (32.3%)** y **\$4.99 (33.6%)**.  
*Impacto metodológico:* **Invalida el cálculo de elasticidades continuas clásicas.** No es posible trazar una curva de demanda continua ni calcular derivadas marginales. La realidad de los datos condiciona a formular el análisis como una **comparación inter-estratos** entre tres políticas tarifarias discretas.

### Tratamiento Justificado de Outliers (Regla IQR de Tukey sobre Ingresos)
Se detectaron 11 películas consideradas *outliers superiores* con ingresos superiores al umbral estadístico (\$181.80), lideradas por *TELEGRAPH VOYAGE* (\$231.73).  
*Decisión justificada:* **NO SE ELIMINAN.** En analítica de negocios, los valores atípicos superiores representan los títulos *blockbuster* de alta rotación legítima. Descartarlos por motivos puramente estadísticos mutilaría los casos de mayor éxito comercial del negocio, sesgando gravemente las conclusiones de rentabilidad.  
Asimismo, las 42 películas con ingreso \$0.00 se conservaron etiquetadas bajo la categoría *"Sin inventario"*.

---

## 4. Hallazgos Narrativos y Toma de Decisiones

### Hallazgo 1 — Inelasticidad Perfecta: El precio no explica la demanda
![Gráfico 1 — Dispersión Precio vs Demanda](../graficos/g1_precio_vs_demanda_burbuja.png)

* **Qué se observa:** Los tres estratos de precio presentan promedios y distribuciones de demanda física prácticamente idénticos:
  $$\bar{Q}_{\$0.99} = 17.3 \text{ alquileres} \quad|\quad \bar{Q}_{\$2.99} = 16.4 \text{ alquileres} \quad|\quad \bar{Q}_{\$4.99} = 16.5 \text{ alquileres}$$
  El coeficiente de correlación lineal de Pearson entre tarifa y cantidad de alquileres es nulo:
  $$r = -0.053 \quad (p = 0.100 > 0.05)$$
* **Qué lo explica:** La demanda de alquiler de películas es inelástica respecto al precio unitario dentro del rango de \$0.99 a \$4.99. La decisión del cliente de alquilar un título está motivada por factores no tarifarios (género, actores, popularidad, exhibición destacada o disponibilidad en estantería). Los clientes no alquilan más copias por pagar \$0.99 ni se inhiben de consumir por abonar \$4.99.
* **Qué decisión de negocio habilita:** **Reestructurar de inmediato la política tarifaria eliminando el piso de \$0.99.** El catálogo debe migrarse hacia tarifas de \$2.99 y \$4.99, dado que no existe riesgo empírico de contracción en el volumen de demanda.

---

### Hallazgo 2 — El precio define la velocidad de recupero, no el volumen (Lección de Anscombe)
![Gráfico 2 — Boxplot Ratio de Recupero](../graficos/g2_boxplot_ratio_recupero.png)
![Gráfico 3 — Cuarteto de Anscombe y Pendientes de Amortización](../graficos/g3_anscombe_recupero_por_precio.png)

* **Qué se observa:** Aunque los tres grupos rotan a una velocidad similar (~3.5 alquileres por copia física), la eficiencia de amortización presenta un desacople estructural extremo:
  * A **\$4.99**, el break-even promedio exige solo **4.6 alquileres/copia**, alcanzando una **tasa de éxito de recupero del 58.4%** con una pendiente de retorno de **$+0.335\times$ por alquiler**.
  * A **\$0.99**, el break-even exige **21.4 alquileres/copia**, y la tasa de éxito colapsa al **3.4%** con una pendiente de apenas **$+0.151\times$**.
* **Qué lo explica:** El costo de reposición promedio de los títulos es homogéneo en todo el catálogo (~$20 por copia), independientemente de la tarifa asignada. Por lo tanto, fijar una tarifa de \$0.99 impone una barrera física insalvable: una película necesitaría circular más de 20 veces por copia para amortizarse, superando el ciclo de vida útil del soporte físico antes de su desgaste.
* **Qué decisión de negocio habilita:** **Prohibir la adquisición de nuevo inventario para títulos tarifados a \$0.99.** Toda compra futura de copias físicas debe asignarse exclusivamente a títulos listados a \$2.99 o \$4.99 para garantizar la viabilidad del capital invertido.

---

### Hallazgo 3 — El 4.2% del catálogo sin inventario representa un costo de oportunidad inmediato
* **Qué se observa:** Existen **42 películas registradas en catálogo con 0 copias en inventario** (`inventory_count = 0`), acumulando \$0.00 de ingresos.
* **Qué lo explica:** Su recaudación nula no responde al rechazo del consumidor ni a obsolescencia temática, sino a un quiebre estructural de stock: nunca estuvieron disponibles físicamente en las sucursales.
* **Qué decisión de negocio habilita:** **Aprobar la compra de un lote inicial de 3 a 4 copias para cada uno de los 42 títulos faltantes, listándolos a tarifa premium de \$4.99.** Dado el comportamiento inelástico demostrado en el Hallazgo 1, estos títulos generarán una recaudación estimada de ~$60 a $70 por película, amortizando su inversión inicial en menos de 5 alquileres por copia.

---

## 5. Limitaciones del Análisis

En cumplimiento con los estándares de rigor y honestidad analítica exigidos por la cátedra (Unidad 5), se reconocen las siguientes limitaciones intrínsecas del conjunto de datos y del modelo:

1. **Incapacidad de Modelar Curvas de Demanda Continuas:**
   Como se demostró en el diagnóstico de calidad, la tarifa de alquiler toma únicamente 3 valores fijos discretos (\$0.99, \$2.99, \$4.99). Por ende, **está metodológicamente prohibido afirmar conclusiones sobre elasticidad-precio continua**. No se puede estimar qué ocurriría si se fijasen precios intermedios (\$1.50, \$3.50) o superiores (\$6.99).
2. **Presencia de Variables Omitidas Críticas:**
   El modelo relacional Sakila no registra variables cualitativas cruciales del consumidor: preferencias de género, elenco de actores, campañas publicitarias de la época, ubicación geográfica de la tienda, ni visibilidad física en la estantería del local. No se puede afirmar que el precio *cause* la demanda ni descartar factores de confusión (*confounding factors*).
3. **Omisión de Costos Operativos y Logísticos:**
   La métrica de recupero contempla exclusivamente el costo de reposición física del disco (`replacement_cost`). No se computan los costos de almacenamiento en tienda, salarios del personal, comisiones ni deterioro por daño físico de las cintas/discos. El ratio de recupero representa un margen de amortización bruto, no el beneficio contable neto de la empresa.
4. **Ausencia de Dinámica Temporal y Canibalización:**
   El dataset consolida un corte histórico acumulado sin distinguir la estacionalidad de los alquileres ni registrar el efecto de canibalización entre títulos de estreno y títulos de catálogo antiguo.

---

## 6. Dificultades Encontradas y Soluciones Implementadas

1. **Configuración Heterogénea de Controladores ODBC en Entornos Linux/Windows:**
   * *Problema:* Al ejecutar la conexión en entornos Linux mediante `pyodbc`, surgían errores de enlace dinámico por la ausencia de las librerías compartidas de `unixodbc`.
   * *Solución:* Se estandarizó la resolución del entorno documentando en el `README.md` la instalación de `msodbcsql18` y la configuración de `ODBC Driver 18 for SQL Server` con `TrustServerCertificate=yes` y `autocommit=True`.
2. **Preservación de Títulos sin Inventario y División por Cero:**
   * *Problema:* Al calcular las métricas unitarias (`total_revenue / inventory_count`), las 42 películas con stock cero generaban indeterminaciones matemáticas (`ZeroDivisionError` o `NaN`/`inf`).
   * *Solución:* Se descartó cualquier filtrado prematuro y se implementó lógica condicional vectorizada con `numpy.where(inventory_count > 0, ..., 0.0)`, etiquetándolas rigurosamente como *"Sin inventario"*.
3. **Garantía de Idempotencia en la Carga Masiva:**
   * *Problema:* La instrucción `TRUNCATE TABLE` podía fallar ante restricciones de claves foráneas o permisos en esquemas corporativos, mientras que inserciones consecutivas duplicaban el volumen de filas.
   * *Solución:* Se adoptó una transacción atómica controlada (`DELETE FROM` transaccional seguido de `to_sql` con verificación poscarga de conteo de filas y unicidad de clave primaria), asegurando que cualquier fallo revierta el estado sin dejar datos corruptos.
4. **Portabilidad de Esquemas para la Defensa Oral:**
   * *Problema:* El acoplamiento de nombres traducidos al español impedía que el código corriera en bases de otros equipos.
   * *Solución:* Se diseñó el módulo dinámico `esquema.py`, abstrayendo la traducción de identificadores y parametrizando las consultas de manera segura.

---
**Trabajo Práctico 2 — Seminario de Actualización 2026**  
*Equipo 6: Precios, recupero y rentabilidad del catálogo.*
