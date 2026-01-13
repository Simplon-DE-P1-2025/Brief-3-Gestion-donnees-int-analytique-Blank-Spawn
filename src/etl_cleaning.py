import pandas as pd

def load_raw_data():
    operations = pd.read_csv("data/operations_raw.csv")
    flotteurs = pd.read_csv("data/flotteurs_raw.csv")
    resultats = pd.read_csv("data/resultats_humain_raw.csv")
    return operations, flotteurs, resultats

def clean_operations(df):
    # nettoyage complet ici
    return df

def clean_flotteurs(df):
    # nettoyage complet ici
    return df

def clean_resultats(df):
    # nettoyage complet ici
    return df

def save_clean_data(ops, flot, res):
    ops.to_csv("data/operations_clean.csv", index=False)
    flot.to_csv("data/flotteurs_clean.csv", index=False)
    res.to_csv("data/resultats_humain_clean.csv", index=False)

if __name__ == "__main__":
    ops, flot, res = load_raw_data()
    ops = clean_operations(ops)
    flot = clean_flotteurs(flot)
    res = clean_resultats(res)
    save_clean_data(ops, flot, res)
