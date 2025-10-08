import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FBrefScraper:
    """
    Scraper for FBref.com to collect advanced football statistics for Serie A players
    """
    
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.serie_a_url = f"{self.base_url}/en/comps/11/Serie-A-Stats"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_team_urls(self):
        """Get URLs for all Serie A teams"""
        try:
            response = requests.get(self.serie_a_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            standings_table = soup.select_one('table.stats_table')
            
            team_urls = []
            if standings_table:
                team_links = standings_table.select('tbody tr td[data-stat="squad"] a')
                for link in team_links:
                    team_urls.append({
                        'name': link.text,
                        'url': f"{self.base_url}{link['href']}"
                    })
            
            logger.info(f"Found {len(team_urls)} Serie A teams")
            return team_urls
        
        except Exception as e:
            logger.error(f"Error getting team URLs: {str(e)}")
            return []
    
    def get_players_from_team(self, team_url):
        """Get player data from a team page"""
        try:
            response = requests.get(team_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            team_name = soup.select_one('h1[itemprop="name"] span').text
            
            # Get player stats table
            players_table = soup.select_one('table#stats_standard_squads')
            
            players = []
            if players_table:
                rows = players_table.select('tbody tr')
                for row in rows:
                    # Skip non-player rows
                    if 'class' in row.attrs and 'thead' in row['class']:
                        continue
                    
                    player_link = row.select_one('th[data-stat="player"] a')
                    if not player_link:
                        continue
                    
                    player_name = player_link.text
                    player_url = f"{self.base_url}{player_link['href']}"
                    
                    # Get basic stats
                    position = row.select_one('td[data-stat="position"]').text if row.select_one('td[data-stat="position"]') else ""
                    age = row.select_one('td[data-stat="age"]').text if row.select_one('td[data-stat="age"]') else ""
                    matches = row.select_one('td[data-stat="games"]').text if row.select_one('td[data-stat="games"]') else ""
                    starts = row.select_one('td[data-stat="games_starts"]').text if row.select_one('td[data-stat="games_starts"]') else ""
                    minutes = row.select_one('td[data-stat="minutes"]').text if row.select_one('td[data-stat="minutes"]') else ""
                    goals = row.select_one('td[data-stat="goals"]').text if row.select_one('td[data-stat="goals"]') else ""
                    assists = row.select_one('td[data-stat="assists"]').text if row.select_one('td[data-stat="assists"]') else ""
                    
                    # Map position to Fantacalcio role
                    role = "MID"  # Default
                    if position:
                        if "GK" in position:
                            role = "GK"
                        elif "DF" in position:
                            role = "DEF"
                        elif "FW" in position or "CF" in position:
                            role = "FWD"
                    
                    players.append({
                        'name': player_name,
                        'team': team_name,
                        'role': role,
                        'url': player_url,
                        'stats': {
                            'position': position,
                            'age': age,
                            'matches': matches,
                            'starts': starts,
                            'minutes': minutes,
                            'goals': goals,
                            'assists': assists
                        }
                    })
            
            logger.info(f"Found {len(players)} players for {team_name}")
            return players
        
        except Exception as e:
            logger.error(f"Error getting players from team {team_url}: {str(e)}")
            return []
    
    def get_player_detailed_stats(self, player_url):
        """Get detailed stats for a player"""
        try:
            response = requests.get(player_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get advanced stats
            stats = {}
            
            # Shooting stats
            shooting_table = soup.select_one('table#stats_shooting_dom_lg')
            if shooting_table:
                stats['shooting'] = self._parse_stats_table(shooting_table)
            
            # Passing stats
            passing_table = soup.select_one('table#stats_passing_dom_lg')
            if passing_table:
                stats['passing'] = self._parse_stats_table(passing_table)
            
            # Defensive stats
            defense_table = soup.select_one('table#stats_defense_dom_lg')
            if defense_table:
                stats['defense'] = self._parse_stats_table(defense_table)
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting detailed stats for player {player_url}: {str(e)}")
            return {}
    
    def _parse_stats_table(self, table):
        """Parse a stats table into a dictionary"""
        stats = {}
        
        # Get the most recent season's data (first row)
        row = table.select('tbody tr')[0] if table.select('tbody tr') else None
        if not row:
            return stats
        
        # Get all stat columns
        for cell in row.select('td'):
            if 'data-stat' in cell.attrs:
                stat_name = cell['data-stat']
                stat_value = cell.text.strip()
                stats[stat_name] = stat_value
        
        return stats
    
    def scrape_all_players(self):
        """Scrape data for all Serie A players"""
        all_players = []
        
        # Get team URLs
        team_urls = self.get_team_urls()
        
        # Get players from each team
        for team in team_urls:
            players = self.get_players_from_team(team['url'])
            
            # Get detailed stats for each player
            for player in players:
                detailed_stats = self.get_player_detailed_stats(player['url'])
                player['stats'].update(detailed_stats)
                all_players.append(player)
        
        logger.info(f"Scraped data for {len(all_players)} players in total")
        return all_players
    
    def save_to_json(self, players, filename="serie_a_players.json"):
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
    scraper = FBrefScraper()
    players = scraper.scrape_all_players()
    scraper.save_to_json(players)