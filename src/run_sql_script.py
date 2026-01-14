import os
import psycopg
from dotenv import load_dotenv

# Charger .env
load_dotenv()

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

conn = psycopg.connect(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

print("Connexion établie à Supabase")

# Lire le fichier SQL
with open("base_de_donnees/script_tables.sql", "r") as f:
    sql_script = f.read()

# Découper les commandes SQL
statements = [s.strip() for s in sql_script.split(";") if s.strip()]

with conn.cursor() as cur:
    for stmt in statements:
        print(f"➡️ Exécution : {stmt[:50]}...")
        cur.execute(stmt + ";")
    conn.commit()

print("🎉 Script SQL exécuté avec succès !")
