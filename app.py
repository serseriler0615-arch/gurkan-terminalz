import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "AKBNK", "TUPRS"]
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP")
        k = st.text_input("💎 VIP KEY", type="password")
        if st.button("BAŞLAT"):
            if k.startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 İDEAL DARK UI CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        
        /* Başlıklar ve Metinler */
        h3 { font-size: 16px !important; color: #00ff88 !important; margin-bottom: 10px !important; }
        p, span, div { color: #e0e0e0 !important; font-size: 13px !important; }
        
        /* Butonlar: Beyazlık Tamamen Kaldırıldı */
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.03) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            border-radius: 6px !important;
            padding: 5px 10px !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button:hover {
            border-color: #00ff88 !important;
            background-color: rgba(0, 255, 136, 0.1) !important;
            box-shadow: 0 0 10px rgba(0,255,136,0.2);
        }

        /* Gürkan AI Yorum Kutusu */
        .asistan-box { 
            background: #0d1117; 
            border: 1px solid #1c2128;
            border-left: 4px solid #00ff88; 
            padding: 12px; 
            border-radius: 8px; 
            margin-bottom: 15px;
        }

        /* Skor ve Metrikler */
        .skor-box { 
            background: #0d1117; 
            border: 1px solid #00ff88; 
            border-radius: 10px; 
            padding: 10px; 
            text-align: center;
        }
        [data-testid="stMetricValue"] { font-size: 22px !important; color: #ffffff !important; }
        
        /* Input Alanı */
        .stTextInput > div > div > input {
            background-color: #0d1117 !important;
            border: 1px solid #1c2128 !important;
            color: #00ff88 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Ana Düzen: Sol (Favori), Orta (Analiz), Sağ (Radar)
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        for f in st.session_state["favorites"][-7:]:
            if st.button(f"🔍 {f}", key=f"fav_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
        
        st.write("") # Boşluk
        new_fav = st.text_input("", placeholder="+Ekle", key="add_f", label_visibility="collapsed").upper().strip()
        if new_fav and len(new_fav) > 2 and st.button("LİSTEYE EKLE"):
            if new_fav not in st.session_state["favorites"]: st.session_state["favorites"].append(new_fav); st.rerun()

    # 2. ORTA: ANA ANALİZ
    with col_main:
        # Arama Barı
        h_input = st.text_input("HİSSE SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                delta = df['Close'].diff(); gain = (delta.where(delta>0,0)).rolling(14).mean(); loss = (-delta.where(delta<0,0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
                skor = (40 if fiyat > ma20 else 0) + (40 if 45 < rsi < 75 else 0) + (20 if degisim > 0 else 0)

                # Üst Bilgi Satırı
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f} TL")
                m2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                with m4: st.markdown(f"<div class='skor-box'><span style='font-size:11px; color:#8b949e;'>VIP
