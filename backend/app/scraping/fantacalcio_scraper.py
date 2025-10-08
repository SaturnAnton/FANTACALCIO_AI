import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FantacalcioScraper:
    """
    Scraper for Fantacalcio.it to collect fantasy ratings and performance data
    """
    
    def __init__(self):
        self.base_url = "https://www.fantacalcio.it"
        self.players_url = f"{self.base_url}/quotazioni/serie-a"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_players_list(self):
        """Get list of all players with their fantasy data"""
        try:
            response = requests.get(self.players_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players_table = soup.select('table.player-table tbody tr')
            
            players = []
            for row in players_table:
                # Extract player info
                player_name_elem = row.select_one('td.player-name a')
                if not player_name_elem:
                    continue
                
                player_name = player_name_elem.text.strip()
                player_url = f"{self.base_url}{player_name_elem['href']}"
                
                # Extract team and role
                team_elem = row.select_one('td.player-team img')
                team = team_elem['alt'] if team_elem and 'alt' in team_elem.attrs else ""
                
                role_elem = row.select_one('td.player-role')
                role = role_elem.text.strip() if role_elem else ""
                
                # Map role to standardized format
                standardized_role = "MID"  # Default
                if role:
                    if role == "P":
                        standardized_role = "GK"
                    elif role == "D":
                        standardized_role = "DEF"
                    elif role == "C":
                        standardized_role = "MID"
                    elif role == "A":
                        standardized_role = "FWD"
                
                # Extract price
                price_elem = row.select_one('td.player-price')
                price = price_elem.text.strip() if price_elem else "0"
                
                # Extract fantasy stats
                fanta_stats = {}
                
                # Average rating
                avg_rating_elem = row.select_one('td.player-average-rating')
                fanta_stats['average_rating'] = avg_rating_elem.text.strip() if avg_rating_elem else "0"
                
                # Goals
                goals_elem = row.select_one('td.player-goals')
                fanta_stats['goals'] = goals_elem.text.strip() if goals_elem else "0"
                
                # Assists
                assists_elem = row.select_one('td.player-assists')
                fanta_stats['assists'] = assists_elem.text.strip() if assists_elem else "0"
                
                # Yellow cards
                yellow_cards_elem = row.select_one('td.player-yellow-cards')
                fanta_stats['yellow_cards'] = yellow_cards_elem.text.strip() if yellow_cards_elem else "0"
                
                # Red cards
                red_cards_elem = row.select_one('td.player-red-cards')
                fanta_stats['red_cards'] = red_cards_elem.text.strip() if red_cards_elem else "0"
                
                players.append({
                    'name': player_name,
                    'team': team,
                    'role': standardized_role,
                    'price': float(price.replace(',', '.')) if price.replace(',', '.').replace('.', '').isdigit() else 0,
                    'url': player_url,
                    'fantacalcio_data': fanta_stats
                })
            
            logger.info(f"Found {len(players)} players on Fantacalcio.it")
            return players
        
        except Exception as e:
            logger.error(f"Error getting players list: {str(e)}")
            return []
    
    def get_player_details(self, player_url):
        """Get detailed fantasy data for a player"""
        try:
            response = requests.get(player_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed stats
            detailed_stats = {}
            
            # Last 5 games performance
            last_games = []
            games_table = soup.select('table.player-last-games tbody tr')
            for game_row in games_table[:5]:  # Get last 5 games
                cells = game_row.select('td')
                if len(cells) >= 4:
                    matchday = cells[0].text.strip()
                    opponent = cells[1].text.strip()
                    result = cells[2].text.strip()
                    rating = cells[3].text.strip()
                    
                    last_games.append({
                        'matchday': matchday,
                        'opponent': opponent,
                        'result': result,
                        'rating': rating
                    })
            
            detailed_stats['last_games'] = last_games
            
            # Season stats
            season_stats = {}
            stats_divs = soup.select('div.player-season-stats div.stat-item')
            for stat_div in stats_divs:
                label = stat_div.select_one('div.stat-label')
                value = stat_div.select_one('div.stat-value')
                
                if label and value:
                    stat_name = label.text.strip().lower().replace(' ', '_')
                    stat_value = value.text.strip()
                    season_stats[stat_name] = stat_value
            
            detailed_stats['season_stats'] = season_stats
            
            return detailed_stats
        
        except Exception as e:
            logger.error(f"Error getting player details from {player_url}: {str(e)}")
            return {}
    
    def scrape_all_players(self):
        """Scrape data for all players on Fantacalcio.it"""
        all_players = []
        
        # Get basic player list
        players = self.get_players_list()
        
        # Get detailed stats for each player
        for player in players:
            detailed_stats = self.get_player_details(player['url'])
            player['fantacalcio_data'].update(detailed_stats)
            all_players.append(player)
        
        logger.info(f"Scraped detailed data for {len(all_players)} players")
        return all_players
    
    def save_to_json(self, players, filename="fantacalcio_players.json"):
        """Save player data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(players, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved player data to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving player data to {filename}: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    scraper = FantacalcioScraper()
    players = scraper.scrape_all_players()
    scraper.save_to_json(players)