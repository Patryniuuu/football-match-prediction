# Parsowanie HTML
import pandas as pd
from bs4 import BeautifulSoup
from config import HEADERS
import cloudscraper
from io import StringIO
from time import sleep
from random import uniform


# === Parsowanie Fbref ===
def parse_team_links(standings_html):
    soup = BeautifulSoup(standings_html, "html.parser")
    try:     
        table = soup.select('table.stats_table')[0]
    except IndexError:
        raise ValueError("Nie znaleziono tabeli z wynikami (table.stats_table)")
    '''
    ta jedna linijka z links opisuje:
    links = standings_table.find_all("a")
    links = [l.get("href") for l in links] 
    links = [l for l  in links if "/squads/" in l]
    '''
    links = [a.get("href") for a in table.find_all("a") if "/squads/" in a.get("href", "")] 
    '''
    Podobnie dla teams:
    teams = [l.split("/")[-1] for l in links] # wyciągam nazwe klubu z linku
    teams = [team[:-6] for team in teams] #pozbywam się koncowki "-Stats"
    teams = [team.replace("-", " ") for team in teams] # zamieniam ewentulane "-", spacjami np: "Man-City" na "Man City"
    '''
    teams = [l.split("/")[-1].replace("-", " ")[:-6] for l in links]
    full_links = [f"https://fbref.com{l}" for l in links]
    return teams, full_links

def parse_team_fixture_df(standing_html: str) -> pd.DataFrame:
    try:
        df = pd.read_html(StringIO(standing_html), match="Scores & Fixtures")[0] #uzywam StringIO, zeby pandas w przyszlosci nie wywalał błędu
        expected_cols = ["Date", "Time", "Comp", "Round", "Venue", "Result", 
                         "GF", "GA", "Opponent", "xG", "xGA", "Poss"]
        df = df[[col for col in expected_cols if col in df.columns]]
        return df
    except ValueError:
        raise ValueError("Nie znaleziono tabeli 'Scores & Fixtures' w HTML-u")
    except Exception as e:
        raise Exception(f"Inny błąd przy parsowaniu: {e}")

def parse_team_detailed_stats(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        reference_links = soup.find_all("a")
        
        #odfiltrowuje "None", ktore powstalyby jesli jakis element <a> nie ma atrybutu "href"
        hrefs = [l.get("href") for l in reference_links if l.get("href") is not None]
    
    
        keywords = ["/schedule/", "/shooting/", "/keeper/", "/passing/", "/passing_types/",
                    "/gca/", "/defense/","/possession/", "/misc/"]
        filtered_links = [
            l for l in hrefs 
            if "/matchlogs/" in l and "/all_comps/" in l and any(keyword in l for keyword in keywords)
        ]
    
        #usuwam duplikaty w filtered_links
        clean_links = []
        for l in filtered_links:
            if l not in clean_links:
                clean_links.append(l)
    
        #dodaje część "https://fbref.com" do linkow
        full_clean_links = [f"https://fbref.com{l}" for l in clean_links]
        
        return full_clean_links
    
    except Exception as e:
        raise ValueError(f"Błąd podczas parsowania linków: {e}")
    
def parse_all_stat_tables(links: list[str]) -> list[pd.DataFrame]:
    '''
    Funkcja która ma za zadanie wyciągnąć wszystkie potrzebne statystyki z tabel z roznych stron HTMLa
    '''
    keyword_to_match_and_columns = {
        "/shooting/" : {
            "match" : "Shooting",
            "columns" :  ["Date", "Time", "Comp", "Round", "Opponent",
                        "SoT%", "G/Sh", "G/SoT", "Dist", "PK", "PKatt",
                        "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"]
        },
        "/passing/" : {
            "match" : "Passing",
            "columns" : ["Date", "Time", "Comp", "Round", "Opponent",
                        "PrgDist", "xA", "PPA", "PrgP"]
        },
        "/possession/" : {
            "match" : "Possession",
            "columns" : ["Date","Time","Comp","Round","Opponent",
                         "Poss", "Def 3rd","Mid 3rd", "Att 3rd", 
                         "Att Pen", "Live", "PrgDist", "1/3", "CPA", "Dis"]
        }
    }
    
    results = []
    scraper = cloudscraper.create_scraper() #tworze sesje udającą przeglądarkę, bo fbref blokuje requests
    
    for keyword, params in keyword_to_match_and_columns.items():
        link = None
        for l in links:
            if keyword in l:
                link = l
                break
        if link is None:
            print(f"Brak linku dla {keyword} - tworzę pusty DF")
            empty_df = pd.DataFrame(columns=params["columns"])
            results.append(empty_df)
            #raise ValueError(f"Nie znaleziono linku dla keyworda '{keyword}'")
        else:
            try:
                response = scraper.get(link, headers=HEADERS, timeout=10)
                df = pd.read_html(StringIO(response.text), match=params["match"])[0] #uzywam StringIO, zeby pandas w przyszlosci nie wywalał błędu
                df = df.droplevel(0, axis=1)
                df = df[[col for col in params["columns"] if col in df.columns]]
                results.append(df)      
                print(f"Pobrano {keyword}: {df.shape}")
            except Exception as e:
                print(f"Błąd przy parsowaniu {keyword}: {e} - tworzę pusty DF")
                empty_df = pd.DataFrame(columns=params["columns"])
                results.append(empty_df)
            
        sleep(uniform(5,10))
    return results


