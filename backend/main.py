from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.routers import auth, players, predictions, squads

# Crea tabelle
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fantacalcio API")

# 🔥 CONFIGURA CORS - AGGIUNGI QUESTO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL del tuo frontend React
    allow_credentials=True,
    allow_methods=["*"],  # Permetti tutti i metodi (GET, POST, OPTIONS, ecc.)
    allow_headers=["*"],  # Permetti tutti gli headers
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players.router, prefix="/api/players", tags=["Players"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(squads.router, prefix="/api/squads", tags=["Squads"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)