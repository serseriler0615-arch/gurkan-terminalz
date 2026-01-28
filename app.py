import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Gürkan AI v172", layout="wide")

# CSS: Sadece karanlık mod ve mikro butonlar için en temel kod
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; }
    /* Mikro Butonlar */
    div.stButton > button {
        background: #0d1117 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 2px !important;
        font-size: 10px !important; padding: 0px 5px !important;
        height: 20px !important; width: auto !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    /* Gereksiz boşlukları sil */
    .block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. TEMİZ VERİ ÇEKME ---
def get_data(symbol):
    try:
        data = yf.download(symbol + ".IS", period="3mo", interval="1d", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data
    except: return None

# --- 3. ARAYÜZ (3 Sütunlu Basit Düzen) ---
st.title(f"🤵 GÜRKAN AI: {st.session_state['last_sorgu']}")

col_fav, col_main, col_radar = st.columns([0.5, 4, 0.5])

# SOL: FAVORİ LİSTESİ
with col_fav:
    st.write("LİSTE")
    for f in ["THYAO", "AKBNK", "ISCTR", "EREGL"]:
        if st.button(f, key=f"f_{f}"):
            st.session_state["last_sorgu"] = f
            st.rerun()

# ORTA: ANA EKRAN
with col_main:
    # Arama
    s_inp = st.text_input("Hisse Ara:", value=st.session_state["last_sorgu"]).upper().strip()
    if st.button("SORGULA"):
        st.session_state["last_sorgu"] = s_inp
        st.rerun()
    
    df = get_data(st.session_state["last_sorgu"])
    if df is not None and not df.empty:
        lp = df['Close'].iloc[-1]
        ch = ((lp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        st.metric(label="Fiyat", value=f"{lp:.2f}", delta=f"{ch:.2f}%")
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(height=500, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# SAĞ: RADAR (MİKRO İNCELE BUTONLU)
with col_radar:
    st.write("RADAR")
    for r in ["TUPRS", "KCHOL", "ASELS", "SAHOL"]:
        st.text(r)
        if st.button("İncele", key=f"r_{r}"):
            st.session_state["last_sorgu"] = r
            st.rerun()
