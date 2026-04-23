from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.team.models import Team
from app.modules.team.schemas import (
    TeamCreate, 
    TeamPublic, 
    TeamUpdate, 
    TeamList, 
    TeamWithHeroes
)
from app.modules.team.unit_of_work import TeamUnitOfWork
from app.modules.hero.schemas import HeroPublic


class TeamService:
    """
    Capa de lógica de negocio para Teams.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: TeamUnitOfWork, team_id: int) -> Team:
        """Obtiene un equipo por ID o lanza HTTP 404."""
        team = uow.teams.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team con id={team_id} no encontrado",
            )
        return team

    def _assert_name_unique(self, uow: TeamUnitOfWork, name: str) -> None:
        """Valida que el nombre del equipo sea único."""
        # Asume que agregaste el método get_by_name en TeamRepository
        if uow.teams.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo con el nombre '{name}'",
            )

    # ── Casos de uso ──────────────────────────────────────────────────────────

    def create(self, data: TeamCreate) -> TeamPublic:
        """Crea un nuevo equipo."""
        with TeamUnitOfWork(self._session) as uow:
            self._assert_name_unique(uow, data.name)
            team = Team.model_validate(data)
            uow.teams.add(team)
            
            result = TeamPublic.model_validate(team)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> TeamList:
        """Obtiene equipos activos con paginación."""
        with TeamUnitOfWork(self._session) as uow:
            teams = uow.teams.get_active(offset=offset, limit=limit)
            total = uow.teams.count_model()

            result = TeamList(
                data=[TeamPublic.model_validate(t) for t in teams],
                total=total,
            )
        return result

    def get_team(self, team_id: int) -> TeamWithHeroes:
        """Obtiene un equipo completo con sus héroes (1:N y N:M)."""
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)
            # Gracias a que usamos BaseModel en el Schema con from_attributes=True,
            # esto se serializa perfectamente sin errores circulares.
            result = TeamWithHeroes.model_validate(team)
        return result

    def update(self, team_id: int, data: TeamUpdate) -> TeamPublic:
        """Actualiza un equipo de forma parcial (PATCH)."""
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)

            if data.name and data.name != team.name:
                self._assert_name_unique(uow, data.name)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(team, field, value)

            uow.teams.add(team)
            result = TeamPublic.model_validate(team)
        return result

    def soft_delete(self, team_id: int) -> None:
        """Borrado lógico del equipo."""
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)
            team.is_active = False
            uow.teams.add(team)