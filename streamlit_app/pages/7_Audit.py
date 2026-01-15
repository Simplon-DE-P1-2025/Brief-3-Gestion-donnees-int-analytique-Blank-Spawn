import streamlit as st
from utils.db import get_supabase_client
import pandas as pd
import json
import os
from datetime import datetime

st.title("🔍 Audit des Données – Historique & Qualité")

supabase = get_supabase_client()

# ---------------------------------------------------------
# 1) Charger les tables
# ---------------------------------------------------------
def load_table(name):
    response = supabase.table(name).select("*").execute()
    return pd.DataFrame(response.data)

tables = {
    "operation": load_table("operation"),
    "flotteurs": load_table("flotteurs"),
    "resultats_humain": load_table("resultats_humain")
}

# ---------------------------------------------------------
# 2) Charger snapshot précédent
# ---------------------------------------------------------
SNAPSHOT_FILE = "audit_snapshot.json"

if os.path.exists(SNAPSHOT_FILE):
    with open(SNAPSHOT_FILE, "r") as f:
        old_snapshot = json.load(f)
    st.success("Snapshot précédent chargé")
else:
    old_snapshot = {}
    st.warning("Aucun snapshot précédent trouvé (premier audit)")

# ---------------------------------------------------------
# 3) Audit structure
# ---------------------------------------------------------
st.header("📐 Structure des tables")

for name, df in tables.items():
    st.subheader(f"Table : {name}")
    st.write(list(df.columns))

# ---------------------------------------------------------
# 4) Audit types
# ---------------------------------------------------------
st.header("🔎 Types de données")

for name, df in tables.items():
    st.subheader(f"Table : {name}")
    st.write(df.dtypes)

# ---------------------------------------------------------
# 5) Audit valeurs manquantes
# ---------------------------------------------------------
st.header("🚨 Valeurs manquantes")

for name, df in tables.items():
    st.subheader(f"Table : {name}")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        st.success("Aucune valeur manquante")
    else:
        st.warning("Valeurs manquantes détectées :")
        st.write(missing)

# ---------------------------------------------------------
# 6) Audit doublons
# ---------------------------------------------------------
st.header("🧩 Doublons")

for name, df in tables.items():
    st.subheader(f"Table : {name}")
    dups = df[df.duplicated()]
    if dups.empty:
        st.success("Aucun doublon détecté")
    else:
        st.warning(f"{len(dups)} doublons détectés")
        st.dataframe(dups)

# ---------------------------------------------------------
# 7) Audit cohérence des clés
# ---------------------------------------------------------
st.header("🔗 Cohérence des relations")

df_op = tables["operation"]
df_fl = tables["flotteurs"]
df_res = tables["resultats_humain"]

# Flotteurs → Operation
st.subheader("Flotteurs → Operation")
invalid_fl = df_fl[~df_fl["operation_id"].isin(df_op["operation_id"])]
if invalid_fl.empty:
    st.success("Tous les flotteurs sont liés à une opération valide")
else:
    st.error("Flotteurs avec operation_id invalide :")
    st.dataframe(invalid_fl)

# Résultats → Operation
st.subheader("Résultats Humains → Operation")
invalid_res = df_res[~df_res["operation_id"].isin(df_op["operation_id"])]
if invalid_res.empty:
    st.success("Tous les résultats sont liés à une opération valide")
else:
    st.error("Résultats avec operation_id invalide :")
    st.dataframe(invalid_res)

# ---------------------------------------------------------
# 8) Audit historique (ajouts / suppressions / modifications)
# ---------------------------------------------------------
st.header("🕒 Historique des modifications")

def compare_tables(name, df_new):
    st.subheader(f"📌 Table : {name}")

    df_new = df_new.fillna("").astype(str)

    # Ancien snapshot
    if name in old_snapshot:
        df_old = pd.DataFrame(old_snapshot[name]).fillna("").astype(str)
    else:
        df_old = pd.DataFrame()

    new_records = df_new.to_dict(orient="records")
    old_records = df_old.to_dict(orient="records")

    # Ajouts
    added = [row for row in new_records if row not in old_records]

    # Suppressions
    removed = [row for row in old_records if row not in new_records]

    # Modifications
    modified = []
    for row in new_records:
        if row in old_records:
            continue
        if "operation_id" in row:
            same_id_old = [r for r in old_records if r.get("operation_id") == row.get("operation_id")]
            if same_id_old and same_id_old[0] != row:
                modified.append(row)

    # Affichage
    if not added and not removed and not modified:
        st.success("Aucun changement détecté")
    else:
        if added:
            st.warning("➕ Lignes ajoutées :")
            st.dataframe(pd.DataFrame(added))

        if removed:
            st.error("➖ Lignes supprimées :")
            st.dataframe(pd.DataFrame(removed))

        if modified:
            st.info("✏️ Lignes modifiées :")
            st.dataframe(pd.DataFrame(modified))

for name, df in tables.items():
    compare_tables(name, df)

# ---------------------------------------------------------
# 9) Sauvegarde snapshot
# ---------------------------------------------------------
snapshot = {name: df.to_dict(orient="records") for name, df in tables.items()}

with open(SNAPSHOT_FILE, "w") as f:
    json.dump(snapshot, f, indent=4)

st.success(f"Snapshot mis à jour à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------------------------------------------------
# 10) Heure de l’audit
# ---------------------------------------------------------
st.header("⏱️ Informations d’audit")
st.write(f"**Heure actuelle :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
