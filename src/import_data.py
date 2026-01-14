import os
import psycopg
import pandas as pd
from dotenv import load_dotenv

# ============================================================
# Chargement des variables d'environnement
# ============================================================

load_dotenv()

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError(" Variables .env manquantes. Vérifie ton fichier .env")

# ============================================================
# Connexion PostgreSQL Supabase
# ============================================================

print(" Connexion à la base Supabase...")

conn = psycopg.connect(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

print(" Connexion établie\n")


# ============================================================
# Fonction utilitaire : COPY FROM STDIN
# ============================================================

def copy_csv_to_table(csv_path: str, table_name: str):
    print(f" Import de {csv_path} → table {table_name}...")

    with conn.cursor() as cur:  # on ne ferme plus la connexion ici
        with open(csv_path, "r") as f:
            cur.copy(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)

    conn.commit()  # commit manuel après chaque import

    print(f" Import terminé pour {table_name}\n")


# ============================================================
# 1. IMPORT TABLE OPERATION
# ============================================================

print("=== 1. Préparation du fichier operations ===")

ops = pd.read_csv("data/operations_clean.csv")

# Vérification colonne cross
if "cross" not in ops.columns:
    raise RuntimeError(" La colonne 'cross' est absente de operations_clean.csv")

# Renommage pour correspondre au SQL
ops = ops.rename(columns={"cross": "cross_type"})

# Vérification colonne est_metropolitain (SQL l'attend)
if "est_metropolitain" not in ops.columns:
    ops["est_metropolitain"] = True  # valeur par défaut

# Sauvegarde du fichier prêt pour COPY
ops_ready_path = "data/operations_ready.csv"
ops.to_csv(ops_ready_path, index=False)

copy_csv_to_table(ops_ready_path, "operation")


# ============================================================
# 2. IMPORT TABLE FLOTTEURS
# ============================================================

print("=== 2. Import de la table flotteurs ===")

flotteurs_path = "data/flotteurs_clean.csv"

flotteurs = pd.read_csv(flotteurs_path)
required_cols_flotteurs = [
    "operation_id", "numero_ordre", "pavillon",
    "resultat_flotteur", "type_flotteur",
    "categorie_flotteur", "numero_immatriculation"
]

missing = [c for c in required_cols_flotteurs if c not in flotteurs.columns]
if missing:
    raise RuntimeError(f" Colonnes manquantes dans flotteurs_clean.csv : {missing}")

copy_csv_to_table(flotteurs_path, "flotteurs")


# ============================================================
# 3. IMPORT TABLE RESULTATS_HUMAIN
# ============================================================

print("=== 3. Import de la table resultats_humain ===")

resultats_path = "data/resultats_humain_clean.csv"

resultats = pd.read_csv(resultats_path)
required_cols_resultats = [
    "operation_id", "categorie_personne",
    "resultat_humain", "nombre", "dont_nombre_blesse"
]

missing = [c for c in required_cols_resultats if c not in resultats.columns]
if missing:
    raise RuntimeError(f" Colonnes manquantes dans resultats_humain_clean.csv : {missing}")

copy_csv_to_table(resultats_path, "resultats_humain")


# ============================================================
# FIN
# ============================================================

print(" Import COMPLET terminé avec succès !")
