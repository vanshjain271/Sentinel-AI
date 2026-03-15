import joblib

def load_scaler(path):

    print("Loading scaler")

    scaler = joblib.load(path)

    return scaler