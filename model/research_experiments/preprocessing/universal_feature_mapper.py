import numpy as np


def extract_universal_features(df):

    n = len(df)

    # Universal feature placeholders
    protocol = np.zeros(n)
    flow_duration = np.zeros(n)
    packet_mean = np.zeros(n)
    packet_std = np.zeros(n)
    packet_rate = np.zeros(n)

    # ----- CIC DATASET FEATURES -----
    if "Flow Duration" in df.columns:

        protocol = df["Protocol"].astype(float).to_numpy().copy()

        flow_duration = df["Flow Duration"].astype(float).to_numpy().copy()

        packet_mean = df["Packet Length Mean"].astype(float).to_numpy().copy()

        packet_std = df["Packet Length Std"].astype(float).to_numpy().copy()

        packet_rate = df["Flow Packets/s"].astype(float).to_numpy().copy()

    # ----- UNSW DATASET FEATURES -----
    elif "dur" in df.columns:

        protocol = df["proto"].astype("category").cat.codes.to_numpy().copy()

        flow_duration = df["dur"].astype(float).to_numpy().copy()

        packet_mean = df["smean"].astype(float).to_numpy().copy()

        packet_std = df["dmean"].astype(float).to_numpy().copy()

        packet_rate = df["rate"].astype(float).to_numpy().copy()

    # Clean values
    cleaned = []

    for arr in [protocol, flow_duration, packet_mean, packet_std, packet_rate]:

        arr = arr.astype(float)  # convert to float first
        arr[np.isinf(arr)] = np.nan
        arr = np.nan_to_num(arr)

        cleaned.append(arr)

    protocol, flow_duration, packet_mean, packet_std, packet_rate = cleaned
    X = np.column_stack([
        protocol,
        flow_duration,
        packet_mean,
        packet_std,
        packet_rate
    ])

    return X