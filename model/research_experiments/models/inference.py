def run_inference(models, X):

    predictions = {}

    for name, model in models.items():

        print("Running model:", name)

        # skip deep models for now
        if name in ["lstm", "autoencoder"]:
            print(f"Skipping {name} (requires sequence input)")
            continue

        y_pred = model.predict(X)

        predictions[name] = y_pred

    return predictions