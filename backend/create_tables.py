# create_tables.py
import sys
import os

# Aggiungi la directory app al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base
# Importa tutti i modelli
from app.db.models import User, Player, Squad, SquadPlayer, Prediction

def create_tables():
    print("Creazione di tutte le tabelle nel database...")
    Base.metadata.create_all(bind=engine)
    print("Tutte le tabelle create con successo!")
    
    # Verifica le tabelle create
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tabelle create:", tables)

if __name__ == "__main__":
    create_tables()