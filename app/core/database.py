from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

# Importamos la configuración global que ya procesó el .env
from app.config.settings import settings 

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    """
    Utilidad para verificar la conexión al inicio del servidor.
    """
    try:
        with engine.connect() as connection:
            print(f"🟢 ¡ÉXITO! Conectado a la base de datos PostgreSQL en Docker.")
    except OperationalError as e:
        print(f"🔴 ERROR: No se pudo conectar a la base de datos.")