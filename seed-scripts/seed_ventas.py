"""Carga masiva de datos ficticios para ventas_db (PostgreSQL).

Genera >= 20,000 filas en ventas_diarias sobre el mismo rango de
producto_id usado en inventario_db, en los ultimos 90 dias.

Uso:
    python seed_ventas.py
"""

import random
from datetime import date, timedelta

import psycopg2
import psycopg2.extras

from common import PRODUCTO_ID_RANGE, chunked, postgres_conn_params

TOTAL_VENTAS = 21000
DIAS_HISTORIA = 90
BATCH_SIZE = 1000


def seed_ventas(cursor):
    hoy = date.today()
    filas = []
    for _ in range(TOTAL_VENTAS):
        producto_id = random.choice(PRODUCTO_ID_RANGE)
        fecha = hoy - timedelta(days=random.randint(0, DIAS_HISTORIA))
        cantidad = random.randint(1, 50)
        precio = round(random.uniform(1.0, 100.0), 2)
        total = round(cantidad * precio, 2)
        filas.append((producto_id, fecha, cantidad, precio, total))

    sql = (
        "INSERT INTO ventas_diarias "
        "(producto_id, fecha, cantidad_vendida, precio_unitario, total) "
        "VALUES %s"
    )
    inserted = 0
    for batch in chunked(filas, BATCH_SIZE):
        psycopg2.extras.execute_values(cursor, sql, batch)
        inserted += len(batch)
    return inserted


def seed_pedidos_proveedor(cursor, n=1500):
    hoy = date.today()
    estados = ["pendiente", "en_transito", "recibido"]
    filas = []
    for _ in range(n):
        producto_id = random.choice(PRODUCTO_ID_RANGE)
        proveedor_id = random.randint(1, 300)
        fecha_pedido = hoy - timedelta(days=random.randint(0, DIAS_HISTORIA))
        entrega_estim = fecha_pedido + timedelta(days=random.randint(1, 15))
        filas.append(
            (
                producto_id,
                proveedor_id,
                fecha_pedido,
                random.randint(10, 500),
                random.choice(estados),
                entrega_estim,
            )
        )

    sql = (
        "INSERT INTO pedidos_proveedor "
        "(producto_id, proveedor_id, fecha_pedido, cantidad_pedida, estado, fecha_estimada_entrega) "
        "VALUES %s"
    )
    psycopg2.extras.execute_values(cursor, sql, filas)
    return len(filas)


def main():
    conn = psycopg2.connect(**postgres_conn_params("ventas_db"))
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        n_ventas = seed_ventas(cursor)
        conn.commit()
        print(f"[ventas] ventas_diarias insertadas: {n_ventas}")

        n_pedidos = seed_pedidos_proveedor(cursor)
        conn.commit()
        print(f"[ventas] pedidos_proveedor insertados: {n_pedidos}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
