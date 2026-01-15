import streamlit as st
import pandas as pd
import json
from utils.db import fetch_data
from utils.auth_ui import render_auth_widget

# --------------------
# Configuration
# --------------------
st.set_page_config(page_title="Journal d'Audit", layout="wide")

# On affiche le widget d'auth pour permettre la connexion depuis cette page
user = render_auth_widget()

st.title("📜 Journal des Modifications")
st.markdown("""
Cette page recense toutes les actions effectuées sur la base de données (Ajouts, Modifications, Suppressions).
""")

# --------------------
# Chargement des Logs
# --------------------
try:
    # On récupère les logs triés par date décroissante (le plus récent en premier)
    # Note : Assure-toi que la table s'appelle bien 'user_logs' dans ta BDD
    logs_data = fetch_data("user_logs", order_by="created_at")
    
    if not logs_data:
        st.info("Aucun log n'a encore été enregistré.")
    else:
        df_logs = pd.DataFrame(logs_data)

        # 1. Nettoyage et Formatage
        # Conversion de la colonne created_at en datetime local
        df_logs["created_at"] = pd.to_datetime(df_logs["created_at"]).dt.strftime('%d/%m/%Y %H:%M:%S')

        # 2. Filtres en haut de page
        st.write("### 🔍 Filtres")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            users_list = ["Tous"] + sorted(df_logs["user_email"].unique().tolist())
            selected_user = st.selectbox("Filtrer par Utilisateur", users_list)
            
        with col2:
            actions_list = ["Toutes"] + sorted(df_logs["action_type"].unique().tolist())
            selected_action = st.selectbox("Filtrer par Action", actions_list)
            
        with col3:
            tables_list = ["Toutes"] + sorted(df_logs["table_name"].unique().tolist())
            selected_table = st.selectbox("Filtrer par Table", tables_list)

        # Application des filtres
        filtered_df = df_logs.copy()
        if selected_user != "Tous":
            filtered_df = filtered_df[filtered_df["user_email"] == selected_user]
        if selected_action != "Toutes":
            filtered_df = filtered_df[filtered_df["action_type"] == selected_action]
        if selected_table != "Toutes":
            filtered_df = filtered_df[filtered_df["table_name"] == selected_table]

        # 3. Affichage du tableau
        # On renomme les colonnes pour l'affichage final
        display_df = filtered_df.rename(columns={
            "created_at": "Date & Heure",
            "user_email": "Utilisateur",
            "action_type": "Action",
            "table_name": "Table concernée",
            "record_id": "ID de la ligne",
            "details": "Données (JSON)"
        })

        # Configuration de l'affichage
        st.dataframe(
            display_df[["Date & Heure", "Utilisateur", "Action", "Table concernée", "ID de la ligne", "Données (JSON)"]],
            use_container_width=True,
            column_config={
                "Données (JSON)": st.column_config.JsonColumn("Détails des données"),
                "Action": st.column_config.TextColumn("Action", width="small"),
            },
            hide_index=True
        )

        st.caption(f"Affichage de {len(filtered_df)} entrée(s) de journal.")

except Exception as e:
    st.error(f"Erreur lors du chargement des logs : {e}")

# Bouton de rafraîchissement manuel
if st.button("🔄 Actualiser le journal"):
    st.rerun()