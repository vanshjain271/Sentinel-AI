import pandas as pd
from pathlib import Path

# Dataset location
DATASET_PATH = Path("model/research_experiments/datasets/cic_ddos2019")

FILES = [
    "DrDoS_DNS.csv",
    "DrDoS_LDAP.csv",
    "DrDoS_NTP.csv",
    "Syn.csv"
]


def load_cic_dataset(sample_rows=None):
    """
    Load CIC-DDoS2019 dataset files and combine them.

    Parameters
    ----------
    sample_rows : int or None
        If provided, only this many rows will be loaded from each file
        (useful for testing on low memory machines).

    Returns
    -------
    pandas.DataFrame
    """

    dfs = []

    for file in FILES:

        path = DATASET_PATH / file
        print(f"Loading {path}")

        df = pd.read_csv(
            path,
            low_memory=False,
            nrows=sample_rows
        )

        # Clean column names (remove leading/trailing spaces)
        df.columns = df.columns.str.strip()

        dfs.append(df)

    dataset = pd.concat(dfs, ignore_index=True)

    print("\nDataset loaded successfully")
    print("Shape:", dataset.shape)
    print("Columns:", list(dataset.columns))

    return dataset