-- Base de datos del microservicio Inventario (VM1, Python/FastAPI)
CREATE DATABASE IF NOT EXISTS inventario_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE inventario_db;

CREATE TABLE IF NOT EXISTS productos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    nombre          VARCHAR(150) NOT NULL,
    categoria       VARCHAR(80) NOT NULL,
    unidad_medida   VARCHAR(20) NOT NULL DEFAULT 'unidad',
    stock_actual    INT NOT NULL DEFAULT 0,
    stock_minimo    INT NOT NULL DEFAULT 0,
    precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_productos_categoria (categoria)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    producto_id       INT NOT NULL,
    tipo_movimiento   ENUM('entrada', 'salida', 'ajuste') NOT NULL,
    cantidad          INT NOT NULL,
    fecha_movimiento  DATETIME NOT NULL,
    motivo            VARCHAR(150),
    usuario           VARCHAR(80),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movimientos_producto FOREIGN KEY (producto_id) REFERENCES productos(id),
    INDEX idx_movimientos_producto_id (producto_id),
    INDEX idx_movimientos_fecha (fecha_movimiento)
) ENGINE=InnoDB;

-- El usuario 'bodega' ya existe (creado por el entrypoint via MYSQL_USER /
-- MYSQL_PASSWORD antes de correr este script). Le damos acceso a esta base:
-- es el mismo DB_USER que usa inventario-api (VM1), ver su .env.example.
GRANT ALL PRIVILEGES ON inventario_db.* TO 'bodega'@'%';
FLUSH PRIVILEGES;
