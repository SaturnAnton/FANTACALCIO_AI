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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
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
            name_tag = row.select_one("th.player-name a")
            name = name_tag.get_text(strip=True) if name_tag else ""
            player_url = name_tag.get("href") if name_tag else None

            # Squadra
            team_tag = row.select_one("td.player-team")
            team = team_tag.get_text(strip=True) if team_tag else ""

            # Statistiche
            stats = {}
            for td in row.find_all("td"):
                data_key = td.get("data-col-key")
                if data_key:
                    stats[data_key] = self._clean_value(td.get_text())

            # Ruolo fantacalcio di default MID
            role = "MID"

            players.append({
                "name": name,
                "team": team,
                "role": role,
                "url": player_url,
                "stats": stats
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
