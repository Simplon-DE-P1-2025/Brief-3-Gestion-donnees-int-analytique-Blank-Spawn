import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    f"postgresql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}?sslmode=require"
)

with conn.cursor() as cur:

    print("\n=== INFO CONNEXION ===")
    cur.execute("SELECT current_database();")
    print("database:", cur.fetchone()[0])

    cur.execute("SELECT current_schema();")
    print("schema:", cur.fetchone()[0])

    print("\n=== TABLES TROUVÉES ===")
    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name IN ('flotteurs', 'resultats_humain', 'operation');
    """)
    for row in cur.fetchall():
        print(row)

    print("\n=== COUNT ===")
    cur.execute("SELECT COUNT(*) FROM operation;")
    print("operations:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM flotteurs;")
    print("flotteurs:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM resultats_humain;")
    print("resultats_humain:", cur.fetchone()[0])
