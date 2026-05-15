from app.core.service import base_service
from app.modules.hero.models import Hero
from app.modules.hero.schemas import HeroCreate, HeroUpdate
from app.modules.hero.unit_of_work import HeroUnitOfWork
from sqlmodel import Session

class HeroService(base_service[Hero, HeroCreate, HeroUpdate, HeroUnitOfWork]):
    def __init__(self, session: Session):
        super().__init__(session=session,uow_class=HeroUnitOfWork,repo_name="heroes", model_class=Hero)