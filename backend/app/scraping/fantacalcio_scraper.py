# app/scraping/fantacalcio_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FantacalcioScraper:
    def __init__(self):
        self.url = "https://www.fantacalcio.it/statistiche-serie-a"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def _clean_value(self, value):
        """Converti valori numerici da stringa a float/int se possibile"""
        value = value.strip().replace(",", ".")
        if "/" in value:  # gestione rigori tipo "1 / 1"
            parts = value.split("/")
            try:
                return sum(float(p.strip()) for p in parts) / len(parts)
            except:
                return value
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except:
            return value

    def scrape_players(self):
        logger.info(f"🔎 Scraping da: {self.url}")
        response = requests.get(self.url, headers=self.headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table tbody tr")
        if not rows:
            logger.warning("⚠️ Nessuna riga giocatore trovata")
            return []

        players = []
        for row in rows:
            # Nome e link
            name_tag = row.select_one("th.player-name a span")
            name = name_tag.get_text(strip=True) if name_tag else ""
            player_url = name_tag.parent.get("href") if name_tag else None

            # Squadra
            team_tag = row.select_one("td.player-team")
            team = team_tag.get_text(strip=True) if team_tag else ""

            # Ruolo classic
            role_tag = row.select_one("th.player-role-classic span.role")
            role = "MID"  # default
            if role_tag:
                val = role_tag.get("data-value", "").lower()
                if val == "p":
                    role = "GK"
                elif val == "d":
                    role = "DEF"
                elif val == "c":
                    role = "MID"
                elif val == "a":
                    role = "FWD"

            # Statistiche principali
            stats = {}
            for td in row.find_all("td"):
                data_key = td.get("data-col-key")
                if data_key:
                    stats[data_key] = self._clean_value(td.get_text())

            # FBref-style data (per unione futura)
            fbref_data = {
                "player": name,
                "xg": stats.get("xg", 0),
                "xg_assist": stats.get("xg_assist", 0),
                "progressive_passes": stats.get("progressive_passes", 0),
                "clean_sheets": stats.get("cs", 0),
                "rigori_parati": stats.get("rp", 0)
            }

            players.append({
                "name": name,
                "team": team,
                "role": role,
                "url": player_url,
                "stats": {
                    "pg": stats.get("pg", 0),
                    "mv": stats.get("mv", 0),
                    "mfv": stats.get("mfv", 0),
                    "gol": stats.get("gol", 0),
                    "ass": stats.get("ass", 0),
                    "gs": stats.get("gs", 0),
                    "rig": stats.get("rig", 0),
                    "rp": stats.get("rp", 0),
                    "amm": stats.get("amm", 0),
                    "esp": stats.get("esp", 0)
                },
                "fbref_data": fbref_data
            })

        logger.info(f"✅ Estratti {len(players)} giocatori da Fantacalcio.it")
        return players

    def save_to_json(self, players, filename="fantacalcio_players.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(players, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Dati salvati in {filename}")
        except Exception as e:
            logger.error(f"Errore salvataggio JSON: {e}")


# Esempio di utilizzo
if __name__ == "__main__":
    scraper = FantacalcioScraper()
    players = scraper.scrape_players()
    scraper.save_to_json(players)
