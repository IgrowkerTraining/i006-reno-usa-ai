import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Lee la URL que le pasa Docker (o usa una por defecto por seguridad)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password123@db-ia:5432/ia_backend_db"
)

# Creamos el motor de conexión
engine = create_engine(DATABASE_URL)

# Función para probar que todo ande bien
def test_db_connection():
    try:
        # Intentamos abrir y cerrar una conexión rápida
        with engine.connect() as connection:
            print("🟢 ¡ÉXITO! Conectado a la base de datos PostgreSQL en Docker.")
    except OperationalError as e:
        print(f"🔴 ERROR: No se pudo conectar a la base de datos. Detalle: {e}")