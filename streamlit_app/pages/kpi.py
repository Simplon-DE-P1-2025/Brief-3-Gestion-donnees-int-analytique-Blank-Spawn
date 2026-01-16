import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

from utils.auth_ui import render_auth_widget

# -------------------------
# Auth
# -------------------------
user = render_auth_widget()

# -------------------------
# ENV
# -------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")          # lecture seule
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # admin / RPC

# Client lecture seule pour afficher les KPI
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Client admin pour recalculer les KPI
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# -------------------------
# UI
# -------------------------
st.title("📊 KPI – Opérations de secours")

# -------------------------
# Bouton refresh
# -------------------------
if st.button("🔄 Recalculer les KPI"):
    try:
        supabase_admin.rpc("refresh_kpi_global").execute()
        st.success("✅ KPIs recalculés")
        # Relire les KPI après recalcul
        kpi = supabase.table("kpi_global").select("*").eq("id", 1).execute().data
    except Exception as e:
        st.error(f"❌ Erreur lors du recalcul des KPI : {e}")


# -------------------------
# Lecture KPI
# -------------------------
try:
    kpi = supabase.table("kpi_global").select("*").eq("id", 1).execute().data

    if not kpi:
        st.warning("KPIs non disponibles")
        st.stop()

    kpi = kpi[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Nombre d'opérations", kpi["nb_operations"])
    col2.metric("Durée moyenne (heures)", kpi["duree_moyenne_heures"])
    col3.metric("Taux de blessés (%)", kpi["taux_blesses"])
    col4.metric("Opérations météo difficiles", kpi["nb_operations_difficiles"])

    st.caption(f"Dernière mise à jour : {kpi['updated_at']}")

except Exception as e:
    st.error(f"❌ Erreur lors de la lecture des KPI : {e}")
