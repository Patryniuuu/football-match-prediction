# Transformacja surowych danych (czyszczenie, formatowanie)
import pandas as pd
from clubelo.teams import FBREF_CLUEBLO_TEAMS_MAPPING
from config import FBREF_ABR_TO_FBREF
import os
from datetime import datetime
from clubelo.io import load_clubelo_csv, clubelo_csv_exists
def merge_tables(dfs: list[pd.DataFrame], fixtures_df : pd.DataFrame) -> pd.DataFrame:
    #Próbuje poprawić funkcje tak aby dzialała z pustymi DF-mi
    if len(dfs) == 0:
        raise ValueError("Nie ma dataframeów do mergowania")
    df = fixtures_df.copy()
    
    for sub_df in dfs:
        if len(sub_df) == 0:
            print(f"Pusty DF - pomijam merge, zostaną NaN w kolumnach")
            # Dodaj kolumny z tego DF jako NaN
            merge_columns = ["Date","Time","Comp","Round","Opponent"] 
            stat_columns = [col for col in sub_df.columns if col not in merge_columns]
            for col in stat_columns:
                if col not in df.columns:
                    df[col] = pd.NA  # lub np.nan
        else:
            try:
                df = df.merge(sub_df, on = ["Date","Time","Comp","Round","Opponent"], how="left")
                print(f"Merge OK: {sub_df.shape}")
            except KeyError as e:
                print(f"Nie ma kolumn do merge: {e}")
    #usuwam duplikaty kolumn powstale przy mergowaniu (dane są te same)
    if "xG_x" in df.columns and "xG_y" in df.columns:
        df["xG"] = df["xG_x"]
        df.drop(columns=["xG_x", "xG_y"], inplace=True)
    if "Poss_x" in df.columns and "Poss_y" in df.columns:
        df["Poss"] = df["Poss_x"]
        df.drop(columns=["Poss_x", "Poss_y"], inplace=True)
    if "PrgDist_x" in df.columns and "PrgDist_y" in df.columns:
        df["PrgDist"] = df["PrgDist_x"]
        df.drop(columns=["PrgDist_x","PrgDist_y"], inplace=True)
    return df


def add_elo_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Dodaje kolumny elo_team oraz elo_opponent. Na bazie mapowania fbref-> clubelo bierze odopowiednie pliki i je merguje na tej zasadzie.
    
    Args:
        df (pd.DataFrame): Dataframe z statystykami danej druzyny

    Returns:
        pd.DataFrame: zwraca Dataframe z dodatkowymi dwoma kolumnami z elo
    """
    df = df.copy()
    try:
        df["Date"] = pd.to_datetime(df["Date"])
    except KeyError as e:
        print(f"Ramka danych nie posiada kolumny Date: {e}")
        return None
    
    for club_col, elo_col in [("Team", "Elo_Team"), ("Opponent", "Elo_Opponent")]: #Pętla iteruje po krotkach w liscie, czyli co iteracje przyjmuje inne parametry, raz club_col = "Team", a raz "Opponent", chodzi o to aby nie pisać dwa razy tego samego kodu dla Team i Oponnent
        if club_col == "Team":
            for club in df[club_col].dropna().unique():
                club_clubelo = FBREF_CLUEBLO_TEAMS_MAPPING.get(club)
                if club_clubelo is None:
                    print(f"Nie znaleziono klubu {club} w mapowaniu, pomijam, nie próbuję pobierać CSVki")
                    continue
                if not clubelo_csv_exists(club_clubelo):
                    print(f"Nie istnieje plik CSV dla klubu {club}")
                    continue
                
                elo_df = load_clubelo_csv(club_clubelo)
                elo_df["From"] = pd.to_datetime(elo_df["From"])
                
                mask = df[club_col] == club #tworzę maskę T/F aby móc wybrać tylko te wiersze gdzie df[club_col] == club
                matches = df[mask].copy()
                merged = pd.merge_asof(
                matches.sort_values("Date"), #sortuje tak dla pewnosci aby merge_asof zadzialal poprawnie
                elo_df[["From", "Elo"]].sort_values("From"),
                left_on="Date",
                right_on="From"
                )
                df.loc[matches.index, elo_col] = merged["Elo"].values
        else:
            for club in df[club_col].dropna().unique():
                full_club_name = FBREF_ABR_TO_FBREF.get(club)
                club_clubelo = FBREF_CLUEBLO_TEAMS_MAPPING.get(full_club_name)
                if club_clubelo is None:
                    print(f"Nie znaleziono klubu {club} w mapowaniu, pomijam, nie próbuję pobierać CSVki")
                    continue
                if not clubelo_csv_exists(club_clubelo):
                    print(f"Nie istnieje plik CSV dla klubu {club}")
                    continue
                
                elo_df = load_clubelo_csv(club_clubelo)
                elo_df["From"] = pd.to_datetime(elo_df["From"])
                
                mask = df[club_col] == club #tworzę maskę T/F aby móc wybrać tylko te wiersze gdzie df[club_col] == club
                matches = df[mask].copy()
                merged = pd.merge_asof(
                matches.sort_values("Date"), #sortuje tak dla pewnosci aby merge_asof zadzialal poprawnie
                elo_df[["From", "Elo"]].sort_values("From"),
                left_on="Date",
                right_on="From",
                )
                df.loc[matches.index, elo_col] = merged["Elo"].values
    return df


def prepare_elo_df(df:pd.DataFrame) -> pd.DataFrame:
    """Funkcja ma za zadanie zmienić typy kolumn w elo_df, tak aby można było ją zmergować z DF-mem z statystykami
    """
    expected_columns = ["From", "To"]
    df = df.copy()
    try:
        for col in expected_columns:
            df[col] = pd.to_datetime(df[col])
        return df
    
    except Exception as e:
        print(f"Błąd konwersji kolumn {expected_columns} na typ datetime: {e} ")
        return None
    
def prepare_stats_df(df:pd.DataFrame) -> pd.DataFrame:
    """Funkcja ma za zadanie zmienić typy kolumn w stats_df, tak aby mogła być poprawnie zmergowana z elo_df, oraz aby kolumny mogły zostac poddane budowaniu featerow
    """
    df = df.copy()
    expected_columns_to_numeric = ['GF', 'GA', 'xGA', 'SoT%', 'G/Sh', 'G/SoT', 'Dist', 'PK', 'PKatt',
       'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG', 'xA', 'PPA', 'PrgP', 'Def 3rd',
       'Mid 3rd', 'Att 3rd', 'Att Pen', 'Live', '1/3', 'CPA', 'Dis', 'xG',
       'Poss', 'PrgDist'] #Lista kolumn z wszystkimi statystykami, które chce zamienić na numeric type
    existing_cols_to_numeric = [col for col in expected_columns_to_numeric if col in df.columns] #lista kolumn które istenieją w df
    try:
        #df["Date"] = pd.to_datetime(df["Date"]) to już zrobione w funkcji add_elo_rating
        for col in existing_cols_to_numeric:
            df[col] = pd.to_numeric(df[col], errors = "coerce")
        return df
    except Exception as e:
        print(f"Błąd konwersji kolumn {existing_cols_to_numeric} na typ numeric: {e} ")
        return None
    



def pair_matches_to_one_row(df:pd.DataFrame) -> pd.DataFrame:
    '''
    Funkcja ma za zadanie zmergowanie meczów w jeden rekord. Używana w pipeline po zmergowaniu df-a z elo_df oraz stworzeniu wszystkich statystyk
    '''
    df = df.copy()
    #Zacznę od odfiltrowania tylko meczów z PL
    try:    
        df = df[df["Comp"] == "Premier League"]    
        #Muszę podmienić nazwę skrótową w kolumnie Opponent na pełną za pomocą FBREF_ABR_TO_FBREF
        df["Opponent"] = df["Opponent"].apply(lambda x: FBREF_ABR_TO_FBREF.get(x))
        #teraz muszę utworzyć df_home i df_away
        df_home = df.loc[df["Venue"] == "Home"].copy()
        df_home = df_home.rename(columns=lambda x: f"{x}_H" if x not in ['Date', 'Team', 'Opponent', 'Time', 'Comp','Round','Season'] else x)
        df_away = df.loc[df["Venue"] == "Away"].copy()
        df_away = df_away.rename(columns=lambda x: f"{x}_A" if x not in ['Date', 'Team', 'Opponent', 'Time', 'Comp','Round', 'Season'] else x)
        # Klucz do łączenia: data + para drużyn
        df_home['match_key'] = df_home['Date'].astype(str) + "_" + df_home['Team'] + "_" + df_home['Opponent']
        df_away['match_key'] = df_away['Date'].astype(str) + "_" + df_away['Opponent'] + "_" + df_away['Team']

        #Usunąłem kolumny które występuja zarówno w df_home jak i df_away, tak aby uniknąc problemu z suffixami w merge-u
        dup_columns = [col for col in df_home.columns if col in df_away.columns]
        dup_columns = dup_columns[:-1]
        dup_columns
        df_away = df_away.drop(dup_columns, axis=1)

        #Merge
        df_merged = pd.merge(df_home, df_away, on='match_key', suffixes=('', ''))  # brak sufiksów, bo już mamy _H / _A
        df_merged
        # Dodaję na czysto: HomeTeam i AwayTeam
        df_merged['HomeTeam'] = df_merged['Team']
        df_merged['AwayTeam'] = df_merged['Opponent']
        #df_merged.drop(["Team", "Opponent"], axis=1, inplace=True) #usuwanie niechcianych kolumn będzie w osobnej funkcji
        return df_merged
    except Exception as e:
        print(f"Błąd przy zmergowaniu meczów: {e}")
        return None
        

    
    
