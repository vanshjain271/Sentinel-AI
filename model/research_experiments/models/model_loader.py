import joblib
from pathlib import Path

# Project root (Sentinel AI/)
BASE_DIR = Path(__file__).resolve().parents[3]

# Correct models folder
MODEL_DIR = BASE_DIR / "model" / "models"


def load_models():

    print("Loading Sentinel models")

    models = {}

    models["rf"] = joblib.load(MODEL_DIR / "random_forest.pkl")

    models["xgb"] = joblib.load(MODEL_DIR / "xgboost.pkl")

    models["ensemble"] = joblib.load(MODEL_DIR / "ensemble_voting.pkl")

    return models