import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password123@db-ia:5432/ia_backend_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Abre una conexión fresca a Postgres para cada petición, y se asegura 
    de cerrarla al final (incluso si hay un error) gracias al 'finally'.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    try:
        with engine.connect() as connection:
            print("🟢 ¡ÉXITO! Conectado a la base de datos PostgreSQL en Docker.")
    except OperationalError as e:
        print(f"🔴 ERROR: No se pudo conectar a la base de datos. Detalle: {e}")