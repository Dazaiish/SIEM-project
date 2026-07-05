import streamlit as st
import pandas as pd
import time
import os


st.set_page_config(
    page_title="Project SOC Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- STYLE CSS KUSTOM  ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e445b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI LOAD DATA ---
def load_data():
    file_path = 'enriched_data.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Pastikan kolom Score bertipe numerik
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# --- HEADER DASHBOARD ---
st.title("🛡️ Project Aegis: Security Operations Center")
st.write("Monitoring ancaman real-time dari log sistem melalui Sentry C++ & Intelijen Python.")
st.divider()

# --- SIDEBAR ---
st.sidebar.header("Konfigurasi & Filter")
refresh_rate = st.sidebar.slider("Auto Refresh (detik)", 5, 60, 10)
min_score = st.sidebar.slider("Minimal Skor Bahaya", 0, 100, 0)

if st.sidebar.button('🔄 Refresh Data Sekarang'):
    st.rerun()

# --- LOGIKA UTAMA ---
data = load_data()

if not data.empty:
    # Filter data berdasarkan skor di sidebar
    filtered_data = data[data['Score'] >= min_score].sort_index(ascending=False)

    # 1. BARIS METRIK RINGKASAN
    col1, col2, col3, col4 = st.columns(4)
    
    total_logs = len(data)
    high_risk = len(data[data['Score'] > 75])
    unique_ips = data['IP'].nunique()
    top_country = data['Country'].mode()[0] if not data['Country'].empty else "N/A"

    col1.metric("Total Log Terproses", total_logs)
    col2.metric("IP Berisiko Tinggi (>75%)", high_risk, delta_color="inverse")
    col3.metric("Unique IP Terdeteksi", unique_ips)
    col4.metric("Negara Sumber Utama", top_country)

    st.divider()

    # 2. VISUALISASI GRAFIK
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📋 Log Ancaman Terakhir")
        # Fungsi styling untuk mewarnai kolom Status
        def color_status(val):
            color = '#ff4b4b' if val == 'BAHAYA' else '#00c853'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            filtered_data.style.applymap(color_status, subset=['Status'])
            .background_gradient(subset=['Score'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )

    with right_col:
        st.subheader("🌍 Top 5 Negara Asal")
        country_counts = filtered_data['Country'].value_counts().head(5)
        st.bar_chart(country_counts)

    # 3. ANALISIS ISP (Opsional)
    with st.expander("🔍 Lihat Detail ISP Pengirim"):
        isp_data = filtered_data[['IP', 'ISP', 'Country']].drop_duplicates()
        st.table(isp_data.head(10))

else:
    st.warning("Menunggu data masuk... Pastikan sentry.exe dan brain.py sedang berjalan.")
    st.info("Tips: Masukkan IP ke target_log.txt lalu simpan untuk melihat data di sini.")

# --- AUTO REFRESH ---
# Ini akan mereload halaman secara otomatis sesuai slider di sidebar
time.sleep(refresh_rate)
st.rerun()