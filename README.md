# VM3 — Bases de datos

VM privada (**sin IP pública**) que aloja las 4 bases de datos del proyecto. No sirve tráfico HTTP: solo expone los puertos nativos de cada motor a las VMs de backend.

**Instancia sugerida:** t3.medium (4 GB RAM, corren 3 motores a la vez), volumen EBS gp3 de 20-30 GB.

## Contenido

| Motor | Contenedor | Base de datos | Puerto | Usada por |
|---|---|---|---|---|
| MySQL 8 | `bodega-mysql` | `inventario_db` | 3306 | `inventario-api` (VM1) |
| MySQL 8 | `bodega-mysql` | `proveedores_db` | 3306 | `proveedores-api` (VM1) |
| PostgreSQL 16 | `bodega-postgres` | `ventas_db` | 5432 | `ventas-api` (VM1) |
| MongoDB 7 | `bodega-mongo` | `prediccion_db` | 27017 | `prediccion-api` (VM2) |

`inventario_db` y `proveedores_db` viven en la **misma instancia de MySQL** (un solo contenedor sirviendo dos bases) para simplificar el despliegue; cada una tiene sus propias tablas e índices y no comparten datos entre sí.

## Usuario de aplicación (contrato con VM1)

Los microservicios de VM1 (`inventario-api`, `proveedores-api`, `ventas-api`) se conectan con `DB_USER=bodega` / `DB_PASSWORD=changeme` (ver sus `.env.example`), no con el usuario administrador de cada motor. Por eso:

- MySQL: además de `MYSQL_ROOT_PASSWORD` (admin), el compose crea el usuario `bodega` vía `MYSQL_USER`/`MYSQL_PASSWORD`, y `mysql/init/01-inventario.sql` y `02-proveedores.sql` le hacen `GRANT ALL PRIVILEGES` sobre `inventario_db` y `proveedores_db` respectivamente.
- PostgreSQL: `POSTGRES_USER` se define directamente como `bodega` (es el único rol de esa instancia, ya que solo sirve `ventas_db`).
- MongoDB: además de `MONGO_INITDB_ROOT_USERNAME`/`PASSWORD` (admin, solo para tareas administrativas), `mongo/init/01-init-prediccion.js` crea el usuario `bodega` con rol `readWrite` scoped a `prediccion_db` — es el que usa `prediccion-api` (VM2) para conectarse (ver `MONGO_URI` en `.env.example`).

Si cambias `MYSQL_PASSWORD`/`POSTGRES_PASSWORD`/`MONGO_PASSWORD` en `.env`, actualiza también `DB_PASSWORD`/`MONGO_URI` en los `.env` de los microservicios que consumen esta VM. Para Mongo, además, el usuario `bodega` está *hardcodeado* en `mongo/init/01-init-prediccion.js` (los scripts de init no leen variables de entorno arbitrarias) — si cambias `MONGO_PASSWORD`, actualiza también ese script.

## Acuerdo de datos ficticios: rango de `producto_id`

Como las bases de datos son independientes (sin foreign keys entre motores/instancias), el equipo usa un rango fijo de `producto_id` compartido: **1 a 1500**. Todas las tablas de todas las bases que referencian un producto (`productos`, `movimientos_inventario`, `ventas_diarias`, `tiempos_entrega`, y los documentos de `predicciones`) usan IDs dentro de ese rango, para que los datos ficticios sean coherentes al cruzarlos entre microservicios.

## Cómo levantarlo

```bash
cd VM3
cp .env.example .env   # editar contraseñas si se desea
docker-compose up -d
docker-compose ps      # esperar a que los 3 healthcheck queden "healthy"
```

## Carga masiva de datos ficticios (una sola vez)

Los scripts en `seed-scripts/` generan e insertan los datos ficticios exigidos por la rúbrica (mínimo 20,000 registros por base). **No** se ejecutan automáticamente al levantar los contenedores — se corren manualmente una vez que las bases están arriba:

```bash
cd seed-scripts
./run_all.sh
```

Esto ejecuta, en orden: `seed_inventario.py` → `seed_proveedores.py` → `seed_ventas.py` → `seed_prediccion.py` (este último es opcional, solo deja documentos de ejemplo en `predicciones` para poder probar `alertas-api` antes de tener corriendo `prediccion-api`). Cada script imprime cuántas filas insertó al final. `run_all.sh` arma automáticamente las variables `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` (y `MONGO_URI`) que cada script necesita a partir de `.env` — ver `seed-scripts/.env.example` para el detalle y para correr un script suelto a mano.

Registros generados:
- `productos`: ~1,500 (uno por `producto_id`).
- `movimientos_inventario`: ≥ 20,000.
- `ventas_diarias`: ≥ 20,000.
- `pedidos_proveedor`: ~1,500 (dato complementario, no es la tabla de carga masiva de Ventas).
- `proveedores`: ~300.
- `tiempos_entrega`: ≥ 20,000.

Si se corren los scripts desde fuera de la VM (por ejemplo en el laptop del equipo apuntando a `localhost` con los puertos publicados), usar las mismas credenciales de `.env`; si se corren desde dentro de la VM en AWS, apuntar `MYSQL_HOST`/`POSTGRES_HOST`/`MONGO_URI` a `localhost` igual (los scripts corren en la misma instancia que los contenedores).

## Seguridad — Security Group

- **Sin IP pública** asociada a la instancia EC2.
- Entrada permitida **únicamente** desde los Security Groups de VM1, VM2 y VM4, en los puertos correspondientes:
  - `3306/tcp` (MySQL) — desde SG de VM1 (inventario-api, proveedores-api) y SG de VM4 (ingesta-inventario, ingesta-proveedores).
  - `5432/tcp` (PostgreSQL) — desde SG de VM1 (ventas-api) y SG de VM4 (ingesta-ventas).
  - `27017/tcp` (MongoDB) — desde SG de VM2 (prediccion-api).
- **Ningún** tráfico entra directo desde el balanceador de carga ni desde internet.
- Acceso administrativo a la instancia vía AWS SSM Session Manager, no SSH abierto.
- Los 3 motores exigen autenticación a nivel de aplicación (usuario `bodega`, ver sección anterior) — el Security Group es una capa adicional, no la única barrera.
