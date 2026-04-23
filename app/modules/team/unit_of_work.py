from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.team.repository import TeamRepository
from app.modules.hero.repository import HeroRepository

class TeamUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo teams.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Team.

        Extiende el UnitOfWork base y registra los repositorios necesarios
        para operar dentro de una misma transacción consistente.

        Repositorios expuestos:
            - teams: acceso a operaciones sobre Team
            - heroes: acceso a operaciones sobre Hero (cross-module, necesario
                      porque asignar/remover héroes toca ambas entidades en la misma transacción)

        Args:
            session (Session): Sesión activa de base de datos compartida
                               por todos los repositorios.

        Responsabilidad:
            - Garantizar que todas las operaciones (Team, Hero)
              se ejecuten dentro de la misma transacción
            - Centralizar commit() y rollback() (heredado del UoW base)
            - Coordinar múltiples repositorios bajo una única unidad de trabajo

        Uso típico:

            with TeamUnitOfWork(session) as uow:
                team = uow.teams.get_by_id(team_id)
                hero = uow.heroes.get_by_id(hero_id)
                hero.team_id = team.id
                uow.heroes.add(hero)
        """
        super().__init__(session)
        self.teams = TeamRepository(session)
        self.heroes = HeroRepository(session)