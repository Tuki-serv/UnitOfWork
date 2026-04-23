from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.hero.models import Hero
from app.modules.hero.schemas import (
    HeroCreate, 
    HeroUpdate, 
    HeroPublic, 
    HeroPublicFull, 
    HeroList,
    TeamBasicRead
)
from app.modules.hero.unit_of_work import HeroUnitOfWork


class HeroService:
    """
    Capa de lógica de negocio para Heroes.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: HeroUnitOfWork, hero_id: int) -> Hero:
        hero = uow.heroes.get_by_id(hero_id)
        if not hero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hero con id={hero_id} no encontrado",
            )
        return hero

    def _assert_alias_unique(self, uow: HeroUnitOfWork, alias: str) -> None:
        # Asume que agregaste get_by_alias en HeroRepository
        if uow.heroes.get_by_alias(alias):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El alias '{alias}' ya está en uso",
            )

    def _get_team_or_404(self, uow: HeroUnitOfWork, team_id: int):
        team = uow.teams.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404, detail=f"Team con id={team_id} no encontrado"
            )
        return team

    # ── Casos de uso CRUD ─────────────────────────────────────────────────────

    def create(self, data: HeroCreate) -> HeroPublic:
        with HeroUnitOfWork(self._session) as uow:
            self._assert_alias_unique(uow, data.alias)
            
            # Verificamos si los IDs enviados existen
            if data.team_id:
                self._get_team_or_404(uow, data.team_id)
            if data.weapon_id:
                # Opcional: Podrías hacer un helper _get_weapon_or_404
                if not uow.weapons.get_by_id(data.weapon_id):
                    raise HTTPException(status_code=404, detail="Weapon no encontrada")

            hero = Hero.model_validate(data)
            uow.heroes.add(hero)
            result = HeroPublic.model_validate(hero)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> HeroList:
        with HeroUnitOfWork(self._session) as uow:
            heroes = uow.heroes.get_active(offset=offset, limit=limit)
            total = uow.heroes.count_model()

            result = HeroList(
                total=total,
                data=[HeroPublic.model_validate(h) for h in heroes]
            )
        return result

    def get_by_id(self, hero_id: int) -> HeroPublicFull:
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            result = HeroPublicFull.model_validate(hero)
        return result

    def update(self, hero_id: int, data: HeroUpdate) -> HeroPublic:
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)

            if data.alias and data.alias != hero.alias:
                self._assert_alias_unique(uow, data.alias)

            if data.team_id and data.team_id != hero.team_id:
                self._get_team_or_404(uow, data.team_id)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(hero, field, value)

            uow.heroes.add(hero)
            result = HeroPublic.model_validate(hero)
        return result

    def soft_delete(self, hero_id: int) -> None:
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            hero.is_active = False
            uow.heroes.add(hero)

    # ── Casos de uso N:M (Hero ↔ Team) ────────────────────────────────────────

    def add_hero_to_team(self, hero_id: int, team_id: int) -> HeroPublicFull:
        """Agrega el Hero a un Team (N:M). ¡SQLModel maneja la tabla intermedia!"""
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            team = self._get_team_or_404(uow, team_id)

            # Evitar duplicados en la lista
            if team not in hero.teams:
                hero.teams.append(team)
                uow.heroes.add(hero)
            
            result = HeroPublicFull.model_validate(hero)
        return result

    def remove_hero_from_team(self, hero_id: int, team_id: int) -> HeroPublicFull:
        """Elimina el Hero de un Team (N:M)."""
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            team = self._get_team_or_404(uow, team_id)

            if team in hero.teams:
                hero.teams.remove(team)
                uow.heroes.add(hero)
            
            result = HeroPublicFull.model_validate(hero)
        return result

    def get_hero_teams(self, hero_id: int) -> List[TeamBasicRead]:
        """Lista todos los Teams secundarios del Hero (N:M)."""
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            result = [TeamBasicRead.model_validate(t) for t in hero.teams]
        return result