# Skrypt do inicjalizacji bazy danych (np. SQLite schema)
import sqlite3
import os

DB_PATH = os.path.join("data", "pl_match_data.db")

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # tworzę tabelę do cacheowania htmlów
    c.execute("""
              CREATE TABLE IF NOT EXISTS html_cache (
                  id INTEGER PRIMARY KEY,
                  team TEXT,
                  season TEXT,
                  html TEXT,
                  html_type TEXT,
                  url TEXT,
                  fetched_at DATETIME,
                  UNIQUE(team, season, html_type)                  
              )
              """)
    
    
    #tworzę tabelę przechowujace surowe dane po zmergowaniu dfów fixtures, shooting, passing itd, ALE PRZED FEATURE ENGINEERINGIEM

    c.execute("""
              CREATE TABLE IF NOT EXISTS team_stats_raw(
                  Date TEXT,
                  Time TEXT,
                  Comp TEXT,
                  Round TEXT,
                  Venue TEXT,
                  Result TEXT,
                  GF REAL,
                  GA REAL,
                  Opponent TEXT,
                  xGA REAL,
                  "SoT%" REAL,
                  "G/Sh" REAL,
                  "G/SoT" REAL,
                  Dist REAL,
                  PK INTEGER,
                  PKatt INTEGER,
                  npxG REAL,
                  "npxG/Sh" REAL,
                  "G-xG" REAL,
                  "np:G-xG" REAL,
                  xA REAL,
                  PPA REAL,
                  PrgP INTEGER,
                  "Def 3rd" INTEGER,
                  "Mid 3rd" INTEGER,
                  "Att 3rd" INTEGER,
                  "Att Pen" INTEGER,
                  Live INTEGER,
                  "1/3" INTEGER,
                  CPA INTEGER,
                  Dis INTEGER,
                  xG REAL,
                  Poss REAL, 
                  PrgDist REAL,
                  Team TEXT,
                  Season TEXT      
              )
              
              
              """)
    
    """
    tego jeszcze nie ma 
    c.execute(
        """
    """
              CREATE TABLE IF NOT EXISTS team_stats_features (
                  tu wszystkie kolumny i ich typpy
              )
              
              
          
    )
    """
    conn.commit()
    conn.close()
