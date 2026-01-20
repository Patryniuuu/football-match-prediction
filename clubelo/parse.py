# Parsowanie HTML
import pandas as pd
from io import StringIO
# === Parsowanie Clubelo ===
def parse_clubelo_teamset(html:str) -> list:
    """Funkcja ma za zadanie stworzyć liste zespołów dla danego kraju

    Args:
        html (str): Html powstały przez użycie funkcji scraping.fetch.fetch_url(CLUBELO_URL_TEMPLATE) 
    """
    try:
        df = pd.read_html(StringIO(html))[1]
        df = df["Club"].str.replace(r"^\d+\s*", "", regex=True)
        result = list(df)
        return result
    except Exception as e:
        print(f"Błąd przy tworzeniu setu: {e}")    
        return None    
    
