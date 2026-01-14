import streamlit as st
from utils.db import get_supabase_client

st.title("🛠️ Gestion des Opérations")

supabase = get_supabase_client()

# ---------------------------------------------------------
# 1) Charger les données
# ---------------------------------------------------------
def load_operations():
    response = (
        supabase
        .table("operation")
        .select("*")
        .order("operation_id", desc=False)
        .execute()
    )
    return response.data

operations = load_operations()

# ---------------------------------------------------------
# 2) Affichage du tableau
# ---------------------------------------------------------
st.subheader("📋 Liste des opérations")
st.dataframe(operations, use_container_width=True)

# ---------------------------------------------------------
# 3) Ajouter une opération
# ---------------------------------------------------------
if st.button("➕ Ajouter une opération"):
    with st.modal("Ajouter une nouvelle opération"):
        st.write("Remplissez les informations ci-dessous.")

        operation_id = st.text_input("ID de l'opération (clé primaire)")
        type_operation = st.text_input("Type d'opération")
        departement = st.text_input("Département")
        evenement = st.text_input("Événement")
        latitude = st.number_input("Latitude", value=0.0)
        longitude = st.number_input("Longitude", value=0.0)

        if st.button("Enregistrer"):
            data = {
                "operation_id": operation_id,
                "type_operation": type_operation,
                "departement": departement,
                "evenement": evenement,
                "latitude": latitude,
                "longitude": longitude,
            }
            supabase.table("operation").insert(data).execute()
            st.success("Opération ajoutée avec succès")
            st.rerun()

# ---------------------------------------------------------
# 4) Modifier une opération
# ---------------------------------------------------------
st.subheader("✏️ Modifier une opération")

operation_ids = [op["operation_id"] for op in operations]
selected_id = st.selectbox("Sélectionnez une opération à modifier", operation_ids)

if selected_id:
    op = next(o for o in operations if o["operation_id"] == selected_id)

    if st.button("Modifier"):
        with st.modal(f"Modifier l'opération {selected_id}"):

            type_operation = st.text_input("Type d'opération", value=op.get("type_operation", ""))
            departement = st.text_input("Département", value=op.get("departement", ""))
            evenement = st.text_input("Événement", value=op.get("evenement", ""))
            latitude = st.number_input("Latitude", value=op.get("latitude", 0.0))
            longitude = st.number_input("Longitude", value=op.get("longitude", 0.0))

            if st.button("Enregistrer les modifications"):
                data = {
                    "type_operation": type_operation,
                    "departement": departement,
                    "evenement": evenement,
                    "latitude": latitude,
                    "longitude": longitude,
                }
                supabase.table("operation").update(data).eq("operation_id", selected_id).execute()
                st.success("Opération mise à jour")
                st.rerun()

# ---------------------------------------------------------
# 5) Supprimer une opération
# ---------------------------------------------------------
st.subheader("🗑️ Supprimer une opération")

delete_id = st.selectbox("Sélectionnez une opération à supprimer", operation_ids, key="delete")

if st.button("Supprimer définitivement"):
    supabase.table("operation").delete().eq("operation_id", delete_id).execute()
    st.warning(f"Opération {delete_id} supprimée")
    st.rerun()
