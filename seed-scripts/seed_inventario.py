"""Carga masiva de datos ficticios para inventario_db (MySQL).

Genera ~1500 productos (uno por cada producto_id del rango acordado) y
>= 20,000 movimientos de inventario distribuidos en los ultimos 90 dias.
Al final, recalcula stock_actual de cada producto segun el balance neto
de sus propios movimientos (entrada suma, salida resta, ajuste suma).

Uso:
    python seed_inventario.py
"""

import random
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker

from common import (
    CATEGORIAS,
    PRODUCTO_ID_RANGE,
    PRODUCTOS_POR_CATEGORIA,
    UNIDADES_MEDIDA,
    chunked,
    mysql_conn_params,
)

fake = Faker("es_PE")

TOTAL_MOVIMIENTOS = 22000
DIAS_HISTORIA = 90
BATCH_SIZE = 1000


def seed_productos(cursor):
    productos = []
    for producto_id in PRODUCTO_ID_RANGE:
        categoria = random.choice(CATEGORIAS)
        base = random.choice(PRODUCTOS_POR_CATEGORIA[categoria])
        marca = fake.company().split()[0].rstrip(",.")
        nombre = f"{base} {marca} {random.choice(['x500g', 'x1kg', 'x1L', 'x350ml', 'x6un', ''])}".strip()
        stock_minimo = random.randint(5, 50)
        stock_actual = random.randint(0, stock_minimo * 4)  # valor provisional, se recalcula al final
        productos.append(
            (
                producto_id,
                f"SKU-{producto_id:05d}",
                nombre[:150],
                categoria,
                random.choice(UNIDADES_MEDIDA),
                stock_actual,
                stock_minimo,
                round(random.uniform(1.5, 120.0), 2),
            )
        )

    sql = (
        "INSERT INTO productos "
        "(id, sku, nombre, categoria, unidad_medida, stock_actual, stock_minimo, precio_unitario) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)"
    )
    inserted = 0
    for batch in chunked(productos, BATCH_SIZE):
        cursor.executemany(sql, batch)
        inserted += len(batch)
    return inserted


def seed_movimientos(cursor):
    tipos = ["entrada", "salida", "ajuste"]
    motivos = {
        "entrada": ["reposicion de stock", "devolucion de cliente", "ingreso por compra"],
        "salida": ["venta mostrador", "merma", "traslado a otra sucursal"],
        "ajuste": ["conteo fisico", "correccion de sistema"],
    }
    usuarios = [f"bodeguero{i}" for i in range(1, 9)]

    now = datetime.now()
    movimientos = []
    for _ in range(TOTAL_MOVIMIENTOS):
        producto_id = random.choice(PRODUCTO_ID_RANGE)
        tipo = random.choice(tipos)
        fecha = now - timedelta(
            days=random.randint(0, DIAS_HISTORIA),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        movimientos.append(
            (
                producto_id,
                tipo,
                random.randint(1, 200),
                fecha,
                random.choice(motivos[tipo]),
                random.choice(usuarios),
            )
        )

    sql = (
        "INSERT INTO movimientos_inventario "
        "(producto_id, tipo_movimiento, cantidad, fecha_movimiento, motivo, usuario) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    inserted = 0
    for batch in chunked(movimientos, BATCH_SIZE):
        cursor.executemany(sql, batch)
        inserted += len(batch)
    return inserted


def recalcular_stock_actual(cursor):
    """Actualiza stock_actual de cada producto segun el balance neto de sus
    movimientos: entrada y ajuste suman, salida resta. Se deja en 0 como
    piso si el balance neto ficticio resultara negativo."""
    sql = """
        UPDATE productos p
        LEFT JOIN (
            SELECT
                producto_id,
                SUM(
                    CASE
                        WHEN tipo_movimiento IN ('entrada', 'ajuste') THEN cantidad
                        ELSE -cantidad
                    END
                ) AS neto
            FROM movimientos_inventario
            GROUP BY producto_id
        ) m ON m.producto_id = p.id
        SET p.stock_actual = GREATEST(COALESCE(m.neto, 0), 0)
    """
    cursor.execute(sql)
    return cursor.rowcount


def main():
    conn = mysql.connector.connect(**mysql_conn_params("inventario_db"))
    cursor = conn.cursor()
    try:
        n_productos = seed_productos(cursor)
        conn.commit()
        print(f"[inventario] productos insertados/actualizados: {n_productos}")

        n_movimientos = seed_movimientos(cursor)
        conn.commit()
        print(f"[inventario] movimientos_inventario insertados: {n_movimientos}")

        n_actualizados = recalcular_stock_actual(cursor)
        conn.commit()
        print(f"[inventario] productos con stock_actual recalculado: {n_actualizados}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
