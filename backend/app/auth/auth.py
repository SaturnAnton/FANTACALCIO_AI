from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.schemas.schemas import TokenData

# 🔥 CAMBIA: usa Argon2 invece di bcrypt (non ha limite di 72 byte)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "INSERISCI_QUI_UNA_CHIAVE_RANDOM"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return TokenData(user_id=user_id)
    except JWTError:
        return None