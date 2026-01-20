# Pobieranie danych 
from time import sleep
import config
import cloudscraper
from random import uniform

def fetch_url(url = config.FBREF_URL_TEMPLATE, retries=5):
    '''
    Pobiera strone HTML z danego urla. Retries służy do tego, aby w razie jakiś błędów tj. krotkie przerwanie połączenia z internetem itd.
    program się nie wywalał, ale mógł się odkuć
    '''
    scraper = cloudscraper.create_scraper() #tworzę sesję która udaje przeglądarke, fbref blokuje zwykły requests
    
    for i in range(retries): 
        try: 
            response = scraper.get(url, timeout=10)
            response.raise_for_status()
            return response.text # tu zwracamy HTMLa jako stringa
        except Exception as e: 
            print(f"Błąd przy próbie pobrania {url} (próba {i+1}/{retries}): {e}") 
            sleep(uniform(5, 10))
    raise Exception(f"Nie udało się pobrać danych z {url} po {retries} próbach.")