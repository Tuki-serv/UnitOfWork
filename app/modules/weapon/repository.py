from typing import Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.modules.weapon.models import Weapon

class WeaponRepository(BaseRepository[Weapon]):
    """
    Acá van las consultas específicas de Weapon.
    Las operaciones CRUD básicas ya las heredó de BaseRepository.
    """
    
    def __init__(self, session):
        # Simplificado: El Unit of Work solo nos va a pasar la sesión.
        # Nosotros le "hardcodeamos" el modelo Weapon a la clase base.
        super().__init__(session, Weapon)

    def get_by_id(self, weapon_id: int) -> Optional[Weapon]:
        # Armamos la consulta
        stmt = (
            select(Weapon)
            .where(Weapon.id == weapon_id)
            .options(selectinload(Weapon.hero))
        )
        
        # Ejecutamos y devolvemos el primer resultado (o None)
        return self.session.exec(stmt).first()