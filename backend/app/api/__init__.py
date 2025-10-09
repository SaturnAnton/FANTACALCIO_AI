# app/api/__init__.py
from fastapi import APIRouter
from . import auth, players  # Importa il nuovo modulo players

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(players.router, prefix="/players", tags=["players"])