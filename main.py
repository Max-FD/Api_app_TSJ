import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import auth
import rondas
from database import test_connection

# Configurar logging para producción
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Detectar entorno
ENV = os.getenv("ENV", "production")

app = FastAPI(
    title="API Sistema de Rondas",
    description="API para gestión de rondas de seguridad",
    version="1.0.0",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rondas.router)


@app.get("/")
def root():
    """
    Endpoint raíz - Redirige a documentación en desarrollo
    """
    return {
        "message": "API Sistema de Rondas",
        "status": "active",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    """
    Health check para monitoreo de servicios (Render/AWS)
    """
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
    }


@app.on_event("startup")
def on_startup():
    """
    Se ejecuta cuando inicia la aplicación
    """
    logger.info("=" * 50)
    logger.info("Iniciando API Sistema de Rondas")
    logger.info(f"Entorno: {ENV}")
    logger.info("=" * 50)

    if not test_connection():
        logger.error("Advertencia: No se pudo conectar a la base de datos")

    logger.info("=" * 50)
    logger.info("API lista")
    logger.info("=" * 50)


@app.on_event("shutdown")
def on_shutdown():
    """
    Se ejecuta cuando se detiene la aplicación
    """
    logger.info("Deteniendo API Sistema de Rondas")
