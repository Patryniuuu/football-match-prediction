import pandas as pd

def feature_selection(df:pd.DataFrame):
    ''' Funkcja wybiera featery do nauki oraz zwraca dwa dfy: train i test, na których następnym etapie model jest trenowany i testowany.'''
    features_df = ['Elo_Team_H', 'Elo_Opponent_H', 'Elo_change_H', 'Elo_gap_H', 'GF_rolling_5_mean_H', 
                   'GA_rolling_5_mean_H', 'xGA_rolling_5_mean_H', 'SoT%_rolling_5_mean_H', 'G/Sh_rolling_5_mean_H', 
                   'G/SoT_rolling_5_mean_H', 'Dist_rolling_5_mean_H','npxG_rolling_5_mean_H', 'npxG/Sh_rolling_5_mean_H', 
                   'G-xG_rolling_5_mean_H', 'np:G-xG_rolling_5_mean_H',
                   'xA_rolling_5_mean_H', 'PPA_rolling_5_mean_H', 'PrgP_rolling_5_mean_H', 'Def 3rd_rolling_5_mean_H',
                   'Mid 3rd_rolling_5_mean_H', 'Att 3rd_rolling_5_mean_H', 'Att Pen_rolling_5_mean_H', 'Live_rolling_5_mean_H',
                   '1/3_rolling_5_mean_H', 'CPA_rolling_5_mean_H', 'Dis_rolling_5_mean_H', 'xG_rolling_5_mean_H', 'Poss_rolling_5_mean_H',
                   'PrgDist_rolling_5_mean_H', 'Elo_Team_rolling_5_mean_H', 'Elo_Opponent_rolling_5_mean_H', 'Elo_change_rolling_5_mean_H',
                   'Elo_gap_rolling_5_mean_H', 'days_since_last_game_H', 'Venue_code_H',
                   'Avg_points_5_H', 'Win_rate_5_H', 'Elo_change_A', 'Elo_gap_A', 'GF_rolling_5_mean_A', 'GA_rolling_5_mean_A',
                   'xGA_rolling_5_mean_A', 'SoT%_rolling_5_mean_A', 'G/Sh_rolling_5_mean_A', 'G/SoT_rolling_5_mean_A', 'Dist_rolling_5_mean_A',
                   'npxG_rolling_5_mean_A', 'npxG/Sh_rolling_5_mean_A', 'G-xG_rolling_5_mean_A',
                   'np:G-xG_rolling_5_mean_A', 'xA_rolling_5_mean_A', 'PPA_rolling_5_mean_A', 'PrgP_rolling_5_mean_A', 'Def 3rd_rolling_5_mean_A',
                   'Mid 3rd_rolling_5_mean_A', 'Att 3rd_rolling_5_mean_A', 'Att Pen_rolling_5_mean_A', 'Live_rolling_5_mean_A', 
                   '1/3_rolling_5_mean_A', 'CPA_rolling_5_mean_A', 'Dis_rolling_5_mean_A', 'xG_rolling_5_mean_A', 'Poss_rolling_5_mean_A',
                   'PrgDist_rolling_5_mean_A', 'Elo_Team_rolling_5_mean_A', 'Elo_Opponent_rolling_5_mean_A', 'Elo_change_rolling_5_mean_A',
                   'Elo_gap_rolling_5_mean_A', 'days_since_last_game_A', 'Avg_points_5_A', 'Win_rate_5_A']
    
    df = df.copy()
    try:
        X = df[features_df]
        y = df["result_coded_H"]
        return X,y
    except Exception as e:
        print(f"Nie mozna wybrać featureow do treningu: {e}")
        return None
    
def handle_missing_values(df, method=None):
    if method == "zero":
        return df.fillna(0)
    elif method == "mean":
        return df.fillna(df.mean(numeric_only=True))
    elif method == "drop":
        return df.dropna()
    else:
        return df  # zostawia NaN-y (dla XGBoost)
    
def train_test_split_timebased(df, date_threhold, format = "%Y-%m-%d"):
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except Exception as e:
        print(f"Błąd konwersji Date na datetime: {e}")
        return None, None
    
    date_threh = pd.to_datetime(date_threhold, format=format)
    try:
        df_train = df[df["Date"] < date_threh]
        df_test = df[df["Date"] >= date_threh]
        return df_train, df_test
    except Exception as e:
        print(f"Bład podczas dzielenia na zbiór treningowy i testowy: {e}")
        return None


def preprocess_for_model(df):
    df = df.copy()
    df_train = train_test_split_timebased(df, "2023-01-01")[0]
    df_test = train_test_split_timebased(df, "2023-01-01")[1]
    X_train = feature_selection(df_train)[0]
    X_train = handle_missing_values(X_train)
    y_train = feature_selection(df_train)[1]
    y_train = handle_missing_values(y_train)
    X_test = feature_selection(df_test)[0]
    X_test = handle_missing_values(X_test)
    y_test = feature_selection(df_test)[1]
    y_test = handle_missing_values(y_test)
    return X_train, y_train, X_test, y_test