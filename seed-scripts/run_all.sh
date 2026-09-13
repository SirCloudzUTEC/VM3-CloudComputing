#!/usr/bin/env bash
# Orquesta la carga masiva de datos ficticios en el orden correcto:
# inventario -> proveedores -> ventas -> prediccion.
# Ejecutar UNA sola vez, con los contenedores de VM3 ya arriba y healthy
# (docker-compose up -d desde VM3/).
#
# Cada script python lee su conexion via DB_HOST/DB_PORT/DB_USER/
# DB_PASSWORD/DB_NAME (mismo naming que usan los microservicios de VM1) o
# MONGO_URI para Mongo. Como aqui corremos varios scripts contra bases
# distintas en secuencia, este orquestador exporta el valor correcto de
# esas variables antes de invocar cada uno. Si existe un .env en esta
# carpeta (copiado de .env.example) o en VM3/../.env, se usa como base de
# host/usuario/password.
set -e

cd "$(dirname "$0")"

echo "== Instalando dependencias =="
pip install -r requirements.txt

# Carga variables base si existe un .env local o el de la raiz de VM3.
if [ -f .env ]; then
    set -a; source .env; set +a
elif [ -f ../.env ]; then
    set -a; source ../.env; set +a
fi

# --- MySQL: inventario_db y proveedores_db viven en el mismo contenedor,
# solo cambia DB_NAME entre un paso y otro. ---
MYSQL_DB_HOST="${MYSQL_HOST:-${DB_HOST:-localhost}}"
MYSQL_DB_PORT="${MYSQL_PORT:-3306}"
MYSQL_DB_USER="${MYSQL_USER:-bodega}"
MYSQL_DB_PASSWORD="${MYSQL_PASSWORD:-changeme}"

# --- PostgreSQL: ventas_db. ---
PG_DB_HOST="${POSTGRES_HOST:-localhost}"
PG_DB_PORT="${POSTGRES_PORT:-5432}"
PG_DB_USER="${POSTGRES_USER:-bodega}"
PG_DB_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

# --- MongoDB: prediccion_db. ---
MONGODB_URI="${MONGO_URI:-mongodb://localhost:27017}"
MONGODB_DB="${MONGO_DB:-prediccion_db}"

echo "== 1/4 Sembrando inventario_db (MySQL) =="
DB_HOST="$MYSQL_DB_HOST" DB_PORT="$MYSQL_DB_PORT" DB_USER="$MYSQL_DB_USER" \
    DB_PASSWORD="$MYSQL_DB_PASSWORD" DB_NAME="inventario_db" \
    python3 seed_inventario.py

echo "== 2/4 Sembrando proveedores_db (MySQL) =="
DB_HOST="$MYSQL_DB_HOST" DB_PORT="$MYSQL_DB_PORT" DB_USER="$MYSQL_DB_USER" \
    DB_PASSWORD="$MYSQL_DB_PASSWORD" DB_NAME="proveedores_db" \
    python3 seed_proveedores.py

echo "== 3/4 Sembrando ventas_db (PostgreSQL) =="
DB_HOST="$PG_DB_HOST" DB_PORT="$PG_DB_PORT" DB_USER="$PG_DB_USER" \
    DB_PASSWORD="$PG_DB_PASSWORD" DB_NAME="ventas_db" \
    python3 seed_ventas.py

echo "== 4/4 Sembrando prediccion_db (MongoDB, opcional) =="
MONGO_URI="$MONGODB_URI" MONGO_DB="$MONGODB_DB" python3 seed_prediccion.py

echo "== Carga masiva completa =="
