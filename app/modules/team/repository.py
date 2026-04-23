from typing import Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.modules.team.models import Team

class TeamRepository(BaseRepository[Team]):
    """
    Acá irían las consultas específicas de Teams.
    Las operaciones CRUD básicas ya las heredó.
    """

    def __init__(self, session):
        # Simplificado: El Unit of Work solo nos va a pasar la sesión.
        # Nosotros le "hardcodeamos" el modelo Team a la clase base.
        super().__init__(session, Team)

    def get_by_id(self, team_id: int) -> Optional[Team]:
        # Armamos la consulta
        stmt = (
            select(Team)
            .where(Team.id == team_id)
            .options(
                selectinload(Team.heroes),
                selectinload(Team.hero_links)
            )
        )
        return self.session.exec(stmt).first()
