from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.crud import players
from app.schemas.schemas import Player, PlayerCreate
from app.auth.auth import verify_token

router = APIRouter()

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

@router.get("/search", response_model=List[Player])
def search_players(name: str, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    return players.search_players(db, name)

@router.post("/add", response_model=Player)
def add_player(player: PlayerCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    return players.create_player(db, player)
