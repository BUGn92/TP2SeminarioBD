# TP2 — Del dato al análisis: Data Analytics e Ingeniería de Datos sobre Sakila

**Equipo 6 — Variante asignada:** Precios, recupero y rentabilidad del catálogo  
**Materia:** Seminario de Actualización — Docente: Jorge Insfran  

---

## Requisitos Previos

* **Python 3.10** o superior.
* **Microsoft SQL Server** con la base de datos `sakila_es` restaurada.
* **Driver ODBC para SQL Server**:
  * En Windows: Generalmente viene preinstalado o se instala *ODBC Driver 17/18 for SQL Server*.
  * En Linux: Paquete `msodbcsql17` o `msodbcsql18` junto con `unixodbc-dev`.

---

## Guía de Instalación y Puesta en Marcha

Seguir estos pasos en orden para clonar y preparar el entorno de trabajo:

### 1. Clonar el repositorio y entrar a la carpeta
```bash
git clone <URL_DEL_REPOSITORIO>
cd "tp2 Bugnoni Zarate"
```

### 2. Crear y activar el entorno virtual (`venv_tp2`)

* **En Linux / macOS:**
  ```bash
  python3 -m venv venv_tp2
  source venv_tp2/bin/activate
  ```

* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv_tp2
  .\venv_tp2\Scripts\Activate.ps1
  ```
  *(Si PowerShell bloquea la ejecución de scripts, ejecutar antes: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **En Windows (CMD / Símbolo del sistema):**
  ```cmd
  python -m venv venv_tp2
  venv_tp2\Scripts\activate.bat
  ```

### 3. Instalar las dependencias fijadas
Con el entorno virtual activado (verás `(venv_tp2)` al inicio de la línea de comandos):
```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno (`.env`)
El archivo `.env` contiene credenciales sensibles y **NUNCA debe subirse a Git**.

1. Copiar la plantilla `.env.example` creando el archivo `.env`:
   * En Linux / macOS:
     ```bash
     cp .env.example .env
     ```
   * En Windows (PowerShell / CMD):
     ```cmd
     copy .env.example .env
     ```

2. Abrir `.env` y completar los valores según tu instancia local de SQL Server:
   ```ini
   DB_SERVER=localhost
   DB_PORT=1433
   DB_NAME=sakila_es
   DB_USER=sa
   DB_PASSWORD=TuContraseñaLocal
   DB_DRIVER=ODBC Driver 18 for SQL Server
   DB_TRUSTED_CONNECTION=no
   DB_TRUST_SERVER_CERTIFICATE=yes
   ```
   *(Si estás en Windows y usás autenticación integrada con tu usuario de Windows, poné `DB_TRUSTED_CONNECTION=yes`).*

### 5. Probar la conexión a la base de datos
Ejecutar el script de prueba para validar que Python se comunica correctamente con SQL Server:
```bash
python config_conexion.py
```
Si todo está en orden, verás el mensaje: `Conexión exitosa a SQL Server`.

---

## Estructura del Proyecto

* `config_conexion.py`: Módulo de conexión segura con SQLAlchemy y variables de entorno.
* `esquema.py`: Diccionario canónico de Sakila hacia los nombres en español de `sakila_es`.
* `sql/`: Scripts de reconciliación y armado del conjunto de trabajo.
* `notebooks/`: Notebooks de perfilado, análisis exploratorio y visualización.
* `pipeline/`: Pipeline ETL autónomo e idempotente.
* `graficos/`: Gráficos exportados a 150 DPI.
* `informe/`: Informes técnicos y anexo de trazabilidad de IA.
