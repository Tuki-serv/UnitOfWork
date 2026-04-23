from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlmodel import SQLModel

# Importamos el engine de la DB
from app.core.database import engine

# Importamos todos los routers
from app.modules.health.router import router as health_router
from app.modules.hero.router import router as hero_router
from app.modules.team.router import router as team_router
from app.modules.weapon.router import router as weapon_router

# Importamos los manejadores de errores
from app.utils.errores import manejar_http_exceptions, manejar_validaciones

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas en PostgreSQL al arrancar si no existen
    SQLModel.metadata.create_all(engine)
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hero API - Estándar Profesional",
        description="Implementación de Repository Pattern y Unit of Work",
        version="2.0.0",
    )

    # Registro de Routers (Ya tienen el prefix adentro de cada archivo)
    app.include_router(health_router)
    app.include_router(hero_router)
    app.include_router(team_router)
    app.include_router(weapon_router)

    # Manejo de errores globales correctos
    app.add_exception_handler(HTTPException, manejar_http_exceptions)
    app.add_exception_handler(RequestValidationError, manejar_validaciones)

    return app

app = create_app()