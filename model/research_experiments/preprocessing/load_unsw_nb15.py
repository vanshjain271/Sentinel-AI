import pandas as pd
from pathlib import Path


DATASET_PATH = Path("model/research_experiments/datasets/unsw_nb15")

FILES = [
    "UNSW_NB15_training-set.parquet",
    "UNSW_NB15_testing-set.parquet"
]


def load_unsw_dataset(sample_rows=None):

    dfs = []

    for file in FILES:

        path = DATASET_PATH / file

        print(f"Loading {path}")

        df = pd.read_parquet(path)

        if sample_rows is not None:
            df = df.sample(sample_rows)

        dfs.append(df)

    dataset = pd.concat(dfs, ignore_index=True)

    print("\nUNSW dataset loaded")
    print("Shape:", dataset.shape)
    print("Columns:", list(dataset.columns))

    return dataset