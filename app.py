import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. OTURUM VE GİRİŞ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="VIP Giriş", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("Gürkan AI VIP Terminal")
        key = st.text_input("VIP Lisans Anahtarı", key="login_key")
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

    # --- GELİŞMİŞ TÜRKÇE CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* VIP ASİSTAN */
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        
        /* RADAR KARTLARI */
        .radar-card { 
            background: #161b22; border: 1px solid #30363d; border-radius: 8px; 
            padding: 8px 12px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; 
        }
        .radar-name { color: #00ff88 !important; font-size: 14px !important; }
        .radar-vol { color: #8b949e !important; font-size: 10px !important; }
