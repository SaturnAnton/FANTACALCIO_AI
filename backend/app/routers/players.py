from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from pathlib import Path

from app.db.database import SessionLocal
from app.crud import players as crud_players
from app.schemas.schemas import Player, PlayerCreate
from app.auth.auth import verify_token

router = APIRouter()

# 🔹 Percorso corretto al file JSON
DATA_FILE = Path(__file__).parent.parent.parent / "players_data.json"

# -------------------- Public Endpoint -------------------- #
@router.get("/", tags=["Players"])
async def get_all_players():
    """
    Restituisce tutti i giocatori dal file JSON (pubblico)
    """
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return {"players": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File JSON non trovato")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Errore nel parsing del JSON")


# -------------------- Database / Auth Endpoints -------------------- #
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Token non valido")
    return user_data

@router.get("/search", response_model=List[Player], tags=["Players"])
def search_players(name: str, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    """
    Ricerca giocatori nel database tramite nome (protetto da token)
    """
    return crud_players.search_players(db, name)

@router.post("/add", response_model=Player, tags=["Players"])
def add_player(player: PlayerCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    """
    Aggiunge un nuovo giocatore nel database (protetto da token)
    """
    return crud_players.create_player(db, player)
