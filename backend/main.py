from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, predictions, players  # Aggiungi 'players' qui

app = FastAPI(title="Fantacalcio AI API", description="API for Fantacalcio AI application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Fantacalcio AI API"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(players.router, prefix="/api", tags=["Players"])  # Aggiungi questa linea

# Other routers (commented out for now)
# app.include_router(squad_router, prefix="/squad", tags=["Squad"])
# app.include_router(formation_router, prefix="/formation", tags=["Formation"])
# app.include_router(trade_router, prefix="/trade-suggestions", tags=["Trades"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)