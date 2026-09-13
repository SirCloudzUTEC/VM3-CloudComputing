"""Helpers compartidos por los scripts de carga masiva de datos ficticios.

Convencion de variables de entorno: cada script lee DB_HOST, DB_PORT,
DB_USER, DB_PASSWORD, DB_NAME -- el mismo naming que usan los
microservicios de VM1 para conectarse a su base (ver
VM1/*/app/db.py y VM1/*/.env.example). Como aqui varios scripts corren en
secuencia contra bases distintas, run_all.sh se encarga de exportar el
valor correcto de cada variable antes de invocar cada uno (ver ese script
y seed-scripts/.env.example para el detalle).

Rango acordado de producto_id: se usa el mismo rango (1-1500) en todas las
tablas de todas las bases que referencian productos (productos,
movimientos_inventario, ventas_diarias, tiempos_entrega, predicciones),
aunque no exista una foreign key real entre bases distintas. Esto mantiene
los datos ficticios coherentes entre microservicios.
"""

import os

from dotenv import load_dotenv

load_dotenv()

PRODUCTO_ID_RANGE = range(1, 1501)  # 1500 productos

CATEGORIAS = [
    "Abarrotes",
    "Bebidas",
    "Limpieza",
    "Lacteos",
    "Snacks",
    "Cuidado Personal",
    "Panaderia",
    "Congelados",
]

UNIDADES_MEDIDA = ["unidad", "kg", "litro", "paquete", "caja"]

# Nombres base realistas de productos de bodega peruana, por categoria.
# Se combinan con una marca/variante generada con Faker para variar el
# nombre final sin perder realismo (ver seed_inventario.py).
PRODUCTOS_POR_CATEGORIA = {
    "Abarrotes": ["Arroz extra", "Azucar rubia", "Aceite vegetal", "Fideos spaghetti",
                  "Menestra de lenteja", "Sal de mesa", "Atun en lata", "Harina sin preparar"],
    "Bebidas": ["Gaseosa cola", "Agua mineral", "Jugo de nectar", "Cerveza",
                "Te helado", "Agua de mesa", "Bebida rehidratante", "Cafe instantaneo"],
    "Limpieza": ["Detergente en polvo", "Lejia", "Jabon de barra", "Limpiatodo",
                 "Papel higienico", "Esponja multiuso", "Bolsas de basura", "Desinfectante"],
    "Lacteos": ["Leche evaporada", "Yogurt bebible", "Queso fresco", "Mantequilla",
                "Leche fresca", "Manjar blanco", "Queso mantecoso", "Crema de leche"],
    "Snacks": ["Papitas fritas", "Galletas de soda", "Galletas rellenas", "Chizitos",
               "Chocolate", "Cancha salada", "Keke individual", "Caramelos"],
    "Cuidado Personal": ["Shampoo", "Jabon de tocador", "Pasta dental", "Papel higienico premium",
                          "Desodorante", "Rastrillo desechable", "Talco", "Algodon"],
    "Panaderia": ["Pan frances", "Pan de molde", "Tostadas", "Keke ingles",
                  "Pan integral", "Bizcocho", "Pan de yema", "Galletas de agua"],
    "Congelados": ["Nuggets de pollo", "Papas fritas congeladas", "Helado", "Pulpa de fruta congelada",
                   "Pescado congelado", "Verduras mixtas congeladas", "Empanada congelada", "Hamburguesa congelada"],
}


def mysql_conn_params(default_db):
    """Parametros de conexion para mysql.connector, leidos de DB_* con
    defaults sensatos para esta base en particular."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "bodega"),
        "password": os.getenv("DB_PASSWORD", "changeme"),
        "database": os.getenv("DB_NAME", default_db),
    }


def postgres_conn_params(default_db):
    """Parametros de conexion para psycopg2, leidos de DB_* con defaults
    sensatos para esta base en particular."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "user": os.getenv("DB_USER", "bodega"),
        "password": os.getenv("DB_PASSWORD", "changeme"),
        "dbname": os.getenv("DB_NAME", default_db),
    }


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB", "prediccion_db")


def chunked(iterable, size):
    """Parte un iterable en listas de tamano `size` (para inserts por lotes)."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
