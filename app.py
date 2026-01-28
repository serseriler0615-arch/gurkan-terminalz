import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. GLOBAL SAYFA AYARLARI ---
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS: SIFIR HATA, TAM KARANLIK, MİKRO BUTON ---
st.markdown("""
<style>
    /* Arkaplan ve Yazı Tipi */
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    /* Input Kutusu: Şık ve Odaklı */
    .stTextInput>div>div>input {
        background: #0d1117 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        height: 38px !important; text-align: center; font-size: 16px !important;
    }
    
    /* MİKRO BUTONLAR: Sadece tık alanı kadar, temiz */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 3px !important;
        font-size: 10px !important; padding: 2px 5px !important;
        height: 22px !important; width: 100% !important;
        line-height: 1 !important; transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; background: #161b22 !important; }

    /* Analiz Kartı */
    .status-box {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 6px;
        padding: 15px; margin-bottom: 10px; border-top: 2px solid #ffcc00;
    }
    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
</style>
""", unsafe_allow_html=True)

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 3. GÜVENLİ VERİ ÇEKME ---
def get_safe_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if df.empty: return None
        # Yfinance'in yeni versiyonlarındaki MultiIndex sütun yapısını düzeltir
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

# --- 4. ARAYÜZ YERLEŞİMİ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; font-weight:lighter; letter-spacing:4px;'>GÜRKAN AI TERMINAL</h3>", unsafe_allow_html=True)

# Üst Arama (Görsel 4'teki gibi merkezlenmiş)
_, mid_search, _ = st.columns([1.5, 1, 1.5])
with mid_search:
    c_in, c_ok = st.columns([4, 1])
    with c_in: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c_ok: 
        if st.button("OK", key="search_btn"): 
            st.session_state["last_sorgu"] = s_inp
            st.rerun()

# Ana Panel
col_list, col_main, col_radar = st.columns([0.7, 4, 0.8])

with col_list:
    st.markdown("<p class='label-mini'>LİSTEM</p>", unsafe_allow_html=True)
    for f in ["THYAO", "AKBNK", "ISCTR", "EREGL", "HUNER"]:
        if st.button(f, key=f"f_{f}"):
            st.session_state["last_sorgu"] = f
            st.rerun()

with col_main:
    df = get_safe_data(st.session_state["last_sorgu"])
    if df is not None:
        lp = df['Close'].iloc[-1]; pc = df['Close'].iloc[-2]; ch = ((lp - pc) / pc) * 100
        
        # Üst Bilgi Kartı
        st.markdown(f"""
        <div class='status-box'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} ANALİZ</span><br>
                    <span style='font-size:32px; font-weight:bold; color:#fff;'>{lp:.2f}</span>
                    <span style='color:{"#00ff88" if ch>0 else "#ff4b4b"}; font-size:18px; margin-left:10px;'>{ch:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini' style='margin:0;'>MOMENTUM</p>
                    <p style='color:#ffcc00; font-weight:bold; font-size:16px; margin:0;'>{"GÜÇLÜ" if ch > 0 else "ZAYIF"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik (Beyazlığı bitiren, saf karanlık Plotly ayarı)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(
            height=500, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d'), showgrid=True),
            xaxis=dict(gridcolor='#161b22', tickfont=dict(color='#4b525d'), showgrid=True)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_radar:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for r in ["TUPRS", "KCHOL", "ASELS", "SAHOL", "PGSUS", "SISE"]:
        st.markdown(f"<div style='margin-bottom:2px;'><span style='color:#ffcc00; font-size:11px; font-weight:bold;'>{r}</span></div>", unsafe_allow_html=True)
        if st.button("İncele", key=f"r_{r}"):
            st.session_state["last_sorgu"] = r
            st.rerun()
