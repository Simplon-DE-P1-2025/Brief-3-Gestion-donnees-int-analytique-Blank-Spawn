import streamlit as st

from utils.auth_ui import render_auth_widget

# Cela affiche le bouton "Déconnexion" si déjà connecté, 
# ou le formulaire si ce n'est pas le cas.
user = render_auth_widget()

st.title("🏠 Accueil")

st.write("""
Bienvenue dans l'application de gestion des opérations de surveillance et de sauvetage.

Utilisez le menu à gauche pour naviguer entre les différentes sections :
- Dashboard analytique
- Gestion des opérations
- Gestion des flotteurs
- Gestion des résultats humains
- Schéma de la base de données
- Audit des modifications
""")

st.info("Sélectionnez une page dans la barre latérale pour commencer.")
