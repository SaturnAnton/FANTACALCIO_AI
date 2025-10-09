# create_test_user.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_test_user():
    db = SessionLocal()
    try:
        # Verifica se l'utente esiste già
        existing_user = db.query(User).filter(User.email == "demo@fantacalcio.ai").first()
        if existing_user:
            print("Utente demo già esistente")
            return
        
        user = User(
            email="demo@fantacalcio.ai",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        print("Utente demo creato con successo!")
        print("Email: demo@fantacalcio.ai")
        print("Password: demo123")
    except Exception as e:
        print(f"Errore: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()