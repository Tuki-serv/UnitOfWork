from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.hero.models import Hero


class Weapon(SQLModel, table=True):
    """
    Relación 1:1 con Hero.
    La FK (weapon_id) vive en Hero, por lo que Weapon no necesita columna extra.
    back_populates='weapon' conecta con Hero.weapon
    """

    __tablename__ = "weapon"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)

    # Lado inverso 1:1 → un Weapon pertenece a un solo Hero
    hero: Optional["Hero"] = Relationship(back_populates="weapon")