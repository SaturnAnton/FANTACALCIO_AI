from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.crud import players
from app.schemas.schemas import Prediction, PredictionCreate
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

@router.post("/add", response_model=Prediction)
def add_prediction(pred: PredictionCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    return players.create_prediction(db, pred)
