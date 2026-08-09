import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="SIEM Center", layout="wide")

st.title("SIEM Center")
st.write("Monitoring ancaman real-time.")
st.divider()

st.sidebar.header("Konfigurasi")
refresh_rate = st.sidebar.slider("Auto Refresh (detik)", 5, 60, 10)

# Koneksi menggunakan Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl=0) # ttl=0 memaksa web mengambil data paling baru
        if not data.empty and 'Score' in data.columns:
            data['Score'] = pd.to_numeric(data['Score'], errors='coerce')
        return data
    except Exception as e:
        st.error(f"Gagal membaca database Cloud: {e}")
        return pd.DataFrame()

data = load_data()

if not data.empty and 'IP' in data.columns:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Log Terproses", len(data))
    col2.metric("IP Berisiko Tinggi", len(data[data['Score'] > 75]))
    col3.metric("Unique IP Terdeteksi", data['IP'].nunique())
    col4.metric("Negara Sumber Utama", data['Country'].mode()[0] if not data['Country'].empty else "N/A")
    st.divider()

    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("📋 Log Ancaman Real-time")
        def color_status(val):
            return 'color: #ff4b4b; font-weight: bold' if val == 'BAHAYA' else 'color: #00c853; font-weight: bold'
        st.dataframe(data.style.map(color_status, subset=['Status']).background_gradient(subset=['Score'], cmap='YlOrRd'), use_container_width=True, height=400)
    
    with right_col:
        st.subheader("🌍 Top 5 Negara Asal")
        st.bar_chart(data['Country'].value_counts().head(5))
else:
    st.info("Menunggu data masuk dari sensor lokal ke Cloud Database...")

time.sleep(refresh_rate)
st.rerun()
