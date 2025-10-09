# app/scraping/data_manager.py
import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
import unicodedata
import re

from ..db.models import Player
from .unified_scraper import UnifiedPlayerScraper  # Usa UnifiedScraper invece dei singoli

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """
    Manages data collection, processing, and storage for the Fantacalcio AI application
    Updated to use UnifiedPlayerScraper
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.unified_scraper = UnifiedPlayerScraper()
    
    def collect_and_process_data(self, league: str = "serie_a") -> List[Dict]:
        """Collect data from unified scraper and process it"""
        logger.info(f"Starting data collection process for {league}")
        
        try:
            # Use unified scraper to get merged data
            merged_players = self.unified_scraper.merge_player_data(league)
            logger.info(f"Collected unified data for {len(merged_players)} players")
            
            # Process and clean data
            processed_players = self._process_player_data(merged_players)
            
            # Save to database
            success = self._save_to_database(processed_players)
            
            if success:
                logger.info("Data collection and processing completed successfully")
                return processed_players
            else:
                logger.error("Failed to save data to database")
                return []
                
        except Exception as e:
            logger.error(f"Error in data collection process: {str(e)}")
            return []
    
    def _process_player_data(self, players: List[Dict]) -> List[Dict]:
        """Process and clean player data for database storage"""
        processed_players = []
        
        for player in players:
            try:
                processed_player = {
                    'name': player['name'],
                    'team': player['team'],
                    'role': player['role'],
                    'price': float(player['price']) if player['price'] else 0.0,
                    'stats': player.get('fbref_data', {}),
                    'fantacalcio_data': player.get('fantacalcio_data', {})
                }
                
                # Validate required fields
                if processed_player['name'] and processed_player['team']:
                    processed_players.append(processed_player)
                else:
                    logger.warning(f"Skipping player with missing data: {player.get('name', 'Unknown')}")
                    
            except Exception as e:
                logger.warning(f"Error processing player {player.get('name', 'Unknown')}: {str(e)}")
                continue
        
        logger.info(f"Processed {len(processed_players)} players")
        return processed_players
    
    def _save_to_database(self, players: List[Dict]) -> bool:
        """Save player data to database with improved error handling"""
        try:
            success_count = 0
            error_count = 0
            
            for player_data in players:
                try:
                    # Check if player already exists
                    existing_player = self.db.query(Player).filter(
                        Player.name == player_data['name'],
                        Player.team == player_data['team']
                    ).first()
                    
                    if existing_player:
                        # Update existing player
                        existing_player.role = player_data['role']
                        existing_player.price = player_data['price']
                        existing_player.stats = player_data.get('stats', {})
                        existing_player.fantacalcio_data = player_data.get('fantacalcio_data', {})
                    else:
                        # Create new player
                        new_player = Player(
                            name=player_data['name'],
                            team=player_data['team'],
                            role=player_data['role'],
                            price=player_data['price'],
                            stats=player_data.get('stats', {}),
                            fantacalcio_data=player_data.get('fantacalcio_data', {})
                        )
                        self.db.add(new_player)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving player {player_data.get('name', 'Unknown')}: {str(e)}")
                    error_count += 1
                    continue
            
            # Commit all changes
            self.db.commit()
            logger.info(f"Database save completed: {success_count} successful, {error_count} errors")
            return error_count == 0
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during save: {str(e)}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during save: {str(e)}")
            return False

    # ... altri metodi rimangono invariati