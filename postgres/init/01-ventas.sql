-- Base de datos del microservicio Ventas (VM1, Java/Spring Boot)
-- La base "ventas_db" ya la crea la imagen de postgres via POSTGRES_DB.

CREATE TABLE IF NOT EXISTS ventas_diarias (
    id                BIGSERIAL PRIMARY KEY,
    producto_id       INT NOT NULL,
    fecha             DATE NOT NULL,
    cantidad_vendida  INT NOT NULL,
    precio_unitario   NUMERIC(10,2) NOT NULL,
    total             NUMERIC(12,2) NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ventas_producto_id ON ventas_diarias (producto_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas_diarias (fecha);

CREATE TABLE IF NOT EXISTS pedidos_proveedor (
    id                       BIGSERIAL PRIMARY KEY,
    producto_id              INT NOT NULL,
    proveedor_id             INT NOT NULL,
    fecha_pedido             DATE NOT NULL,
    cantidad_pedida          INT NOT NULL,
    estado                   VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_estimada_entrega   DATE,
    created_at               TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pedidos_producto_id ON pedidos_proveedor (producto_id);
