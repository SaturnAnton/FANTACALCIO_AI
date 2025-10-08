import logging
import pandas as pd
from sqlalchemy.orm import Session
from ..db.models import Player
from .fbref_scraper import FBrefScraper
from .fantacalcio_scraper import FantacalcioScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """
    Manages data collection, processing, and storage for the Fantacalcio AI application
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.fbref_scraper = FBrefScraper()
        self.fantacalcio_scraper = FantacalcioScraper()
    
    def collect_and_process_data(self):
        """Collect data from both sources and process it"""
        logger.info("Starting data collection process")
        
        # Collect data from FBref
        fbref_players = self.fbref_scraper.scrape_all_players()
        logger.info(f"Collected data for {len(fbref_players)} players from FBref")
        
        # Collect data from Fantacalcio.it
        fantacalcio_players = self.fantacalcio_scraper.scrape_all_players()
        logger.info(f"Collected data for {len(fantacalcio_players)} players from Fantacalcio.it")
        
        # Merge data from both sources
        merged_players = self._merge_player_data(fbref_players, fantacalcio_players)
        logger.info(f"Merged data for {len(merged_players)} players")
        
        # Save to database
        self._save_to_database(merged_players)
        
        return merged_players
    
    def _merge_player_data(self, fbref_players, fantacalcio_players):
        """Merge player data from both sources based on name and team"""
        merged_players = []
        
        # Create dataframes for easier merging
        fbref_df = pd.DataFrame(fbref_players)
        fantacalcio_df = pd.DataFrame(fantacalcio_players)
        
        # Normalize player names for better matching
        fbref_df['normalized_name'] = fbref_df['name'].apply(self._normalize_name)
        fantacalcio_df['normalized_name'] = fantacalcio_df['name'].apply(self._normalize_name)
        
        # Merge dataframes on normalized name and team
        for _, fbref_row in fbref_df.iterrows():
            # Find matching player in Fantacalcio data
            matches = fantacalcio_df[
                (fantacalcio_df['normalized_name'] == fbref_row['normalized_name']) &
                (fantacalcio_df['team'] == fbref_row['team'])
            ]
            
            if not matches.empty:
                # Use the first match
                fantacalcio_row = matches.iloc[0]
                
                # Create merged player data
                player = {
                    'name': fbref_row['name'],
                    'team': fbref_row['team'],
                    'role': fbref_row['role'],
                    'price': fantacalcio_row['price'],
                    'stats': fbref_row['stats'],
                    'fantacalcio_data': fantacalcio_row['fantacalcio_data']
                }
                
                merged_players.append(player)
            else:
                # Use only FBref data
                player = {
                    'name': fbref_row['name'],
                    'team': fbref_row['team'],
                    'role': fbref_row['role'],
                    'price': 0,
                    'stats': fbref_row['stats'],
                    'fantacalcio_data': {}
                }
                
                merged_players.append(player)
        
        # Add Fantacalcio players that weren't matched
        for _, fantacalcio_row in fantacalcio_df.iterrows():
            # Check if this player is already in merged_players
            if not any(
                self._normalize_name(p['name']) == fantacalcio_row['normalized_name'] and
                p['team'] == fantacalcio_row['team']
                for p in merged_players
            ):
                # Add player with only Fantacalcio data
                player = {
                    'name': fantacalcio_row['name'],
                    'team': fantacalcio_row['team'],
                    'role': fantacalcio_row['role'],
                    'price': fantacalcio_row['price'],
                    'stats': {},
                    'fantacalcio_data': fantacalcio_row['fantacalcio_data']
                }
                
                merged_players.append(player)
        
        return merged_players
    
    def _normalize_name(self, name):
        """Normalize player name for better matching"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove accents (simplified approach)
        accents = {
            'à': 'a', 'è': 'e', 'é': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
        }
        for accent, replacement in accents.items():
            name = name.replace(accent, replacement)
        
        # Remove special characters
        name = ''.join(c for c in name if c.isalnum() or c.isspace())
        
        return name
    
    def _save_to_database(self, players):
        """Save player data to database"""
        try:
            # Clear existing players (optional, depends on your update strategy)
            # self.db.query(Player).delete()
            
            # Add new players
            for player_data in players:
                # Check if player already exists
                existing_player = self.db.query(Player).filter(
                    Player.name == player_data['name'],
                    Player.team == player_data['team']
                ).first()
                
                if existing_player:
                    # Update existing player
                    existing_player.role = player_data['role']
                    existing_player.price = player_data['price']
                    existing_player.stats = player_data['stats']
                    existing_player.fantacalcio_data = player_data['fantacalcio_data']
                else:
                    # Create new player
                    new_player = Player(
                        name=player_data['name'],
                        team=player_data['team'],
                        role=player_data['role'],
                        price=player_data['price'],
                        stats=player_data['stats'],
                        fantacalcio_data=player_data['fantacalcio_data']
                    )
                    self.db.add(new_player)
            
            self.db.commit()
            logger.info(f"Saved {len(players)} players to database")
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving players to database: {str(e)}")
            return False