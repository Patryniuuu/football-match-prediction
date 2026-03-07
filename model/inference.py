# import pandas as pd
# import joblib
# import os

# # --- KONFIGURACJA FEATURE'ÓW (To samo co wcześniej) ---
# EXPECTED_FEATURES = [
#     "Elo_Team_H", "Elo_Opponent_H", "Elo_change_H", "Elo_gap_H",
#     "GF_rolling_5_mean_H", "GA_rolling_5_mean_H", "xGA_rolling_5_mean_H",
#     "SoT%_rolling_5_mean_H", "G/Sh_rolling_5_mean_H", "G/SoT_rolling_5_mean_H",
#     "Dist_rolling_5_mean_H", "npxG_rolling_5_mean_H", "npxG/Sh_rolling_5_mean_H",
#     "G-xG_rolling_5_mean_H", "np:G-xG_rolling_5_mean_H", "xA_rolling_5_mean_H",
#     "PPA_rolling_5_mean_H", "PrgP_rolling_5_mean_H", "Def 3rd_rolling_5_mean_H",
#     "Mid 3rd_rolling_5_mean_H", "Att 3rd_rolling_5_mean_H", "Att Pen_rolling_5_mean_H",
#     "Live_rolling_5_mean_H", "1/3_rolling_5_mean_H", "CPA_rolling_5_mean_H",
#     "Dis_rolling_5_mean_H", "xG_rolling_5_mean_H", "Poss_rolling_5_mean_H",
#     "PrgDist_rolling_5_mean_H", "Elo_Team_rolling_5_mean_H", "Elo_Opponent_rolling_5_mean_H",
#     "Elo_change_rolling_5_mean_H", "Elo_gap_rolling_5_mean_H", "days_since_last_game_H",
#     "Venue_code_H", "Avg_points_5_H", "Win_rate_5_H",
#     "Elo_change_A", "Elo_gap_A", "GF_rolling_5_mean_A", "GA_rolling_5_mean_A",
#     "xGA_rolling_5_mean_A", "SoT%_rolling_5_mean_A", "G/Sh_rolling_5_mean_A",
#     "G/SoT_rolling_5_mean_A", "Dist_rolling_5_mean_A", "npxG_rolling_5_mean_A",
#     "npxG/Sh_rolling_5_mean_A", "G-xG_rolling_5_mean_A", "np:G-xG_rolling_5_mean_A",
#     "xA_rolling_5_mean_A", "PPA_rolling_5_mean_A", "PrgP_rolling_5_mean_A",
#     "Def 3rd_rolling_5_mean_A", "Mid 3rd_rolling_5_mean_A", "Att 3rd_rolling_5_mean_A",
#     "Att Pen_rolling_5_mean_A", "Live_rolling_5_mean_A", "1/3_rolling_5_mean_A",
#     "CPA_rolling_5_mean_A", "Dis_rolling_5_mean_A", "xG_rolling_5_mean_A",
#     "Poss_rolling_5_mean_A", "PrgDist_rolling_5_mean_A", "Elo_Team_rolling_5_mean_A",
#     "Elo_Opponent_rolling_5_mean_A", "Elo_change_rolling_5_mean_A", "Elo_gap_rolling_5_mean_A",
#     "days_since_last_game_A", "Avg_points_5_A", "Win_rate_5_A"
# ]

# def load_resources(model_path, data_path):
#     """
#     Ładuje model i dane z dysku.
#     Zwraca: (model, df)
#     """
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"Brak modelu: {model_path}")
#     if not os.path.exists(data_path):
#         raise FileNotFoundError(f"Brak danych: {data_path}")

#     print(f"Ładowanie modelu z {model_path}...")
#     model = joblib.load(model_path)
    
#     print(f"Ładowanie danych z {data_path}...")
#     df = pd.read_csv(data_path)
#     df['Date'] = pd.to_datetime(df['Date'])
#     df = df.sort_values('Date') # Sortujemy, żeby ostatni wiersz był najnowszy
    
#     return model, df

# def get_latest_stats(df, team_name):
#     """
#     Wyciąga ostatni wiersz dla danej drużyny i czyści go z suffixów _H/_A.
#     """
#     # Filtrujemy mecze gdzie grała ta drużyna (jako Home lub Away)
#     team_matches = df[(df['HomeTeam'] == team_name) | (df['AwayTeam'] == team_name)]
    
#     if team_matches.empty:
#         return None
        
#     # Bierzemy ostatni mecz (najnowszy)
#     last_match = team_matches.iloc[-1]
    
#     stats = {}
    
#     # Sprawdzamy, czy w tym ostatnim meczu byli Gospodarzem czy Gościem,
#     # żeby wiedzieć, które kolumny (z _H czy z _A) brać.
#     if last_match['HomeTeam'] == team_name:
#         current_suffix = '_H'
#     else:
#         current_suffix = '_A'
        
#     # Iterujemy po kolumnach i bierzemy tylko te pasujące do drużyny
#     for col in last_match.index:
#         if str(col).endswith(current_suffix):
#             # Usuwamy końcówkę, np. zamieniamy "Elo_Team_H" na "Elo_Team"
#             # Dzięki temu mamy "czyste" statystyki, niezależne od tego gdzie grali.
#             clean_name = col[:-len(current_suffix)]
#             stats[clean_name] = last_match[col]
            
#     return stats

# def make_prediction(model, df, home_team, away_team):
#     """
#     Główna funkcja: bierze model, dane i nazwy drużyn -> zwraca wynik.
#     """
#     # 1. Pobieramy statystyki
#     stats_home = get_latest_stats(df, home_team)
#     stats_away = get_latest_stats(df, away_team)
    
#     if not stats_home or not stats_away:
#         return {"error": "Brak danych historycznych dla jednej z drużyn"}

#     # 2. Budujemy jeden wiersz do modelu
#     input_data = {}
    
#     # Przechodzimy przez listę kolumn, których oczekuje model
#     for feature in EXPECTED_FEATURES:
#         if feature.endswith('_H'):
#             base_name = feature[:-2] # np. "GF_rolling_5_mean"
#             if base_name == "Venue_code":
#                 input_data[feature] = 1 # Gospodarz zawsze ma Venue=1
#             else:
#                 input_data[feature] = stats_home.get(base_name, 0)
                
#         elif feature.endswith('_A'):
#             base_name = feature[:-2]
#             if base_name == "Venue_code":
#                 input_data[feature] = 0 # Gość zawsze ma Venue=0
#             else:
#                 input_data[feature] = stats_away.get(base_name, 0)
#         else:
#             input_data[feature] = 0 # Fallback

#     # 3. Tworzymy DataFrame i robimy predykcję
#     input_df = pd.DataFrame([input_data])
    
#     # Ważne: kolejność kolumn musi być idealna
#     input_df = input_df[EXPECTED_FEATURES]

#     probs = model.predict_proba(input_df)[0]
    
#     return {
#         "home_team": home_team,
#         "away_team": away_team,
#         "away_win": round(probs[0], 2),
#         "draw": round(probs[1], 2),
#         "home_win": round(probs[2], 2)
#     }
    
    
    
    


import pandas as pd
import joblib
import os

class MatchPredictor:
    
    # Podpowiedź: To jest zmienna "klasowa" (wspólna dla wszystkich),
    # trzyma listę kolumn, których wymaga Twój model. Zostaw ją tak jak jest.
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

    # ==========================================
    # ZADANIE 1: Konstruktor (Pakowanie plecaka)
    # ==========================================
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

    # ==========================================
    # ZADANIE 2: Pobieranie czystych statystyk
    # ==========================================
    def _get_latest_stats(self, team_name):
        """
        Zwraca słownik z "czystymi" statystykami drużyny z jej ostatniego meczu 
        (np. 'GF_rolling_5_mean': 2.0).
        """
        # KROK 1: Przefiltruj self.df, aby zostawić tylko wiersze, gdzie 'HomeTeam' 
        #         to team_name LUB 'AwayTeam' to team_name. Zapisz do zmiennej lokalnej.
        rows = self.df.loc[(self.df['HomeTeam'] == team_name) | (self.df['AwayTeam'] == team_name), :]
        # KROK 2: Weź ostatni wiersz z tego przefiltrowanego DataFrame (np. używając .iloc[-1]).
        last_row = rows.iloc[-1]
        # KROK 3: Stwórz pusty słownik, np. `stats = {}`
        stats = {}
        # KROK 4: Sprawdź, czy drużyna w tym ostatnim meczu grała u siebie (HomeTeam == team_name).
        #         Jeśli tak, ustaw zmienną suffix na '_H'. Jeśli nie, na '_A'.
        if last_row['HomeTeam']== team_name:
            suffix = '_H'
        else:
            suffix = '_A'
        # KROK 5: Zrób pętlę po wszystkich nazwach kolumn z tego ostatniego wiersza (ostatni_wiersz.index).
        #         Jeśli nazwa kolumny kończy się na Twój suffix (użyj .endswith()):
        #         a) Utnij ten suffix z nazwy kolumny (np. "Elo_Team_H" -> "Elo_Team").
        #         b) Zapisz w słowniku `stats` nową uciętą nazwę jako klucz, 
        #            a wartość z wiersza jako wartość.
        for col in last_row.index: #tutaj nie uzywam .columns bo jeden wiersz to juz obiekt Series ktory ma metode .index
            if col.endswith(suffix):
                col_clear = col[:-2]
                stats[col_clear] = last_row[col]
            
        # KROK 6: Zwróć wypełniony słownik.
        return stats


    # ==========================================
    # ZADANIE 3: Budowanie wektora dla modelu
    # ==========================================
    def _prepare_features(self, home_team, away_team):
        """
        Łączy statystyki gospodarza i gościa w jeden wiersz idealnie pasujący do modelu.
        """
        # KROK 1: Wywołaj metodę self._get_latest_stats() dla home_team i zapisz jako stats_home.
        stats_home = self._get_latest_stats(home_team)
        # KROK 2: Wywołaj tę samą metodę dla away_team i zapisz jako stats_away.
        stats_away = self._get_latest_stats(away_team)
        # (Obsłuż błąd: jeśli któraś zwróci pusto/None, wyrzuć błąd lub zwróć None)
        if stats_home == None or stats_away == None:
            raise Exception("Nie mamy statystyk wszystkich drużyn")
        # KROK 3: Stwórz pusty słownik `input_data = {}`
        input_data = {}
        # KROK 4: Zrób pętlę po liście self.EXPECTED_FEATURES:
        #         a) Jeśli cecha z listy kończy się na '_H':
        #            - Utnij '_H', żeby poznać czystą nazwę.
        #            - Sprawdź czy to "Venue_code". Jeśli tak, wpisz do input_data wartość 1.
        #            - Jeśli nie, pobierz wartość z `stats_home` i wpisz do input_data.
        #         b) Jeśli cecha kończy się na '_A':
        #            - Utnij '_A'.
        #            - Sprawdź czy to "Venue_code". Jeśli tak, wpisz 0.
        #            - Jeśli nie, pobierz wartość z `stats_away`.
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
        # KROK 5: Zamień słownik `input_data` na DataFrame (np. pd.DataFrame([input_data])).
        df = pd.DataFrame([input_data])
        # KROK 6: Upewnij się, że kolumny są w poprawnej kolejności 
        #         (df = df[self.EXPECTED_FEATURES]) i zwróć ten DataFrame.
        df = df[self.EXPECTED_FEATURES]
        return df


    # ==========================================
    # ZADANIE 4: Główna funkcja predykcyjna
    # ==========================================
    def predict(self, home_team, away_team):
        """
        Oblicza szanse na wynik meczu.
        """
        # KROK 1: Wywołaj self._prepare_features() przekazując home_team i away_team.
        #         Zapisz wynikowy DataFrame.
        df = self._prepare_features(home_team=home_team, away_team=away_team)
        # KROK 2: Użyj metody predict_proba() z atrybutu self.model, podając mu DataFrame z Kroku 1.
        #         Metoda zwróci tablicę z prawdopodobieństwami (klasy: 0=Away, 1=Draw, 2=Home).
        res = self.model.predict_proba(df)
        # predict_proba zwraca dwuwymiarową tablice np res = [[0.2345, 0.3121, 0.4534]]
        # KROK 3: Zwróć ładny słownik z wynikami, np:
        #         {"home_win": ..., "draw": ..., "away_win": ...}
        #         Pamiętaj, by zaokrąglić wyniki dla czytelności!
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
# ==========================================
# SEKCJA TESTOWA (odpal ten plik, by sprawdzić czy działa)
# ==========================================
if __name__ == "__main__":
    print("Rozpoczynam testy logiki biznesowej...")
    team_h = 'Leeds United'
    team_a = 'Everton'
    # Podmień ścieżki na poprawne dla Twojego repozytorium!
    PATH_MODEL = "models/xgb_20260120_010322.pkl"
    PATH_DATA = "data/processed/df_processed.csv"
    
    
    try:
        # Tworzymy naszego "robota"
        predictor = MatchPredictor(PATH_MODEL, PATH_DATA)
        print("✅ Inicjalizacja zakończona sukcesem!")
        print(predictor.get_all_teams())
        # Testujemy pobieranie statystyk
        stats = predictor._get_latest_stats(team_h)
        print(f"Ostatnie Elo {team_h}:", stats.get('Elo_Team'))
        
        # Wywołujemy główną metodę
        print(f"\nObliczam predykcję: {team_h} vs {team_a}...")
        wynik = predictor.predict(team_h,team_a)
        print("\n🎉 WYNIK PREDYKCJI:")
        print(wynik)
        
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas testów: {e}")