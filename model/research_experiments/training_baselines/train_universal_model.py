import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from preprocessing.universal_feature_mapper import extract_universal_features


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_SAVE_PATH = BASE_DIR / "models" / "universal_rf.pkl"


def train_universal_model(df):

    print("\nExtracting universal features...")

    X = extract_universal_features(df)
    if "Label" in df.columns:
        y = df["Label"].apply(lambda x: 0 if x == "BENIGN" else 1)

    elif "label" in df.columns:
        y = df["label"].astype(int)

    else:
        raise ValueError("No label column found in dataset")

    

    print("Feature matrix shape:", X.shape)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print("\nTraining RandomForest on universal features...")

    model = RandomForestClassifier(
        n_estimators=150,
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("\nEvaluation on validation split:\n")

    y_pred = model.predict(X_test)

    print(classification_report(y_test, y_pred))

    print("\nSaving model...")

    joblib.dump(model, MODEL_SAVE_PATH)

    print("Saved universal model →", MODEL_SAVE_PATH)

    return model