import streamlit as st
import pandas as pd
from model.inference import MatchPredictor

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="PL Match Predictor", 
    page_icon="⚽", 
    layout="wide"  # Zmieniliśmy na 'wide', żeby tabela miała więcej miejsca
)

# --- 2. ŁADOWANIE MODELU (CACHE) ---
PATH_MODEL = "models/xgb_20260120_010322.pkl"
PATH_DATA = "data/processed/df_processed.csv"

@st.cache_resource
def get_predictor():
    return MatchPredictor(PATH_MODEL, PATH_DATA)

try:
    predictor = get_predictor()
    lista_druzyn = predictor.get_all_teams()
except Exception as e:
    st.error(f"❌ Błąd inicjalizacji silnika predykcji: {e}")
    st.stop()

# --- 3. INTERFEJS UŻYTKOWNIKA ---
st.title("⚽ Premier League Batch Predictor")
st.markdown("Skonfiguruj listę spotkań i przewiduj wiele wyników za jednym kliknięciem.")
st.markdown("---")

# Pytamy użytkownika, ile meczów chce dodać do kuponu/listy
ile_meczow = st.number_input("Ile meczów chcesz przewidzieć naraz?", min_value=1, max_value=10, value=3)
st.markdown("<br>", unsafe_allow_html=True)

# Lista, do której będziemy zapisywać wybrane pary drużyn
mecze_do_predykcji = []

# Dynamicznie generujemy pola wyboru w pętli
for i in range(ile_meczow):
    st.markdown(f"**Mecz nr {i+1}**")
    col1, col2 = st.columns(2)
    
    with col1:
        # Ważne: w pętli każdy widżet MUSI mieć unikalny argument 'key'
        home = st.selectbox(f"🏠 Gospodarz", lista_druzyn, index=0, key=f"home_{i}")
    
    with col2:
        away = st.selectbox(f"✈️ Gość", lista_druzyn, index=1, key=f"away_{i}")
        
    mecze_do_predykcji.append((home, away))
    st.markdown("---")

# --- 4. AKCJA (PRZYCISK I WYNIKI) ---
if st.button("🔮 Przewiduj wszystkie mecze!", use_container_width=True, type="primary"):
    
    with st.spinner("Analizuję formę, przeliczam Elo i symuluję mecze..."):
        
        # Tworzymy pustą listę na zebrane wyniki
        tabela_wynikow = []
        czy_blad = False
        
        # Iterujemy po wszystkich wybranych meczach
        for idx, (home_team, away_team) in enumerate(mecze_do_predykcji):
            
            if home_team == away_team:
                st.warning(f"⚠️ Mecz nr {idx+1} pominięty: Wybrano dwie takie same drużyny ({home_team}).")
                continue
                
            try:
                # Wywołujemy predykcję z naszej klasy
                wynik = predictor.predict(home_team, away_team)
                
                # Zabezpieczenie przed dzieleniem przez zero (choć model rzadko daje okrągłe 0)
                prob_home = max(wynik['home_win'], 0.01)
                prob_draw = max(wynik['draw'], 0.01)
                prob_away = max(wynik['away_win'], 0.01)
                
                # Obliczamy "sprawiedliwe" kursy (1 / prawdopodobieństwo)
                kurs_home = 1 / prob_home
                kurs_draw = 1 / prob_draw
                kurs_away = 1 / prob_away
                
                # Dodajemy zgrabny słownik do naszej listy wyników
                tabela_wynikow.append({
                    "Mecz": f"{home_team} vs {away_team}",
                    "🏠 Szansa (1)": f"{wynik['home_win'] * 100:.0f}%",
                    "🤝 Szansa (X)": f"{wynik['draw'] * 100:.0f}%",
                    "✈️ Szansa (2)": f"{wynik['away_win'] * 100:.0f}%",
                    "📈 Kurs (1)": f"{kurs_home:.2f}",
                    "📈 Kurs (X)": f"{kurs_draw:.2f}",
                    "📈 Kurs (2)": f"{kurs_away:.2f}"
                })
            except Exception as e:
                st.error(f"Błąd przy meczu {home_team} vs {away_team}: {e}")
                czy_blad = True
                
        # --- WIZUALIZACJA ZBIORCZA ---
        if tabela_wynikow and not czy_blad:
            st.success("✅ Analiza wszystkich spotkań zakończona pomyślnie!")
            
            # Zamieniamy naszą listę słowników na piękny DataFrame
            df_wyniki = pd.DataFrame(tabela_wynikow)
            
            # Index zaczynający się od 1 zamiast 0
            df_wyniki.index = range(1, len(df_wyniki) + 1)
            
            # Wyświetlamy jako interaktywną tabelę w Streamlit
            st.dataframe(df_wyniki, use_container_width=True)
            
            # Możliwość pobrania wyników do CSV
            csv = df_wyniki.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Pobierz wyniki jako CSV",
                data=csv,
                file_name='predykcje_pl.csv',
                mime='text/csv',
            )