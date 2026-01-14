import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    f"postgresql://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}?sslmode=require"
)

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM operation;")
    print("operations:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM flotteurs;")
    print("flotteurs:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM resultats_humain;")
    print("resultats_humain:", cur.fetchone()[0])
