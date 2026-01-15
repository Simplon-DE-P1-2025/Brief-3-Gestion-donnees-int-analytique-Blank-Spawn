import streamlit as st
from utils.db import get_supabase_client

st.title("🧍 Gestion des Résultats Humains")

supabase = get_supabase_client()

# ---------------------------------------------------------
# 1) Charger les données
# ---------------------------------------------------------
def load_resultats():
    response = (
        supabase
        .table("resultats_humain")
        .select("*")
        .execute()
    )
    return response.data

resultats = load_resultats()

# ---------------------------------------------------------
# 2) Affichage du tableau
# ---------------------------------------------------------
st.subheader("📋 Liste des résultats humains")
st.dataframe(resultats, use_container_width=True)

# ---------------------------------------------------------
# 3) Ajouter un résultat
# ---------------------------------------------------------
with st.expander("➕ Ajouter un résultat humain"):
    nombre = st.number_input("Nombre total de personnes", min_value=0)
    dont_blesses = st.number_input("Dont blessés", min_value=0)
    operation_id = st.text_input("ID de l'opération liée")
    categorie = st.text_input("Catégorie de personne")
    resultat = st.text_input("Résultat humain")

    if st.button("Enregistrer le résultat", key="save_new_resultat"):
        data = {
            "nombre": nombre,
            "dont_nombre_blesse": dont_blesses,
            "operation_id": operation_id,
            "categorie_personne": categorie,
            "resultat_humain": resultat,
        }
        supabase.table("resultats_humain").insert(data).execute()
        st.success("Résultat ajouté avec succès")
        st.rerun()

# ---------------------------------------------------------
# 4) Modifier un résultat
# ---------------------------------------------------------
st.subheader("✏️ Modifier un résultat")

if len(resultats) > 0:
    index = st.selectbox(
        "Sélectionnez un résultat à modifier",
        list(range(len(resultats))),
        format_func=lambda i: f"{resultats[i]['operation_id']} – {resultats[i]['categorie_personne']}"
    )

    r = resultats[index]

    with st.expander("Modifier ce résultat"):

        nombre = st.number_input("Nombre total", value=r.get("nombre", 0))
        dont_blesses = st.number_input("Dont blessés", value=r.get("dont_nombre_blesse", 0))
        operation_id = st.text_input("ID opération", value=r.get("operation_id", ""))
        categorie = st.text_input("Catégorie", value=r.get("categorie_personne", ""))
        resultat = st.text_input("Résultat humain", value=r.get("resultat_humain", ""))

        if st.button("Enregistrer les modifications", key="save_edit_resultat"):
            data = {
                "nombre": nombre,
                "dont_nombre_blesse": dont_blesses,
                "operation_id": operation_id,
                "categorie_personne": categorie,
                "resultat_humain": resultat,
            }
            # Pas de clé primaire → on utilise un filtre complet
            supabase.table("resultats_humain").update(data).match(r).execute()
            st.success("Résultat mis à jour")
            st.rerun()

# ---------------------------------------------------------
# 5) Supprimer un résultat
# ---------------------------------------------------------
st.subheader("🗑️ Supprimer un résultat")

if len(resultats) > 0:
    delete_index = st.selectbox(
        "Sélectionnez un résultat à supprimer",
        list(range(len(resultats))),
        key="delete_resultat",
        format_func=lambda i: f"{resultats[i]['operation_id']} – {resultats[i]['categorie_personne']}"
    )

    if st.button("Supprimer définitivement", key="delete_button_resultat"):
        supabase.table("resultats_humain").delete().match(resultats[delete_index]).execute()
        st.warning("Résultat supprimé")
        st.rerun()
