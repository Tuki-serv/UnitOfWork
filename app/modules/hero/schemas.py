from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# ── Esquemas Auxiliares (Para evitar importaciones circulares) ───────────────

class TeamBasicRead(SQLModel):
    """Esquema reducido de Team para mostrar dentro de un Hero sin bucles."""
    id: int
    name: str
    headquarters: str

class WeaponBasicRead(SQLModel):
    """Esquema reducido de Weapon para mostrar dentro de un Hero."""
    id: int
    name: str
    description: Optional[str] = None


# ── Base (Validaciones Centralizadas) ────────────────────────────────────────

class HeroBase(SQLModel):
    """
    Acá ponemos las validaciones estrictas. 
    Cualquier esquema que herede de acá (Create, Public) ya nace validado.
    """
    name: str = Field(min_length=2, max_length=100)
    alias: str = Field(min_length=2, max_length=100)
    power_level: int = Field(ge=1, le=100)


# ── Entrada (Requests) ───────────────────────────────────────────────────────

class HeroCreate(HeroBase):
    """Body para POST /heroes/"""
    team_id: Optional[int] = None
    weapon_id: Optional[int] = None  # <- Agregamos el arma


class HeroUpdate(SQLModel):
    """
    Body para PATCH /heroes/{id}.
    Como todo es opcional, tenemos que reescribir las validaciones.
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    alias: Optional[str] = Field(default=None, min_length=2, max_length=100)
    power_level: Optional[int] = Field(default=None, ge=1, le=100)
    team_id: Optional[int] = None
    weapon_id: Optional[int] = None  # <- Agregamos el arma
    is_active: Optional[bool] = None


class HeroTeamAssign(SQLModel):
    """Body para POST /heroes/{id}/teams (Para tu relación N:M)"""
    team_id: int


# ── Salida (Responses) ───────────────────────────────────────────────────────

class HeroPublic(HeroBase):
    """Response model: campos que se exponen al cliente (sin anidaciones)."""
    id: int
    is_active: bool
    team_id: Optional[int] = None
    weapon_id: Optional[int] = None  # <- Agregamos el arma

class HeroPublicFull(BaseModel):
    """
    Response model que incluye TODAS las relaciones cargadas.
    Usamos BaseModel puro (Pydantic) para evitar el bug de validación
    de SQLModel al anidar objetos.
    """
    id: int
    name: str
    alias: str
    power_level: int
    is_active: bool

    # Las 3 relaciones cargadas:
    weapon: Optional[WeaponBasicRead] = None  # Relación 1:1 (Arma)
    team: Optional[TeamBasicRead] = None      # Relación 1:N (Equipo principal)
    teams: List[TeamBasicRead] = []           # Relación N:M (Afiliaciones extra)

    model_config = {"from_attributes": True}


class HeroList(SQLModel):
    """Response model paginado para GET /heroes/"""
    total: int
    data: List[HeroPublic]