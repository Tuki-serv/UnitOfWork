from typing import Generic, TypeVar, Type, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel
from datetime import datetime, timezone
from app.core.unit_of_work import UnitOfWork
from app.core.repository import BaseRepository

ModelType = TypeVar("ModelType", bound=SQLModel) # hero
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
UoWType = TypeVar("UowType", bound=UnitOfWork)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class base_service(Generic[ModelType, CreateSchemaType, UpdateSchemaType, UoWType]):
    def __init__(self, uow: UoWType, repo_name: str, model_class: Type[ModelType],):
        self.uow = uow
        self.repo = self._repo()
        self.model_class = model_class

    def _repo(self) -> BaseRepository[ModelType]:
        return getattr(self.uow, self.repo_name)
    
    
    def get_all(self, offset: int = 0, limit: int = 20):
        with self.uow as uow:

        
            items = self.uow.repo.get_all_by_state(offset=offset, limit= limit)

            # items = self._repo.get_all_by_state(offset=offset, limit= limit)
            total = self.uow._repo.count_model()
            return {"data": items, "total": total}
        
    def _get_or_404(self, item_id) -> ModelType:
        item = self._repo.get_by_id(item_id)
        if not item or getattr(item, "deleted_at", None) is not None:
            raise HTTPException(status_code=404, detail=f"{self.model_class.__name__} not found")
        return item

    def get_by_id(self, item_id: int | str) -> ModelType:
        with self.uow as uow:
            return self._get_or_404(item_id)
        
    def create(self, item_in: CreateSchemaType) -> ModelType:
        with self.uow as uow:
            nuevo_item = self.model_class(**item_in.model_dump())
            self._repo.add(nuevo_item)
            return nuevo_item
        
    def update(self, item_id: int | str, item_in: UpdateSchemaType) -> ModelType:
        with self.uow as uow:
            item_db = self.get_by_id(item_id)

            update_data = item_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(item_db, key, value)

            if hasattr(item_db, "updated_at"):
                item_db.updated_at = datetime.now(timezone.utc)

            self._repo.update(item_db)
            return item_db
        
    def delete(self, item_id: int | str):
        with self.uow as uow:
            item_db = self._get_or_404(item_id)

            if hasattr(item_db, "deleted_at"):
                item_db.deleted_at = datetime.now(timezone.utc)
                self._repo.update(item_db)

        return {"message": f"{self.model_class.__name__} eliminado/a correctamente"}