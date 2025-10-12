# app/scripts/update_and_save_players.py
import logging
import json
import sqlite3
from app.scraping.fantacalcio_scraper import FantacalcioScraper
from app.scraping.fbref_scraper import FBrefScraper
import unicodedata
import re
from rapidfuzz import fuzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "fantacalcio.db"
JSON_FILE = "players_data.json"

# --- Classe per unire i dati ---
class UnifiedPlayerScraper:
    def __init__(self):
        self.fanta_scraper = FantacalcioScraper()
        self.fbref_scraper = FBrefScraper()
        self.team_mapping = {
            'Inter': ['Inter', 'Internazionale', 'Inter Milan', 'INT'],
            'Milan': ['Milan', 'AC Milan', 'MIL'],
            'Juventus': ['Juventus', 'Juventus Turin', 'JUV'],
            'Roma': ['Roma', 'AS Roma', 'ROM'],
            'Napoli': ['Napoli', 'SSC Napoli', 'NAP'],
            'Atalanta': ['Atalanta', 'Atalanta Bergamo', 'ATA'],
            'Lazio': ['Lazio', 'SS Lazio', 'LAZ'],
            'Fiorentina': ['Fiorentina', 'ACF Fiorentina', 'FIO'],
            'Bologna': ['Bologna', 'FC Bologna', 'BOL'],
            'Torino': ['Torino', 'FC Torino', 'TOR'],
            'Genoa': ['Genoa', 'Genoa CFC', 'GEN'],
            'Lecce': ['Lecce', 'US Lecce', 'LEC'],
            'Sassuolo': ['Sassuolo', 'US Sassuolo', 'SAS'],
            'Udinese': ['Udinese', 'Udinese Calcio', 'UDI'],
            'Cagliari': ['Cagliari', 'Cagliari Calcio', 'CAG'],
            'Verona': ['Verona', 'Hellas Verona', 'VER'],
            'Parma': ['Parma', 'Parma Calcio', 'PAR'],
            'Como': ['Como', 'Como 1907', 'COM'],
            'Pisa': ['Pisa', 'Pisa SC', 'PIS'],
            'Cremonese': ['Cremonese', 'US Cremonese', 'CRE']
        }

    def normalize_name(self, name: str) -> str:
        name = unicodedata.normalize('NFKD', name).encode('ASCII','ignore').decode('ASCII')
        name = re.sub(r'\s+', ' ', name.lower().strip())
        name = re.sub(r'\b(jr|sr|ii|iii|iv)\b', '', name)
        parts = name.split()
        return parts[-1] if parts else name  # usa solo cognome

    def normalize_team(self, team: str) -> str:
        team_lower = team.lower().strip()
        for standard_name, variants in self.team_mapping.items():
            if any(variant.lower() in team_lower for variant in variants):
                return standard_name
        return team

    def normalize_role(self, fbref_role: str) -> str:
        fbref_role = fbref_role.upper()
        if "GK" in fbref_role: return "GK"
        elif any(x in fbref_role for x in ["DF", "CB", "LB", "RB"]): return "DEF"
        elif any(x in fbref_role for x in ["MF", "CM", "LM", "RM", "WM"]): return "MID"
        elif any(x in fbref_role for x in ["FW", "ST", "CF", "LW", "RW"]): return "FWD"
        return "MID"

    def merge_data(self, threshold=80):
        # Scrape Fantacalcio
        logger.info("🔎 Scraping Fantacalcio.it...")
        fanta_players = self.fanta_scraper.scrape_players()
        fanta_dict = {(self.normalize_name(p['name']), self.normalize_team(p['team'])): p for p in fanta_players}

        # Scrape FBref
        logger.info("🔎 Scraping FBref.com...")
        fbref_players = self.fbref_scraper.scrape_players()
        fbref_dict = {}
        for p in fbref_players:
            p['role'] = self.normalize_role(p.get('role', 'MID'))
            fbref_dict[(self.normalize_team(p['team']), p['name'])] = p

        # Merge dati con fuzzy matching
        merged_players = []
        for f_key, fanta in fanta_dict.items():
            f_name, f_team = f_key
            merged = fanta.copy()
            best_match = None
            best_score = 0
            for fb_key, fb in fbref_dict.items():
                fb_team, fb_name = fb_key
                if fb_team != f_team:
                    continue
                score = fuzz.ratio(f_name, self.normalize_name(fb_name))
                if score > best_score:
                    best_score = score
                    best_match = fb
            if best_score >= threshold:
                merged['fbref_data'] = best_match['stats']
                if merged['role'] == 'MID' and best_match['role'] != 'MID':
                    merged['role'] = best_match['role']
            else:
                merged['fbref_data'] = {}
            merged_players.append(merged)

        # Aggiungi giocatori presenti solo su FBref
        for fb_key, fb in fbref_dict.items():
            fb_team, fb_name = fb_key
            found = False
            for mp in merged_players:
                if self.normalize_name(mp['name']) == self.normalize_name(fb_name) and self.normalize_team(mp['team']) == fb_team:
                    found = True
                    break
            if not found:
                merged_players.append({
                    'name': fb['name'],
                    'team': fb_team,
                    'role': fb['role'],
                    'price': 0.0,
                    'fantacalcio_data': {},
                    'fbref_data': fb['stats']
                })

        logger.info(f"✅ Merged data for {len(merged_players)} players")
        return merged_players

    def save_to_json(self, players):
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Dati salvati in {JSON_FILE}")


# --- Funzioni DB ---
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team TEXT,
        role TEXT,
        price REAL,
        UNIQUE(name, team)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fantacalcio_stats (
        player_id INTEGER,
        matches_played INTEGER,
        avg_grade REAL,
        avg_fanta_grade REAL,
        goals INTEGER,
        assists INTEGER,
        penalty_made REAL,
        penalty_attempted REAL,
        yellow_cards INTEGER,
        red_cards INTEGER,
        FOREIGN KEY(player_id) REFERENCES players(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fbref_stats (
        player_id INTEGER,
        stat_name TEXT,
        stat_value REAL,
        FOREIGN KEY(player_id) REFERENCES players(id)
    )""")
    conn.commit()
    logger.info("✅ Tabelle create o già presenti")

def insert_data(conn, players):
    cursor = conn.cursor()
    for p in players:
        cursor.execute("""
            INSERT OR IGNORE INTO players(name, team, role, price)
            VALUES (?, ?, ?, ?)""", (p['name'], p['team'], p['role'], p.get('price', 0.0)))
        cursor.execute("SELECT id FROM players WHERE name = ? AND team = ?", (p['name'], p['team']))
        player_id = cursor.fetchone()[0]

        f_stats = p.get('fantacalcio_data', {})
        cursor.execute("""
            INSERT INTO fantacalcio_stats(
                player_id, matches_played, avg_grade, avg_fanta_grade,
                goals, assists, penalty_made, penalty_attempted,
                yellow_cards, red_cards
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id,
            f_stats.get('pg', 0),
            f_stats.get('mv', 0.0),
            f_stats.get('mfv', 0.0),
            f_stats.get('gol', 0),
            f_stats.get('ass', 0),
            f_stats.get('rig', 0),
            f_stats.get('rp', 0),
            f_stats.get('amm', 0),
            f_stats.get('esp', 0)
        ))

        fb_stats = p.get('fbref_data', {})
        for stat_name, stat_value in fb_stats.items():
            cursor.execute("""
                INSERT INTO fbref_stats(player_id, stat_name, stat_value)
                VALUES (?, ?, ?)""", (player_id, stat_name, stat_value))
    conn.commit()
    logger.info(f"✅ Inseriti {len(players)} giocatori nel database")


# --- Main ---
def main():
    scraper = UnifiedPlayerScraper()
    players = scraper.merge_data()
    scraper.save_to_json(players)

    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    insert_data(conn, players)
    conn.close()
    logger.info("🏁 Operazione completata!")

if __name__ == "__main__":
    main()
