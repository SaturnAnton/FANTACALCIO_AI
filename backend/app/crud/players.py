from sqlalchemy.orm import Session
from app.db.models import Player, Prediction
from app.schemas.schemas import PlayerCreate, PredictionCreate

def create_player(db: Session, player: PlayerCreate):
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def search_players(db: Session, name: str):
    return db.query(Player).filter(Player.name.ilike(f"%{name}%")).all()

def create_prediction(db: Session, pred: PredictionCreate):
    db_pred = Prediction(**pred.dict())
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred
