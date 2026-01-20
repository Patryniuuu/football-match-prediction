import joblib
import pandas as pd

def load_model(model_path):
    """Ładuje wytrenowany model z pliku .pkl"""
    return joblib.load(model_path)

def predict_upcoming_matches(model, df_upcoming, features):
    """
    Przewiduje wyniki dla przyszłych meczów.
    df_upcoming - dane z najbliższych meczów (po feature engineeringu)
    features - lista kolumn z treningu
    """
    # Upewnij się, że kolumny są w tej samej kolejności
    X = df_upcoming[features].copy()
    
    # Predykcja
    preds_proba = model.predict_proba(X)
    preds_class = model.predict(X)

    df_upcoming["predicted_class"] = preds_class
    df_upcoming["prob_home_win"] = preds_proba[:, 0]
    df_upcoming["prob_draw"] = preds_proba[:, 1]
    df_upcoming["prob_away_win"] = preds_proba[:, 2]

    return df_upcoming[["Team", "Opponent", "predicted_class", "prob_home_win", "prob_draw", "prob_away_win"]]
