import numpy as np
import joblib
from pathlib import Path


# Load Sentinel feature schema
BASE_DIR = Path(__file__).resolve().parents[3]
FEATURE_FILE = BASE_DIR / "model" / "models" / "5g_feature_names.pkl"

SENTINEL_FEATURES = joblib.load(FEATURE_FILE)


def map_cic_to_sentinel(df):

    n_samples = len(df)
    n_features = len(SENTINEL_FEATURES)

    # Create empty feature matrix
    X = np.zeros((n_samples, n_features))

    # Map CIC features to some Sentinel positions
    feature_map = {
        "protocol": "Protocol",
        "packet_size_entropy": "Packet Length Mean",
        "priority_level": "Flow Packets/s",
        "max_delay_budget": "Flow Duration"
    }

    for sentinel_feature, cic_feature in feature_map.items():

        if sentinel_feature in SENTINEL_FEATURES and cic_feature in df.columns:

            idx = SENTINEL_FEATURES.index(sentinel_feature)

            values = df[cic_feature].astype(float)

            values.replace([np.inf, -np.inf], np.nan, inplace=True)
            values.fillna(0, inplace=True)

            X[:, idx] = values

    return X


def extract_labels(df):

    y = df["Label"].apply(lambda x: 0 if x == "BENIGN" else 1)

    return y.values