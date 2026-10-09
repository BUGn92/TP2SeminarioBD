# Análisis y Pipeline de Datos sobre Sakila (SQL Server + Python)

Este repositorio contiene el flujo completo de extracción, perfilado de calidad, análisis y pipeline ETL automatizado sobre la base de datos **Sakila** migrada a **Microsoft SQL Server**.

---

## Requisitos Previos

* **Python 3.10** o superior.
* Instancia accesible de **Microsoft SQL Server** con la base de datos `sakila_es` restaurada.
* **Driver ODBC de Microsoft para SQL Server**:
  * `pyodbc` requiere que el sistema operativo disponga del controlador ODBC correspondiente.

---

## Instalación de Dependencias del Sistema (ODBC)

Antes de instalar las dependencias de Python, asegurarse de contar con el driver en el sistema operativo:

### En Linux (Ubuntu / Debian / Mint)
1. **Instalar la biblioteca base de ODBC y utilidades (unixODBC + odbcinst):**
   ```bash
   sudo apt update
   sudo apt install -y unixodbc unixodbc-dev odbcinst
   ```
   *(Este paquete provee `libodbc.so.2` requerido por `pyodbc` y la herramienta `odbcinst` de diagnóstico).*

2. **Instalar el controlador oficial de Microsoft (ODBC Driver 18 for SQL Server):**
   ```bash
   # Importar claves y repositorio de Microsoft
   curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
   curl -fsSL https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

   # Instalar el driver
   sudo apt update
   sudo ACCEPT_EULA=Y apt install -y msodbcsql18
   ```

3. **Verificar los controladores instalados:**
   ```bash
   odbcinst -q -d
   ```
   *(Debería listar `[ODBC Driver 18 for SQL Server]` confirmando que el sistema lo reconoce).*

### En Windows
1. Si ya contás con **SQL Server Management Studio (SSMS)** instalado, el controlador ODBC suele encontrarse disponible por defecto.
2. Si necesitás instalarlo manualmente, podés descargarlo desde el sitio oficial de Microsoft:
   * **[Descargar Microsoft ODBC Driver 18 for SQL Server (x64)](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server)**.

---

## Puesta en Marcha del Proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/BUGn92/TP2SeminarioBD.git
cd TP2SeminarioBD
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
  *(Si PowerShell restringe la ejecución de scripts, habilitar temporalmente con: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **En Windows (CMD / Símbolo del sistema):**
  ```cmd
  python -m venv venv_tp2
  venv_tp2\Scripts\activate.bat
  ```

### 3. Instalar las dependencias de Python
Con el entorno virtual activado (se observará `(venv_tp2)` en el prompt de la terminal):
```bash
pip install -r requirements.txt
```

### 4. Registrar el kernel de Jupyter
Este paso es obligatorio para que el notebook reconozca el entorno virtual `venv_tp2`. Sin él, Jupyter no encontrará el kernel y no podrá ejecutar las celdas:
```bash
python -m ipykernel install --user --name=venv_tp2 --display-name "venv_tp2"
```
*(Solo es necesario hacerlo una vez por entorno virtual. Si más adelante creás un nuevo venv, repetir este comando con ese entorno activado).*

### 5. Configurar las credenciales de conexión (`.env`)
Las credenciales de acceso a la base de datos se configuran mediante variables de entorno locales:

1. Crear el archivo `.env` a partir de la plantilla:
   * **Linux / macOS:** `cp .env.example .env`
   * **Windows:** `copy .env.example .env`

2. Abrir `.env` y completar los parámetros de tu instancia local:
   ```ini
   DB_SERVER=localhost
   DB_PORT=1433
   DB_NAME=sakila_es
   DB_USER=sa
   DB_PASSWORD=TuPasswordSegura
   DB_DRIVER=ODBC Driver 18 for SQL Server
   DB_TRUSTED_CONNECTION=no
   DB_TRUST_SERVER_CERTIFICATE=yes
   ```
   *(Si estás en Windows y utilizás autenticación integrada con tu cuenta de usuario, configurar `DB_TRUSTED_CONNECTION=yes`).*

   Para una instancia con nombre, por ejemplo `LOLO_PC\SQLEXPRESS`, usar ese valor en `DB_SERVER` y dejar `DB_PORT` vacío. En SQL Server Configuration Manager, habilitar **TCP/IP** para esa instancia y reiniciar el servicio de SQL Server. Si la instancia usa un puerto dinámico, iniciar también el servicio **SQL Server Browser**; alternativamente, asignar un puerto TCP fijo y configurar `DB_SERVER` con el nombre del equipo y `DB_PORT` con ese puerto.

### 6. Verificar la conexión a SQL Server
Ejecutar el script de verificación para validar la conectividad:
```bash
python config_conexion.py
```
Si la configuración es correcta, la consola mostrará:
```text
 Conexión exitosa a SQL Server:
  - Base actual: sakila_es
  - Versión del motor: Microsoft SQL Server ...
```

### 7. Abrir el notebook de análisis
Con el entorno virtual activado y la conexión verificada:
```bash
jupyter notebook notebooks/analisis.ipynb
```
Si preferís Jupyter Lab:
```bash
jupyter lab
```
Una vez abierto el notebook, seleccionar el kernel **`venv_tp2`** en el menú `Kernel → Change Kernel`. Para re-ejecutar el notebook completo de arriba a abajo usar `Kernel → Restart & Run All`.

---

## Estructura del Repositorio

```text
├── README.md               # Instrucciones de instalación y ejecución local
├── requirements.txt        # Dependencias del entorno Python
├── .env.example            # Plantilla pública de variables de entorno
├── config_conexion.py      # Módulo de conexión a SQL Server con SQLAlchemy y pyodbc
├── esquema.py              # Diccionario de mapeo canónico y resolución de consultas
├── sql/
│   ├── reconciliacion.sql  # Script de reconciliación de filas (Actividad 0)
│   └── conjunto_trabajo.sql# Consulta base del conjunto de trabajo (Actividad 1)
├── notebooks/
│   └── analisis.ipynb      # Actividades 1–3: integración SQL-Python, calidad y análisis
├── pipeline/               # (se genera en Actividad 4)
│   ├── pipeline_tp2.py     # Script ETL autónomo e idempotente
│   └── datos/              # Archivo plano complementario del pipeline
├── graficos/               # (se genera en Actividad 3) PNG a 150 DPI
└── informe/                # (se genera en Actividad 5) PDF + anexo IA
```
