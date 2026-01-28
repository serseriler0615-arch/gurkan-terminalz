import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Anahtarı Girin...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. CLEAN MATRIX CSS ---
st.set_page_config(page_title="Gürkan AI v155", layout="wide")
st.markdown("""
<style>
    .stApp { background: #0a0c10 !important; color: #e1e1e1 !important; }
    /* Butonları Sabitle */
    div.stButton > button {
        background: #161b22 !important;
        color: #ffcc00 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        width: 100%;
    }
    /* Ana Kart Tasarımı */
    .main-card {
        background: #0d1117;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .price-text { font-size: 42px; font-weight: bold; margin: 0; }
    .change-text { font-size: 20px; font-weight: bold; }
    .label-text { color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_clean_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Basit ama Zeki Destek/Direnç
        std = df['Close'].tail(20).std()
        high_target = lp + (std * 2)
        low_support = lp - (std * 2)
        
        return {"p": lp, "ch": ch, "h": high_target, "l": low_support, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI</h2>", unsafe_allow_html=True)

# Arama Bölümü
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# İçerik
col_side, col_main = st.columns([1, 4])

with col_side:
    st.markdown("<p class='label-text'>FAVORİLERİM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        c_f1, c_f2 = st.columns([4, 1])
        if c_f1.button(f, key=f"btn_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        if c_f2.button("X", key=f"del_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_clean_data(st.session_state["last_sorgu"])
    if res:
        clr = "#00ff88" if res['ch'] >= 0 else "#ff4b4b"
        
        # ANA PANEL
        st.markdown(f"""
        <div class='main-card'>
            <p class='label-text'>{st.session_state["last_sorgu"]} GÜNCEL DURUM</p>
            <p class='price-text'>{res['p']:.2f}</p>
            <p class='change-text' style='color:{clr};'>{res['ch']:+.2f}%</p>
            <hr style='border: 0.5px solid #30363d; margin: 20px 0;'>
            <div style='display:flex; justify-content:space-around;'>
                <div><p class='label-text'>ÜST HEDEF</p><p style='font-size:18px; color:#00ff88; font-weight:bold;'>{res['h']:.2f}</p></div>
                <div><p class='label-text'>ALT DESTEK</p><p style='font-size:18px; color:#ff4b4b; font-weight:bold;'>{res['l']:.2f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
