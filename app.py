import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR & GÜVENLİK ---
st.set_page_config(page_title="Gürkan AI v171", layout="wide", initial_sidebar_state="collapsed")

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]

# --- 2. KESKİN CSS (Sıfır Beyazlık, Mikro Butonlar) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    header, .stActionButton { visibility: hidden !important; }
    
    /* Input */
    .stTextInput>div>div>input {
        background: #0d1117 !important; color: #ffcc00 !important;
        border: 1px solid #1c2128 !important; text-align: center;
    }

    /* Ana Panel Kartı */
    .status-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 4px;
        padding: 15px; margin-bottom: 10px; border-top: 2px solid #ffcc00;
    }

    /* MİKRO BUTON (Tam istediğin küçüklükte) */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; padding: 0px 5px !important;
        min-height: 20px !important; height: 20px !important; width: 100% !important;
        transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }

    .label-mini { color: #4b525d; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .radar-box { border-bottom: 1px solid #111418; padding: 5px 0; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. VERİ MOTORU (Hatasız Çekim) ---
def get_data(symbol):
    try:
        data = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if data.empty: return None
        # Yfinance MultiIndex hatasını temizle
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data
    except: return None

# --- 4. ARAYÜZ YERLEŞİMİ ---
st.markdown("<h4 style='text-align:center; color:#ffcc00; letter-spacing:5px;'>GÜRKAN AI</h4>", unsafe_allow_html=True)

# ÜST ARAMA
_, mid_search, _ = st.columns([1.5, 1, 1.5])
with mid_search:
    c_in, c_ok = st.columns([3, 1])
    with c_in: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c_ok: 
        if st.button("OK"): st.session_state["last_sorgu"] = s_inp; st.rerun()

l, m, r = st.columns([0.6, 4, 0.8])

with l:
    st.markdown("<p class='label-mini'>LİSTE</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

with m:
    df = get_data(st.session_state["last_sorgu"])
    if df is not None:
        lp = df['Close'].iloc[-1]; pc = df['Close'].iloc[-2]; ch = ((lp-pc)/pc)*100
        # ÖZET
        st.markdown(f"""
        <div class='status-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]}</span><br>
                    <span style='font-size:28px; font-weight:bold;'>{lp:.2f}</span>
                    <span style='color:{"#00ff88" if ch>0 else "#ff4b4b"}; font-size:16px;'> {ch:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>TREND</p>
                    <p style='color:#ffcc00; font-weight:bold;'>{"GÜÇLÜ" if ch > 0 else "ZAYIF"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#0d1117', tickfont=dict(color='#30363d')),
                          xaxis=dict(gridcolor='#0d1117', tickfont=dict(color='#30363d')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for r_sym in ["THYAO", "AKBNK", "EREGL", "TUPRS", "KCHOL"]:
        st.markdown(f"""
        <div class='radar-box'>
            <div style='display:flex; justify-content:space-between; margin-bottom:2px;'>
                <span style='color:#ffcc00; font-size:11px; font-weight:bold;'>{r_sym}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("İncele", key=f"rad_{r_sym}"):
            st.session_state["last_sorgu"] = r_sym; st.rerun()
