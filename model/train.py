from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.utils.class_weight import compute_sample_weight
import pandas as pd
import numpy as np
import random, os, json, joblib, pathlib, datetime as dt

#ustalam seed, aby wyniki byly reprudokowalne

def set_seed(seed=42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

#tworze podzial
def make_cv(n_splits=5):
    return TimeSeriesSplit(n_splits=n_splits)

#Budujemy baseline model, do porownania

def build_xgb_base():
    return XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        n_estimators=400,
        learning_rate=0.1,
        max_depth=4,
        min_child_weight=5,
        colsample_bytree=0.8,
        reg_alpha=0.5,
        reg_lambda=2.0,
        #early_stopping_rounds=20,
        random_state=42,
        n_jobs=-1
    )

#Robie gridsearch

def run_gridsearch(model, param_grid, X_train, y_train, scoring="f1_macro", cv=None):
    ''' Funkcja która przeprowadza grid search po parametrach. 
        Zwraca:
        grid.best_estimator_ - model z najlepszymi parametrami
        grid.best_params_ - słownik z parami (parametr, najlepsza wartosc)
        grid.best_score_ - najwyzszą wartosc metryki    
    '''
    cv = cv or make_cv()
    grid = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring=scoring,
        cv=cv,
        n_jobs=-1,
        verbose=1,
        refit=True,  # po wyborze najlepszych parametrów, trenuje na całym train
    )
    grid.fit(X_train, y_train)
    print("Najlepsze parametry",grid.best_params_)
    print("Najlepszy wynik", grid.best_score_)
    return grid.best_estimator_, grid.best_params_, grid.best_score_


#Robimy sekwencyjny trening modelu

def sequential_training_xgb(X_train, y_train, scoring = "f1_macro", cv_splits = 5):
    cv = make_cv(cv_splits)
    model = build_xgb_base()
    best_params = {}
    
    #Najpierw szukam optymalnej struktury drzewa
    grid_1 = {'max_depth': [3, 4, 5, 6], 'min_child_weight': [1, 3, 5, 7]}
    model, p1, _ = run_gridsearch(model=model, param_grid=grid_1, X_train=X_train, y_train=y_train, scoring=scoring, cv=cv)
    best_params.update(p1)
    
    # Potem regularyzacja
    grid_2 = {'reg_alpha': [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1], 'reg_lambda': [0.1, 1,2, 5, 10]}
    model, p2, _ = run_gridsearch(model=model, param_grid=grid_2, X_train=X_train, y_train=y_train, scoring=scoring, cv=cv)
    best_params.update(p2)
    
    # Na końcu subsampling
    grid_3 = {'colsample_bytree': [0.6, 0.8, 1.0]}
    model, p3, _ = run_gridsearch(model=model, param_grid=grid_3, X_train=X_train, y_train=y_train, scoring=scoring, cv=cv)
    best_params.update(p3)
    
    return model, best_params


#Tworzymy early stopping dla xgboost. Bierze ostatnie 10% z zbioru treningowego jako wewnetrzny test do wczesnego zatrzymania
def split_train_val_for_early_stopping(X, y, val_ratio=0.1):
    split_ix = int(len(X) * (1 - val_ratio))
    return X.iloc[:split_ix], X.iloc[split_ix:], y.iloc[:split_ix], y.iloc[split_ix:]

#Ewaluacja
def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_weighted": f1_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred, digits=3)
    }
    return metrics


#zapisujemy artefakty

def save_artifacts(model, params, features, out_dir="models", name_prefix="xgb"):
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"{out_dir}/{name_prefix}_{stamp}.pkl"
    meta_path  = f"{out_dir}/{name_prefix}_{stamp}_meta.json"
    joblib.dump(model, model_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": stamp,
            "best_params": params,
            "features": features
        }, f, ensure_ascii=False, indent=2)
    return model_path, meta_path



#GLOWNA FUNKCJA

def train_model(
    X_train, y_train, X_test, y_test,
    do_tuning=False,
    scoring="f1_macro",
    cv_splits=5,
    save_dir="models",
    name_prefix="xgb"
):
    set_seed(42)

    # baseline
    model = build_xgb_base()

    #opcjonalny tuning sekwencyjny
    best_params = {}
    if do_tuning:
        tuned_model, best_params = sequential_training_xgb(
            X_train, y_train, scoring=scoring, cv_splits=cv_splits
        )
        model = tuned_model  # model ma już ustawione najlepsze parametry
    
    #dodaję wagi dla zbalansowania klas
    sample_weights = compute_sample_weight('balanced', y_train)
    
    # early stopping na końcu (retrain z walidacją wewnętrzną)
    X_tr, X_val, y_tr, y_val = split_train_val_for_early_stopping(X_train, y_train, val_ratio=0.1)
    
    # Obliczam wagi dla train subset
    weights_tr = compute_sample_weight('balanced', y_tr)
    draw_mask_tr = (y_tr == 1)
    weights_tr[draw_mask_tr] *= 1.1  # boost Draw o 10%
    
    weights_val = compute_sample_weight('balanced', y_val)
    draw_mask_val = (y_val == 1)
    weights_val[draw_mask_val] *= 1.1
    
    #early stopping do final fit
    model.set_params(early_stopping_rounds=20)  
    
    
    model.fit(X_tr, y_tr,
              sample_weight=weights_tr, 
              eval_set=[(X_val, y_val)], 
              sample_weight_eval_set=[weights_val],
              verbose=False)
    
    # ewaluacja na teście
    metrics = evaluate(model, X_test, y_test)

    # zapis artefaktów
    features = list(X_train.columns)
    model_path, meta_path = save_artifacts(model, best_params, features, out_dir=save_dir, name_prefix=name_prefix)

    print("Model zapisany:", model_path)
    print("Wyniki:", metrics)
    
    return {
        "model": model,
        "metrics": metrics,
        "best_params": best_params,
        "model_path": model_path,
        "meta_path": meta_path
    }
    
    