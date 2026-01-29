import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Stability+", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS", "ASTOR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL"]

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 15px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 12px; font-weight: bold; font-size: 11px; height: 35px; width: 100%; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 10px !important; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    .price-main { font-size: 45px; font-weight: bold; font-family: 'JetBrains Mono'; color: #fff; }
    @media (max-width: 1000px) { .radar-container { height: auto; max-height: 400px; margin-top: 20px; } }
</style>
""", unsafe_allow_html=True)

# --- 3. MOTORLAR ---
@st.cache_data(ttl=300)
def deep_radar_engine(symbols):
    results = []
    for s in symbols:
        try:
            df = yf.download(s + ".IS", period="30d", interval="1d", progress=False)
            if len(df) < 15: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            cp = df['Close'].iloc[-1]; ma20 = df['Close'].rolling(20).mean().iloc[-1]
            vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            score = 0
            if cp > ma20: score += 50
            if vol_r > 1.1: score += 40
            if score >= 50: results.append({"s": s, "p": cp, "score": score, "vol": vol_r})
        except: continue
    return sorted(results, key=lambda x: x['score'], reverse=True)

def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]; atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": lp+(atr*2.7), "stop": min(lp-(atr*2.3), ma20*0.95), "vol": df['Volume'].iloc[-1]/df['Volume'].rolling(10).mean().iloc[-1]}
    except: return None

# --- 4. LAYOUT ---
main_col, radar_col = st.columns([3.2, 1])

with main_col:
    # Arama ve Favori Kontrolleri
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐ EKLE"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Çubukları
    if st.session_state["favorites"]:
        fav_list = st.session_state["favorites"]
        f_cols = st.columns(len(fav_list))
        for i, fav in enumerate(fav_list):
            if f_cols[i].button(fav):
                st.session_state["last_sorgu"] = fav
                st.rerun()

    res = get_analysis(st.session_state["last_sorgu"])
    if res:
        change_color = "#00ff88" if res['ch'] > 0 else "#ff4b4b"
        vol_color = "#00ff88" if res['vol'] > 1.2 else "#8b949e"
        
        # HTML Bloğu - f-string karmaşasından kurtarıldı
        html_card = f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} // CORE</p>
                    <span class='price-main'>{res['p']:.2f}</span>
                    <span style='color:{change_color}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='label-mini'>HACİM GÜCÜ: {res['vol']:.1f}x</span><br>
                    <span style='color:{vol_color}; font-weight:bold;'>GÜÇ ANALİZİ TAMAM</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:20px;'>
                <div style='background:#161b22; padding:15px
