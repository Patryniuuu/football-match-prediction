import pandas as pd
import numpy as np

def add_team_column(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """
    Dodaje kolumnę 'Team' z nazwą drużyny do podanego DataFrame'a.
    
    Parametry:
        df (pd.DataFrame): dane statystyczne jednego klubu
        team_name (str): nazwa klubu, np. "Liverpool"

    Zwraca:
        pd.DataFrame: ten sam DataFrame z dodaną kolumną 'Team'
    """
    df = df.copy()
    df["Team"] = team_name
    return df

def add_season_from_date(date_str:str ) -> str:
    # Przykład: "2024-05-13" → sezon 2023-2024
    year = pd.to_datetime(date_str).year
    month = pd.to_datetime(date_str).month

    if month >= 7:
        # Sezon np. 2024–2025
        return f"{year}-{year+1}"
    else:
        # np. styczeń–czerwiec 2024 -> sezon 2023–2024
        return f"{year-1}-{year}"


def create_rolling_stats(df: pd.DataFrame, window = 5, method : str = "mean") -> pd.DataFrame:
    """
    Tworzy rolling statistics używając nazwy metody jako string
    
    Args:
        df: DataFrame z danymi
        window: wielkość okna
        method: nazwa metody ("mean", "sum", "std", "min", "max", "median")
    """
    df_result = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        rolling_obj = df[col].shift(1).rolling(window=window, min_periods=1)
        
        # Zastosowuje odpowiednią metodę
        if method == "mean":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.mean().round(2)
        elif method == "sum":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.sum().round(2)
        elif method == "std":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.std().round(2)
        elif method == "min":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.min()
        elif method == "max":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.max()
        elif method == "median":
            df_result[f"{col}_rolling_{window}_{method}"] = rolling_obj.median().round(2)
        else:
            raise ValueError(f"Nieznana metoda: {method}")
    
    return df_result

def create_elo_features(df:pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    try:
        df["Elo_change"] = df["Elo_Team"].diff().round(2)
        df["Elo_gap"] = (df["Elo_Team"] - df["Elo_Opponent"]).round(2)
    except KeyError as e:
        print(f"Nie ma kolumn do budowania featerow: {e}")
        return None
    return df

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    try:
        df["days_since_last_game"] = df["Date"].diff().dt.days
    except KeyError as e:
        print(f"Nie ma kolumn do budowania featerow: {e}")
        return None
    return df
    
def create_code_features(df: pd.DataFrame) -> pd.DataFrame:
    """ 
    Tworzy kodowanie:
    - Venue_code: mecz domowy/wyjazd (0/1)
    - Points_gained: "W"=3, "D"=1, "L"=0
    - is_win, is_draw, is_loss (0/1)
    - result_coded: "L"=0, "D"=1, "W"=2
    - rolling statystyki odpowiadającym formie (ostatnie 5 meczów)
    """
    
    df = df.copy()
    try:
        df["Venue_code"] = df["Venue"].astype("category").cat.codes
        df["Points_gained"] = df["Result"].astype("category").map({"W": 3, "D": 1, "L": 0})
        df["is_win"] = (df["Result"] == "W").astype(int)
        df["is_draw"] = (df["Result"] == "D").astype(int)
        df["is_loss"] = (df["Result"] == "L").astype(int)
        df["result_coded"] = df["Result"].map(({"L": 0, "D": 1, "W": 2})).astype(int)
        # rolling (ostatnie 5 meczów, bez bieżącego)
        df["Avg_points_5"] = df["Points_gained"].shift(1).rolling(5, min_periods=1).mean().round(2)
        df["Win_rate_5"]   = df["is_win"].shift(1).rolling(5, min_periods=1).mean().round(2)
        
    except KeyError as e:
        print(f"Nie ma kolumn do budowania featerow: {e}")
        return None
    return df

def build_features(df):
    """Master funkcja wszystkich funkcji do budowania featerow"""
    df = create_elo_features(df)
    df = create_rolling_stats(df)
    df = create_time_features(df)
    df = create_code_features(df)
    return df