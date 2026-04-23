from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# ── Esquemas Auxiliares ───────────────────────────────────────────────────────

class HeroBasicRead(SQLModel):
    """
    Esquema reducido para evitar importaciones circulares (no importamos HeroPublic)
    y para prevenir bucles infinitos en el JSON.
    """
    id: int
    name: str
    alias: str
    power_level: int


# ── Base (Validaciones Centralizadas) ─────────────────────────────────────────

class TeamBase(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    headquarters: str = Field(min_length=2, max_length=200)


# ── Entrada (Requests) ────────────────────────────────────────────────────────

class TeamCreate(TeamBase):
    """Body para POST /teams/"""
    pass

class TeamUpdate(SQLModel):
    """Body para PATCH /teams/{id} — todos los campos opcionales."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    headquarters: Optional[str] = Field(default=None, min_length=2, max_length=200)
    is_active: Optional[bool] = None


# ── Salida (Responses) ────────────────────────────────────────────────────────

class TeamPublic(TeamBase):
    """Response model básico para GET /teams/ (Sin relaciones anidadas)"""
    id: int
    is_active: bool

class TeamList(SQLModel):
    """Response model paginado para GET /teams/"""
    total: int
    data: List[TeamPublic]

class TeamWithHeroes(BaseModel):
    """
    Response model para GET /teams/{id}
    Usa BaseModel puro para evitar conflictos de SQLModel al anidar.
    """
    id: int
    name: str
    headquarters: str
    is_active: bool
    
    # Traemos AMBAS relaciones usando nuestro esquema básico
    heroes: List[HeroBasicRead] = []       # Relación 1:N (Equipo principal)
    hero_links: List[HeroBasicRead] = []   # Relación N:M (Afiliaciones)

    model_config = {"from_attributes": True}