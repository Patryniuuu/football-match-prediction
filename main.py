
# main.py - Główny pipeline projektu
import config
import db.init_db
from db.io import (
    save_html_to_db, 
    load_html_from_db, 
    save_raw_team_data_to_db, 
    delete_team_stats_raw, 
    load_all_teams_raw_stats_from_every_season_db
)
from scraping.fetch import fetch_url
from scraping.parse import (
    parse_team_links, 
    parse_team_fixture_df, 
    parse_team_detailed_stats, 
    parse_all_stat_tables
)
from scraping.transform import (
    merge_tables, 
    add_elo_rating, 
    prepare_stats_df, 
    pair_matches_to_one_row
)
from features.build_features import add_team_column, add_season_from_date, build_features
from model.preprocessing import preprocess_for_model
from model.train import train_model

from random import uniform
from time import sleep
import pandas as pd

RUN_SCRAPING = False        # Scrapuj dane z FBref (czasochłonne)
RUN_TRANSFORM = True
RUN_TRAINING = True         # Trenuj model

def scrape_and_save_data(seasons: list[str]):
    """
    ETAP 1 & 2: Scrapowanie danych i zapisywanie do bazy
    
    Args:
        seasons: Lista sezonów do scrapowania (np. ["2023-2024", "2024-2025"])
    """
    print("="*60)
    print("ROZPOCZYNAM SCRAPOWANIE DANYCH")
    print("="*60)
    
    for season in seasons:
        print(f"\n{'='*60}")
        print(f"PRZETWARZAM SEZON: {season}")
        print(f"{'='*60}")
        
        # Pobieramy główną stronę z tabelą ligową
        fbref_url = config.FBREF_URL_TEMPLATE.format(season=season)
        print(f"Pobieram stronę główną: {fbref_url}")
        
        try:
            res_html = fetch_url(fbref_url)
            print(f"Pobrano stronę główną dla sezonu {season}")
        except Exception as e:
            print(f"Nie udało się pobrać strony głównej dla {season}: {e}")
            continue
        
        # Pobieramy linki do wszystkich drużyn
        try:
            teams, full_links = parse_team_links(res_html)
            print(f"Znaleziono {len(teams)} drużyn w sezonie {season}")
        except Exception as e:
            print(f"Nie udało się sparsować linków drużyn dla {season}: {e}")
            continue
        
        # ETAP 1: Pobieranie i zapisywanie HTML-i
        print(f"\nETAP 1: Pobieranie HTML-i dla {len(teams)} drużyn...")
        for i, (team_name, link) in enumerate(zip(teams, full_links), 1): 
            print(f"[{i}/{len(teams)}] Pobieram HTML dla: {team_name}")
            
            try:
                html = fetch_url(link)
                save_html_to_db(team_name, season=season, html=html, url=link)
                print(f"Zapisano HTML dla {team_name}")
            except Exception as e:
                print(f"Nie udało się zapisać HTML-a dla {team_name}: {e}")
                continue
            
            # Opóźnienie między requestami
            sleep(uniform(3, 6))
        
        # ETAP 2: Przetwarzanie HTML-i i tworzenie DataFrame-ów
        print(f"\n ETAP 2: Przetwarzanie danych dla {len(teams)} drużyn...")
        for i, team_name in enumerate(teams, 1):
            print(f" [{i}/{len(teams)}] Przetwarzam: {team_name}")
            
            try:
                # Ładujemy HTML z bazy danych
                html = load_html_from_db(team_name, season=season)
                if html is None:
                    print(f" Brak HTML-a dla {team_name}, pomijam")
                    continue
                
                # Parsujemy podstawowe dane z fixtures
                fixture_df = parse_team_fixture_df(html)
                print(f"   Fixtures: {len(fixture_df)} meczów")
                
                # Pobieramy linki do szczegółowych statystyk
                full_stats_links = parse_team_detailed_stats(html)
                print(f"  Statystyki: {len(full_stats_links)} linków")
                
                # Parsujemy wszystkie tabele statystyk
                temp_res = parse_all_stat_tables(full_stats_links)
                print(f"   Sparsowano: {len(temp_res)} tabel")
                
                # Mergujemy wszystkie tabele
                merged_temp_df = merge_tables(temp_res, fixture_df)
                print(f"   Merged DF: {merged_temp_df.shape}")
                
                # Dodajemy kolumnę z nazwą drużyny
                merged_temp_df = add_team_column(merged_temp_df, team_name)
                
                # Dodajemy kolumnę sezonu
                merged_temp_df["Season"] = merged_temp_df["Date"].apply(add_season_from_date)
                
                # Usuwamy stare dane przed zapisaniem nowych
                delete_team_stats_raw(team_name, season)
                
                # Zapisujemy do bazy danych
                save_raw_team_data_to_db(merged_temp_df)
                print(f"   Zapisano: {len(merged_temp_df)} rekordów")
                
            except Exception as e:
                print(f"   Błąd: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f" Zakończono przetwarzanie sezonu {season}")
    
    print(f"\n{'='*60}")
    print(" SCRAPOWANIE ZAKOŃCZONE!")
    print(f"{'='*60}")


def transform_and_engineer_features():
    """
    ETAP 3: Transformacja danych i inżynieria cech
    
    Returns:
        pd.DataFrame: Dane z dodanymi cechami, sparowane do jednego wiersza na mecz
    """
    print("\n" + "="*60)
    print(" ETAP 3: TRANSFORMACJA I INŻYNIERIA CECH")
    print("="*60)
    
    # Ładujemy wszystkie dane z bazy
    print(" Ładuję dane z bazy...")
    df = load_all_teams_raw_stats_from_every_season_db()
    print(f" Załadowano {len(df)} rekordów z {df['Season'].nunique()} sezonów")
    
    # Przygotowanie danych
    print(" Przygotowuję dane...")
    df = prepare_stats_df(df)
    
    # Dodanie ratingu ELO
    print(" Obliczam rating ELO...")
    df = add_elo_rating(df)
    
    # Budowanie cech
    print(" Buduję cechy...")
    df = build_features(df)
    
    # Parowanie meczów do jednego wiersza
    print(" Paruję mecze do jednego wiersza...")
    df = pair_matches_to_one_row(df)
    
    print(f" Transformacja zakończona! Wynikowy DataFrame: {df.shape}")
    
    return df


def train_prediction_model(df: pd.DataFrame):
    """
    ETAP 4: Preprocessing i trenowanie modelu
    
    Args:
        df: DataFrame z danymi po inżynierii cech
        
    Returns:
        dict: Wyniki trenowania modelu
    """
    print("\n" + "="*60)
    print(" ETAP 4: TRENOWANIE MODELU")
    print("="*60)
    
    # Przygotowanie danych
    print(" Przygotowuję dane...")
    df = prepare_stats_df(df)
    
    # Preprocessing dla modelu
    print(" Preprocessing danych...")
    X_train, y_train, X_test, y_test = preprocess_for_model(df)
    print(f" Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Trenowanie modelu
    print(" Trenuję model...")
    wyniki = train_model(X_train, y_train, X_test, y_test)
    
    print("Trenowanie zakończone!")
    
    return wyniki


def main():
    """
    Główny pipeline projektu - uruchamia wszystkie etapy
    """
    print("="*60)
    print("URUCHAMIAM GŁÓWNY PIPELINE")
    print("="*60)
    
    # Inicjalizacja bazy danych
    print("\n Inicjalizuję bazę danych...")
    db.init_db.initialize_database()
    print(" Baza danych gotowa")
    
    # Definiujemy sezony do przetworzenia
    seasons_to_scrape = [
        "2014-2015",
        "2015-2016", 
        "2016-2017",
        "2017-2018",
        "2018-2019",
        "2019-2020",
        "2020-2021",
        "2021-2022",
        "2022-2023",
        "2023-2024",
        "2024-2025"
    ]
    
    # ETAP 1 & 2: Scrapowanie danych
    if RUN_SCRAPING:
        scrape_and_save_data(seasons_to_scrape)
    else:
        print("Pomijam scrapowanie (RUN_SCRAPING=False)")

    if RUN_TRANSFORM:
        # ETAP 3: Transformacja i inżynieria cech
        df_transformed = transform_and_engineer_features()
    else:
        print("Pomijam transformacje danych (RUN_TRANSFORM=False)")
    if RUN_TRAINING:
        # ETAP 4: Trenowanie modelu
        wyniki = train_prediction_model(df_transformed)
    else:
        print("Pomijam trenowanie modelu (RUN_TRAINING=False)")

    
    # Wyświetlanie końcowych wyników
    print("\n" + "="*60)
    print(" PIPELINE ZAKOŃCZONY POMYŚLNIE!")
    print("="*60)
    print("\n WYNIKI MODELU:")
    print(wyniki)
    print(wyniki['metrics']['classification_report'])
    print("\n" + "="*60)


if __name__ == "__main__":
    main()