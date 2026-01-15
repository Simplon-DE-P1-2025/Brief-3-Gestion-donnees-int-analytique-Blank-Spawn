from utils.auth_ui import render_auth_widget

# Cela affiche le bouton "Déconnexion" si déjà connecté, 
# ou le formulaire si ce n'est pas le cas.
user = render_auth_widget()

import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import matplotlib.pyplot as plt

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
st.title("📊 Dashboard – Opérations de secours")

# -------------------------
# Chargement des données
# -------------------------
def load_table(name):
    return pd.DataFrame(supabase.table(name).select("*").execute().data)

df_op = load_table("operation")
df_fl = load_table("flotteurs")
df_res = load_table("resultats_humain")

# -------------------------
# Filtres
# -------------------------
st.sidebar.header("🔎 Filtres")

# Années
if "date_heure_reception_alerte" in df_op.columns:
    df_op["year"] = df_op["date_heure_reception_alerte"].astype(str).str[:4]
    years = sorted(df_op["year"].dropna().unique())
else:
    years = []

year_filter = st.sidebar.selectbox("Année", ["Toutes"] + years)

# Département
dept_filter = st.sidebar.selectbox(
    "Département",
    ["Tous"] + sorted(df_op["departement"].dropna().unique())
)

# Type d'opération
type_filter = st.sidebar.selectbox(
    "Type d'opération",
    ["Tous"] + sorted(df_op["type_operation"].dropna().unique())
)

# Application des filtres
df_filtered = df_op.copy()

if year_filter != "Toutes":
    df_filtered = df_filtered[df_filtered["year"] == year_filter]

if dept_filter != "Tous":
    df_filtered = df_filtered[df_filtered["departement"] == dept_filter]

if type_filter != "Tous":
    df_filtered = df_filtered[df_filtered["type_operation"] == type_filter]

# -------------------------
# Section KPI
# -------------------------
st.header("📌 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

# KPI 1 : Nombre d'opérations
col1.metric("Nombre d'opérations", len(df_filtered))

# KPI 2 : Durée moyenne
if "date_heure_fin_operation" in df_filtered.columns:
    try:
        df_filtered["start"] = pd.to_datetime(df_filtered["date_heure_reception_alerte"])
        df_filtered["end"] = pd.to_datetime(df_filtered["date_heure_fin_operation"])
        df_filtered["duration"] = (df_filtered["end"] - df_filtered["start"]).dt.total_seconds() / 3600
        col2.metric("Durée moyenne (h)", round(df_filtered["duration"].mean(), 2))
    except:
        col2.metric("Durée moyenne (h)", "N/A")
else:
    col2.metric("Durée moyenne (h)", "N/A")

# KPI 3 : Blessés (%)
if not df_res.empty and df_res["nombre"].sum() > 0:
    taux = round((df_res["dont_nombre_blesse"].sum() / df_res["nombre"].sum()) * 100, 2)
    col3.metric("Blessés (%)", taux)
else:
    col3.metric("Blessés (%)", "N/A")

# KPI 4 : Météo difficile
if "vent_force" in df_filtered.columns and "mer_force" in df_filtered.columns:
    meteo_diff = df_filtered[(df_filtered["vent_force"] >= 7) | (df_filtered["mer_force"] >= 5)]
    col4.metric("Météo difficile", len(meteo_diff))
else:
    col4.metric("Météo difficile", "N/A")

# -------------------------
# Graphique : répartition des types d'opérations
# -------------------------
st.header("📊 Répartition des types d'opérations")

if df_filtered["type_operation"].dropna().empty:
    st.info("Aucune donnée disponible pour ce graphique.")
else:
    fig, ax = plt.subplots()
    df_filtered["type_operation"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Types d'opérations")
    ax.set_xlabel("Type")
    ax.set_ylabel("Nombre")
    st.pyplot(fig)

# -------------------------
# Graphique : opérations par département
# -------------------------
st.header("📍 Opérations par département")

if df_filtered["departement"].dropna().empty:
    st.info("Aucune donnée disponible pour ce graphique.")
else:
    fig, ax = plt.subplots()
    df_filtered["departement"].value_counts().plot(kind="bar", ax=ax, color="orange")
    ax.set_title("Opérations par département")
    st.pyplot(fig)

# -------------------------
# Carte des opérations
# -------------------------
st.header("🗺️ Carte des opérations")

if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
    df_map = df_filtered[["latitude", "longitude"]].dropna()
    if not df_map.empty:
        st.map(df_map)
    else:
        st.info("Pas de coordonnées disponibles.")
else:
    st.info("Colonnes latitude/longitude manquantes.")

# -------------------------
# Analyse flotteurs
# -------------------------
st.header("🛟 Analyse des flotteurs")

if df_fl["type_flotteur"].dropna().empty:
    st.info("Aucun flotteur enregistré.")
else:
    fig, ax = plt.subplots()
    df_fl["type_flotteur"].value_counts().plot(kind="bar", ax=ax, color="green")
    ax.set_title("Types de flotteurs utilisés")
    st.pyplot(fig)

# -------------------------
# Analyse résultats humains
# -------------------------
st.header("🧍 Résultats humains")

if df_res.empty:
    st.info("Aucun résultat humain enregistré.")
else:
    colA, colB = st.columns(2)
    colA.metric("Total sauvés", df_res["nombre"].sum())
    colB.metric("Total blessés", df_res["dont_nombre_blesse"].sum())

    if df_res["categorie_personne"].dropna().empty:
        st.info("Aucune catégorie disponible.")
    else:
        fig, ax = plt.subplots()
        df_res["categorie_personne"].value_counts().plot(kind="bar", ax=ax, color="red")
        ax.set_title("Catégories de personnes")
        st.pyplot(fig)