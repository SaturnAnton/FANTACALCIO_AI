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
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_players_list(self):
        """Get list of all players with their fantasy data"""
        try:
            response = self.session.get(self.players_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players_table = soup.select('table.player-table tbody tr')
            
            if not players_table:
                logger.warning("No players table found - website structure may have changed")
                return []
            
            players = []
            for row in players_table:
                player_data = self._parse_player_row(row)
                if player_data:
                    players.append(player_data)
            
            logger.info(f"Found {len(players)} players on Fantacalcio.it")
            return players
            
        except requests.RequestException as e:
            logger.error(f"Network error getting players list: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []
    
    def _parse_player_row(self, row) -> Optional[Dict]:
        """Parse a single player row from the table"""
        try:
            # Extract player info
            player_name_elem = row.select_one('td.player-name a')
            if not player_name_elem:
                return None
            
            player_name = player_name_elem.text.strip()
            player_url = f"{self.base_url}{player_name_elem['href']}"
            
            # Extract team and role
            team_elem = row.select_one('td.player-team img')
            team = team_elem['alt'] if team_elem and 'alt' in team_elem.attrs else "Unknown"
            
            role_elem = row.select_one('td.player-role')
            role = role_elem.text.strip() if role_elem else ""
            
            # Map role to standardized format
            role_mapping = {
                "P": "GK",
                "D": "DEF", 
                "C": "MID",
                "A": "FWD"
            }
            standardized_role = role_mapping.get(role, "MID")
            
            # Extract price
            price_elem = row.select_one('td.player-price')
            price_text = price_elem.text.strip() if price_elem else "0"
            try:
                price = float(price_text.replace(',', '.'))
            except ValueError:
                price = 0.0
            
            # Extract fantasy stats
            fanta_stats = self._extract_fantasy_stats(row)
            
            return {
                'name': player_name,
                'team': team,
                'role': standardized_role,
                'price': price,
                'url': player_url,
                'fantacalcio_data': fanta_stats
            }
            
        except Exception as e:
            logger.warning(f"Error parsing player row: {str(e)}")
            return None
    
    def _extract_fantasy_stats(self, row) -> Dict:
        """Extract fantasy statistics from table row"""
        stats = {}
        
        # Definizione di tutti i selettori per le statistiche
        stat_selectors = {
            'media_voto': [
                'td.player-average-rating',
                'td.media-voto',
                'td[data-stat="average_rating"]'
            ],
            'fantamedia': [
                'td.player-fantamedia', 
                'td.fantamedia',
                'td[data-stat="fantamedia"]'
            ],
            'gol_fatti': [
                'td.player-goals',
                'td.gol',
                'td[data-stat="goals"]'
            ],
            'gol_subiti': [
                'td.player-goals-conceded',
                'td.gol-subiti',
                'td[data-stat="goals_conceded"]'
            ],
            'assist': [
                'td.player-assists',
                'td.assist',
                'td[data-stat="assists"]'
            ],
            'ammonizioni': [
                'td.player-yellow-cards',
                'td.ammonizioni',
                'td[data-stat="yellow_cards"]'
            ],
            'espulsioni': [
                'td.player-red-cards', 
                'td.espulsioni',
                'td[data-stat="red_cards"]'
            ],
            'rigori_segnati': [
                'td.player-penalty-goals',
                'td.rigori-segnati',
                'td[data-stat="penalty_goals"]'
            ],
            'rigori_sbagliati': [
                'td.player-penalty-missed',
                'td.rigori-sbagliati',
                'td[data-stat="penalty_missed"]'
            ],
            'rigori_parati': [
                'td.player-penalty-saved',
                'td.rigori-parati',
                'td[data-stat="penalty_saved"]'
            ],
            'autogol': [
                'td.player-own-goals',
                'td.autogol',
                'td[data-stat="own_goals"]'
            ]
        }
        
        # Prova ogni selettore per ogni statistica
        for stat_name, selectors in stat_selectors.items():
            value = "0"
            for selector in selectors:
                elem = row.select_one(selector)
                if elem and elem.text.strip():
                    value = elem.text.strip()
                    break
            stats[stat_name] = self._clean_stat_value(value)
        
        return stats
    
    def _clean_stat_value(self, value: str):
        """Clean and convert statistic values"""
        if not value or value == "-":
            return 0
        
        # Rimuovi caratteri non numerici e converti
        try:
            # Gestisci valori con virgola (es: "6,5")
            cleaned = value.replace(',', '.').replace('"', '').replace("'", "")
            # Rimuovi spazi e caratteri extra
            cleaned = ''.join(char for char in cleaned if char.isdigit() or char == '.')
            
            if cleaned and cleaned != '.':
                return float(cleaned)
            else:
                return 0
        except (ValueError, TypeError):
            return 0
    
    def get_player_details(self, player_url):
        """Get detailed fantasy data for a player"""
        try:
            response = self.session.get(player_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed stats
            detailed_stats = {}
            
            # Last 5 games performance
            last_games = self._extract_last_games(soup)
            detailed_stats['ultime_partite'] = last_games
            
            # Season stats
            season_stats = self._extract_season_stats(soup)
            detailed_stats['statistiche_stagione'] = season_stats
            
            # Performance trends
            trends = self._extract_performance_trends(soup)
            detailed_stats['andamento'] = trends
            
            return detailed_stats
        
        except Exception as e:
            logger.error(f"Error getting player details from {player_url}: {str(e)}")
            return {}
    
    def _extract_last_games(self, soup) -> List[Dict]:
        """Extract last 5 games performance"""
        last_games = []
        
        try:
            # Prova diversi selettori per la tabella delle ultime partite
            games_selectors = [
                'table.player-last-games tbody tr',
                'table.ultime-partite tbody tr',
                'div.recent-games table tbody tr'
            ]
            
            games_table = None
            for selector in games_selectors:
                games_table = soup.select(selector)
                if games_table:
                    break
            
            for game_row in games_table[:5]:  # Get last 5 games
                cells = game_row.select('td')
                if len(cells) >= 4:
                    try:
                        matchday = cells[0].text.strip()
                        opponent = cells[1].text.strip()
                        result = cells[2].text.strip()
                        rating = cells[3].text.strip()
                        
                        # Estrai voti e fantavoto se disponibili
                        fantasy_points = "0"
                        if len(cells) > 4:
                            fantasy_points = cells[4].text.strip()
                        
                        last_games.append({
                            'giornata': matchday,
                            'avversario': opponent,
                            'risultato': result,
                            'voto': rating,
                            'fantavoto': fantasy_points
                        })
                    except Exception as e:
                        logger.debug(f"Error parsing game row: {e}")
                        continue
        
        except Exception as e:
            logger.debug(f"Error extracting last games: {e}")
        
        return last_games
    
    def _extract_season_stats(self, soup) -> Dict:
        """Extract detailed season statistics"""
        season_stats = {}
        
        try:
            # Prova diversi selettori per le statistiche stagione
            stats_selectors = [
                'div.player-season-stats div.stat-item',
                'div.stats-container div.stat-row',
                'table.season-stats tbody tr'
            ]
            
            for selector in stats_selectors:
                stats_divs = soup.select(selector)
                if stats_divs:
                    for stat_div in stats_divs:
                        try:
                            label_elem = stat_div.select_one('.stat-label, .stat-name, td:first-child')
                            value_elem = stat_div.select_one('.stat-value, .stat-number, td:last-child')
                            
                            if label_elem and value_elem:
                                label = label_elem.text.strip().lower()
                                value = value_elem.text.strip()
                                
                                # Mappa i nomi delle statistiche
                                stat_mapping = {
                                    'partite giocate': 'partite_giocate',
                                    'presenze': 'presenze',
                                    'titolarità': 'titolarita',
                                    'minuti giocati': 'minuti_giocati',
                                    'media voto': 'media_voto_stagione',
                                    'fantamedia': 'fantamedia_stagione'
                                }
                                
                                mapped_label = stat_mapping.get(label, label)
                                season_stats[mapped_label] = self._clean_stat_value(value)
                        except Exception as e:
                            logger.debug(f"Error parsing stat item: {e}")
                            continue
                    break
        
        except Exception as e:
            logger.debug(f"Error extracting season stats: {e}")
        
        return season_stats
    
    def _extract_performance_trends(self, soup) -> Dict:
        """Extract performance trends and averages"""
        trends = {}
        
        try:
            # Estrai trend degli ultimi mesi/partite
            trend_selectors = {
                'media_ultime_5': [
                    'div.trend-last-5 .average-rating',
                    'div.last-5-games .avg-rating'
                ],
                'fantamedia_ultime_5': [
                    'div.trend-last-5 .fantamedia',
                    'div.last-5-games .fantamedia'
                ],
                'forma_attuale': [
                    'div.current-form .rating',
                    'div.forma-attuale .value'
                ]
            }
            
            for trend_name, selectors in trend_selectors.items():
                for selector in selectors:
                    elem = soup.select_one(selector)
                    if elem and elem.text.strip():
                        trends[trend_name] = self._clean_stat_value(elem.text.strip())
                        break
        
        except Exception as e:
            logger.debug(f"Error extracting trends: {e}")
        
        return trends
    
    def scrape_all_players(self, max_workers=3, delay=1.0):
        """Scrape data for all players with rate limiting"""
        all_players = []
        
        # Get basic player list
        players = self.get_players_list()
        
        if not players:
            logger.error("No players found to scrape")
            return []
        
        logger.info(f"Starting detailed scraping for {len(players)} players...")
        
        def get_player_with_details(player):
            time.sleep(delay)  # Rate limiting
            try:
                detailed_stats = self.get_player_details(player['url'])
                player['fantacalcio_data'].update(detailed_stats)
                logger.debug(f"Scraped details for {player['name']}")
                return player
            except Exception as e:
                logger.error(f"Error scraping {player['name']}: {str(e)}")
                return player
        
        # Use threading for parallel requests (with rate limiting)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            all_players = list(executor.map(get_player_with_details, players))
        
        logger.info(f"Completed scraping for {len(all_players)} players")
        return all_players
    
    def save_to_json(self, players, filename="fantacalcio_players.json"):
        """Save player data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(players, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved player data to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving player data to {filename}: {str(e)}")
            return False
    
    def save_to_csv(self, players, filename="fantacalcio_players.csv"):
        """Save player data to CSV file"""
        try:
            # Crea un DataFrame flattenizzato per CSV
            flat_data = []
            for player in players:
                flat_player = {
                    'nome': player['name'],
                    'squadra': player['team'],
                    'ruolo': player['role'],
                    'prezzo': player['price'],
                    'url': player['url']
                }
                
                # Aggiungi tutte le statistiche fantasy
                for stat_key, stat_value in player['fantacalcio_data'].items():
                    if isinstance(stat_value, (dict, list)):
                        flat_player[stat_key] = json.dumps(stat_value, ensure_ascii=False)
                    else:
                        flat_player[stat_key] = stat_value
                
                flat_data.append(flat_player)
            
            df = pd.DataFrame(flat_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved player data to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving player data to {filename}: {str(e)}")
            return False

# Example usage with improved error handling
if __name__ == "__main__":
    scraper = FantacalcioScraper()
    
    try:
        print("Starting Fantacalcio.it scraper...")
        players = scraper.scrape_all_players(max_workers=2, delay=1.5)
        
        if players:
            scraper.save_to_json(players, "fantacalcio_players_complete.json")
            scraper.save_to_csv(players, "fantacalcio_players_complete.csv")
            print(f"Successfully scraped {len(players)} players")
        else:
            print("No players were scraped")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Scraping failed: {e}")