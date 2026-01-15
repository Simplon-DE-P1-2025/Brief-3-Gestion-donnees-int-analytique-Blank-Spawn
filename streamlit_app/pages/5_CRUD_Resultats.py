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
        .order("resultat_id", desc=False)
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
    resultat_id = st.text_input("ID du résultat (clé primaire)")
    operation_id = st.text_input("ID de l'opération liée")
    nb_sauves = st.number_input("Nombre de personnes sauvées", min_value=0)
    nb_decedes = st.number_input("Nombre de personnes décédées", min_value=0)
    commentaire = st.text_area("Commentaire")

    if st.button("Enregistrer le résultat", key="save_new_resultat"):
        data = {
            "resultat_id": resultat_id,
            "operation_id": operation_id,
            "nb_sauves": nb_sauves,
            "nb_decedes": nb_decedes,
            "commentaire": commentaire,
        }
        supabase.table("resultats_humain").insert(data).execute()
        st.success("Résultat ajouté avec succès")
        st.rerun()

# ---------------------------------------------------------
# 4) Modifier un résultat
# ---------------------------------------------------------
st.subheader("✏️ Modifier un résultat")

resultat_ids = [r["resultat_id"] for r in resultats]
selected_id = st.selectbox("Sélectionnez un résultat", resultat_ids)

if selected_id:
    r = next(x for x in resultats if x["resultat_id"] == selected_id)

    with st.expander(f"Modifier le résultat {selected_id}"):

        operation_id = st.text_input("ID opération", value=r.get("operation_id", ""))
        nb_sauves = st.number_input("Sauvés", value=r.get("nb_sauves", 0))
        nb_decedes = st.number_input("Décédés", value=r.get("nb_decedes", 0))
        commentaire = st.text_area("Commentaire", value=r.get("commentaire", ""))

        if st.button("Enregistrer les modifications", key="save_edit_resultat"):
            data = {
                "operation_id": operation_id,
                "nb_sauves": nb_sauves,
                "nb_decedes": nb_decedes,
                "commentaire": commentaire,
            }
            supabase.table("resultats_humain").update(data).eq("resultat_id", selected_id).execute()
            st.success("Résultat mis à jour")
            st.rerun()

# ---------------------------------------------------------
# 5) Supprimer un résultat
# ---------------------------------------------------------
st.subheader("🗑️ Supprimer un résultat")

delete_id = st.selectbox("Sélectionnez un résultat à supprimer", resultat_ids, key="delete_resultat")

if st.button("Supprimer définitivement", key="delete_button_resultat"):
    supabase.table("resultats_humain").delete().eq("resultat_id", delete_id).execute()
    st.warning(f"Résultat {delete_id} supprimé")
    st.rerun()
