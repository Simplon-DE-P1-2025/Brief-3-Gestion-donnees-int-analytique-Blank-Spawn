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

    try:
        with conn.cursor() as cur:
            with open(csv_path, "r") as f:
                cur.copy(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)

        conn.commit()
        print(f" Import terminé pour {table_name}\n")

    except Exception as e:
        print(f"❌ ERREUR COPY pour la table {table_name} : {e}\n")
        conn.rollback()


# ============================================================
# 1. IMPORT TABLE OPERATION
# ============================================================

print("=== 1. Préparation du fichier operations ===")

ops = pd.read_csv("pipeline/data/operations_clean.csv")

# Vérification colonne cross
if "cross" not in ops.columns:
    raise RuntimeError(" La colonne 'cross' est absente de operations_clean.csv")

# Renommage pour correspondre au SQL
ops = ops.rename(columns={"cross": "cross_type"})

# Vérification colonne est_metropolitain (SQL l'attend)
if "est_metropolitain" not in ops.columns:
    ops["est_metropolitain"] = True  # valeur par défaut

# Sauvegarde du fichier prêt pour COPY
ops_ready_path = "pipeline/data/operations_ready.csv"
ops.to_csv(ops_ready_path, index=False)

copy_csv_to_table(ops_ready_path, "operation")


# ============================================================
# 2. IMPORT TABLE FLOTTEURS
# ============================================================

print("=== 2. Import de la table flotteurs ===")

flotteurs_ready_path = "csv_clean2/flotteurs_ready.csv"

if not os.path.exists(flotteurs_ready_path):
    raise RuntimeError(" Le fichier flotteurs_ready.csv est introuvable. Lance clean_hum_flot.py")

copy_csv_to_table(flotteurs_ready_path, "flotteurs")


# ============================================================
# 3. IMPORT TABLE RESULTATS_HUMAIN
# ============================================================

print("=== 3. Import de la table resultats_humain ===")

resultats_ready_path = "csv_clean2/resultats_humain_ready.csv"

if not os.path.exists(resultats_ready_path):
    raise RuntimeError(" Le fichier resultats_humain_ready.csv est introuvable. Lance clean_hum_flot.py")

copy_csv_to_table(resultats_ready_path, "resultats_humain")


# ============================================================
# FIN
# ============================================================

print(" Import COMPLET terminé avec succès !")
