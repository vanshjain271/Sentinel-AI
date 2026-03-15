def map_features(df, mapping):

    print("Mapping dataset features...")

    df = df.rename(columns=mapping)

    return df