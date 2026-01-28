import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Anahtarı Girin...")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. MASTERMIND UI CSS ---
st.set_page_config(page_title="Gürkan AI v156", layout="wide")
st.markdown("""
<style>
    .stApp { background: #080a0d !important; color: #e1e1e1 !important; }
    div.stButton > button {
        background: #111418 !important;
        color: #ffcc00 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    .quantum-card {
        background: #0d1117;
        border: 1px solid #ffcc0044;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .stat-box { text-align: center; border-right: 1px solid #333; }
    .stat-box:last-child { border-right: none; }
    .label-text { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .val-text { font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA MOTORU ---
def get_mastermind_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # RSI
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        # Zeka Skoru (Güven Skoru)
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = 0
        if lp > ma20: score += 40
        if 45 < rsi < 65: score += 40
        if df['Volume'].iloc[-1] > df['Volume'].tail(5).mean(): score += 20
        
        # Hedefler
        std = df['Close'].tail(20).std()
        return {"p": lp, "ch": ch, "rsi": rsi, "score": score, "h": lp+(std*2), "l": lp-(std*2), "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00; font-family:serif;'>🤵 GÜRKAN AI</h2>", unsafe_allow_html=True)

# Üst Kontrol
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([4, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Ana Gövde
col_fav, col_main, col_rad = st.columns([0.8, 4, 1])

with col_fav:
    st.markdown("<p class='label-text'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f_c1, f_c2 = st.columns([4, 1])
        if f_c1.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        if f_c2.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with col_main:
    res = get_mastermind_analysis(st.session_state["last_sorgu"])
    if res:
        # QUANTUM ANALİZ PANELİ (Resim 1 ve 2'nin birleşimi)
        st.markdown(f"""
        <div class='quantum-card'>
            <div style='display:flex; justify-content:space-between; margin-bottom:15px; border-bottom:1px solid #333; padding-bottom:10px;'>
                <span style='color:#ffcc00; font-weight:bold;'>{st.session_state["last_sorgu"]} QUANTUM RAPORU</span>
                <span style='color:{"#00ff88" if res['ch']>=0 else "#ff4b4b"}; font-weight:bold;'>GÜNLÜK: {res['ch']:+.2f}%</span>
            </div>
            <div style='display:flex; justify-content:space-around;'>
                <div class='stat-box' style='flex:1;'><p class='label-text'>FİYAT</p><p class='val-text'>{res['p']:.2f}</p></div>
                <div class='stat-box' style='flex:1;'><p class='label-text'>GÜVEN SKORU</p><p class='val-text' style='color:#ffcc00;'>%{res['score']}</p></div>
                <div class='stat-box' style='flex:1;'><p class='label-text'>RSI</p><p class='val-text'>{res['rsi']:.1f}</p></div>
                <div class='stat-box' style='flex:1;'><p class='label-text'>ÜST HEDEF</p><p class='val-text' style='color:#00ff88;'>{res['h']:.2f}</p></div>
                <div class='stat-box' style='flex:1; border:none;'><p class='label-text'>ALT DESTEK</p><p class='val-text' style='color:#ff4b4b;'>{res['l']:.2f}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_rad:
    st.markdown("<p class='label-text'>HIZLI RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
