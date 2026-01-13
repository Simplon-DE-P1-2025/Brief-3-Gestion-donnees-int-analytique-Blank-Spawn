import pandas as pd

def check_structure(raw_path, clean_path, table_name):
    print(f"\n🔍 Vérification de la structure pour : {table_name}")

    # Charger les deux versions
    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(clean_path)

    # Colonnes
    raw_cols = set(raw_df.columns)
    clean_cols = set(clean_df.columns)

    # Vérifier colonnes manquantes
    missing_in_clean = raw_cols - clean_cols
    missing_in_raw = clean_cols - raw_cols

    if not missing_in_clean and not missing_in_raw:
        print("✅ Structure OK : mêmes colonnes avant et après nettoyage")
    else:
        print("❌ Structure différente !")

        if missing_in_clean:
            print("  ➤ Colonnes présentes dans RAW mais absentes dans CLEAN :")
            for col in missing_in_clean:
                print("     -", col)

        if missing_in_raw:
            print("  ➤ Colonnes présentes dans CLEAN mais absentes dans RAW :")
            for col in missing_in_raw:
                print("     -", col)

    # Vérifier l’ordre des colonnes
    if list(raw_df.columns) != list(clean_df.columns):
        print("⚠️ L’ordre des colonnes est différent")
    else:
        print("✔ Ordre des colonnes identique")


if __name__ == "__main__":
    check_structure("data/operations.csv", "data/operations_clean.csv", "operations")
    check_structure("data/flotteurs.csv", "data/flotteurs_clean.csv", "flotteurs")
    check_structure("data/resultats_humain.csv", "data/resultats_humain_clean.csv", "resultats_humain")
