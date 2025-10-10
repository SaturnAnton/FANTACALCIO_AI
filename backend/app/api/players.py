# app/api/players.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import sqlite3
import unicodedata
import re

router = APIRouter()

DB_PATH = "fantacalcio.db"

def normalize_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ASCII','ignore').decode('ASCII')
    name = re.sub(r'\s+', ' ', name.lower().strip())
    return name

@router.get("/search")
def search_players(name: str = Query(..., min_length=2)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query_norm = f"%{normalize_name(name)}%"
    cursor.execute("""
        SELECT id, name, team, role, price
        FROM players
    """)
    players = cursor.fetchall()
    conn.close()

    # Ricerca fuzzy semplice
    results = []
    for p in players:
        pid, pname, pteam, prole, pprice = p
        if query_norm.strip('%') in normalize_name(pname):
            results.append({
                "id": pid,
                "name": pname,
                "team": pteam,
                "role": prole,
                "price": pprice
            })
    return JSONResponse({"status": "success", "players": results})
