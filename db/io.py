#Tu będą wszystkie funkcje potrzebne do obsługi DB
import sqlite3
import os
import config
import datetime
import pandas as pd


### HTML CACHE ###
def save_html_to_db(team: str, season: str, html: str, html_type = "main",url = ""):
    """
    Zapisuje stronę HTML do tabeli html_cache. Jeśli wpis już istnieje (team + season + html_type), dodaje nowy.
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO html_cache(team, season, html, html_type, url, fetched_at)
                values(?, ?, ?, ?, ?, ?)
                    """, (team, season, html, html_type, url, datetime.datetime.now())
            )
            conn.commit()
    except Exception as e:
        print(f"Nie udało się zapisać danych do bazy: {e}")
        
        
def load_html_from_db(team: str, season: str, html_type = "main") -> str:
    """ Funkcja wczytuje htmla z DB zamiast ponownie pobierać to z sieci

    Args:
        team (str): nazwa drużyny
        season (str): sezon z którego dane mają byc wzięte
        html_type (str, optional): typ tabeli z którego html ma zostać wzięty. Domyślnie "main" 

    Returns:
        str: Zwraca htmla
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                    SELECT html
                    FROM html_cache
                    WHERE team = ? AND season = ? AND html_type = ?
                    """, (team, season, html_type))
            result = c.fetchone()
            if result:
                return result[0] #zwraca HTMLa jako string, musze to zrobic [0], bo fetchone zwraca krotkę
            else:
                return None
    except Exception as e:
        print(f"Bład przy pobieraniu danych z bazy danych: {e}")
        return None
    
    
### Raw Team data ###

def save_raw_team_data_to_db(df):
    """
    Zapisuje surowe dane danej drużyny do tabeli team_stats_raw
    Automatycznie dodaje brakujące kolumny jako NULL/NaN.
    """
    df = df.copy()
    #kolumny w surowym df
    
    expected_columns = ['Date', 'Time', 'Comp', 'Round', 'Venue', 'Result', 'GF', 'GA', 'Opponent',
               'xGA', 'SoT%', 'G/Sh', 'G/SoT', 'Dist', 'PK', 'PKatt', 'npxG', 'npxG/Sh', 
               'G-xG', 'np:G-xG', 'xA', 'PPA', 'PrgP', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 
               'Att Pen', 'Live', '1/3', 'CPA', 'Dis', 'xG', 'Poss', 'PrgDist', 'Team', 'Season']
    
    missing = [col for col in expected_columns if col not in df.columns]
    existing = [col for col in expected_columns if col in df.columns]
    
    
    if missing:
        print(f"Brakujące kolumny (dodaję jako NaN): {missing}")
        #raise ValueError(f"Nie ma następujących kolumn w DF: {missing}")
    
    if existing:
        print(f"Dostępne kolumny ({len(existing)}/{len(expected_columns)}): {existing}")
    
    # Dodaję brakujące kolumny jako NaN, ze wzgledu na to ze SQL ma stałą strukturę, i jak bedzie chcial zapisac do ustalonej tabeli wartosci z kolumn które nie istnieją to napotka problem
    for col in missing:
        df[col] = None     
        df = df.where(pd.notnull(df), None)  #uzupełniam None, bo sqlite nie akceptuje np.nan
    #Upewniam się ze kolumny są w odpowiedniej kolejnosci
    df = df[expected_columns]
    
    #konwersja do listy wartosci 
    values = df.values.tolist()
    placeholders = ", ".join(["?"] * len(expected_columns)) #łącze wszystkie pytajniki w jeden string "?, ?, ...., ?"
    sql_columns = [f'"{col}"' for col in expected_columns] #obkładam kolumny "", zeby nie bylo probelmu ze znakami specjalnymi 
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.executemany(
                f"""
                INSERT INTO team_stats_raw ({", ".join(sql_columns)})
                VALUES ({placeholders}) 
                        """, values)
            conn.commit()
            print(f"Zapisano {len(df)} rekordów do bazy danych")
    except Exception as e:
        print(f"Nie udało się zapisać danych do bazy: {e}")
        raise ValueError
            
def load_raw_team_stats_from_db(team:str, season:str) -> pd.DataFrame:
    """Pobiera surowe dane dla danej druzyny z danego sezonu z bazy danych
    zwraca df
    """
    
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT *
                FROM team_stats_raw
                WHERE team = ? AND season = ?
                    """, (team, season))
            result = c.fetchall()
            columns = [desc[0] for desc in c.description] #wydobywam nazwę kolumny z tabeli sql. Bez tego dostaje df-a z nazwami kolumn 0,1,2,....
            df = pd.DataFrame(result, columns=columns)
            return df     
    except Exception as e:
        print(f"Nie mozna pobrać danych z bazy danych: {e}")
        return pd.DataFrame()
    
def load_all_teams_raw_stats_from_db(season :str) -> pd.DataFrame:
    """
    Zwraca wszystkie dane surowe z danego sezonu jako jeden DataFrame.
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM team_stats_raw
                WHERE season = ?
                """, (season,))
            result = c.fetchall()
            columns = [desc[0] for desc in c.description]
            df = pd.DataFrame(result, columns = columns)
            return df
    except Exception as e:
        print(f"Błąd przy pobieraniu danych z bazy: {e}")
        return pd.DataFrame()

def load_all_teams_raw_stats_from_every_season_db() -> pd.DataFrame:
    """
    Zwraca wszystkie dane surowe z wszystkich sezonow jako jeden DataFrame.
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM team_stats_raw
                """)
            result = c.fetchall()
            columns = [desc[0] for desc in c.description]
            df = pd.DataFrame(result, columns = columns)
            return df
    except Exception as e:
        print(f"Błąd przy pobieraniu danych z bazy: {e}")
        return pd.DataFrame()

def delete_team_stats_raw(team: str, season: str) -> None:
    """
    Usuwa wszystkie rekordy z tabeli `team_stats_raw`
    dla podanej drużyny i sezonu.

    Args:
        team (str): nazwa drużyny (np. "Liverpool")
        season (str): sezon w formacie "2023-2024"
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            c = conn.cursor()
            c.execute("""
                DELETE FROM team_stats_raw
                WHERE Team = ? AND Season = ?
            """, (team, season))
            conn.commit()
            print(f"Usunięto dane dla {team}, sezon {season}")
    except Exception as e:
        print(f"Błąd przy usuwaniu danych: {e}")
        
