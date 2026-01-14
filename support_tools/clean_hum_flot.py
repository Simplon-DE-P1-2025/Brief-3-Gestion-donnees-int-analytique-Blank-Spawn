import pandas as pd
import os

# Resolve project root and data directory relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "src", "data")

# ============================================================
# Préparation du dossier de sortie
# ============================================================

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "csv_clean2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📁 Dossier de sortie : {OUTPUT_DIR}\n")
print(f"📁 Dossier de données : {DATA_DIR}\n")


# ============================================================
# 1. Nettoyage flotteurs
# ============================================================

print("=== Nettoyage flotteurs ===")

df_flotteurs = pd.read_csv(os.path.join(DATA_DIR, "flotteurs_clean.csv"))

cols_flotteurs = [
    "operation_id", "numero_ordre", "pavillon",
    "resultat_flotteur", "type_flotteur",
    "categorie_flotteur", "numero_immatriculation"
]

# Garder uniquement les colonnes utiles
df_flotteurs = df_flotteurs[cols_flotteurs]

# Convertir les types numériques
df_flotteurs["operation_id"] = pd.to_numeric(df_flotteurs["operation_id"], errors="coerce").fillna(0).astype(int)
df_flotteurs["numero_ordre"] = pd.to_numeric(df_flotteurs["numero_ordre"], errors="coerce").fillna(0).astype(int)

# Colonnes texte : remplacer NaN par chaîne vide
text_cols = ["pavillon", "resultat_flotteur", "type_flotteur", "categorie_flotteur", "numero_immatriculation"]
for col in text_cols:
    df_flotteurs[col] = df_flotteurs[col].fillna("").astype(str)

# Sauvegarde
flotteurs_ready_path = f"{OUTPUT_DIR}/flotteurs_ready.csv"
df_flotteurs.to_csv(flotteurs_ready_path, index=False)

print(f"→ {flotteurs_ready_path} généré\n")


# ============================================================
# 2. Nettoyage resultats_humain
# ============================================================

print("=== Nettoyage resultats_humain ===")

df_res = pd.read_csv(os.path.join(DATA_DIR, "resultats_humain_clean.csv"))

cols_res = [
    "operation_id", "categorie_personne",
    "resultat_humain", "nombre", "dont_nombre_blesse"
]

df_res = df_res[cols_res]

# Convertir les types numériques
df_res["operation_id"] = pd.to_numeric(df_res["operation_id"], errors="coerce").fillna(0).astype(int)
df_res["nombre"] = pd.to_numeric(df_res["nombre"], errors="coerce").fillna(0).astype(int)
df_res["dont_nombre_blesse"] = pd.to_numeric(df_res["dont_nombre_blesse"], errors="coerce").fillna(0).astype(int)

# Colonnes texte
df_res["categorie_personne"] = df_res["categorie_personne"].fillna("").astype(str)
df_res["resultat_humain"] = df_res["resultat_humain"].fillna("").astype(str)

# Sauvegarde
resultats_ready_path = f"{OUTPUT_DIR}/resultats_humain_ready.csv"
df_res.to_csv(resultats_ready_path, index=False)

print(f"→ {resultats_ready_path} généré\n")

print("🎉 Nettoyage terminé !")
