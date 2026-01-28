import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Neural Key...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. NEXUS UI CSS ---
st.set_page_config(page_title="Gürkan AI v161", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #161b22 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 6px !important; font-size: 11px !important; transition: 0.3s; width: 100%;}
    div.stButton > button:hover { border-color: #ffcc00 !important; background: #1c2128 !important; }
    .report-card { background: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .research-box { background: rgba(0, 255, 136, 0.03); border: 1px dashed #00ff8866; padding: 15px; border-radius: 10px; text-align: center; margin: 10px 0; }
    .label-text { color: #8b949e; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }
    .val-text { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_nexus_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Aşırı Araştırma (Volatilite Tabanlı Olasılık)
        returns = df['Close'].pct_change().dropna()
        vol = returns.tail(20).std(); drift = returns.tail(20).mean()
        p_move = (drift + (vol * 1.645)) * 100
        m_move = (drift - (vol * 1.645)) * 100
        
        # Zeka Skoru
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = 80 if lp > ma20 else 45
        
        return {"p": lp, "ch": ch, "score": score, "plus": round(p_move,2), "minus": round(m_move,2), "df": df}
    except: return None

# --- 4. ARAYÜZ (NEXUS LAYOUT) ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; margin-bottom:10px;'>🤵 GÜRKAN AI : NEURAL NEXUS</h3>", unsafe_allow_html=True)

# ARAMA MOTORU (Merkezi)
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed", placeholder="Hisse Ara...").upper().strip()
    with c2: 
        if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# ANA PANEL YAPISI
col_fav, col_main, col_rad = st.columns([0.8, 4, 0.8])

with col_fav:
    st.markdown("<p class='label-text'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1])
        if cf1.button(f, key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        if cf2.button("X", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_nexus_data(st.session_state["last_sorgu"])
    if res:
        # 1. RAPOR KARTI
        st.markdown(f"""
        <div class='report-card'>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label-text'>FİYAT</p><p class='val-text'>{res['p']:.2f}</p></div>
                <div style='flex:1;'><p class='label-text'>DEĞİŞİM</p><p class='val-text' style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
                <div style='flex:1;'><p class='label-text'>ZEKA SKORU</p><p class='val-text' style='color:#ffcc00;'>%{res['score']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. ARAŞTIRMA KATMANI (Aşırı Zeki Tahmin)
        st.markdown(f"""
        <div class='research-box'>
            <p class='label-text' style='color:#00ff88;'>📊 24 SAATLİK ARAŞTIRMA TAHMİNİ</p>
            <span style='font-size:22px; font-weight:bold; color:#00ff88;'>+%{res['plus']}</span>
            <span style='font-size:20px; color:#333; margin:0 10px;'>/</span>
            <span style='font-size:22px; font-weight:bold; color:#ff4b4b;'>-%{abs(res['minus'])}</span>
            <p style='font-size:9px; color:#8b949e; margin-top:5px;'>Olasılıklar son 1 yıllık volatilite karakterine göre hesaplanmıştır.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. ÇİZELGE
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_rad:
    st.markdown("<p class='label-text'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "BIMAS"]:
        if st.button(f"⚡ {r}", key=f"r_{r}"): st.session_state["last_sorgu"] = r; st.rerun()
