// Inicializa la base prediccion_db para el microservicio Predicción (VM2, Node.js)
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
