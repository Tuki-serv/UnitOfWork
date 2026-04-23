from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

# Importamos HeroTeamLink desde hero.models (donde está definida)
# Esto no crea ciclo porque hero.models no importa team.models en runtime
from app.modules.hero.models import HeroTeamLink

if TYPE_CHECKING:
    # Solo para type hints: evita import circular en runtime
    from app.modules.hero.models import Hero


class Team(SQLModel, table=True):
    """
    Relaciones:

    1:N  heroes     → Un Team tiene muchos Heroes (Hero guarda la FK team_id)
    N:M  hero_links → Un Team está en múltiples Heroes (via HeroTeamLink)
    """

    __tablename__ = "team"  # Todo en singular

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    headquarters: str

    # Campo para borrado lógico (Soft Delete)
    is_active: bool = Field(default=True)

    # ── Relación 1:N ─────────────────────────────────────────────
    # back_populates='team' conecta con Hero.team
    # SQLModel carga la lista cuando se hace selectinload(Team.heroes)
    heroes: List["Hero"] = Relationship(back_populates="team")

    # ── Relación N:M via HeroTeamLink ────────────────────────────
    # back_populates='teams' conecta con Hero.teams
    hero_links: List["Hero"] = Relationship(
        back_populates="teams",
        link_model=HeroTeamLink,
    )
