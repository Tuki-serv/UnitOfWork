from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.weapon.schemas import (
    WeaponCreate, 
    WeaponRead, 
    WeaponUpdate, 
    WeaponList,
    WeaponReadWithHero
)
from app.modules.weapon.service import WeaponService

router = APIRouter(prefix="/weapons", tags=["weapons"])

# ── Factory de Dependencias ──
def get_weapon_service(session: Session = Depends(get_session)) -> WeaponService:
    return WeaponService(session)

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=WeaponRead, status_code=status.HTTP_201_CREATED)
def create_weapon(
    data: WeaponCreate, 
    svc: WeaponService = Depends(get_weapon_service)
) -> WeaponRead:
    return svc.create(data)

@router.get("/", response_model=WeaponList)
def list_weapons(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: WeaponService = Depends(get_weapon_service)
) -> WeaponList:
    return svc.get_all(offset=offset, limit=limit)

@router.get("/{weapon_id}", response_model=WeaponReadWithHero)
def get_weapon(
    weapon_id: int, 
    svc: WeaponService = Depends(get_weapon_service)
) -> WeaponReadWithHero:
    return svc.get_by_id(weapon_id)

@router.patch("/{weapon_id}", response_model=WeaponRead)
def update_weapon(
    weapon_id: int, 
    data: WeaponUpdate, 
    svc: WeaponService = Depends(get_weapon_service)
) -> WeaponRead:
    return svc.update(weapon_id, data)

@router.delete("/{weapon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weapon(
    weapon_id: int, 
    svc: WeaponService = Depends(get_weapon_service)
) -> None:
    svc.soft_delete(weapon_id)