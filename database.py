import logging
import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

# Obtener la ruta del directorio actual y cargar .env si existe
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Configurar logging
logger = logging.getLogger(__name__)

# Obtener DATABASE_URL desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL no está configurada. Define la variable de entorno DATABASE_URL"
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10,  # Conexiones adicionales permitidas
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de BD
    Se usa con Depends() en los endpoints
    """
    with Session(engine) as session:
        yield session


def test_connection() -> bool:
    """
    Prueba de conexión a la base de datos
    """
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            logger.info("Conexión a base de datos exitosa")
            return True
    except Exception as e:
        logger.error(f"Error de conexión a base de datos: {e}")
        return False
