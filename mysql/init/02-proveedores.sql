-- Base de datos del microservicio Proveedores (VM1, Python/FastAPI)
CREATE DATABASE IF NOT EXISTS proveedores_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE proveedores_db;

CREATE TABLE IF NOT EXISTS proveedores (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    contacto    VARCHAR(100),
    telefono    VARCHAR(20),
    email       VARCHAR(100),
    direccion   VARCHAR(200),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tiempos_entrega (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id           INT NOT NULL,
    producto_id            INT NOT NULL,
    dias_entrega_promedio  INT NOT NULL,
    dias_entrega_min       INT NOT NULL,
    dias_entrega_max       INT NOT NULL,
    updated_at             DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tiempos_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    INDEX idx_tiempos_producto_id (producto_id),
    INDEX idx_tiempos_proveedor_id (proveedor_id)
) ENGINE=InnoDB;

-- Mismo usuario 'bodega' de 01-inventario.sql: aqui solo se agrega el
-- privilegio sobre esta segunda base. Es el DB_USER que usa
-- proveedores-api (VM1), ver su .env.example.
GRANT ALL PRIVILEGES ON proveedores_db.* TO 'bodega'@'%';
FLUSH PRIVILEGES;
