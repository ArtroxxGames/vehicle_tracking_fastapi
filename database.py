from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
# Para desarrollo usamos SQLite, para producción MySQL
USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() == "true"

if USE_MYSQL:
    # Configuración MySQL
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "alarma_rastreadora")
    
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
else:
    # Configuración SQLite para desarrollo
    DATABASE_URL = "sqlite:///./alarma_rastreadora.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if not USE_MYSQL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
