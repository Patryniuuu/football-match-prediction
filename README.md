# Premier League Match Outcome Predictor

End-to-end machine learning project for predicting Premier League match outcomes (Home Win / Draw / Away Win) based on historical match data and advanced football statistics.

The project covers the full data pipeline:
- web scraping
- data storage
- feature engineering
- model training
- evaluation
- match outcome prediction

---

## Project Overview

This project collects historical Premier League match data from FBref, processes and enriches it with advanced features such as rolling statistics and Elo ratings, and trains an XGBoost classification model to predict match outcomes.

The main goal of the project is to demonstrate:
- real-world data engineering
- time-aware machine learning pipelines
- reproducible model training
- clean project structure

---

## Data Sources

- **FBref** – match results and advanced team statistics
- **ClubElo** – Elo rating data for football teams

---

## Tech Stack

- Python 3.10+
- pandas, numpy
- scikit-learn
- xgboost
- SQLite
- requests, BeautifulSoup
- joblib

---

## Project Structure

PL_match_predictor/
├── main.py # Main pipeline entry point
├── config.py # Global configuration
├── requirements.txt
├── README.md
├── scraping/ # Web scraping logic
├── features/ # Feature engineering
├── model/ # Preprocessing, training, evaluaction, prediction
├── db/ # Database logic (SQLite)
├── data/ # Local database (ignored in git)
├── models/ # Trained models (ignored in git)


---
## How to Run

### 1. Clone the repository
```bash
git clone [https://github.com/your_username/PL_match_predictor.git](https://github.com/your_username/PL_match_predictor.git)
cd PL_match_predictor

```

### 2. Create and activate virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate

```

**Linux / Mac**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install dependencies

```bash
pip install -r requirements.txt

```

### 4. Run the main pipeline

```bash
python main.py

```

---
## Model Performance

The model was evaluated using a time-aware cross-validation strategy to prevent data leakage.

### Key Metrics
- **Overall Accuracy:** 61.5%
- **Weighted F1-Score:** 0.62
- **Macro F1-Score:** 0.56

### Detailed Classification Report
| Class | Outcome | Precision | Recall | F1-Score | Support |
|-------|---------|-----------|--------|----------|---------|
| **0** | Away Win| 0.50      | 0.69   | 0.58     | 335     |
| **1** | Draw    | 0.38      | 0.36   | 0.37     | 404     |
| **2** | Home Win| 0.79      | 0.69   | 0.74     | 985     |

*Note: The model performs best on Home Wins (Class 2), which is consistent with the home advantage phenomenon in football. Draws (Class 1) remain the hardest outcome to predict.*

### Best Hyperparameters
The model was tuned using `XGBClassifier` with the following key parameters:
```python
{
    'n_estimators': 400,
    'learning_rate': 0.1,
    'max_depth': 4,
    'colsample_bytree': 0.8,
    'min_child_weight': 5,
    'early_stopping_rounds': 20
}
```

## Current Status

* [x] Data scraping
* [x] Feature engineering
* [x] Model training and evaluation
* [x] Reproducible pipeline
* [ ] Automated prediction of upcoming fixtures
* [ ] Model monitoring and retraining
* [ ] Basic Frontend for interaction
* [ ] Adding more leagues
---

## Disclaimer

This project is for educational and demonstration purposes only.

It is not intended for betting or gambling applications.

```

```