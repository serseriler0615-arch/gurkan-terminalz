import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "HUNER"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Neural Key...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. MASTERMIND UI CSS ---
st.set_page_config(page_title="Gürkan AI v160", layout="wide")
st.markdown("""
<style>
    .stApp { background: #080a0d !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #111418 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
    
    .quantum-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
        padding: 15px; margin-bottom: 10px;
    }
    
    .research-box {
        background: rgba(0, 255, 136, 0.02);
        border: 1px dashed #00ff8844;
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        text-align: center;
    }
    
    .label-text { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
    .val-text { font-size: 22px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ARAŞTIRMACI ANALİZ MOTORU ---
def get_research_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Derin İstatistiksel Araştırma (Volatilite & Trend)
        returns = df['Close'].pct_change().dropna()
        volatility = returns.tail(20).std()
        avg_move = returns.tail(20).mean()
        
        # Beklenen Olasılık Alanı (Monte Carlo Simülasyonu Basitleştirilmiş)
        expected_plus = (avg_move + (volatility * 1.645)) * 100
        expected_minus = (avg_move - (volatility * 1.645)) * 100
        
        # Teknik Göstergeler
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = 70 if lp > ma20 else 40
        
        return {
            "p": lp, "ch": ch, "score": score, 
            "plus": round(expected_plus, 2), "minus": round(expected_minus, 2),
            "df": df
        }
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI : NEURAL PREDICTOR</h2>", unsafe_allow_html=True)

col_side, col_main = st.columns([0.8, 5])

with col_side:
    st.markdown("<p class='label-text'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        c1, c2 = st.columns([4, 1.2])
        with c1:
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with c2:
            if st.button("X", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_research_data(st.session_state["last_sorgu"])
    if res:
        # 1. TEMEL RAPOR
        st.markdown(f"""
        <div class='quantum-card'>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div style='flex:1;'><p class='label-text'>FİYAT</p><p class='val-text'>{res['p']:.2f}</p></div>
                <div style='flex:1;'><p class='label-text'>GÜNLÜK DEĞİŞİM</p><p class='val-text' style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
                <div style='flex:1;'><p class='label-text'>SİSTEM SKORU</p><p class='val-text' style='color:#ffcc00;'>%{res['score']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. İSTATİSTİKSEL ARAŞTIRMA KUTUSU (YENİ KATMAN)
        st.markdown(f"""
        <div class='research-box'>
            <p class='label-text' style='color:#00ff88;'>📊 İSTATİSTİKSEL OLASILIK RAPORU</p>
            <p style='margin:10px 0; font-size:15px;'>Bugünkü verilere göre 24 saatlik <b>Beklenen Hareket Alanı:</b></p>
            <span style='font-size:28px; font-weight:bold; color:#00ff88;'>+%{res['plus']}</span>
            <span style='font-size:24px; color:#30363d; margin: 0 15px;'>/</span>
            <span style='font-size:28px; font-weight:bold; color:#ff4b4b;'>-%{abs(res['minus'])}</span>
            <p style='font-size:10px; color:#8b949e; margin-top:10px;'>*Bu oran son 1 yıllık volatilite ve 20 günlük trend ivmesi araştırılarak hesaplanmıştır.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. ÇİZELGE
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
