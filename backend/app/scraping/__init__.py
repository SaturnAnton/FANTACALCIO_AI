# app/scraping/__init__.py
from .fantacalcio_scraper import FantacalcioScraper
from .fbref_scraper import FBrefScraper
from .unified_scraper import UnifiedPlayerScraper
from .data_manager import DataManager

__all__ = [
    'FantacalcioScraper',
    'FBrefScraper', 
    'UnifiedPlayerScraper',
    'DataManager'
]