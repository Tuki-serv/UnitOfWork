from typing import Generic, TypeVar, Type, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel, Session
from datetime import datetime, timezone
from app.core.unit_of_work import UnitOfWork
from app.core.repository import BaseRepository
from typing import Protocol, runtime_checkable

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
UoWType = TypeVar("UowType", bound=UnitOfWork)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class base_service(Generic[ModelType, CreateSchemaType, UpdateSchemaType, UoWType]):
    def __init__(self,session: Session, uow_class: UoWType, repo_name: str, model_class: Type[ModelType],):
        self.session = session
        self.uow = uow_class(session)
        self.repo_name = repo_name
        self.model_class = model_class

    @property
    def repo(self) -> BaseRepository[ModelType]:
        return getattr(self.uow, self.repo_name)
    
    
    def get_all(self, offset: int = 0, limit: int = 20):
        with self.uow:
            items = self.repo.get_all_by_state(offset=offset, limit=limit)
            total = self.repo.count_model()
            return {"data": items, "total": total}