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
    vk = st.text_input("Neural Key", type="password")
    if st.button("SİSTEMİ UYANDIR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. ULTRA-DARK CSS ---
st.set_page_config(page_title="Gürkan AI PRO v154", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #030406 !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 4px !important; }
    .intel-card { background: #0d1117; border-left: 4px solid #ffcc00; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    .stat-label { font-size: 10px; color: #8b949e; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
    .stat-val { font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
    .perc-box { padding: 2px 8px; border-radius: 5px; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU (YÜZDESEL ODAKLI) ---
def get_neural_tracker(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        # GÜNLÜK DEĞİŞİM HESABI
        daily_change = ((lp - prev_close) / prev_close) * 100
        
        std = df['Close'].tail(20).std()
        
        # Zeka Skoru
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        score = 0
        if lp > ma20: score += 40
        if 45 < rsi < 65: score += 40
        if df['Volume'].iloc[-1] > df['Volume'].tail(5).mean(): score += 20
        
        color = "#00ff88" if daily_change >= 0 else "#ff4b4b"
        
        return {
            "p": lp, 
            "ch": daily_change, 
            "score": score, 
            "rsi": rsi, 
            "high": round(lp+(std*1.6),2), 
            "low": round(lp-(std*1.6),2), 
            "df": df,
            "color": color
        }
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00; font-family:monospace;'>🤵 GÜRKAN AI : NEURAL TRACKER</h4>", unsafe_allow_html=True)

# Üst Arama Çubuğu
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([4, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("TRACK", use_container_width=True): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Paneller
col_fav, col_main, col_rad = st.columns([0.8, 4, 1.2])

with col_fav:
    st.markdown("<p class='stat-label'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([4, 1.5])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_neural_tracker(st.session_state["last_sorgu"])
    if res:
        # ANA PANEL: FİYAT VE % DEĞİŞİM MERKEZDE
        st.markdown(f"""
        <div class='intel-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
                <b style='color:#ffcc00; font-size:16px;'>{st.session_state["last_sorgu"]} SCAN REPORT</b>
                <span style='color:{res['color']}; background:rgba({(0,255,136,0.1) if res['ch']>=0 else (255,75,75,0.1)}); padding:5px 15px; border-radius:8px; font-weight:bold;'>
                    GÜNLÜK: {res['ch']:+.2f}%
                </span>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div><p class='stat-label'>ANLIK FİYAT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>3G TAVAN (TAHMİN)</p><p class='stat-val' style='color:#00ff88;'>{res['high']}</p></div>
                <div><p class='stat-label'>3G TABAN (TAHMİN)</p><p class='stat-val' style='color:#ff4b4b;'>{res['low']}</p></div>
                <div><p class='stat-label'>ZEKA SKORU</p><p class='stat-val' style='color:#ffcc00;'>%{res['score']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True)

with col_rad:
    st.markdown("<p class='stat-label'>HIZLI RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): 
            st.session_state["last_sorgu"] = r; st.rerun()
