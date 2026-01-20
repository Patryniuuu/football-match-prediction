# test_pipeline.py - Testowanie pipeline na małej próbce
import config
import db.init_db
from db.io import save_html_to_db, load_html_from_db, save_raw_team_data_to_db, delete_team_stats_raw, load_all_teams_raw_stats_from_db, load_all_teams_raw_stats_from_every_season_db
from scraping.fetch import fetch_url
from scraping.parse import parse_team_links, parse_team_fixture_df, parse_team_detailed_stats, parse_all_stat_tables
from scraping.transform import merge_tables
from features.build_features import add_team_column, add_season_from_date

from random import uniform
from time import sleep
import pandas as pd
from features.build_features import build_features
from scraping.transform import add_elo_rating, prepare_elo_df, prepare_stats_df, pair_matches_to_one_row

from model.preprocessing import preprocess_for_model
from model.train import train_model

def test_pipeline():
    """
    Testuje cały pipeline na małej próbce: 3 sezony, maksymalnie 3 drużyny z każdego sezonu
    """
    print("🧪 ROZPOCZYNAM TEST PIPELINE...")
    
    # Inicjalizuje bazę danych
    db.init_db.initialize_database()
    
    # Testujemy tylko na 3 ostatnich sezonach
    test_seasons = ["2014-2015", "2015-2016", "2018-2019"]
    max_teams_per_season = 3  # Ograniczamy do 3 drużyn na sezon
    
    for season in test_seasons:
        print(f"\n{'='*50}")
        print(f"🔄 TESTUJE SEZON: {season}")
        print(f"{'='*50}")
        
        # Pobieramy główną stronę z tabelą ligową
        fbref_url = config.FBREF_URL_TEMPLATE.format(season=season)
        print(f"📥 Pobieram stronę główną: {fbref_url}")
        
        try:
            res_html = fetch_url(fbref_url)
            print(f"✅ Pobrano stronę główną dla sezonu {season}")
        except Exception as e:
            print(f"❌ Nie udało się pobrać strony głównej dla {season}: {e}")
            continue
        
        # Pobieramy linki do drużyn
        try:
            teams, full_links = parse_team_links(res_html)
            print(f"📊 Znaleziono {len(teams)} drużyn w sezonie {season}")
            
            # OGRANICZAMY DO PIERWSZYCH 3 DRUŻYN dla testu
            teams = teams[:max_teams_per_season]
            full_links = full_links[:max_teams_per_season]
            print(f"🧪 TEST: Ograniczam do {len(teams)} drużyn: {teams}")
        except Exception as e:
            print(f"❌ Nie udało się sparsować linków drużyn dla {season}: {e}")
            continue
        
        # ETAP 1: Pobieranie i zapisywanie HTML-i
        print(f"\n🌐 ETAP 1: Pobieranie HTML-i dla {len(teams)} drużyn...")
        for i, (team_name, link) in enumerate(zip(teams, full_links), 1): 
            print(f"➡️ [{i}/{len(teams)}] Pobieram HTML dla: {team_name}")
            
            try:
                html = fetch_url(link)
                save_html_to_db(team_name, season=season, html=html, url=link)
                print(f"✅ Zapisano HTML dla {team_name}")
            except Exception as e:
                print(f"❌ Nie udało się zapisać HTML-a dla {team_name}: {e}")
                continue
            
            # Krótsze opóźnienie dla testu
            sleep(uniform(2, 4))
        
        # ETAP 2: Przetwarzanie HTML-i i tworzenie DataFrame-ów
        print(f"\n🔄 ETAP 2: Przetwarzanie danych dla {len(teams)} drużyn...")
        for i, team_name in enumerate(teams, 1):
            print(f"⚙️ [{i}/{len(teams)}] Przetwarzam: {team_name}")
            
            try:
                # Ładujemy HTML z bazy danych
                html = load_html_from_db(team_name, season=season)
                if html is None:
                    print(f"⚠️ Brak HTML-a dla {team_name}, pomijam")
                    continue
                
                # Parsujemy podstawowe dane z fixtures
                fixture_df = parse_team_fixture_df(html)
                print(f"  📈 Fixtures: {len(fixture_df)} meczów")
                
                # Pobieramy linki do szczegółowych statystyk
                full_stats_links = parse_team_detailed_stats(html)
                print(f"  🔗 Statystyki: {len(full_stats_links)} linków")
                
                # Parsujemy wszystkie tabele statystyk
                temp_res = parse_all_stat_tables(full_stats_links)
                print(f"  📊 Sparsowano: {len(temp_res)} tabel")
                
                # Mergujemy wszystkie tabele
                merged_temp_df = merge_tables(temp_res, fixture_df)
                print(f"  🔄 Merged DF: {merged_temp_df.shape}")
                
                # Dodajemy kolumnę z nazwą drużyny
                merged_temp_df = add_team_column(merged_temp_df, team_name)
                
                # Dodajemy kolumnę sezonu (używam Twojej funkcji)
                merged_temp_df["Season"] = merged_temp_df["Date"].apply(add_season_from_date)
                
                # Usuwamy stare dane przed zapisaniem nowych
                delete_team_stats_raw(team_name, season)
                
                # Zapisujemy do bazy danych
                save_raw_team_data_to_db(merged_temp_df)
                print(f"  ✅ Zapisano: {len(merged_temp_df)} rekordów")
                
            except Exception as e:
                print(f"  ❌ Błąd: {e}")
                import traceback
                traceback.print_exc()  # Wyświetli pełny stack trace
                continue
        
        print(f"🎉 Zakończono test sezonu {season}")
    
    print(f"\n{'='*50}")
    print("🏁 TEST PIPELINE ZAKOŃCZONY!")
    print("📊 Sprawdź bazę danych, czy dane zostały poprawnie zapisane")
    print(f"{'='*50}")

def quick_db_check():
    """
    Szybkie sprawdzenie co jest w bazie danych po teście
    """
    import sqlite3
    import pandas as pd
    
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            # Sprawdź cache HTML-i
            html_count = pd.read_sql("SELECT COUNT(*) as count FROM html_cache", conn)
            print(f"📄 HTML cache: {html_count['count'].iloc[0]} rekordów")
            
            # Sprawdź surowe dane
            raw_count = pd.read_sql("SELECT COUNT(*) as count FROM team_stats_raw", conn)
            print(f"📊 Raw team stats: {raw_count['count'].iloc[0]} rekordów")
            
            # Sprawdź ile drużyn i sezonów
            teams_seasons = pd.read_sql("""
                SELECT Team, Season, COUNT(*) as matches 
                FROM team_stats_raw 
                GROUP BY Team, Season 
                ORDER BY Season, Team
            """, conn)
            
            print("\n📋 PODSUMOWANIE DANYCH:")
            print(teams_seasons.to_string(index=False))
            
    except Exception as e:
        print(f"❌ Błąd przy sprawdzaniu bazy: {e}")



def test_transformations():
    """
    Szybkie sprawdzenie czy dodanie featerow działa poprawnie
    """
    print("\n🧪 TESTY TRANSFORMACJI...")
    #Laduje dane
    #df = load_all_teams_raw_stats_from_db("2024-2025")
    df = load_all_teams_raw_stats_from_every_season_db()
    #przygotowanie danych
    df = prepare_stats_df(df)
    df = add_elo_rating(df)
    
    #obrobka
    df = build_features(df)
    # print(df.head(10))
    #parowanie do jednego wiersza
    df = pair_matches_to_one_row(df)
    #print(df.isna().sum().to_dict())
    #print(df.columns)
    return df

def test_preprocess_and_train(df):
    print("\n🧪 TEST PREPROCESS...")
    df = prepare_stats_df(df)
    X_train, y_train, X_test, y_test = preprocess_for_model(df)
    wyniki = train_model(X_train, y_train, X_test, y_test)
    return wyniki

if __name__ == "__main__":
    # Uruchom test
    #test_pipeline()
    a = test_transformations()
    # Sprawdź wyniki
    print("\n" + "="*50)
    print("🔍 SPRAWDZAM BAZĘ DANYCH...")
    #quick_db_check()
    b = test_preprocess_and_train(a)
    print(b)