import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. OTURUM VE GİRİŞ ---
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
            key = st.text_input("Lisans Anahtarı", key="login_key")
            if st.button("Sistemi Aktive Et"):
                if key.startswith("GAI-"): 
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=30)
                    st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- OKUNABİLİR VE RENKLİ CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* VIP ASİSTAN KUTUSU (BOZULMAYAN ESKİ STİL) */
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 15px; border-radius: 12px; margin-top: 5px; }
        .asistan-header { color: #00ff88 !important; font-size: 16px !important; border-bottom: 1px solid #333; margin-bottom: 8px; }
        
        /* RADAR TASARIMI */
        .radar-card { 
            background: #161b22; border: 1px solid #30363d; border-radius: 8px; 
            padding: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; 
        }
        .radar-info { display: flex; flex-direction: column; }
        .radar-name { color: #00ff88 !important; font-size: 15px !important; }
        .radar-vol { color: #8b949e !important; font-size: 11px !important; font-weight: normal !important; }
        .radar-pct { font-size: 14px !important; padding: 4px 8px; border-radius: 6px; min-width: 65px; text-align: center; }
        .pct-up { background: rgba(0, 255, 136, 0.2); color: #00ff88 !important; border: 1px solid #00ff88; }
        .pct-down { background: rgba(255, 75, 75, 0.2); color: #ff4b4b !important; border: 1px solid #ff4b4b; }
        
        /* Metrikler */
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 22px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST BAR ---
    c_st1, c_st2, c_st3 = st.columns([3, 1, 1])
    with c_st1: st.markdown(f"🚀 **GÜRKAN AI VIP DASHBOARD**")
    with c_st3: 
        if st.button("Güvenli Çıkış", use_container_width=True): st.session_state.clear(); st.rerun()

    # --- ANA DASHBOARD ---
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", placeholder="SASA", key="fav_in", label_visibility="collapsed").upper()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div style='background:#161b22; padding:6px; border-radius:4px; margin-bottom:3px; color:#00ff88;'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE RENKLİ GRAFİK
    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96

                m1, m2, m3 = st.columns(3)
                m1.metric("FİYAT", f"{fiyat:.2f} TL")
                m2.metric("TRENDY", "YUKARI" if fiyat > ma20 else "AŞAĞI")
                m3.metric("STOP-LOSS", f"{stop:.2f}")

                # RENKLENDİRİLMİŞ ALAN GRAFİĞİ
                st.area_chart(df['Close'].tail(25), color="#00ff88", height=180)

                # VIP YORUMU (BOZULMAYAN DETAYLI STİL)
                st.markdown(f"""
                    <div class='asistan-box'>
                        <div class='asistan-header'>🤵 VIP STRATEJİ MERKEZİ: {h_input}</div>
                        <p style='margin:5px 0;'>🔥 <b>Trend:</b> <span style='color:{"#00ff88" if fiyat > ma20 else "#ff4b4b"};'>{"GÜÇLÜ (YUKARI)" if fiyat > ma20 else "ZAYIF (AŞAĞI)"}</span></p>
                        <p style='margin:5px 0;'>🎯 <b>Hedefler:</b> <span style='color:#00ff88;'>{h1:.2f}</span> / <span style='color:#00ff88;'>{h2:.2f}</span></p>
                        <p style='margin:5px 0;'>🛡️ <b>Zarar Kes:</b> <span style='color:#ff4b4b;'>{stop:.2f} TL</span></p>
                        <p style='border-top:1px solid #333; padding-top:5px; margin-top:5px;'><b>Sinyal:</b> {h_input} hissesinde teknik görünüm {'kademeli alım için pozitif böl
