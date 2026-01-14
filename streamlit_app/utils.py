import psycopg
import streamlit as st

@st.cache_resource
def get_connection():
    """
    Retourne une connexion PostgreSQL (Supabase ou autre).
    La connexion est mise en cache par Streamlit pour éviter
    de se reconnecter à chaque interaction.
    """
    try:
        conn = psycopg.connect(
            f"postgresql://{st.secrets['user']}:{st.secrets['password']}@"
            f"{st.secrets['host']}:{st.secrets['port']}/{st.secrets['dbname']}?sslmode=require"
        )
        return conn
    except Exception as e:
        st.error(" Erreur de connexion à la base de données")
        st.exception(e)
        return None


def run_query(query: str, params=None):
    """
    Exécute une requête SQL SELECT et retourne les résultats.
    """
    conn = get_connection()
    if conn is None:
        return []

    with conn.cursor() as cur:
        cur.execute(query, params or ())
        rows = cur.fetchall()
    return rows


def run_execute(query: str, params=None):
    """
    Exécute une requête SQL INSERT/UPDATE/DELETE.
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        st.error("Erreur lors de l'exécution de la requête")
        st.exception(e)
        return False
