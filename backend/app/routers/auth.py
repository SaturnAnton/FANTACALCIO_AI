from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate, UserOut, Token
from app.crud import users
from app.auth.auth import create_access_token, verify_password
from app.db.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if users.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email già registrata")
    return users.create_user(db, user)

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o password errati")
    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}
