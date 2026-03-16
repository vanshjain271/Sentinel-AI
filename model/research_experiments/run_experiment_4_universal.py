from preprocessing.load_unsw_nb15 import load_unsw_dataset
from preprocessing.load_cic_ddos import load_cic_dataset
from preprocessing.universal_feature_mapper import extract_universal_features

from training_baselines.train_universal_model import train_universal_model
from evaluation.metrics import evaluate_model
from evaluation.result_saver import save_results


print("\n==============================")
print("Experiment 4: Universal Feature Model")
print("==============================\n")

print("Loading UNSW dataset for training...")

unsw_df = load_unsw_dataset()

model = train_universal_model(unsw_df)

print("\nLoading CIC dataset for cross-dataset testing...")

cic_df = load_cic_dataset(sample_rows=200000)

X_test = extract_universal_features(cic_df)

y_test = cic_df["Label"].apply(lambda x: 0 if x == "BENIGN" else 1)

print("\nRunning cross-dataset evaluation...")

y_pred = model.predict(X_test)

metrics = evaluate_model(y_test, y_pred)

save_results(
    model_name="universal_rf",
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred,
    dataset="CIC_cross_test"
)