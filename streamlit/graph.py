import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import altair as alt

# -------------------------
# ENV
# -------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# UI
# -------------------------
st.title("📈 Visualisations des opérations")

# -------------------------
# Bouton Refresh
# -------------------------
if st.button("🔄 Rafraîchir les données"):
    supabase.rpc("refresh_graph_operations").execute()
    st.success("✅ Les données ont été rafraîchies côté Supabase !")
    st.rerun()
# -------------------------
# Répartition par type
# -------------------------
st.subheader("Répartition des opérations par type")
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

# -------------------------
# Activité par département
# -------------------------
st.subheader("Opérations par département")
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

# -------------------------
# Résultat flotteurs
# -------------------------
st.subheader("Résultat des flotteurs")
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