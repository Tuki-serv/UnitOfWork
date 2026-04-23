from sqlalchemy import text
from app.core.database import engine

def nuke_database():
    with engine.connect() as conn:
        # Borramos la tabla que confunde a Alembic
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        
        # De paso, limpiamos las tablas viejas para que no haya conflictos
        conn.execute(text("DROP TABLE IF EXISTS hero_team_link CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS hero CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS weapon CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS team CASCADE;"))
        
        conn.commit()
    print("💥 ¡Base de datos reseteada por completo! Alembic ya no tiene memoria.")

if __name__ == "__main__":
    nuke_database()