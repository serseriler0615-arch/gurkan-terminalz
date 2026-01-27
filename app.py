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
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "EREGL"]

# --- GİRİŞ KONTROLÜ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı", type="password")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2026!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 GÖRSELDEKİ BİREBİR TASARIM (CSS) ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .main-header { font-size: 24px; font-weight: bold; color: #ffcc00; margin-bottom: 20px; }
        .gurkan-ai-box { 
            background: #0d1117; border: 1px solid #1c2128; padding: 18px; 
            border-radius: 8px; color: #e0e0e0; margin-bottom: 15px;
            border-left: 5px solid #ffcc00;
        }
        .guven-box {
            background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88;
            padding: 15px; border-radius: 10px; text-align: center;
        }
        div.stButton > button {
            background-color: #161b22 !important; color: #ffffff !important;
            border: 1px solid #30363d !important; text-align: left !important;
            border-radius: 4px !important; height: 45px !important;
            font-family: monospace;
        }
        .active-btn button { background-color: #00c853 !important; border: none !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔐 KOMPAKT ADMİN ŞERİDİ ---
    if st.session_state["role"] == "admin":
        with st.container():
            ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.5])
            with ac1: s_gun = st.selectbox("Süre", [30, 90, 365], label_visibility="collapsed")
            with ac2: 
                if st.button("💎 KEY ÜRET"): 
                    st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
            with ac3: 
                if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
            with ac4:
                if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- ÜST PANEL (LOGO VE ARAMA) ---
    h_col1, h_col2 = st.columns([1, 4])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Hisse veya Endeks ara...", label_visibility="collapsed").upper().strip()

    col_side, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_side:
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"🔍 {f}", key=f"btn_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
