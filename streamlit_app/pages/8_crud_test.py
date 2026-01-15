import streamlit as st
import pandas as pd
import random
from datetime import datetime
from utils.db import fetch_data, insert_row, update_row, delete_row

# --------------------
# Configuration & Styles
# --------------------
st.set_page_config(page_title="CRUD Pro - Supabase", layout="wide")

def sanitize_dict(d: dict) -> dict:
    clean_dict = {}
    for k, v in d.items():
        if k == "🗑️ Supprimer": continue
        if pd.isna(v) or v == "None" or v == "": continue
        
        # Sécurité pour les entiers
        try:
            if isinstance(v, (float, str)) and float(v).is_integer():
                clean_dict[k] = int(float(v))
            else:
                clean_dict[k] = v
        except:
            clean_dict[k] = v
    return clean_dict

# --------------------
# Paramétrage des Tables
# --------------------
TABLE_KEYS = {
    "operation": ["operation_id"],
    "flotteurs": ["flotteur_id"],
    "resultats_humain": ["resultat_id"],
}
AUTO_COLUMNS = ["flotteur_id", "resultat_id"]

st.title("🎛️ Gestion des Données (CRUD)")

selected_table = st.selectbox("Table active :", options=list(TABLE_KEYS.keys()))
pk = TABLE_KEYS[selected_table]

# --------------------
# Chargement & Nettoyage pour Arrow
# --------------------
try:
    raw_data = fetch_data(selected_table, order_by=pk[0])
    df = pd.DataFrame(raw_data)
    
    # CORRECTIF ARROW : Conversion des types pour éviter le crash de sérialisation
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("")
            
    list_operations = []
    if selected_table != "operation":
        ops_data = fetch_data("operation", columns="operation_id", order_by="operation_id")
        list_operations = [op['operation_id'] for op in ops_data]
except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

if f"original_{selected_table}" not in st.session_state:
    st.session_state[f"original_{selected_table}"] = df.copy()

# --------------------
# SECTION 1 : AJOUTER
# --------------------
with st.expander(f"➕ Ajouter une ligne dans {selected_table}", expanded=False):
    with st.form("add_new_row_form", clear_on_submit=True):
        new_row_data = {}
        cols = st.columns(3)
        columns_to_show = df.columns if not df.empty else []
        
        col_idx = 0
        for col_name in columns_to_show:
            if col_name in ["🗑️ Supprimer"] + AUTO_COLUMNS: continue

            with cols[col_idx % 3]:
                if col_name == "operation_id":
                    if selected_table == "operation":
                        st.info("🆔 ID : Auto-généré")
                    else:
                        new_row_data[col_name] = st.selectbox("Opération *", options=list_operations)
                elif col_name == "numero_ordre" and selected_table == "flotteurs":
                    new_row_data[col_name] = st.number_input(f"{col_name}", value=1, step=1)
                else:
                    new_row_data[col_name] = st.text_input(f"{col_name}")
            col_idx += 1

        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            if selected_table == "operation":
                new_row_data["operation_id"] = f"OP-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            try:
                insert_row(selected_table, sanitize_dict(new_row_data))
                st.toast("✅ Ligne ajoutée !", icon="🎉")
                del st.session_state[f"original_{selected_table}"]
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

# --------------------
# SECTION 2 : MODIFIER & SUPPRIMER
# --------------------
st.divider()
df_editor = df.copy()
df_editor.insert(0, "🗑️ Supprimer", False)

column_cfg = {
    "🗑️ Supprimer": st.column_config.CheckboxColumn("Supprimer ?", default=False)
}
for k in pk:
    column_cfg[k] = st.column_config.Column(disabled=True)

edited_df = st.data_editor(
    df_editor,
    num_rows="fixed",
    width="stretch",
    column_config=column_cfg,
    key=f"editor_{selected_table}"
)

if st.button("💾 Appliquer les changements", type="primary"):
    original = st.session_state[f"original_{selected_table}"]
    rows_to_delete = edited_df[edited_df["🗑️ Supprimer"] == True]
    edited_clean = edited_df[edited_df["🗑️ Supprimer"] == False].drop(columns=["🗑️ Supprimer"])
    
    try:
        # A. SUPPRESSIONS
        if not rows_to_delete.empty:
            for _, row in rows_to_delete.iterrows():
                delete_row(selected_table, row_id=sanitize_dict(row[pk].to_dict()), id_column=pk)
            st.toast(f"🗑️ {len(rows_to_delete)} ligne(s) supprimée(s)", icon="✅")

        # B. MISES À JOUR
        common_idx = edited_clean.index.intersection(original.index)
        changed_mask = (edited_clean.loc[common_idx] != original.loc[common_idx]).any(axis=1)
        changed_indices = common_idx[changed_mask]
        
        if not changed_indices.empty:
            for idx in changed_indices:
                full_row = sanitize_dict(edited_clean.loc[idx].to_dict())
                update_row(selected_table, row_id={k: full_row[k] for k in pk}, 
                           data={k: v for k, v in full_row.items() if k not in pk}, id_column=pk)
            st.toast(f"✏️ {len(changed_indices)} ligne(s) modifiée(s)", icon="✅")

        if not (rows_to_delete.empty and changed_indices.empty):
            st.session_state[f"original_{selected_table}"] = edited_clean.copy()
            st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")