import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI ULTRA", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#ffcc00; font-family:monospace;'>🧠 NEURAL OMNISCIENCE v153</h2>", unsafe_allow_html=True)
    vk = st.text_input("Neural Key", type="password")
    if st.button("SİSTEMİ UYANDIR", use_container_width=True):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. ULTRA-DARK CSS ---
st.set_page_config(page_title="Gürkan AI PRO v153", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #030406 !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 4px !important; font-size: 11px !important; }
    div.stButton > button:hover { border-color: #ffcc00 !important; box-shadow: 0 0 8px rgba(255,204,0,0.2); }
    .intel-card { background: #0d1117; border-left: 4px solid #ffcc00; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    .stat-label { font-size: 9px; color: #8b949e; letter-spacing: 1px; text-transform: uppercase; }
    .stat-val { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_neural_scan(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        std = df['Close'].tail(20).std()
        
        # Zeka Hesaplama
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        score = 0
        if lp > ma20: score += 40
        if 45 < rsi < 65: score += 40
        if df['Volume'].iloc[-1] > df['Volume'].tail(5).mean(): score += 20
        
        return {"p": lp, "score": score, "rsi": rsi, "high": round(lp+(std*1.6),2), "low": round(lp-(std*1.6),2), "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00; font-family:monospace;'>🤵 GÜRKAN AI : NEURAL OMNISCIENCE</h4>", unsafe_allow_html=True)

# Arama
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([4, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("SCA-NN", use_container_width=True): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Paneller
col_fav, col_main, col_rad = st.columns([1, 4, 1.2])

with col_fav:
    st.markdown("<p class='stat-label'>ZEKİ FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([4, 1.5])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_neural_scan(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='intel-card'>
            <div style='display:flex; justify-content:space-between; margin-bottom:15px;'>
                <b style='color:#ffcc00;'>CORE SCAN: {st.session_state["last_sorgu"]}</b>
                <b style='color:{"#00ff88" if res['score']>60 else "#ffcc00"};'>INTELLIGENCE: %{res['score']}</b>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div><p class='stat-label'>FİYAT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>3G TAVAN</p><p class='stat-val' style='color:#00ff88;'>{res['high']}</p></div>
                <div><p class='stat-label'>3G TABAN</p><p class='stat-val' style='color:#ff4b4b;'>{res['low']}</p></div>
                <div><p class='stat-label'>RSI GÜCÜ</p><p class='stat-val'>{res['rsi']:.1f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True)

with col_rad:
    st.markdown("<p class='stat-label'>ZEKİ RADAR (SCAN)</p>", unsafe_allow_html=True)
    radar_list = ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]
    for r in radar_list:
        # Radardaki her hisse için küçük bir ön tarama skoru (opsiyonel ama aşırı zeki)
        if st.button(f"🔍 {r}", key=f"r_{r}", use_container_width=True): 
            st.session_state["last_sorgu"] = r; st.rerun()
