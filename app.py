import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Deep Validation", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS", "ASTOR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 15px; height: 850px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; border-left: 4px solid #484f58; }
    .scan-item.gold { border-left: 4px solid #ffcc00; background: rgba(255, 204, 0, 0.05); }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 12px; font-weight: bold; font-size: 11px; height: 35px; width: 100%; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    .price-main { font-size: 45px; font-weight: bold; font-family: 'JetBrains Mono'; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- 3. DERİN ANALİZ MOTORU ---
@st.cache_data(ttl=300)
def deep_validation_engine(symbols):
    results = []
    for s in symbols:
        try:
            df = yf.download(s + ".IS", period="60d", interval="1d", progress=False)
            if len(df) < 30: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # Veri Hazırlama
            cp = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean()
            std =
