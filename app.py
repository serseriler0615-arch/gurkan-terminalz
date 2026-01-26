import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SİSTEM AYARLARI ---
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
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # ULTRA DASHBOARD CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* Metrik ve Asistan */
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 20px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        
        /* RADAR KARTLARI (YENİ TASARIM) */
        .radar-box { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 8px; margin-bottom:
