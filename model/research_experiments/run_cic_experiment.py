from preprocessing.load_cic_ddos import load_cic_dataset
from preprocessing.cic_feature_mapper import map_cic_to_sentinel, extract_labels

from models.model_loader import load_models
from evaluation.metrics import evaluate_model
from evaluation.result_saver import save_results


print("\n=== Experiment 3 : CIC-DDoS2019 ===\n")

df = load_cic_dataset(sample_rows=200000)

X = map_cic_to_sentinel(df)
y = extract_labels(df)

models = load_models()

for name, model in models.items():

    print(f"\nRunning model: {name}")

    y_pred = model.predict(X)

    metrics = evaluate_model(y, y_pred)

    save_results(
        model_name=name,
        metrics=metrics,
        y_true=y,
        y_pred=y_pred,
        dataset="CIC-DDoS2019"
    )