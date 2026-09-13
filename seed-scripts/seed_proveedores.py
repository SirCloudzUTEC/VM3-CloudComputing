"""Carga masiva de datos ficticios para proveedores_db (MySQL).

Genera ~300 proveedores y >= 20,000 filas en tiempos_entrega
(combinaciones proveedor x producto), sobre el mismo rango de
producto_id usado en inventario_db.

Uso:
    python seed_proveedores.py
"""

import random

import mysql.connector
from faker import Faker

from common import PRODUCTO_ID_RANGE, chunked, mysql_conn_params

fake = Faker("es_PE")

TOTAL_PROVEEDORES = 300
TOTAL_TIEMPOS_ENTREGA = 21000
BATCH_SIZE = 1000


def seed_proveedores(cursor):
    proveedores = []
    for proveedor_id in range(1, TOTAL_PROVEEDORES + 1):
        proveedores.append(
            (
                proveedor_id,
                fake.company()[:150],
                fake.name()[:100],
                fake.phone_number()[:20],
                fake.company_email()[:100],
                fake.address().replace("\n", ", ")[:200],
            )
        )

    sql = (
        "INSERT INTO proveedores (id, nombre, contacto, telefono, email, direccion) "
        "VALUES (%s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)"
    )
    cursor.executemany(sql, proveedores)
    return len(proveedores)


def seed_tiempos_entrega(cursor):
    filas = []
    for _ in range(TOTAL_TIEMPOS_ENTREGA):
        proveedor_id = random.randint(1, TOTAL_PROVEEDORES)
        producto_id = random.choice(PRODUCTO_ID_RANGE)
        dias_promedio = random.randint(1, 15)
        dias_min = max(1, dias_promedio - random.randint(0, 3))
        dias_max = dias_promedio + random.randint(0, 3)
        filas.append((proveedor_id, producto_id, dias_promedio, dias_min, dias_max))

    sql = (
        "INSERT INTO tiempos_entrega "
        "(proveedor_id, producto_id, dias_entrega_promedio, dias_entrega_min, dias_entrega_max) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    inserted = 0
    for batch in chunked(filas, BATCH_SIZE):
        cursor.executemany(sql, batch)
        inserted += len(batch)
    return inserted


def main():
    conn = mysql.connector.connect(**mysql_conn_params("proveedores_db"))
    cursor = conn.cursor()
    try:
        n_proveedores = seed_proveedores(cursor)
        conn.commit()
        print(f"[proveedores] proveedores insertados/actualizados: {n_proveedores}")

        n_tiempos = seed_tiempos_entrega(cursor)
        conn.commit()
        print(f"[proveedores] tiempos_entrega insertados: {n_tiempos}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
