from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..db.database import get_db
from ..db.models import Player, Prediction, User, Squad, SquadPlayer
from ..ml.prediction_model import FantacalcioPredictionModel
from ..ml.formation_optimizer import FormationOptimizer
from pydantic import BaseModel
import logging

router = APIRouter()
prediction_model = FantacalcioPredictionModel()
formation_optimizer = FormationOptimizer()
logger = logging.getLogger(__name__)

class PredictionResponse(BaseModel):
    player_id: int
    player_name: str
    team: str
    role: str
    predicted_score: float
    confidence: float

class FormationResponse(BaseModel):
    formation: str
    players: List[PredictionResponse]
    expected_total_score: float

@router.get("/predict/{matchday}", response_model=List[PredictionResponse])
def get_predictions(
    matchday: int,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    team: Optional[str] = None,
    min_confidence: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get predicted performances for the specified matchday.
    Optionally filter by user's squad, player role, team, or minimum confidence.
    """
    query = db.query(
        Prediction, 
        Player.name.label("player_name"),
        Player.team,
        Player.role
    ).join(
        Player, 
        Prediction.player_id == Player.id
    ).filter(
        Prediction.matchday == matchday
    )
    
    # Filter by user's squad if user_id is provided
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        squad = db.query(Squad).filter(Squad.user_id == user_id).first()
        if not squad:
            raise HTTPException(status_code=404, detail="Squad not found for this user")
        
        # Get player IDs from the squad
        player_ids = [p.id for p in squad.players]
        query = query.filter(Prediction.player_id.in_(player_ids))
    
    # Apply additional filters
    if role:
        query = query.filter(Player.role == role)
    
    if team:
        query = query.filter(Player.team == team)
    
    if min_confidence:
        query = query.filter(Prediction.confidence >= min_confidence)
    
    # Execute query
    results = query.all()
    
    # Format response
    predictions = []
    for result in results:
        prediction, player_name, team, role = result
        predictions.append(PredictionResponse(
            player_id=prediction.player_id,
            player_name=player_name,
            team=team,
            role=role,
            predicted_score=prediction.predicted_score,
            confidence=prediction.confidence
        ))
    
    return predictions

@router.post("/predict/update/{matchday}")
def update_predictions(matchday: int, db: Session = Depends(get_db)):
    """
    Update predictions for all players for the specified matchday.
    This endpoint should be called after new data is scraped.
    """
    success = prediction_model.update_predictions(db, matchday)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update predictions")
    
    return {"status": "success", "message": f"Predictions updated for matchday {matchday}"}

@router.get("/optimize/formation/{user_id}")
def optimize_formation(
    user_id: int,
    matchday: int,
    formation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Optimize lineup for a user based on predictions for the specified matchday.
    Optionally specify a formation, otherwise the best formation will be determined.
    """
    # Get user's squad
    squad = db.query(Squad).filter(Squad.user_id == user_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found for this user")
    
    # Get all players in the squad with their predictions
    squad_players = []
    for player in squad.players:
        prediction = db.query(Prediction).filter(
            Prediction.player_id == player.id,
            Prediction.matchday == matchday
        ).first()
        
        if prediction:
            squad_players.append({
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "role": player.role,
                "price": player.price,
                "prediction": prediction.predicted_score,
                "confidence": prediction.confidence
            })
    
    # Use the formation optimizer to get the best lineup
    optimized = formation_optimizer.optimize_lineup(squad_players, formation, matchday)
    
    if not optimized:
        raise HTTPException(status_code=500, detail="Failed to optimize lineup")
    
    # Format the response
    lineup_players = []
    for role, players in optimized["lineup"].items():
        for player in players:
            lineup_players.append(PredictionResponse(
                player_id=player["id"],
                player_name=player["name"],
                team=player["team"],
                role=player["role"],
                predicted_score=player["prediction"],
                confidence=player.get("confidence", 0.8)
            ))
    
    return FormationResponse(
        formation=optimized["formation"],
        players=lineup_players,
        expected_total_score=sum(p.predicted_score for p in lineup_players)
    )

@router.get("/recommend/transfers/{user_id}")
def recommend_transfers(
    user_id: int,
    matchday: int,
    budget: float = 0,
    max_transfers: int = 2,
    db: Session = Depends(get_db)
):
    """
    Recommend player transfers for a user based on predictions and available budget.
    """
    # Get user's squad
    squad = db.query(Squad).filter(Squad.user_id == user_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found for this user")
    
    # Get all players in the squad with their predictions
    squad_players = []
    for player in squad.players:
        prediction = db.query(Prediction).filter(
            Prediction.player_id == player.id,
            Prediction.matchday == matchday
        ).first()
        
        if prediction:
            squad_players.append({
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "role": player.role,
                "price": player.price,
                "prediction": prediction.predicted_score,
                "confidence": prediction.confidence
            })
    
    # Get available players (not in user's squad)
    available_players = []
    for player in db.query(Player).all():
        if player.id not in [p["id"] for p in squad_players]:
            prediction = db.query(Prediction).filter(
                Prediction.player_id == player.id,
                Prediction.matchday == matchday
            ).first()
            
            if prediction:
                available_players.append({
                    "id": player.id,
                    "name": player.name,
                    "team": player.team,
                    "role": player.role,
                    "price": player.price,
                    "prediction": prediction.predicted_score,
                    "confidence": prediction.confidence
                })
    
    # Use the formation optimizer to recommend transfers
    recommendations = formation_optimizer.recommend_transfers(
        squad_players, available_players, budget, max_transfers
    )
    
    # Format the response
    return recommendations
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update predictions")
    
    return {"status": "success", "message": f"Predictions updated for matchday {matchday}"}

@router.get("/formation", response_model=FormationResponse)
def get_recommended_formation(
    user_id: int,
    matchday: int,
    db: Session = Depends(get_db)
):
    """
    Get recommended formation and starting 11 for a user's squad.
    """
    # Get user's squad
    squad = db.query(Squad).filter(Squad.user_id == user_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found for this user")
    
    # Get predictions for all players in the squad
    player_predictions = []
    for player in squad.players:
        prediction = db.query(Prediction).filter(
            Prediction.player_id == player.id,
            Prediction.matchday == matchday
        ).first()
        
        if prediction:
            player_predictions.append({
                "player_id": player.id,
                "player_name": player.name,
                "team": player.team,
                "role": player.role,
                "predicted_score": prediction.predicted_score,
                "confidence": prediction.confidence
            })
    
    # Group players by role
    goalkeepers = [p for p in player_predictions if p["role"] == "GK"]
    defenders = [p for p in player_predictions if p["role"] == "DEF"]
    midfielders = [p for p in player_predictions if p["role"] == "MID"]
    forwards = [p for p in player_predictions if p["role"] == "FWD"]
    
    # Sort each group by predicted score (descending)
    goalkeepers.sort(key=lambda x: x["predicted_score"], reverse=True)
    defenders.sort(key=lambda x: x["predicted_score"], reverse=True)
    midfielders.sort(key=lambda x: x["predicted_score"], reverse=True)
    forwards.sort(key=lambda x: x["predicted_score"], reverse=True)
    
    # Define possible formations
    formations = [
        {"name": "3-4-3", "DEF": 3, "MID": 4, "FWD": 3},
        {"name": "3-5-2", "DEF": 3, "MID": 5, "FWD": 2},
        {"name": "4-3-3", "DEF": 4, "MID": 3, "FWD": 3},
        {"name": "4-4-2", "DEF": 4, "MID": 4, "FWD": 2},
        {"name": "4-5-1", "DEF": 4, "MID": 5, "FWD": 1},
        {"name": "5-3-2", "DEF": 5, "MID": 3, "FWD": 2},
        {"name": "5-4-1", "DEF": 5, "MID": 4, "FWD": 1}
    ]
    
    # Find best formation
    best_formation = None
    best_score = 0
    best_players = []
    
    for formation in formations:
        # Check if we have enough players for this formation
        if (len(defenders) < formation["DEF"] or 
            len(midfielders) < formation["MID"] or 
            len(forwards) < formation["FWD"]):
            continue
        
        # Select top players for each position
        selected_gk = goalkeepers[0] if goalkeepers else None
        selected_def = defenders[:formation["DEF"]]
        selected_mid = midfielders[:formation["MID"]]
        selected_fwd = forwards[:formation["FWD"]]
        
        # Skip if we don't have a goalkeeper
        if not selected_gk:
            continue
        
        # Calculate total expected score
        total_score = selected_gk["predicted_score"]
        total_score += sum(p["predicted_score"] for p in selected_def)
        total_score += sum(p["predicted_score"] for p in selected_mid)
        total_score += sum(p["predicted_score"] for p in selected_fwd)
        
        # Update best formation if this one is better
        if total_score > best_score:
            best_score = total_score
            best_formation = formation["name"]
            best_players = [selected_gk] + selected_def + selected_mid + selected_fwd
    
    # If no valid formation found
    if not best_formation:
        raise HTTPException(
            status_code=400, 
            detail="Could not find a valid formation. Make sure your squad has enough players in each role."
        )
    
    # Convert to response model
    response_players = [
        PredictionResponse(
            player_id=p["player_id"],
            player_name=p["player_name"],
            team=p["team"],
            role=p["role"],
            predicted_score=p["predicted_score"],
            confidence=p["confidence"]
        ) for p in best_players
    ]
    
    return FormationResponse(
        formation=best_formation,
        players=response_players,
        expected_total_score=best_score
    )

@router.get("/trade-suggestions")
def get_trade_suggestions(
    user_id: int,
    matchday: int,
    role: Optional[str] = None,
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get suggested trades for underperforming players in the user's squad.
    """
    # Get user's squad
    squad = db.query(Squad).filter(Squad.user_id == user_id).first()
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found for this user")
    
    # Get all players with their predictions
    all_players = db.query(
        Player, 
        Prediction.predicted_score,
        Prediction.confidence
    ).join(
        Prediction,
        Player.id == Prediction.player_id
    ).filter(
        Prediction.matchday == matchday
    )
    
    # Filter by role if specified
    if role:
        all_players = all_players.filter(Player.role == role)
    
    all_players = all_players.all()
    
    # Group players by role
    players_by_role = {}
    for player, score, confidence in all_players:
        if player.role not in players_by_role:
            players_by_role[player.role] = []
        
        players_by_role[player.role].append({
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "role": player.role,
            "price": player.price,
            "predicted_score": score,
            "confidence": confidence,
            "in_squad": player in squad.players
        })
    
    # Find underperforming players in the squad
    suggestions = []
    for role_name, players in players_by_role.items():
        # Skip if role filter doesn't match
        if role and role != role_name:
            continue
        
        # Get squad players for this role
        squad_players = [p for p in players if p["in_squad"]]
        
        # Sort squad players by predicted score (ascending)
        squad_players.sort(key=lambda x: x["predicted_score"])
        
        # Get non-squad players for this role
        available_players = [p for p in players if not p["in_squad"]]
        
        # Sort available players by predicted score (descending)
        available_players.sort(key=lambda x: x["predicted_score"], reverse=True)
        
        # For each underperforming player, suggest better alternatives
        for underperforming in squad_players[:limit]:
            better_alternatives = [
                p for p in available_players 
                if p["predicted_score"] > underperforming["predicted_score"]
            ][:3]  # Limit to top 3 alternatives
            
            if better_alternatives:
                suggestions.append({
                    "underperforming_player": underperforming,
                    "alternatives": better_alternatives
                })
    
    return {"trade_suggestions": suggestions[:limit]}