import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

#-------------------------
#ENV
#-------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#-------------------------
#UI
#-------------------------
st.title("📊 KPI – Opérations de secours")

#-------------------------
#Bouton refresh
#-------------------------
if st.button("🔄 Recalculer les KPI"):
    supabase.rpc("refresh_kpi_global").execute()
    st.success("KPIs recalculés")
    st.rerun()

#-------------------------
#Lecture KPI
#-------------------------
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
