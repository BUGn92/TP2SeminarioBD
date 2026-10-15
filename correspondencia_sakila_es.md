# Correspondencia entre Sakila y `sakila_es`

La tabla compara los nombres canónicos de Sakila con los nombres físicos definidos
en `sakila_es`. Las columnas se listan como **nombre canónico → nombre local**.
Se incluyen las 15 tablas presentes en el esquema SQL del proyecto.

| Tabla Sakila | Tabla `sakila_es` | Correspondencia de columnas |
|---|---|---|
| `actor` | `actor` | `actor_id` → `id_actor`; `first_name` → `nombre`; `last_name` → `apellido`; `last_update` → `ultima_actualizacion` |
| `category` | `categoria` | `category_id` → `id_categoria`; `name` → `nombre`; `last_update` → `ultima_actualizacion` |
| `language` | `idioma` | `language_id` → `id_idioma`; `name` → `nombre`; `last_update` → `ultima_actualizacion` |
| `country` | `pais` | `country_id` → `id_pais`; `country` → `pais`; `last_update` → `ultima_actualizacion` |
| `city` | `ciudad` | `city_id` → `id_ciudad`; `city` → `ciudad`; `country_id` → `id_pais`; `last_update` → `ultima_actualizacion` |
| `address` | `direccion` | `address_id` → `id_direccion`; `address` → `direccion`; `address2` → `direccion2`; `district` → `distrito`; `city_id` → `id_ciudad`; `postal_code` → `codigo_postal`; `phone` → `telefono`; `last_update` → `ultima_actualizacion` |
| `film` | `pelicula` | `film_id` → `id_pelicula`; `title` → `titulo`; `description` → `descripcion`; `release_year` → `anio_lanzamiento`; `language_id` → `id_idioma`; `original_language_id` → `id_idioma_original`; `rental_duration` → `duracion_alquiler`; `rental_rate` → `tarifa_alquiler`; `length` → `duracion`; `replacement_cost` → `costo_reemplazo`; `rating` → `clasificacion`; `special_features` → `caracteristicas_especiales`; `last_update` → `ultima_actualizacion` |
| `store` | `tienda` | `store_id` → `id_tienda`; `manager_staff_id` → `id_gerente_personal`; `address_id` → `id_direccion`; `last_update` → `ultima_actualizacion` |
| `staff` | `personal` | `staff_id` → `id_personal`; `first_name` → `nombre`; `last_name` → `apellido`; `address_id` → `id_direccion`; `email` → `correo_electronico`; `store_id` → `id_tienda`; `active` → `activo`; `username` → `nombre_usuario`; `password` → `contrasena`; `last_update` → `ultima_actualizacion`; `picture` → `foto` |
| `customer` | `cliente` | `customer_id` → `id_cliente`; `store_id` → `id_tienda`; `first_name` → `nombre`; `last_name` → `apellido`; `email` → `correo_electronico`; `address_id` → `id_direccion`; `active` → `activo`; `create_date` → `fecha_creacion`; `last_update` → `ultima_actualizacion` |
| `inventory` | `inventario` | `inventory_id` → `id_inventario`; `film_id` → `id_pelicula`; `store_id` → `id_tienda`; `last_update` → `ultima_actualizacion` |
| `rental` | `alquiler` | `rental_id` → `id_alquiler`; `rental_date` → `fecha_alquiler`; `inventory_id` → `id_inventario`; `customer_id` → `id_cliente`; `return_date` → `fecha_devolucion`; `staff_id` → `id_personal`; `last_update` → `ultima_actualizacion` |
| `payment` | `pago` | `payment_id` → `id_pago`; `customer_id` → `id_cliente`; `staff_id` → `id_personal`; `rental_id` → `id_alquiler`; `amount` → `monto`; `payment_date` → `fecha_pago`; `last_update` → `ultima_actualizacion` |
| `film_actor` | `pelicula_actor` | `actor_id` → `id_actor`; `film_id` → `id_pelicula`; `last_update` → `ultima_actualizacion` |
| `film_category` | `pelicula_categoria` | `film_id` → `id_pelicula`; `category_id` → `id_categoria`; `last_update` → `ultima_actualizacion` |

## Diferencias de cobertura

La tabla canónica auxiliar `film_text` no está creada en el esquema local; sus
campos, por lo tanto, no tienen correspondencia física en `sakila_es`. El resto
de las tablas y columnas listadas se cotejaron con `sakila-schemaSQLserver.sql`.

El diccionario programático de la misma correspondencia se mantiene en
[`esquema.py`](./esquema.py).
