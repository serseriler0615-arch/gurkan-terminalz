import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. GLOBAL AYARLAR ---
st.set_page_config(page_title="Gürkan AI v173", layout="wide", initial_sidebar_state="collapsed")

# Tüm hataları ve beyazlıkları temizleyen CSS
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input ve Sorgula Butonu Yan Yana */
    .stTextInput>div>div>input {
        background: #0d1117 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        height: 35px !important;
    }
    
    /* MİKRO BUTONLAR (Radar ve Liste İçin) */
    div.stButton > button {
        background: #0d1117 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 3px !important;
        font-size: 10px !important; padding: 0px 5px !important;
        height: 22px !important; width: 100% !important;
        transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }

    /* Ana Kart Tasarımı */
    .info-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 15px; border-top: 2px solid #ffcc00; margin-bottom: 10px;
    }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. VERİ ÇEKME ---
def get_clean_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- 3. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; margin-bottom:20px;'>🤵 GÜRKAN AI TERMINAL</h3>", unsafe_allow_html=True)

# ÜST ARAMA PANELİ
_, search_col, _ = st.columns([1.5, 1.5, 1.5])
with search_col:
    c1, c2 = st.columns([3, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("OK", key="main_search"): 
            st.session_state["last_sorgu"] = s_inp
            st.rerun()

# ANA GÖVDE
l, m, r = st.columns([0.6, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTE</p>", unsafe_allow_html=True)
    for f in ["THYAO", "AKBNK", "ISCTR", "EREGL", "HUNER"]:
        if st.button(f, key=f"l_{f}"):
            st.session_state["last_sorgu"] = f
            st.rerun()

with m:
    df = get_clean_data(st.session_state["last_sorgu"])
    if df is not None:
        lp = df['Close'].iloc[-1]
        ch = ((lp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        # BİLGİ KARTI
        st.markdown(f"""
        <div class='info-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ</span><br>
                    <span style='font-size:32px; font-weight:bold; color:#fff;'>{lp:.2f}</span>
                    <span style='color:{"#00ff88" if ch>0 else "#ff4b4b"}; font-size:18px; margin-left:10px;'>{ch:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>MOMENTUM</p>
                    <p style='color:#ffcc00; font-weight:bold; margin:0;'>{"GÜÇLÜ" if ch > 0 else "ZAYIF"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # GRAFİK (Tamamen Karanlık ve Hizalı)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(
            height=500, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d')),
            xaxis=dict(gridcolor='#161b22', tickfont=dict(color='#4b525d'))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for rd in ["TUPRS", "KCHOL", "ASELS", "SAHOL", "PGSUS"]:
        st.markdown(f"<div style='margin-bottom:5px;'><span style='color:#ffcc00; font-size:11px;'>{rd}</span></div>", unsafe_allow_html=True)
        if st.button("İncele", key=f"r_{rd}"):
            st.session_state["last_sorgu"] = rd
            st.rerun()
