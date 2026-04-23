"""
Script de seed para desarrollo.
Ejecutar: python seed.py
Crea datos de prueba para demostrar el flujo completo.
"""
from sqlmodel import Session, SQLModel
from app.core.database import engine
from app.modules.hero.models import Hero, HeroTeamLink
from app.modules.team.models import Team
from app.modules.weapon.models import Weapon


def seed() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Equipos
        avengers = Team(name="Avengers", headquarters="Stark Tower, New York")
        xmen = Team(name="X-Men", headquarters="Xavier Institute, Westchester")
        session.add(avengers)
        session.add(xmen)
        session.flush()

        # Weapons
        shield = Weapon(name="Vibranium Shield", description="Escudo indestructible de Cap")
        suit   = Weapon(name="Iron Suit Mark L",  description="Armadura nanotecnológica")
        bow    = Weapon(name="Compound Bow",      description="Arco de precisión")
        session.add_all([shield, suit, bow])
        session.flush()

        # Héroes
        cap      = Hero(name="Steve Rogers",  alias="Captain America", power_level=88, team_id=avengers.id, weapon_id=shield.id)
        ironman  = Hero(name="Tony Stark",    alias="Iron Man",        power_level=95, team_id=avengers.id, weapon_id=suit.id)
        widow    = Hero(name="Natasha R.",    alias="Black Widow",     power_level=80, team_id=avengers.id)
        cyclops  = Hero(name="Scott Summers", alias="Cyclops",         power_level=82, team_id=xmen.id)
        phoenix  = Hero(name="Jean Grey",     alias="Phoenix",         power_level=98, team_id=xmen.id)
        spidey   = Hero(name="Peter Parker",  alias="Spider-Man",      power_level=85)
        
        session.add_all([cap, ironman, widow, cyclops, phoenix, spidey])
        session.flush()

        # Relaciones N:M (afiliaciones extra)
        session.add(HeroTeamLink(hero_id=cap.id,     team_id=xmen.id))
        session.add(HeroTeamLink(hero_id=spidey.id,  team_id=avengers.id))

        session.commit()
        print(f"Seed OK: 6 héroes, 2 equipos, 3 weapons creados.")


if __name__ == "__main__":
    seed()