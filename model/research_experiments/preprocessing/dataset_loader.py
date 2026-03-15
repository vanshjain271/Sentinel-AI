import pandas as pd
import numpy as np
import os

def load_dataset(path):

    print("Loading dataset:", path)

    # detect file type
    if path.endswith(".csv"):
        df = pd.read_csv(path)

    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)

    else:
        raise ValueError("Unsupported dataset format")

    print("Original shape:", df.shape)

    # clean data
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    print("Cleaned shape:", df.shape)

    return df