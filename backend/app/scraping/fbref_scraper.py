# app/scraping/fbref_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

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
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_team_urls(self):
        """Get URLs for all Serie A teams"""
        try:
            response = self.session.get(self.serie_a_url, timeout=10)
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
            response = self.session.get(team_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            team_name = soup.select_one('h1 span').text if soup.select_one('h1 span') else "Unknown"
            
            # Get player stats table
            table_selectors = [
                'table#stats_standard',
                'table.stats_table',
                'table#stats_standard_squads'
            ]
            
            players_table = None
            for selector in table_selectors:
                players_table = soup.select_one(selector)
                if players_table:
                    break
            
            players = []
            if players_table:
                rows = players_table.select('tbody tr')
                for row in rows:
                    # Skip non-player rows
                    if row.get('class') and 'thead' in row.get('class', []):
                        continue
                    
                    player_link = row.select_one('th[data-stat="player"] a')
                    if not player_link:
                        continue
                    
                    player_name = player_link.text
                    player_url = f"{self.base_url}{player_link['href']}"
                    
                    # Get basic stats
                    position_elem = row.select_one('td[data-stat="position"]')
                    position = position_elem.text if position_elem else ""
                    
                    # Map position to Fantacalcio role
                    role = "MID"  # Default
                    if position:
                        if "GK" in position:
                            role = "GK"
                        elif "DF" in position:
                            role = "DEF"
                        elif "FW" in position or "CF" in position:
                            role = "FWD"
                    
                    # Extract basic statistics
                    basic_stats = {}
                    stat_columns = row.select('td[data-stat]')
                    for col in stat_columns:
                        stat_name = col['data-stat']
                        stat_value = col.text.strip()
                        basic_stats[stat_name] = self._clean_stat_value(stat_value)
                    
                    players.append({
                        'name': player_name,
                        'team': team_name,
                        'role': role,
                        'url': player_url,
                        'stats': basic_stats
                    })
            
            logger.info(f"Found {len(players)} players for {team_name}")
            return players
        
        except Exception as e:
            logger.error(f"Error getting players from team {team_url}: {str(e)}")
            return []
    
    def get_player_detailed_stats(self, player_url):
        """Get detailed stats for a player"""
        try:
            response = self.session.get(player_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get advanced stats
            stats = {}
            
            # Advanced statistics tables
            advanced_stats = {
                'shooting': self._parse_advanced_table(soup, 'shooting'),
                'passing': self._parse_advanced_table(soup, 'passing'),
                'passing_types': self._parse_advanced_table(soup, 'passing_types'),
                'gca': self._parse_advanced_table(soup, 'gca'),
                'defense': self._parse_advanced_table(soup, 'defense'),
                'possession': self._parse_advanced_table(soup, 'possession'),
                'misc': self._parse_advanced_table(soup, 'misc')
            }
            
            # Filter out empty stats
            stats = {k: v for k, v in advanced_stats.items() if v}
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting detailed stats for player {player_url}: {str(e)}")
            return {}
    
    def _parse_advanced_table(self, soup, stat_type):
        """Parse advanced statistics tables from FBref"""
        try:
            table_id = f"stats_{stat_type}_dom_lg"
            table = soup.select_one(f'table#{table_id}')
            
            if not table:
                return {}
            
            # Get the most recent season (first row in tbody)
            rows = table.select('tbody tr')
            if not rows:
                return {}
            
            latest_season = rows[0]
            stats = {}
            
            # Extract all statistics from the row
            for cell in latest_season.select('td[data-stat]'):
                stat_name = cell['data-stat']
                stat_value = cell.text.strip()
                stats[stat_name] = self._clean_stat_value(stat_value)
            
            return stats
        
        except Exception as e:
            logger.debug(f"Error parsing {stat_type} table: {e}")
            return {}

    def _clean_stat_value(self, value):
        """Clean and convert statistic values"""
        if not value or value == '-' or value == '':
            return 0
        
        try:
            # Remove percentage signs and convert
            cleaned = value.replace('%', '').replace(',', '')
            
            # Handle range values (e.g., "5-10" -> take average)
            if '-' in cleaned and cleaned.count('-') == 1:
                parts = cleaned.split('-')
                if len(parts) == 2:
                    try:
                        return (float(parts[0]) + float(parts[1])) / 2
                    except ValueError:
                        pass
            
            # Convert to float if possible
            if cleaned.replace('.', '').isdigit():
                return float(cleaned)
            else:
                return value  # Return string if not convertible
        
        except (ValueError, TypeError):
            return value

    def scrape_all_players(self):
        """Scrape data for all Serie A players with rate limiting"""
        all_players = []
        
        # Get team URLs
        team_urls = self.get_team_urls()
        
        if not team_urls:
            logger.error("No teams found to scrape")
            return []
        
        # Get players from each team with rate limiting
        for team in team_urls:
            logger.info(f"Scraping players from {team['name']}")
            players = self.get_players_from_team(team['url'])
            
            # Get detailed stats for each player
            def get_player_details(player):
                time.sleep(0.5)  # Rate limiting
                detailed_stats = self.get_player_detailed_stats(player['url'])
                player['stats'].update(detailed_stats)
                return player
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                detailed_players = list(executor.map(get_player_details, players))
            
            all_players.extend(detailed_players)
            time.sleep(1)  # Rate limiting between teams
        
        logger.info(f"Scraped data for {len(all_players)} players in total")
        return all_players
    
    def save_to_json(self, players, filename="fbref_players.json"):
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