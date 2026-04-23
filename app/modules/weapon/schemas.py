from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# ── Esquemas Auxiliares (Para evitar importaciones circulares) ───────────────

class HeroBasicRead(SQLModel):
    """Esquema reducido de Hero para mostrar dentro de un Weapon sin bucles."""
    id: int
    name: str
    alias: str
    power_level: int


# ── Base (Validaciones Centralizadas) ────────────────────────────────────────

class WeaponBase(SQLModel):
    """Validaciones estrictas para Weapon."""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# ── Entrada (Requests) ───────────────────────────────────────────────────────

class WeaponCreate(WeaponBase):
    """Body para POST /weapons/"""
    pass


class WeaponUpdate(SQLModel):
    """Body para PATCH /weapons/{id}. Todo es opcional."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


# ── Salida (Responses) ───────────────────────────────────────────────────────

class WeaponRead(WeaponBase):
    """Response model básico para GET /weapons/ (Sin relaciones anidadas)"""
    id: int
    is_active: bool

class WeaponList(SQLModel):
    total: int
    data: List[WeaponRead]

class WeaponReadWithHero(BaseModel):
    """
    Response model para cuando queremos ver el arma junto con su dueño.
    Usamos BaseModel puro (Pydantic) para evitar el bug de SQLModel al anidar.
    """
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    
    # El hueco rellenado: Relación 1:1 inversa (El héroe dueño de esta arma)
    hero: Optional[HeroBasicRead] = None

    model_config = {"from_attributes": True}