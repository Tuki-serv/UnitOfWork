from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.hero.schemas import (
    HeroCreate, 
    HeroUpdate, 
    HeroPublic, 
    HeroPublicFull, 
    HeroList,
    HeroTeamAssign,
    TeamBasicRead
)
from app.modules.hero.service import HeroService

router = APIRouter(prefix="/heroes", tags=["heroes"])

# ── Factory de Dependencias ──
def get_hero_service(session: Session = Depends(get_session)) -> HeroService:
    """Inyecta el servicio con su Session de base de datos lista para usar."""
    return HeroService(session)

# ── Endpoints CRUD ────────────────────────────────────────────────────────────

@router.post("/", response_model=HeroPublic, status_code=status.HTTP_201_CREATED)
def create_hero(
    data: HeroCreate, 
    svc: HeroService = Depends(get_hero_service)
) -> HeroPublic:
    return svc.create(data)

@router.get("/", response_model=HeroList)
def list_heroes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: HeroService = Depends(get_hero_service)
) -> HeroList:
    return svc.get_all(offset=offset, limit=limit)

@router.get("/{hero_id}", response_model=HeroPublicFull)
def get_hero(
    hero_id: int, 
    svc: HeroService = Depends(get_hero_service)
) -> HeroPublicFull:
    return svc.get_by_id(hero_id)

@router.patch("/{hero_id}", response_model=HeroPublic)
def update_hero(
    hero_id: int, 
    data: HeroUpdate, 
    svc: HeroService = Depends(get_hero_service)
) -> HeroPublic:
    return svc.update(hero_id, data)

@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(
    hero_id: int, 
    svc: HeroService = Depends(get_hero_service)
) -> None:
    svc.soft_delete(hero_id)


# ── Endpoints N:M (Hero ↔ Team) ───────────────────────────────────────────────

@router.post("/{hero_id}/teams", response_model=HeroPublicFull)
def assign_to_team(
    hero_id: int,
    body: HeroTeamAssign,
    svc: HeroService = Depends(get_hero_service)
) -> HeroPublicFull:
    return svc.add_hero_to_team(hero_id, body.team_id)

@router.delete("/{hero_id}/teams/{team_id}", response_model=HeroPublicFull)
def remove_from_team(
    hero_id: int,
    team_id: int,
    svc: HeroService = Depends(get_hero_service)
) -> HeroPublicFull:
    return svc.remove_hero_from_team(hero_id, team_id)

@router.get("/{hero_id}/teams", response_model=List[TeamBasicRead])
def get_hero_teams(
    hero_id: int, 
    svc: HeroService = Depends(get_hero_service)
) -> List[TeamBasicRead]:
    return svc.get_hero_teams(hero_id)