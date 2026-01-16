import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import altair as alt

from utils.auth_ui import render_auth_widget

# -------------------------
# Authentification
# -------------------------
user = render_auth_widget()

# -------------------------
# ENV
# -------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # lecture seule
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # admin / refresh

# Client lecture seule pour récupérer les données
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Client admin pour les opérations RPC
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# -------------------------
# UI
# -------------------------
st.title("📈 Visualisations des opérations")

# -------------------------
# Bouton Refresh
# -------------------------
if st.button("🔄 Rafraîchir les données"):
    try:
        supabase_admin.rpc("refresh_graph_operations").execute()
        st.success("✅ Les données ont été rafraîchies côté Supabase !")

        # Recharger immédiatement les données pour les graphiques
        data_type = supabase.rpc("graph_operations_par_type").execute().data
        df_type = pd.DataFrame(data_type)

        data_dep = supabase.rpc("graph_operations_par_departement").execute().data
        df_dep = pd.DataFrame(data_dep)

        data_flot = supabase.rpc("graph_resultat_flotteurs").execute().data
        df_flot = pd.DataFrame(data_flot)

    except Exception as e:
        st.error(f"❌ Erreur lors du refresh : {e}")


# -------------------------
# Répartition par type
# -------------------------
st.subheader("Répartition des opérations par type")
try:
    data_type = supabase.rpc("graph_operations_par_type").execute().data
    df_type = pd.DataFrame(data_type)

    if not df_type.empty:
        chart_type = alt.Chart(df_type).mark_bar().encode(
            x=alt.X("type_operation:N", title="Type d'opération"),
            y=alt.Y("nb:Q", title="Nombre"),
            tooltip=["type_operation", "nb"]
        )
        st.altair_chart(chart_type, use_container_width=True)
    else:
        st.info("Pas de données disponibles pour les types d'opérations.")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des types : {e}")

# -------------------------
# Activité par département
# -------------------------
st.subheader("Opérations par département")
try:
    data_dep = supabase.rpc("graph_operations_par_departement").execute().data
    df_dep = pd.DataFrame(data_dep)

    if not df_dep.empty:
        chart_dep = alt.Chart(df_dep).mark_bar().encode(
            x=alt.X("departement:N", sort="-y"),
            y="nb_operations:Q",
            tooltip=["departement", "nb_operations"]
        )
        st.altair_chart(chart_dep, use_container_width=True)
    else:
        st.info("Pas de données disponibles pour les départements.")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des départements : {e}")

# -------------------------
# Résultat flotteurs
# -------------------------
st.subheader("Résultat des flotteurs")
try:
    data_flot = supabase.rpc("graph_resultat_flotteurs").execute().data
    df_flot = pd.DataFrame(data_flot)

    if not df_flot.empty:
        chart_flot = alt.Chart(df_flot).mark_bar().encode(
            x="resultat_flotteur:N",
            y="nb:Q",
            tooltip=["resultat_flotteur", "nb"]
        )
        st.altair_chart(chart_flot, use_container_width=True)
    else:
        st.info("Pas de données disponibles pour les flotteurs.")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des flotteurs : {e}")
