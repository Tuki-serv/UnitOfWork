from app.core.service import base_service as BaseService
from app.modules.hero.models import Hero
from app.modules.hero.schemas import HeroCreate, HeroUpdate
from app.modules.hero.unit_of_work import HeroUnitOfWork

class HeroService(BaseService[Hero, HeroCreate, HeroUpdate, HeroUnitOfWork]):
    def __init__(self, uow: HeroUnitOfWork):
        super().__init__(uow, "heroes", Hero)