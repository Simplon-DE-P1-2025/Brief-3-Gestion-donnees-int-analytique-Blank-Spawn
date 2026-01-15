import streamlit as st
from utils.db import get_supabase_client

def sign_in(email, password):
    """Connecte l'utilisateur et stocke la session."""
    supabase = get_supabase_client()
    try:
        # Supabase Auth renvoie un objet contenant 'user' et 'session'
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if auth_response.user:
            st.session_state.user = auth_response.user
            return True, "Succès"
    except Exception as e:
        # On nettoie le message d'erreur pour l'utilisateur final
        error_msg = str(e).split(':')[-1].strip()
        return False, error_msg

def sign_up(email, password, full_name):
    """Crée un compte et insère le profil dans la table publique."""
    supabase = get_supabase_client()
    try:
        # 1. Création du compte dans auth.users
        auth_response = supabase.auth.sign_up({"email": email, "password": password})
        
        if auth_response.user:
            # 2. Insertion du profil (table créée précédemment en SQL)
            # On utilise .insert() directement ici pour lier l'ID
            profile_data = {
                "id": auth_response.user.id,
                "email": email,
                "full_name": full_name
            }
            supabase.table("profiles").insert(profile_data).execute()
            return True, "Compte créé ! Un email de confirmation a été envoyé."
    except Exception as e:
        return False, str(e)

def sign_out():
    """Déconnecte et réinitialise l'interface."""
    supabase = get_supabase_client()
    supabase.auth.sign_out()
    if "user" in st.session_state:
        del st.session_state.user
    st.rerun()

def render_auth_widget():
    """
    Fonction UI Tout-en-un :
    Affiche le statut ou le formulaire dans la sidebar.
    """
    if "user" not in st.session_state:
        st.session_state.user = None

    user = st.session_state.user

    if user:
        with st.sidebar:
            st.divider()
            st.markdown(f"**👤 Utilisateur connecté**")
            st.caption(f"{user.email}")
            if st.button("Se déconnecter", use_container_width=True, type="secondary"):
                sign_out()
            st.divider()
    else:
        with st.sidebar.expander("🔐 Connexion / Inscription", expanded=True):
            mode = st.radio("Mode", ["Connexion", "Inscription"], horizontal=True)
            
            # Utilisation d'un formulaire pour éviter les rechargements inutiles
            with st.form("auth_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                
                name = ""
                if mode == "Inscription":
                    name = st.text_input("Nom Complet")
                
                submit_label = "Se connecter" if mode == "Connexion" else "Créer mon compte"
                submitted = st.form_submit_button(submit_label, use_container_width=True, type="primary")
                
                if submitted:
                    if not email or not password:
                        st.error("Veuillez remplir tous les champs.")
                    elif mode == "Connexion":
                        success, msg = sign_in(email, password)
                        if success:
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        if not name:
                            st.error("Le nom est obligatoire pour l'inscription.")
                        else:
                            success, msg = sign_up(email, password, name)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
    
    return st.session_state.user