import streamlit as st
import pandas as pd
import random
from datetime import datetime
from utils.db import fetch_data, insert_row, update_row, delete_row

# --------------------
# Configuration & Styles
# --------------------
st.set_page_config(page_title="CRUD Pro - Supabase", layout="wide")

# Fonction utilitaire pour corriger les types Pandas
def sanitize_dict(d: dict) -> dict:
    clean_dict = {}
    for k, v in d.items():
        # On retire la colonne technique de suppression si elle traine
        if k == "🗑️ Supprimer":
            continue
            
        if isinstance(v, float) and v.is_integer():
            clean_dict[k] = int(v)
        elif pd.isna(v):
            continue
        else:
            clean_dict[k] = v
    return clean_dict

# --------------------
# Paramétrage des Tables
# --------------------
TABLE_KEYS = {
    "operation": ["operation_id"],
    "flotteurs": ["operation_id", "numero_ordre"],
    "resultats_humain": ["operation_id", "categorie_personne"],
}

st.title("🎛️ Gestion des Données (CRUD)")

col_choice, _ = st.columns([1, 3])
with col_choice:
    selected_table = st.selectbox("Table active :", options=list(TABLE_KEYS.keys()))
pk = TABLE_KEYS[selected_table]

# --------------------
# Chargement des données
# --------------------
try:
    # 1. Charger les données de la table sélectionnée
    raw_data = fetch_data(selected_table, order_by=pk[0])
    df = pd.DataFrame(raw_data)
    
    # 2. Si on est sur une table enfant, on charge la liste des IDs opérations pour les selectbox
    list_operations = []
    if selected_table != "operation":
        ops_data = fetch_data("operation", columns="operation_id", order_by="operation_id")
        list_operations = [op['operation_id'] for op in ops_data]

except Exception as e:
    st.error(f"Erreur de connexion : {e}")
    st.stop()

# Initialisation du snapshot
if f"original_{selected_table}" not in st.session_state:
    st.session_state[f"original_{selected_table}"] = df.copy()

# --------------------
# SECTION 1 : AJOUTER (Formulaire Intelligent)
# --------------------
with st.expander(f"➕ Ajouter une ligne dans {selected_table}", expanded=False):
    with st.form("add_new_row_form", clear_on_submit=True):
        new_row_data = {}
        cols = st.columns(3)
        
        # --- LOGIQUE INTELLIGENTE DES CHAMPS ---
        for i, col_name in enumerate(df.columns):
            # On ignore la colonne de suppression si elle existe déjà dans le dataframe
            if col_name == "🗑️ Supprimer": 
                continue

            with cols[i % 3]:
                # CAS 1 : C'est l'ID de l'opération (Clé Primaire ou Étrangère)
                if col_name == "operation_id":
                    if selected_table == "operation":
                        st.info("🆔 ID Opération : Sera généré automatiquement.")
                    else:
                        # Dropdown pour choisir l'opération parente
                        new_row_data[col_name] = st.selectbox("Opération parente *", options=list_operations)
                
                # CAS 2 : Numéro d'ordre (pour flotteurs) -> Auto-incrément suggéré
                elif col_name == "numero_ordre" and selected_table == "flotteurs":
                    # On essaie de deviner le prochain numéro
                    next_val = 1
                    if not df.empty:
                        # On prend le max, attention si filtre par opération non appliqué ici c'est global
                        # Pour faire bien, il faudrait filtrer par l'opération choisie, 
                        # mais comme le selectbox est dans le form, on ne l'a pas encore.
                        # On propose juste max global + 1 par défaut pour l'UX
                        try:
                            next_val = int(df["numero_ordre"].max()) + 1
                        except:
                            pass
                    new_row_data[col_name] = st.number_input(f"{col_name}", value=next_val, step=1)

                # CAS 3 : Champs classiques
                else:
                    if "date" in col_name:
                        new_row_data[col_name] = st.text_input(f"{col_name} (YYYY-MM-DD HH:MM)")
                    elif df[col_name].dtype == 'int64' or df[col_name].dtype == 'float64':
                         new_row_data[col_name] = st.number_input(f"{col_name}", step=1)
                    else:
                        is_required = " *" if col_name in pk else ""
                        new_row_data[col_name] = st.text_input(f"{col_name}{is_required}")

        submitted = st.form_submit_button("Enregistrer la nouvelle ligne")
        
        if submitted:
            # Génération auto de l'ID si on est sur la table operation
            if selected_table == "operation":
                # Format: OP-YYYYMMDD-Random
                timestamp = datetime.now().strftime("%Y%m%d")
                rand_suffix = random.randint(1000, 9999)
                gen_id = f"OP-{timestamp}-{rand_suffix}"
                new_row_data["operation_id"] = gen_id
                
            # Validation
            if any(not str(new_row_data.get(k, '')).strip() for k in pk):
                st.error(f"Erreur : Clés manquantes {pk}")
            else:
                try:
                    payload = sanitize_dict(new_row_data)
                    insert_row(selected_table, payload)
                    st.toast("✅ Ligne ajoutée avec succès !", icon="🎉")
                    del st.session_state[f"original_{selected_table}"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur d'insertion : {e}")

# --------------------
# SECTION 2 : MODIFIER & SUPPRIMER (Checkbox UX)
# --------------------
st.divider()
st.subheader("📝 Modifier ou Supprimer")

# 1. Ajouter la colonne "Supprimer" au DataFrame pour l'interface
df_editor = df.copy()
df_editor.insert(0, "🗑️ Supprimer", False)

# 2. Configuration des colonnes
column_cfg = {
    "🗑️ Supprimer": st.column_config.CheckboxColumn(
        "Supprimer ?",
        help="Cochez pour supprimer cette ligne",
        default=False,
    )
}
# On désactive l'édition des Clés Primaires
for k in pk:
    column_cfg[k] = st.column_config.TextColumn(disabled=True)

# 3. Affichage de l'éditeur
edited_df = st.data_editor(
    df_editor,
    num_rows="fixed", # On interdit l'ajout/suppr via les raccourcis clavier pour forcer l'usage explicite
    width="stretch",
    column_config=column_cfg,
    key=f"editor_{selected_table}",
    height=400
)

# 4. Bouton d'action global
col_btn, col_info = st.columns([1, 4])
with col_btn:
    save_clicked = st.button("💾 Appliquer les changements", type="primary")

if save_clicked:
    original = st.session_state[f"original_{selected_table}"]
    
    # Récupération des lignes à supprimer (celles cochées)
    rows_to_delete = edited_df[edited_df["🗑️ Supprimer"] == True]
    
    # Récupération des lignes à modifier (non cochées et différentes de l'original)
    # On enlève la colonne 'Supprimer' pour la comparaison
    edited_data_only = edited_df[edited_df["🗑️ Supprimer"] == False].drop(columns=["🗑️ Supprimer"])
    
    try:
        # A. SUPPRESSION
        if not rows_to_delete.empty:
            count_del = 0
            for idx, row in rows_to_delete.iterrows():
                # On récupère l'ID original pour la suppression
                # (Attention : si l'index a changé, il faut se baser sur les valeurs de PK)
                row_id_values = sanitize_dict(row[pk].to_dict())
                delete_row(selected_table, row_id=row_id_values, id_column=pk)
                count_del += 1
            st.toast(f"🗑️ {count_del} ligne(s) supprimée(s)", icon="check")

        # B. MISE A JOUR
        # On compare edited_data_only avec original
        # Attention aux index : data_editor préserve l'index Pandas
        common_idx = edited_data_only.index.intersection(original.index)
        
        # Masque des changements
        changed_mask = (edited_data_only.loc[common_idx] != original.loc[common_idx]).any(axis=1)
        changed_indices = common_idx[changed_mask]
        
        if not changed_indices.empty:
            count_upd = 0
            for idx in changed_indices:
                full_row_clean = sanitize_dict(edited_data_only.loc[idx].to_dict())
                
                # Séparation ID / DATA
                row_id_values = {k: full_row_clean[k] for k in pk}
                data_to_update = {k: v for k, v in full_row_clean.items() if k not in pk}
                
                update_row(selected_table, row_id=row_id_values, data=data_to_update, id_column=pk)
                count_upd += 1
            st.toast(f"✏️ {count_upd} ligne(s) modifiée(s)", icon="check")

        # Refresh
        if rows_to_delete.empty and changed_indices.empty:
            st.info("Aucune modification détectée.")
        else:
            st.session_state[f"original_{selected_table}"] = edited_data_only.copy()
            import time
            time.sleep(1) # Petit délai pour laisser lire les toasts
            st.rerun()

    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")