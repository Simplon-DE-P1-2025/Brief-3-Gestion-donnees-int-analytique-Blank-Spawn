import streamlit as st
from utils.db import get_supabase_client

st.title("🛟 Gestion des Flotteurs")

supabase = get_supabase_client()

# ---------------------------------------------------------
# 1) Charger les données
# ---------------------------------------------------------
def load_flotteurs():
    response = (
        supabase
        .table("flotteurs")
        .select("*")
        .order("flotteur_id", desc=False)
        .execute()
    )
    return response.data

flotteurs = load_flotteurs()

# ---------------------------------------------------------
# 2) Affichage du tableau
# ---------------------------------------------------------
st.subheader("📋 Liste des flotteurs")
st.dataframe(flotteurs, use_container_width=True)

# ---------------------------------------------------------
# 3) Ajouter un flotteur
# ---------------------------------------------------------
with st.expander("➕ Ajouter un nouveau flotteur"):
    flotteur_id = st.text_input("ID du flotteur (clé primaire)")
    type_flotteur = st.text_input("Type de flotteur")
    statut = st.text_input("Statut")
    localisation = st.text_input("Localisation")

    if st.button("Enregistrer le flotteur", key="save_new_flotteur"):
        data = {
            "flotteur_id": flotteur_id,
            "type_flotteur": type_flotteur,
            "statut": statut,
            "localisation": localisation,
        }
        supabase.table("flotteurs").insert(data).execute()
        st.success("Flotteur ajouté avec succès")
        st.rerun()

# ---------------------------------------------------------
# 4) Modifier un flotteur
# ---------------------------------------------------------
st.subheader("✏️ Modifier un flotteur")

flotteur_ids = [f["flotteur_id"] for f in flotteurs]
selected_id = st.selectbox("Sélectionnez un flotteur", flotteur_ids)

if selected_id:
    f = next(x for x in flotteurs if x["flotteur_id"] == selected_id)

    with st.expander(f"Modifier le flotteur {selected_id}"):

        type_flotteur = st.text_input("Type", value=f.get("type_flotteur", ""))
        statut = st.text_input("Statut", value=f.get("statut", ""))
        localisation = st.text_input("Localisation", value=f.get("localisation", ""))

        if st.button("Enregistrer les modifications", key="save_edit_flotteur"):
            data = {
                "type_flotteur": type_flotteur,
                "statut": statut,
                "localisation": localisation,
            }
            supabase.table("flotteurs").update(data).eq("flotteur_id", selected_id).execute()
            st.success("Flotteur mis à jour")
            st.rerun()

# ---------------------------------------------------------
# 5) Supprimer un flotteur
# ---------------------------------------------------------
st.subheader("🗑️ Supprimer un flotteur")

delete_id = st.selectbox("Sélectionnez un flotteur à supprimer", flotteur_ids, key="delete_flotteur")

if st.button("Supprimer définitivement", key="delete_button_flotteur"):
    supabase.table("flotteurs").delete().eq("flotteur_id", delete_id).execute()
    st.warning(f"Flotteur {delete_id} supprimé")
    st.rerun()
