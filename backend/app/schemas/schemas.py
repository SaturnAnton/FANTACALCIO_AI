from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict

# ---------- Player ----------
class PlayerBase(BaseModel):
    name: str
    team: str
    role: str
    price: float
    stats: Optional[Dict] = {}
    fantacalcio_data: Optional[Dict] = {}

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    class Config:
        from_attributes = True

# ---------- Prediction ----------
class PredictionCreate(BaseModel):
    player_id: int
    matchday: int
    predicted_fantamedia: float
    predicted_media_voto: float

class Prediction(PredictionCreate):
    id: int
    class Config:
        from_attributes = True

# ---------- User ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError('La password deve essere di almeno 8 caratteri')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('La password non può superare i 72 byte (circa 50-60 caratteri)')
        return v

class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int