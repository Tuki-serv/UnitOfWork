from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

# El TYPE_CHECKING es un truco ninja de Python.
# Solo se ejecuta cuando el editor lee el código (para autocompletado), 
# pero se ignora cuando FastAPI está corriendo, evitando el import circular.
if TYPE_CHECKING:
    from app.modules.team.models import Team
    from app.modules.weapon.models import Weapon

# 1. La Tabla Intermedia (El equivalente a @JoinTable en java)
class HeroTeamLink(SQLModel, table=True):
    __tablename__ = "hero_team_link"

    hero_id: int = Field(
        sa_column=Column(Integer, ForeignKey("hero.id", ondelete="CASCADE"), primary_key=True)
    )
    team_id: int = Field(
        sa_column=Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), primary_key=True)
    )

# 2. El modelo principal
class Hero(SQLModel, table=True):
    __tablename__ = "hero"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    alias: str = Field(unique=True)
    power_level: int = Field(default=1)
    is_active: bool = Field(default=True)

    weapon_id: Optional[int] = Field(default=None,foreign_key="weapon.id")
    weapon: Optional["Weapon"] = Relationship(back_populates="hero")

    # --- RELACIÓN 1:N (Equipo Principal) ---
    # La FK va del lado "N". Un héroe tiene un equipo principal.
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional["Team"] = Relationship(back_populates="heroes")

    # --- RELACIÓN N:M (Afiliaciones extra) ---
    # Usa la tabla intermedia explícita que creamos arriba.
    teams: List["Team"] = Relationship(
        back_populates="hero_links",
        link_model=HeroTeamLink
    )