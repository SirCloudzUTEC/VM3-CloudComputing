"""Siembra inicial (opcional) de prediccion_db (MongoDB).

No reemplaza el calculo real de prediccion-api: solo deja documentos de
ejemplo para que alertas-api tenga algo que leer antes de que
prediccion-api haya corrido su primer calculo.

Uso:
    python seed_prediccion.py
"""

import random
from datetime import datetime

from pymongo import MongoClient, UpdateOne

from common import MONGO_DB_NAME, MONGO_URI, PRODUCTO_ID_RANGE

MUESTRA = 1500  # ~1500 documentos iniciales, uno por producto_id


def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    coleccion = db["predicciones"]

    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    operaciones = []
    for producto_id in random.sample(list(PRODUCTO_ID_RANGE), MUESTRA):
        velocidad = round(random.uniform(0.5, 25.0), 2)
        stock_actual = random.randint(0, 300)
        dias_hasta_agotamiento = round(stock_actual / velocidad, 1) if velocidad > 0 else None
        tiempo_entrega_promedio = random.randint(2, 12)

        if dias_hasta_agotamiento is None:
            prob_quiebre = 0.0
        else:
            ratio = dias_hasta_agotamiento / tiempo_entrega_promedio
            prob_quiebre = max(0.0, min(1.0, 1 - (ratio - 1))) if ratio <= 2 else max(0.0, 1 - (ratio / 4))

        nivel_riesgo = "alto" if prob_quiebre > 0.66 else "medio" if prob_quiebre > 0.33 else "bajo"

        documento = {
            "producto_id": producto_id,
            "fecha": hoy,
            "velocidad_venta_diaria": velocidad,
            "stock_actual": stock_actual,
            "dias_hasta_agotamiento": dias_hasta_agotamiento,
            "tiempo_entrega_promedio": tiempo_entrega_promedio,
            "prob_quiebre": round(prob_quiebre, 3),
            "nivel_riesgo": nivel_riesgo,
            "created_at": datetime.utcnow(),
        }
        operaciones.append(
            UpdateOne(
                {"producto_id": producto_id, "fecha": hoy},
                {"$set": documento},
                upsert=True,
            )
        )

    if operaciones:
        resultado = coleccion.bulk_write(operaciones)
        print(
            f"[prediccion] documentos insertados: {resultado.upserted_count}, "
            f"actualizados: {resultado.modified_count}"
        )
    client.close()


if __name__ == "__main__":
    main()
