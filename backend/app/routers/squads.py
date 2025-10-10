from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models import Squad, SquadPlayer, Player
from app.schemas.schemas import PlayerCreate
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

@router.post("/create", response_model=dict)
def create_squad(name: str, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    squad = Squad(name=name, user_id=token.user_id)
    db.add(squad)
    db.commit()
    db.refresh(squad)
    return {"id": squad.id, "name": squad.name}

@router.post("/{squad_id}/add-player", response_model=dict)
def add_player_to_squad(squad_id: int, player: PlayerCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    squad = db.query(Squad).filter(Squad.id == squad_id, Squad.user_id == token.user_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squadra non trovata")
    
    db_player = db.query(Player).filter(Player.name == player.name, Player.team == player.team).first()
    if not db_player:
        db_player = Player(**player.dict())
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
    
    squad_player = SquadPlayer(squad_id=squad.id, player_id=db_player.id)
    db.add(squad_player)
    db.commit()
    return {"squad_id": squad.id, "player_id": db_player.id}
