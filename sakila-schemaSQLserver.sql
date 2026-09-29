--creacion base de datos
CREATE DATABASE [sakila_es];
GO
USE [sakila_es];
GO

-------------------------------------
--TABLAS BASE
-------------------------------------
--tabla actor
CREATE TABLE [actor] (
  [id_actor] INT IDENTITY(1,1) NOT NULL,
  [nombre] VARCHAR(45) NOT NULL,
  [apellido] VARCHAR(45) NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_actor] PRIMARY KEY CLUSTERED ([id_actor])
);
GO

--tabla categoria
CREATE TABLE [categoria] (
  [id_categoria] INT IDENTITY(1,1) NOT NULL, 
  [nombre] VARCHAR(25) NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_categoria] PRIMARY KEY CLUSTERED ([id_categoria])
);
GO

--tabla idioma
CREATE TABLE [idioma] (
  [id_idioma] INT IDENTITY(1,1) NOT NULL,
  [nombre] CHAR(20) NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_idioma] PRIMARY KEY CLUSTERED ([id_idioma])
);
GO

----------------------------------------
--TABLAS GEOGRAFICAS
----------------------------------------
--tabla pais
CREATE TABLE [pais] (
  [id_pais] INT IDENTITY(1,1) NOT NULL,
  [pais] VARCHAR(50) NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_pais] PRIMARY KEY CLUSTERED ([id_pais])
);
GO

--tabla ciudad
CREATE TABLE [ciudad] (
  [id_ciudad] INT IDENTITY(1,1) NOT NULL,
  [ciudad] VARCHAR(50) NOT NULL,
  [id_pais] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_ciudad] PRIMARY KEY CLUSTERED ([id_ciudad]),
  CONSTRAINT [FK_ciudad_pais] FOREIGN KEY ([id_pais]) REFERENCES [pais] ([id_pais])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla direccion
CREATE TABLE [direccion] (
  [id_direccion] INT IDENTITY(1,1) NOT NULL,
  [direccion] VARCHAR(50) NOT NULL,
  [direccion2] VARCHAR(50) NULL,
  [distrito] VARCHAR(20) NOT NULL,
  [id_ciudad] INT NOT NULL,
  [codigo_postal] VARCHAR(10) NULL,
  [telefono] VARCHAR(20) NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_direccion] PRIMARY KEY CLUSTERED ([id_direccion]),
  CONSTRAINT [FK_direccion_ciudad] FOREIGN KEY ([id_ciudad]) REFERENCES [ciudad] ([id_ciudad])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla pelicula
CREATE TABLE [pelicula] (
  [id_pelicula] INT IDENTITY(1,1) NOT NULL,
  [titulo] VARCHAR(255) NOT NULL,
  [descripcion] VARCHAR(MAX) NULL, -- Reemplaza TEXT/BLOB de MySQL
  [anio_lanzamiento] INT NULL,     -- Reemplaza YEAR de MySQL
  [id_idioma] INT NOT NULL,
  [id_idioma_original] INT NULL,
  [duracion_alquiler] INT NOT NULL DEFAULT 3,
  [tarifa_alquiler] DECIMAL(4,2) NOT NULL DEFAULT 4.99,
  [duracion] INT NULL,
  [costo_reemplazo] DECIMAL(5,2) NOT NULL DEFAULT 19.99,
  [clasificacion] VARCHAR(10) NULL DEFAULT 'G', -- Reemplaza ENUM
  [caracteristicas_especiales] VARCHAR(255) NULL, -- Reemplaza SET
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_pelicula] PRIMARY KEY CLUSTERED ([id_pelicula]),
  
  -- Claves Foráneas referenciando a la tabla [idioma] creada en el paso anterior
  CONSTRAINT [FK_pelicula_idioma] FOREIGN KEY ([id_idioma]) REFERENCES [idioma] ([id_idioma])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_pelicula_idioma_original] FOREIGN KEY ([id_idioma_original]) REFERENCES [idioma] ([id_idioma])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
    
  -- Restricción CHECK para simular el comportamiento de ENUM de MySQL
  CONSTRAINT [CHK_pelicula_clasificacion] CHECK (
      [clasificacion] IN ('G', 'PG', 'PG-13', 'R', 'NC-17')
  )
);
GO

----------------------
--ESTRUCTURA NEGOCIO
-- -------------------
--tabla tienda
CREATE TABLE [tienda] (
  [id_tienda] INT IDENTITY(1,1) NOT NULL,
  [id_gerente_personal] INT NOT NULL, -- Se relacionará con la tabla personal más adelante
  [id_direccion] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_tienda] PRIMARY KEY CLUSTERED ([id_tienda]),
  CONSTRAINT [FK_tienda_direccion] FOREIGN KEY ([id_direccion]) REFERENCES [direccion] ([id_direccion])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla personal
CREATE TABLE [personal] (
  [id_personal] INT IDENTITY(1,1) NOT NULL,
  [nombre] VARCHAR(45) NOT NULL,
  [apellido] VARCHAR(45) NOT NULL,
  [id_direccion] INT NOT NULL,
  [correo_electronico] VARCHAR(50) NULL,
  [id_tienda] INT NOT NULL,
  [activo] BIT NOT NULL DEFAULT 1, -- Reemplaza TINYINT(1) / BOOLEAN
  [nombre_usuario] VARCHAR(16) NOT NULL,
  [contrasena] VARCHAR(40) NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_personal] PRIMARY KEY CLUSTERED ([id_personal]),
  CONSTRAINT [FK_personal_direccion] FOREIGN KEY ([id_direccion]) REFERENCES [direccion] ([id_direccion])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_personal_tienda] FOREIGN KEY ([id_tienda]) REFERENCES [tienda] ([id_tienda])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--clave foranea pendiente a la tabla tienda
ALTER TABLE [tienda]
  ADD CONSTRAINT [FK_tienda_personal] FOREIGN KEY ([id_gerente_personal]) REFERENCES [personal] ([id_personal])
  ON DELETE NO ACTION ON UPDATE NO ACTION;
GO

--tabla cliente
CREATE TABLE [cliente] (
  [id_cliente] INT IDENTITY(1,1) NOT NULL,
  [id_tienda] INT NOT NULL,
  [nombre] VARCHAR(45) NOT NULL,
  [apellido] VARCHAR(45) NOT NULL,
  [correo_electronico] VARCHAR(50) NULL,
  [id_direccion] INT NOT NULL,
  [activo] BIT NOT NULL DEFAULT 1, -- Reemplaza TINYINT(1) / BOOLEAN
  [fecha_creacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_cliente] PRIMARY KEY CLUSTERED ([id_cliente]),
  CONSTRAINT [FK_cliente_tienda] FOREIGN KEY ([id_tienda]) REFERENCES [tienda] ([id_tienda])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_cliente_direccion] FOREIGN KEY ([id_direccion]) REFERENCES [direccion] ([id_direccion])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla inventario
CREATE TABLE [inventario] (
  [id_inventario] INT IDENTITY(1,1) NOT NULL,
  [id_pelicula] INT NOT NULL,
  [id_tienda] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_inventario] PRIMARY KEY CLUSTERED ([id_inventario]),
  CONSTRAINT [FK_inventario_tienda] FOREIGN KEY ([id_tienda]) REFERENCES [tienda] ([id_tienda])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_inventario_pelicula] FOREIGN KEY ([id_pelicula]) REFERENCES [pelicula] ([id_pelicula])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla alquiler
CREATE TABLE [alquiler] (
  [id_alquiler] INT IDENTITY(1,1) NOT NULL,
  [fecha_alquiler] DATETIME2 NOT NULL,
  [id_inventario] INT NOT NULL,
  [id_cliente] INT NOT NULL,
  [fecha_devolucion] DATETIME2 NULL,
  [id_personal] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_alquiler] PRIMARY KEY CLUSTERED ([id_alquiler]),
  CONSTRAINT [FK_alquiler_personal] FOREIGN KEY ([id_personal]) REFERENCES [personal] ([id_personal])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_alquiler_inventario] FOREIGN KEY ([id_inventario]) REFERENCES [inventario] ([id_inventario])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_alquiler_cliente] FOREIGN KEY ([id_cliente]) REFERENCES [cliente] ([id_cliente])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--tabla pago
CREATE TABLE [pago] (
  [id_pago] INT IDENTITY(1,1) NOT NULL,
  [id_cliente] INT NOT NULL,
  [id_personal] INT NOT NULL,
  [id_alquiler] INT NULL,
  [monto] DECIMAL(5,2) NOT NULL,
  [fecha_pago] DATETIME2 NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_pago] PRIMARY KEY CLUSTERED ([id_pago]),
  CONSTRAINT [FK_pago_alquiler] FOREIGN KEY ([id_alquiler]) REFERENCES [alquiler] ([id_alquiler])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_pago_cliente] FOREIGN KEY ([id_cliente]) REFERENCES [cliente] ([id_cliente])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_pago_personal] FOREIGN KEY ([id_personal]) REFERENCES [personal] ([id_personal])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

--En el esquema original de Sakila en MySQL, esta columna se utiliza para guardar la foto de perfil del empleado y su tipo de dato original es un BLOB (Binary Large Object).
ALTER TABLE [personal]
ADD [foto] VARBINARY(MAX) NULL;
GO

-- -----------------------------------------------------
-- Tabla [pelicula_categoria] (Original: film_category)
-- -----------------------------------------------------
CREATE TABLE [pelicula_categoria] (
  [id_pelicula] INT NOT NULL,
  [id_categoria] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  
  -- Clave Primaria Compuesta
  CONSTRAINT [PK_pelicula_categoria] PRIMARY KEY CLUSTERED ([id_pelicula], [id_categoria]),
  
  -- Claves Foráneas con prevención de cascadas cíclicas
  CONSTRAINT [FK_pelicula_categoria_pelicula] FOREIGN KEY ([id_pelicula]) REFERENCES [pelicula] ([id_pelicula])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_pelicula_categoria_categoria] FOREIGN KEY ([id_categoria]) REFERENCES [categoria] ([id_categoria])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO
-- -----------------------------------------------------
-- Tabla [pelicula_actor] (Original: film_actor)
-- -----------------------------------------------------
CREATE TABLE [pelicula_actor] (
  [id_actor] INT NOT NULL,
  [id_pelicula] INT NOT NULL,
  [ultima_actualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
  CONSTRAINT [PK_pelicula_actor] PRIMARY KEY CLUSTERED ([id_actor], [id_pelicula]),
  CONSTRAINT [FK_pelicula_actor_actor] FOREIGN KEY ([id_actor]) REFERENCES [actor] ([id_actor])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [FK_pelicula_actor_pelicula] FOREIGN KEY ([id_pelicula]) REFERENCES [pelicula] ([id_pelicula])
    ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

