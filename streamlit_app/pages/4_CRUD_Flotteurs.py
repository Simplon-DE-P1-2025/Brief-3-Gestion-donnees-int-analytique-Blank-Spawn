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
    numero_ordre = st.number_input("Numéro d'ordre", min_value=0)
    pavillon = st.text_input("Pavillon")
    operation_id = st.text_input("ID de l'opération liée")
    type_flotteur = st.text_input("Type de flotteur")
    categorie_flotteur = st.text_input("Catégorie de flotteur")
    numero_immatriculation = st.text_input("Numéro d'immatriculation")
    resultat_flotteur = st.text_input("Résultat du flotteur")

    if st.button("Enregistrer le flotteur", key="save_new_flotteur"):
        data = {
            "numero_ordre": numero_ordre,
            "pavillon": pavillon,
            "operation_id": operation_id,
            "type_flotteur": type_flotteur,
            "categorie_flotteur": categorie_flotteur,
            "numero_immatriculation": numero_immatriculation,
            "resultat_flotteur": resultat_flotteur,
        }
        supabase.table("flotteurs").insert(data).execute()
        st.success("Flotteur ajouté avec succès")
        st.rerun()

# ---------------------------------------------------------
# 4) Modifier un flotteur
# ---------------------------------------------------------
st.subheader("✏️ Modifier un flotteur")

if len(flotteurs) > 0:
    index = st.selectbox(
        "Sélectionnez un flotteur à modifier",
        list(range(len(flotteurs))),
        format_func=lambda i: f"{flotteurs[i]['numero_ordre']} – {flotteurs[i]['type_flotteur']}"
    )

    f = flotteurs[index]

    with st.expander(f"Modifier le flotteur {f['numero_ordre']}"):

        numero_ordre = st.number_input("Numéro d'ordre", value=f.get("numero_ordre", 0))
        pavillon = st.text_input("Pavillon", value=f.get("pavillon", ""))
        operation_id = st.text_input("ID opération", value=f.get("operation_id", ""))
        type_flotteur = st.text_input("Type", value=f.get("type_flotteur", ""))
        categorie_flotteur = st.text_input("Catégorie", value=f.get("categorie_flotteur", ""))
        numero_immatriculation = st.text_input("Numéro d'immatriculation", value=f.get("numero_immatriculation", ""))
        resultat_flotteur = st.text_input("Résultat flotteur", value=f.get("resultat_flotteur", ""))

        if st.button("Enregistrer les modifications", key="save_edit_flotteur"):
            data = {
                "numero_ordre": numero_ordre,
                "pavillon": pavillon,
                "operation_id": operation_id,
                "type_flotteur": type_flotteur,
                "categorie_flotteur": categorie_flotteur,
                "numero_immatriculation": numero_immatriculation,
                "resultat_flotteur": resultat_flotteur,
            }
            supabase.table("flotteurs").update(data).match(f).execute()
            st.success("Flotteur mis à jour")
            st.rerun()

# ---------------------------------------------------------
# 5) Supprimer un flotteur
# ---------------------------------------------------------
st.subheader("🗑️ Supprimer un flotteur")

if len(flotteurs) > 0:
    delete_index = st.selectbox(
        "Sélectionnez un flotteur à supprimer",
        list(range(len(flotteurs))),
        key="delete_flotteur",
        format_func=lambda i: f"{flotteurs[i]['numero_ordre']} – {flotteurs[i]['type_flotteur']}"
    )

    if st.button("Supprimer définitivement", key="delete_button_flotteur"):
        supabase.table("flotteurs").delete().match(flotteurs[delete_index]).execute()
        st.warning("Flotteur supprimé")
        st.rerun()
