import requests
from bs4 import BeautifulSoup, Comment
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FBrefScraper:
    def __init__(self):
        self.base_url = "https://fbref.com"
        self.url = "https://fbref.com/en/comps/11/stats/Serie-A-Stats"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            )
        }

    def _clean_value(self, val: str):
        val = val.strip().replace(",", "")
        if val == "" or val == "—":
            return 0
        try:
            return float(val) if "." in val else int(val)
        except ValueError:
            return val

    def _get_table(self, soup):
        # Cerca la tabella visibile
        table = soup.find("table", id="stats_standard")
        if table:
            return table

        # Se è dentro un commento HTML (FBref lo fa spesso)
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if 'id="stats_standard"' in comment:
                comment_soup = BeautifulSoup(comment, "html.parser")
                table = comment_soup.find("table", id="stats_standard")
                if table:
                    logger.info("✅ Tabella trovata dentro un commento HTML")
                    return table
        return None

    def scrape_players(self):
        logger.info(f"🔎 Scraping da: {self.url}")
        response = requests.get(self.url, headers=self.headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        table = self._get_table(soup)
        if not table:
            logger.warning("⚠️ Nessuna tabella trovata (id='stats_standard')")
            return []

        headers = [th.get("data-stat") for th in table.select("thead tr th") if th.get("data-stat")]
        rows = table.select("tbody tr")

        logger.info(f"📊 Colonne trovate: {len(headers)}")
        logger.info(f"🔢 Righe totali: {len(rows)}")

        players = []
        for row in rows:
            if "class" in row.attrs and "thead" in row["class"]:
                continue

            player_cell = row.find("td", {"data-stat": "player"})
            if not player_cell:
                continue

            name = player_cell.text.strip()
            if not name:
                continue

            link_tag = player_cell.find("a")
            player_url = f"{self.base_url}{link_tag['href']}" if link_tag else None

            team_cell = row.find("td", {"data-stat": "team"})
            team = team_cell.text.strip() if team_cell else ""

            pos_cell = row.find("td", {"data-stat": "position"})
            position = pos_cell.text.strip() if pos_cell else ""

            # Ruolo dedotto
            role = "MID"
            if "GK" in position:
                role = "GK"
            elif "DF" in position:
                role = "DEF"
            elif any(x in position for x in ["FW", "ST", "CF"]):
                role = "FWD"

            stats = {}
            for cell in row.find_all("td"):
                stat_name = cell.get("data-stat")
                if not stat_name:
                    continue
                stats[stat_name] = self._clean_value(cell.text)

            players.append({
                "name": name,
                "team": team,
                "role": role,
                "position": position,
                "url": player_url,
                "stats": stats
            })

        logger.info(f"✅ Estratti {len(players)} giocatori da FBref")
        return players

    def save_to_json(self, players, filename="fbref_players.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Dati salvati in {filename}")


if __name__ == "__main__":
    scraper = FBrefScraper()
    players = scraper.scrape_players()
    scraper.save_to_json(players)
    logger.info(f"🏁 Operazione completata - {len(players)} giocatori trovati")
