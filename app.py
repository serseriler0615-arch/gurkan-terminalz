import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL", "TUPRS"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Oracle Key", type="password", placeholder="Neural Key...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. ORACLE UI CSS ---
st.set_page_config(page_title="Gürkan AI v163", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #030508 !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 4px !important; width: 100%; transition: 0.2s; }
    div.stButton > button:hover { border-color: #ffcc00 !important; box-shadow: 0 0 10px rgba(255,204,0,0.2); }
    .oracle-card { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 10px; border-top: 3px solid #ffcc00; }
    .insight-box { background: rgba(255, 204, 0, 0.05); border-left: 4px solid #ffcc00; padding: 15px; border-radius: 5px; margin: 10px 0; font-family: 'Segoe UI', sans-serif; }
    .label { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
    .val { font-size: 22px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ORACLE MOTORU ---
def get_oracle_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Gelişmiş İstatistik (Araştırma Katmanı)
        rets = df['Close'].pct_change().dropna()
        vol = rets.tail(30).std(); trend = rets.tail(20).mean()
        p_move = (trend + (vol * 1.96)) * 100  # %95 Güven Aralığı
        m_move = (trend - (vol * 1.96)) * 100
        
        # Oracle Kararı ve İçgörü
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (rets.tail(14).where(rets > 0, 0).mean() / -rets.tail(14).where(rets < 0, 0).mean())))
        
        if lp > ma20 and rsi < 60:
            dec = "AGRESİF AL"; clr = "#00ff88"; insight = f"🚀 <b>Balina Aktivitesi:</b> Hacimli kırılım onaylanmış. {lp*0.97:.2f} altına inmedikçe yön yukarı."
        elif rsi > 70:
            dec = "DİKKAT: SAT"; clr = "#ff4b4b"; insight = f"⚠️ <b>Yorulma Sinyali:</b> RSI {rsi:.1f} ile aşırı alımda. Kar realizasyonu için {lp:.2f} güçlü bir direnç."
        else:
            dec = "BEKLE"; clr = "#ffcc00"; insight = f"⚖️ <b>Denge Bölgesi:</b> Piyasa yön tayin edemiyor. {lp*1.02:.2f} üzerinde kalıcılık aranmalı."
            
        return {"p": lp, "ch": ch, "p_move": p_move, "m_move": m_move, "dec": dec, "clr": clr, "ins": insight, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; margin-bottom:5px;'>🤵 GÜRKAN AI : NEURAL ORACLE</h3>", unsafe_allow_html=True)

# ARAMA & EKLEME
_, mid, _ = st.columns([1, 2, 1])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("TARAMA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

col_fav, col_main, col_rad = st.columns([0.8, 4, 0.8])

with col_fav:
    st.markdown("<p class='label'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1.2])
        if cf1.button(f, key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        if cf2.button("X", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_oracle_data(st.session_state["last_sorgu"])
    if res:
        # ANA PANEL
        st.markdown(f"""
        <div class='oracle-card'>
            <div style='display:flex; justify-content:space-around; text-align:center; align-items:center;'>
                <div style='flex:1;'><p class='label'>FİYAT</p><p class='val'>{res['p']:.2f}</p></div>
                <div style='flex:1;'>
                    <div style='border:2px solid {res['clr']}; color:{res['clr']}; padding:5px; border-radius:8px; font-weight:bold;'>{res['dec']}</div>
                    <p class='label' style='margin-top:5px;'>ORACLE KARARI</p>
                </div>
                <div style='flex:1;'><p class='label'>GÜNLÜK %</p><p class='val' style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
            </div>
            <div class='insight-box'>
                <span style='color:#ffcc00; font-size:11px; font-weight:bold;'>🤵 GÜRKAN AI İÇGÖRÜSÜ:</span><br>
                <span style='font-size:14px;'>{res['ins']}</span>
            </div>
            <div style='display:flex; justify-content:center; gap:50px; border-top:1px solid #1c2128; padding-top:10px;'>
                <div><p class='label'>BEKLENEN MAX (+)</p><p style='color:#00ff88; font-weight:bold; font-size:20px;'>+%{res['p_move']:.2f}</p></div>
                <div><p class='label'>BEKLENEN MAX (-)</p><p style='color:#ff4b4b; font-weight:bold; font-size:20px;'>-%{abs(res['m_move']):.2f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ÇİZELGE
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_rad:
    st.markdown("<p class='label'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "ISCTR", "PGSUS"]:
        if st.button(f"⚡ {r}", key=f"r_{r}"): st.session_state["last_sorgu"] = r; st.rerun()
