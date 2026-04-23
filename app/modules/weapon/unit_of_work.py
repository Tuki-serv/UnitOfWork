from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.weapon.repository import WeaponRepository
from app.modules.hero.repository import HeroRepository

class WeaponUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo weapons.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Weapon.

        Extiende el UnitOfWork base y registra los repositorios necesarios
        para operar dentro de una misma transacción consistente.

        Repositorios expuestos:
            - weapons: acceso a operaciones sobre Weapon
            - heroes: acceso a operaciones sobre Hero (usado para validaciones
                      de integridad o verificación de dueños antes de persistir armas)

        Args:
            session (Session): Sesión activa de base de datos compartida
                               por todos los repositorios.

        Responsabilidad:
            - Garantizar que todas las operaciones (Weapon, Hero, etc.)
              se ejecuten dentro de la misma transacción
            - Centralizar commit() y rollback() (heredado del UoW base)
            - Coordinar múltiples repositorios bajo una única unidad de trabajo

        Uso típico:

            with WeaponUnitOfWork(session) as uow:
                hero = uow.heroes.get_by_id(hero_id)
                weapon = Weapon(...)
                weapon.hero = hero  # Asignamos la relación
                uow.weapons.add(weapon)
        """
        super().__init__(session)
        self.weapons = WeaponRepository(session)
        self.heroes = HeroRepository(session)