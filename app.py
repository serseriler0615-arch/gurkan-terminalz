import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SÜRE VE GİRİŞ SİSTEMİ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="VIP Login", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            key = st.text_input("Lisans Anahtarı")
            if st.button("Giriş"):
                if key.startswith("GAI-"): 
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=30)
                    st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # TEK EKRAN CSS (Sıkıştırma ve Renkler)
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; overflow: hidden; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 14px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        .asistan-box { background: #1c2128; border: 1px solid #00ff88; padding: 10px; border-radius: 10px; font-size: 12px !important; }
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 5px; margin-bottom: 2px; }
        .radar-card { background: #161b22; border-left: 3px solid #00ff88; padding: 8px; margin-bottom: 5px; border-radius: 5px; }
        /* Scroll engelleme ve kompakt görünüm */
        .main .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST BAR (STATUS) ---
    c_st1, c_st2, c_st3 = st.columns([2, 2, 1])
    with c_st1: st.markdown(f"⭐ **Gürkan AI VIP** | {datetime.now().strftime('%H:%M')}")
    with c_st2: 
        if st.session_state["role"] == "user": st.markdown(f"⏳ Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Çıkış", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

    # --- ANA DASHBOARD YERLEŞİMİ ---
    col_fav, col_main, col_radar = st.columns([0.8, 3, 1])

    # 1. SOL SÜTUN: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        yeni_fav = st.text_input("Ekle:", placeholder="Örn: SASA", label_visibility="collapsed").upper()
        if st.button("➕", use_container_width=True) and yeni_fav:
            if yeni_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(yeni_fav)
                st.rerun()
        
        for f in st.session_state["favorites"][-6:]: # Son 6 favoriyi göster
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)
        if st.button("🗑️ Temizle"): 
            st.session_state["favorites"] = []
            st.rerun()

    # 2. ORTA SÜTUN: ANALİZ VE GRAFİK
    with col_main:
        h_input = st.text_input("Hisse Sorgu:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # Sıkıştırılmış Metrikler ve Grafik
                m_c1, m
