import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

from preprocessing.dataset_loader import load_dataset

print("Loading UNSW dataset")

train = load_dataset("../datasets/UNSW_NB15_training-set.parquet")
test = load_dataset("../datasets/UNSW_NB15_testing-set.parquet")

df = pd.concat([train, test], ignore_index=True)

print("Dataset shape:", df.shape)

# encode categorical columns
cat_cols = df.select_dtypes(include=["object"]).columns

for col in cat_cols:
    df[col] = df[col].astype("category").cat.codes

# label
y = df["label"]

X = df.drop(columns=["label", "attack_cat"])

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training Random Forest")

rf = RandomForestClassifier(n_estimators=200)

rf.fit(X_train, y_train)

pred_rf = rf.predict(X_test)

print("RF Results")
print(classification_report(y_test, pred_rf))


print("Training XGBoost")

xgb_model = xgb.XGBClassifier()

xgb_model.fit(X_train, y_train)

pred_xgb = xgb_model.predict(X_test)

print("XGB Results")
print(classification_report(y_test, pred_xgb))