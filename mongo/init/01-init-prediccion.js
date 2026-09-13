// Inicializa la base prediccion_db para el microservicio Predicción (VM2, Node.js)
// Este script corre autenticado como el usuario root (MONGO_INITDB_ROOT_USERNAME/
// PASSWORD en docker-compose.yml), por eso puede crear el usuario de abajo sin
// credenciales adicionales.
db = db.getSiblingDB('prediccion_db');

if (!db.getCollectionNames().includes('predicciones')) {
    db.createCollection('predicciones');
}

// Un documento por producto/día: el índice único evita duplicar el cálculo
// del mismo día para el mismo producto (se hace upsert desde prediccion-api).
db.predicciones.createIndex(
    { producto_id: 1, fecha: -1 },
    { unique: true, name: 'idx_producto_fecha' }
);

// Usuario de aplicacion 'bodega' (mismo patron que MYSQL_USER/POSTGRES_USER
// en MySQL/PostgreSQL): prediccion-api (VM2) se conecta con este usuario,
// nunca con el root. Con permisos limitados a esta base unicamente. Si
// cambias la contraseña aqui, actualiza tambien MONGO_URI en el
// .env.example de VM3 y en seed-scripts/.env.example.
if (db.getUser('bodega') === null) {
    db.createUser({
        user: 'bodega',
        pwd: 'changeme',
        roles: [{ role: 'readWrite', db: 'prediccion_db' }],
    });
}
