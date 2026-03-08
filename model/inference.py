import pandas as pd
import joblib
import os

class MatchPredictor:
    
    EXPECTED_FEATURES = [
        "Elo_Team_H", "Elo_Opponent_H", "Elo_change_H", "Elo_gap_H",
        "GF_rolling_5_mean_H", "GA_rolling_5_mean_H", "xGA_rolling_5_mean_H",
        "SoT%_rolling_5_mean_H", "G/Sh_rolling_5_mean_H", "G/SoT_rolling_5_mean_H",
        "Dist_rolling_5_mean_H", "npxG_rolling_5_mean_H", "npxG/Sh_rolling_5_mean_H",
        "G-xG_rolling_5_mean_H", "np:G-xG_rolling_5_mean_H", "xA_rolling_5_mean_H",
        "PPA_rolling_5_mean_H", "PrgP_rolling_5_mean_H", "Def 3rd_rolling_5_mean_H",
        "Mid 3rd_rolling_5_mean_H", "Att 3rd_rolling_5_mean_H", "Att Pen_rolling_5_mean_H",
        "Live_rolling_5_mean_H", "1/3_rolling_5_mean_H", "CPA_rolling_5_mean_H",
        "Dis_rolling_5_mean_H", "xG_rolling_5_mean_H", "Poss_rolling_5_mean_H",
        "PrgDist_rolling_5_mean_H", "Elo_Team_rolling_5_mean_H", "Elo_Opponent_rolling_5_mean_H",
        "Elo_change_rolling_5_mean_H", "Elo_gap_rolling_5_mean_H", "days_since_last_game_H",
        "Venue_code_H", "Avg_points_5_H", "Win_rate_5_H",
        "Elo_change_A", "Elo_gap_A", "GF_rolling_5_mean_A", "GA_rolling_5_mean_A",
        "xGA_rolling_5_mean_A", "SoT%_rolling_5_mean_A", "G/Sh_rolling_5_mean_A",
        "G/SoT_rolling_5_mean_A", "Dist_rolling_5_mean_A", "npxG_rolling_5_mean_A",
        "npxG/Sh_rolling_5_mean_A", "G-xG_rolling_5_mean_A", "np:G-xG_rolling_5_mean_A",
        "xA_rolling_5_mean_A", "PPA_rolling_5_mean_A", "PrgP_rolling_5_mean_A",
        "Def 3rd_rolling_5_mean_A", "Mid 3rd_rolling_5_mean_A", "Att 3rd_rolling_5_mean_A",
        "Att Pen_rolling_5_mean_A", "Live_rolling_5_mean_A", "1/3_rolling_5_mean_A",
        "CPA_rolling_5_mean_A", "Dis_rolling_5_mean_A", "xG_rolling_5_mean_A",
        "Poss_rolling_5_mean_A", "PrgDist_rolling_5_mean_A", "Elo_Team_rolling_5_mean_A",
        "Elo_Opponent_rolling_5_mean_A", "Elo_change_rolling_5_mean_A", "Elo_gap_rolling_5_mean_A",
        "days_since_last_game_A", "Avg_points_5_A", "Win_rate_5_A"
    ]

    def __init__(self, model_path, data_path):
        """
        KROK 1: Użyj joblib.load(), aby wczytać plik z podanej ścieżki 'model_path' 
                i przypisz go do atrybutu obiektu (self.model).
        KROK 2: Użyj pd.read_csv(), aby wczytać dane z 'data_path'
                i przypisz je do atrybutu (self.df).
        KROK 3: Zamień kolumnę 'Date' w self.df na format datetime (pd.to_datetime).
        KROK 4: Posortuj self.df po dacie rosnąco (aby najnowsze mecze były na dole).
        """
        self.model = joblib.load(model_path)
        self.df = pd.read_csv(data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.sort_values(by='Date', ascending=True, inplace=True)

    def _get_latest_stats(self, team_name):
        """
        Zwraca słownik z "czystymi" statystykami drużyny z jej ostatniego meczu 
        (np. 'GF_rolling_5_mean': 2.0).
        """
        rows = self.df.loc[(self.df['HomeTeam'] == team_name) | (self.df['AwayTeam'] == team_name), :]
        last_row = rows.iloc[-1]
        stats = {}
        
        if last_row['HomeTeam']== team_name:
            suffix = '_H'
        else:
            suffix = '_A'
        
        for col in last_row.index: #tutaj nie uzywam .columns bo jeden wiersz to juz obiekt Series ktory ma metode .index
            if col.endswith(suffix):
                col_clear = col[:-2]
                stats[col_clear] = last_row[col]
            
        return stats

    def _prepare_features(self, home_team, away_team):
        """
        Łączy statystyki gospodarza i gościa w jeden wiersz idealnie pasujący do modelu.
        """
        stats_home = self._get_latest_stats(home_team)
        stats_away = self._get_latest_stats(away_team)
        if stats_home == None or stats_away == None:
            raise Exception("Nie mamy statystyk wszystkich drużyn")
        
        input_data = {}
        
        for el in self.EXPECTED_FEATURES:
            if el.endswith('_H'):
                el_cl = el[:-2]
                if el_cl == 'Venue_code':
                    input_data[el] = 1
                else:
                    input_data[el] = stats_home.get(el_cl, 0)
            elif el.endswith('_A'):
                el_cl = el[:-2]
                if el_cl == 'Venue_code':
                    input_data[el] = 0
                else:
                    input_data[el] = stats_away.get(el_cl, 0)
        
        df = pd.DataFrame([input_data])
        df = df[self.EXPECTED_FEATURES]
        return df


    def predict(self, home_team, away_team):
        """
        Oblicza szanse na wynik meczu.
        """
        df = self._prepare_features(home_team=home_team, away_team=away_team)
        res = self.model.predict_proba(df)
        probs = res[0]
        wynik = {
            "away_win": float(round(probs[0], 2)), # Klasa 0
            "draw": float(round(probs[1], 2)),     # Klasa 1
            "home_win": float(round(probs[2], 2))  # Klasa 2
        }
        
        return wynik

    def get_all_teams(self):
        """
        Pobiera unikalną listę wszystkich drużyn dostępnych w bazie danych.
        """
        # Bierzemy unikalne wartości z kolumny HomeTeam (tam na pewno każdy kiedyś grał)
        # Zamieniamy to na standardową listę w Pythonie i sortujemy alfabetycznie
        teams = sorted(self.df['HomeTeam'].dropna().unique().tolist())
        return teams

#test czy działa
if __name__ == "__main__":
    print("Rozpoczynam testy...")
    team_h = 'Leeds United'
    team_a = 'Everton'
    
    PATH_MODEL = "models/xgb_20260120_010322.pkl"
    PATH_DATA = "data/processed/df_processed.csv"
    
    
    try:
        predictor = MatchPredictor(PATH_MODEL, PATH_DATA)
        print("✅ Inicjalizacja zakończona sukcesem!")
        print(predictor.get_all_teams())
        stats = predictor._get_latest_stats(team_h)
        print(f"Ostatnie Elo {team_h}:", stats.get('Elo_Team'))
        
        print(f"\nObliczam predykcję: {team_h} vs {team_a}...")
        wynik = predictor.predict(team_h,team_a)
        print("\n🎉 WYNIK PREDYKCJI:")
        print(wynik)
        
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas testów: {e}")