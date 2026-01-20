#Plik do zapisu/odczytu danych z API Clubelo
import cloudscraper
from pathlib import Path
import os
import pandas as pd
def save_elo_csv(club:str, folder_docelowy = r"data\raw\elo_raw_eng"):
    
    base_url = "http://api.clubelo.com"
    url = f"{base_url}/{club}"
    
    # Tworzymy folder jeśli nie istnieje
    folder = Path(folder_docelowy)
    folder.mkdir(parents=True, exist_ok=True)
    
    scraper = cloudscraper.create_scraper()
    
    try:
        # Pobieramy dane z API
        response = scraper.get(url)
        response.raise_for_status()
        
        filename = f"{club}.csv"  # domyślna nazwa
        filepath = folder / filename
    
        # Zapisujemy to co API zwraca
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"CSV zapisany w: {filepath}")
        
    except Exception as e: 
        print(f"Błąd przy pobieraniu z API: {e}")
        

def load_clubelo_csv(club: str) -> pd.DataFrame:
    path = os.path.join("data", "raw", "elo_raw_eng" ,f"{club}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Plik CSV dla klubu {club} nie istnieje.")
    return pd.read_csv(path)

#Sprawdza czy csvka dla klubu isteniej
def clubelo_csv_exists(club: str) -> bool:
    path = os.path.join("data", "raw", "elo_raw_eng", f"{club}.csv")
    return os.path.exists(path)
