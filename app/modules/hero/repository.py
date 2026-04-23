from typing import Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.modules.hero.models import Hero

class HeroRepository(BaseRepository[Hero]):
    """
    Acá irían las consultas específicas de Héroes.
    Ej: get_heroes_by_power_level()
    Las operaciones CRUD básicas ya las heredó.
    """

    def __init__(self, session):
        # Simplificado: El Unit of Work solo nos va a pasar la sesión.
        # Nosotros le "hardcodeamos" el modelo Heroe a la clase base.
        super().__init__(session, Hero)

    def get_by_id(self, hero_id: int) -> Optional[Hero]:
        # Armamos la consulta
        stmt = (
            select(Hero)
            .where(Hero.id == hero_id)
            .options(
                selectinload(Hero.weapon),
                selectinload(Hero.team),
                selectinload(Hero.teams)
            )
        )
        return self.session.exec(stmt).first()

    def get_by_alias(self, alias: str) -> Optional[Hero]:
        """
        Obtiene un héroe por su alias.

        Args:
            alias (str): Alias del héroe.

        Returns:
            Hero | None: Instancia encontrada o None si no existe.

        Nota:
            Se asume que 'alias' es único a nivel de base de datos.
        """
        return self.session.exec(
            select(Hero).where(Hero.alias == alias)
        ).first()
    
    def get_active(self, offset: int = 0, limit: int = 20) -> list[Hero]:
        """
        Obtiene héroes activos con paginación.

        Args:
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Hero]: Lista de héroes activos.

        Nota:
            - No se define orden explícito → resultados no determinísticos
            - Se usa '== True' por limitaciones del ORM (evita warnings de estilo)
        """
        return list(
            self.session.exec(
                select(Hero)
                .where(Hero.is_active == True)  # noqa: E712
                .offset(offset)
                .limit(limit)
            ).all()
        )