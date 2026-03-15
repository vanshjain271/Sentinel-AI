import joblib
from tensorflow.keras.models import load_model

def load_models():

    models = {}

    print("Loading Sentinel models")

    models["rf"] = joblib.load("../models/random_forest.pkl")

    models["xgb"] = joblib.load("../models/xgboost.pkl")

    models["ensemble"] = joblib.load("../models/ensemble_voting.pkl")

    models["lstm"] = load_model("../models/lstm.keras")

    models["autoencoder"] = load_model("../models/autoencoder.keras")

    return models