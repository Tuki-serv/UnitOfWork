from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.team.schemas import (
    TeamCreate, 
    TeamPublic, 
    TeamUpdate, 
    TeamList, 
    TeamWithHeroes
)
from app.modules.team.service import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])

# ── Factory de Dependencias ──
def get_team_service(session: Session = Depends(get_session)) -> TeamService:
    """Inyecta el servicio con su Session de base de datos lista para usar."""
    return TeamService(session)

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=TeamPublic, status_code=status.HTTP_201_CREATED)
def create_team(
    data: TeamCreate, 
    svc: TeamService = Depends(get_team_service)
) -> TeamPublic:
    return svc.create(data)

@router.get("/", response_model=TeamList)
def list_teams(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: TeamService = Depends(get_team_service)
) -> TeamList:
    return svc.get_all(offset=offset, limit=limit)

@router.get("/{team_id}", response_model=TeamWithHeroes)
def get_team(
    team_id: int, 
    svc: TeamService = Depends(get_team_service)
) -> TeamWithHeroes:
    return svc.get_team(team_id)

@router.patch("/{team_id}", response_model=TeamPublic)
def update_team(
    team_id: int, 
    data: TeamUpdate, 
    svc: TeamService = Depends(get_team_service)
) -> TeamPublic:
    return svc.update(team_id, data)

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int, 
    svc: TeamService = Depends(get_team_service)
) -> None:
    svc.soft_delete(team_id)