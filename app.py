import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS", "BIMAS"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v95", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .asistan-box { 
            background: linear-gradient(135deg, #0d1117 0%, #05070a 100%); 
            border-left: 5px solid #00ff88; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid #1c2128; 
            color: #e0e0e0; 
            line-height: 1.6;
            margin-bottom: 20px;
        }
        h3 { font-size: 14px !important; color: #00ff88 !important; }
        div.stButton > button {
            background-color: rgba(0, 255, 136, 0.02) !important;
            color: #00ff88 !important;
            border: 1px solid #1c2128 !important;
            font-family: 'Courier New', monospace !important;
            font-size: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.4])

    # 1. SOL: FAVORİ YÖNETİMİ (v94'ten korundu)
    with col_fav:
        st.markdown("### ⭐ TAKİP LİSTEM")
        for f in st.session_state["favorites"]:
            cols = st.columns([4, 1])
            with cols[0]:
                if st.button(f"🔍 {f}", key=f"v95_f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
            with cols[1]:
                if st.button("X", key=f"del_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()

    # 2. ORTA: ANALİZ VE BİLGE YORUMLAR
    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1:
            h_input = st.text_input("HİSSE ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            if h_input not in st.session_state["favorites"]:
                if st.button("⭐ LİSTEYE EKLE", use_
