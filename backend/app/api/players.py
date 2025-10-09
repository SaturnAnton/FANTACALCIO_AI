# app/api/players.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..db.database import get_db
from ..db.models import Player, Squad, SquadPlayer, User
from ..scraping.data_manager import DataManager
from ..scraping.unified_scraper import UnifiedPlayerScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/players/search")
async def search_players(
    name: str = Query(..., min_length=2, description="Nome del giocatore da cercare"),
    team: Optional[str] = Query(None, description="Filtra per squadra"),
    role: Optional[str] = Query(None, description="Filtra per ruolo (GK, DEF, MID, FWD)"),
    db: Session = Depends(get_db)
):
    """
    Cerca giocatori per nome con possibilità di filtrare per squadra e ruolo
    """
    try:
        # Query base per cercare giocatori
        query = db.query(Player)
        
        # Filtro per nome (case insensitive)
        if name:
            query = query.filter(Player.name.ilike(f"%{name}%"))
        
        # Filtro per squadra
        if team:
            query = query.filter(Player.team.ilike(f"%{team}%"))
        
        # Filtro per ruolo
        if role and role in ['GK', 'DEF', 'MID', 'FWD']:
            query = query.filter(Player.role == role)
        
        # Limita a 20 risultati
        players = query.limit(20).all()
        
        return {
            "status": "success",
            "count": len(players),
            "players": [
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "role": player.role,
                    "price": float(player.price) if player.price else 0.0,
                    "fantacalcio_data": player.fantacalcio_data or {},
                    "stats": player.stats or {}
                }
                for player in players
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching players: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nella ricerca: {str(e)}")

@router.get("/players/{player_id}/stats")
async def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    """
    Ottieni statistiche dettagliate per un giocatore specifico
    """
    try:
        player = db.query(Player).filter(Player.id == player_id).first()
        
        if not player:
            raise HTTPException(status_code=404, detail="Giocatore non trovato")
        
        return {
            "status": "success",
            "player_id": player_id,
            "stats": {
                "fantacalcio_data": player.fantacalcio_data or {},
                "fbref_data": player.stats.get('advanced', {}) if player.stats else {}
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting player stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel recupero statistiche: {str(e)}")

@router.post("/players/add-to-squad")
async def add_to_squad(
    player_data: dict,
    db: Session = Depends(get_db)
):
    """
    Aggiungi un giocatore alla squadra dell'utente
    """
    try:
        # Per ora usiamo un utente demo - in futuro prendere dall'autenticazione
        user_id = 1  # Utente demo
        
        # Verifica che il giocatore esista nel database
        existing_player = db.query(Player).filter(
            Player.name == player_data['name'],
            Player.team == player_data['team']
        ).first()
        
        player_id = None
        
        if existing_player:
            # Aggiorna i dati del giocatore esistente
            existing_player.role = player_data.get('role', existing_player.role)
            existing_player.price = player_data.get('price', existing_player.price)
            existing_player.stats = player_data.get('stats', existing_player.stats)
            existing_player.fantacalcio_data = player_data.get('fantacalcio_data', existing_player.fantacalcio_data)
            player_id = existing_player.id
        else:
            # Crea un nuovo giocatore
            new_player = Player(
                name=player_data['name'],
                team=player_data['team'],
                role=player_data['role'],
                price=player_data.get('price', 0.0),
                stats=player_data.get('stats', {}),
                fantacalcio_data=player_data.get('fantacalcio_data', {})
            )
            db.add(new_player)
            db.flush()  # Per ottenere l'ID senza commit
            player_id = new_player.id
        
        # Crea o recupera la squadra dell'utente
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            squad = Squad(user_id=user_id, name="La Mia Squadra")
            db.add(squad)
            db.flush()
        
        # Verifica che il giocatore non sia già in squadra
        existing_squad_player = db.query(SquadPlayer).filter(
            SquadPlayer.squad_id == squad.id,
            SquadPlayer.player_id == player_id
        ).first()
        
        if existing_squad_player:
            raise HTTPException(status_code=400, detail="Giocatore già presente in squadra")
        
        # Aggiungi il giocatore alla squadra
        squad_player = SquadPlayer(
            squad_id=squad.id,
            player_id=player_id
        )
        db.add(squad_player)
        
        # Commit di tutte le modifiche
        db.commit()
        
        return {
            "status": "success",
            "message": "Giocatore aggiunto alla squadra",
            "player_id": player_id,
            "squad_id": squad.id
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding player to squad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nell'aggiunta alla squadra: {str(e)}")

@router.delete("/players/{player_id}/remove-from-squad")
async def remove_from_squad(player_id: int, db: Session = Depends(get_db)):
    """
    Rimuovi un giocatore dalla squadra dell'utente
    """
    try:
        user_id = 1  # Utente demo
        
        # Trova la squadra dell'utente
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            raise HTTPException(status_code=404, detail="Squadra non trovata")
        
        # Trova l'associazione squadra-giocatore
        squad_player = db.query(SquadPlayer).filter(
            SquadPlayer.squad_id == squad.id,
            SquadPlayer.player_id == player_id
        ).first()
        
        if not squad_player:
            raise HTTPException(status_code=404, detail="Giocatore non trovato nella squadra")
        
        # Rimuovi l'associazione
        db.delete(squad_player)
        db.commit()
        
        return {
            "status": "success",
            "message": "Giocatore rimosso dalla squadra"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing player from squad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nella rimozione: {str(e)}")

@router.get("/squad")
async def get_user_squad(db: Session = Depends(get_db)):
    """
    Ottieni la squadra completa dell'utente con tutti i giocatori
    """
    try:
        user_id = 1  # Utente demo
        
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            return {
                "status": "success",
                "squad": {
                    "name": "La Mia Squadra",
                    "players": []
                }
            }
        
        # Recupera tutti i giocatori della squadra
        squad_players = db.query(SquadPlayer).filter(SquadPlayer.squad_id == squad.id).all()
        
        players = []
        for squad_player in squad_players:
            player = db.query(Player).filter(Player.id == squad_player.player_id).first()
            if player:
                players.append({
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "role": player.role,
                    "price": float(player.price) if player.price else 0.0,
                    "fantacalcio_data": player.fantacalcio_data or {},
                    "stats": player.stats or {}
                })
        
        return {
            "status": "success",
            "squad": {
                "id": squad.id,
                "name": squad.name,
                "player_count": len(players),
                "players": players
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user squad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel recupero squadra: {str(e)}")

@router.post("/squad/clear")
async def clear_squad(db: Session = Depends(get_db)):
    """
    Svuota completamente la squadra dell'utente
    """
    try:
        user_id = 1  # Utente demo
        
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            return {
                "status": "success",
                "message": "Squadra già vuota"
            }
        
        # Rimuovi tutte le associazioni giocatori-squadra
        deleted_count = db.query(SquadPlayer).filter(SquadPlayer.squad_id == squad.id).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Squadra svuotata - rimossi {deleted_count} giocatori"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing squad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nello svuotamento squadra: {str(e)}")

@router.get("/players/top/{role}")
async def get_top_players_by_role(
    role: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Ottieni i migliori giocatori per ruolo, ordinati per fantamedia
    """
    try:
        if role not in ['GK', 'DEF', 'MID', 'FWD']:
            raise HTTPException(status_code=400, detail="Ruolo non valido. Usa: GK, DEF, MID, FWD")
        
        # Query per giocatori del ruolo specificato
        players = db.query(Player).filter(Player.role == role).all()
        
        # Ordina per fantamedia (decrescente)
        sorted_players = sorted(
            players,
            key=lambda p: float(p.fantacalcio_data.get('basic', {}).get('fantamedia', 0) if p.fantacalcio_data else 0),
            reverse=True
        )[:limit]
        
        return {
            "status": "success",
            "role": role,
            "players": [
                {
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "price": float(player.price) if player.price else 0.0,
                    "fantamedia": player.fantacalcio_data.get('basic', {}).get('fantamedia', 0) if player.fantacalcio_data else 0,
                    "media_voto": player.fantacalcio_data.get('basic', {}).get('media_voto', 0) if player.fantacalcio_data else 0
                }
                for player in sorted_players
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top players by role: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel recupero top giocatori: {str(e)}")

@router.post("/players/refresh-data")
async def refresh_player_data(db: Session = Depends(get_db)):
    """
    Aggiorna i dati di tutti i giocatori dagli scraper
    """
    try:
        data_manager = DataManager(db)
        updated_players = data_manager.collect_and_process_data()
        
        return {
            "status": "success",
            "message": f"Dati aggiornati per {len(updated_players)} giocatori",
            "updated_count": len(updated_players)
        }
        
    except Exception as e:
        logger.error(f"Error refreshing player data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nell'aggiornamento dati: {str(e)}")

# Endpoint per statistiche squadra
@router.get("/squad/stats")
async def get_squad_stats(db: Session = Depends(get_db)):
    """
    Ottieni statistiche aggregate della squadra dell'utente
    """
    try:
        user_id = 1  # Utente demo
        
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            return {
                "status": "success",
                "stats": {
                    "total_players": 0,
                    "total_cost": 0,
                    "average_fantamedia": 0,
                    "players_by_role": {}
                }
            }
        
        # Recupera giocatori della squadra
        squad_players = db.query(SquadPlayer).filter(SquadPlayer.squad_id == squad.id).all()
        player_ids = [sp.player_id for sp in squad_players]
        
        players = db.query(Player).filter(Player.id.in_(player_ids)).all()
        
        # Calcola statistiche
        total_cost = sum(float(p.price) for p in players)
        
        fantamedie = []
        for p in players:
            if p.fantacalcio_data and p.fantacalcio_data.get('basic', {}).get('fantamedia'):
                try:
                    fantamedie.append(float(p.fantacalcio_data['basic']['fantamedia']))
                except (ValueError, TypeError):
                    pass
        
        average_fantamedia = sum(fantamedie) / len(fantamedie) if fantamedie else 0
        
        # Giocatori per ruolo
        players_by_role = {}
        for p in players:
            role = p.role
            if role not in players_by_role:
                players_by_role[role] = []
            players_by_role[role].append(p.name)
        
        return {
            "status": "success",
            "stats": {
                "total_players": len(players),
                "total_cost": total_cost,
                "average_fantamedia": round(average_fantamedia, 2),
                "players_by_role": players_by_role
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting squad stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore nel recupero statistiche squadra: {str(e)}")