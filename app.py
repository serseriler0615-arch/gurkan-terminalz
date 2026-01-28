import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "AKBNK"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<style>.stApp {background:#05070a;}</style>", unsafe_allow_html=True)
    vk = st.text_input("Giriş Anahtarı", type="password")
    if st.button("TERMİNALİ AKTİF ET"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. MICRO-UI CSS (Sıfır Beyazlık & Mini Butonlar) ---
st.set_page_config(page_title="Gürkan AI v169", layout="wide")
st.markdown("""
<style>
    .stApp { background: #05070a !important; color: #a1a1a1 !important; }
    header, .stActionButton { visibility: hidden !important; }
    
    /* Girdi Kutusu */
    .stTextInput>div>div>input {
        background: #0d1117 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
    }
    
    /* Executive Kart */
    .hunter-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 6px;
        padding: 12px; margin-bottom: 10px; border-left: 3px solid #ffcc00;
    }
    
    /* MİKRO BUTON TASARIMI */
    div.stButton > button {
        background: #111418 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; border-radius: 3px !important;
        font-size: 9px !important; /* Yazı boyutu makul */
        padding: 0px 5px !important; /* İç boşlukları öldürdük */
        min-height: 20px !important; /* Butonu incelttik */
        line-height: 20px !important;
        width: auto !important;
        transition: 0.2s;
        margin: 0 auto !important;
        display: block;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; background: #1c2128 !important; }
    
    .radar-box {
        background: #080a0d; border: 1px solid #161b22;
        padding: 6px; border-radius: 4px; margin-bottom: 4px;
        text-align: center;
    }
    
    .label-mini { color: #4b525d; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 3. VERİ MOTORU ---
def get_radar_data():
    stocks = ["THYAO", "ASELS", "AKBNK", "ISCTR", "EREGL", "TUPRS", "PGSUS", "KCHOL"]
    res = []
    for s in stocks:
        try:
            df = yf.download(s + ".IS", period="5d", interval="1d", progress=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            lp = df['Close'].iloc[-1]; ch = ((lp - df['Close'].iloc[-2])/df['Close'].iloc[-2])*100
            res.append({"s": s, "p": lp, "ch": ch})
        except: continue
    return res

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00; margin-bottom:15px; font-weight:lighter; letter-spacing:5px;'>GÜRKAN AI</h4>", unsafe_allow_html=True)

# Üst Arama
_, mid, _ = st.columns([1.5, 1, 1.5])
with mid:
    c1, c2 = st.columns([3, 1])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("OK", use_container_width=True): st.session_state["last_sorgu"] = s_inp; st.rerun()

l, m, r = st.columns([0.6, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTE</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    df_main = yf.download(st.session_state["last_sorgu"] + ".IS", period="1mo", interval="1d", progress=False)
    if not df_main.empty:
        if isinstance(df_main.columns, pd.MultiIndex): df_main.columns = df_main.columns.get_level_values(0)
        lp = df_main['Close'].iloc[-1]; ch = ((lp - df_main['Close'].iloc[-2])/df_main['Close'].iloc[-2])*100
        
        st.markdown(f"""
        <div class='hunter-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]}</p>
                    <span style='font-size:28px; font-weight:bold; color:#fff;'>{lp:.2f}</span>
                    <span style='color:{"#00ff88" if ch>0 else "#ff4b4b"}; margin-left:8px; font-size:16px;'>{ch:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>DURUM</p>
                    <p style='color:#ffcc00; font-weight:bold; font-size:12px;'>{"MOMENTUM OK" if ch > 0 else "BEKLEMEDE"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=df_main.index, open=df_main['Open'], high=df_main['High'], low=df_main['Low'], close=df_main['Close'])])
        fig.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#0d1117', tickfont=dict(color='#30363d')),
                          xaxis=dict(gridcolor='#0d1117', tickfont=dict(color='#30363d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>🎯 RADAR</p>", unsafe_allow_html=True)
    r_list = get_radar_data()
    for rd in r_list:
        st.markdown(f"""
        <div class='radar-box'>
            <div style='display:flex; justify-content:space-between; margin-bottom:2px;'>
                <span style='color:#ffcc00; font-size:11px; font-weight:bold;'>{rd['s']}</span>
                <span style='color:{"#00ff88" if rd['ch']>0 else "#ff4b4b"}; font-size:10px;'>{rd['ch']:+.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # İşte o küçülen buton patron
        if st.button("İncele", key=f"in_{rd['s']}"):
            st.session_state["last_sorgu"] = rd['s']; st.rerun()
