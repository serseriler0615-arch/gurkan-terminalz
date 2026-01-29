import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Master Layout", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS", "ASTOR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL"]

# --- 2. CSS (FAVORİ CHIPS VE DUAL PANEL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    
    /* Sağ Radar */
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 20px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; }
    
    /* Favori Chip'leri */
    div.stButton > button { 
        background: #21262d !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; border-radius: 12px; 
        font-weight: bold; font-size: 12px; height: 35px;
    }
    
    /* Arama ve Favori Ekle Butonları */
    .search-row button { height: 45px !important; }
    
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    .price-main { font-size: clamp(30px, 5vw, 45px); font-weight: bold; font-family: 'JetBrains Mono'; color: #fff; }

    @media (max-width: 1000px) {
        .radar-container { height: auto; max-height: 400px; margin-top: 20px; }
    }
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
    # Arama Satırı
    c1, c2, c3 = st.columns([3, 0.6, 0.6])
    with c1: 
        s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # FAVORİ CHIPS (Geri Geldi!)
    if st.session_state["favorites"]:
        fav_cols = st.columns(len(st.session_state["favorites"]))
        for idx, fav in enumerate(st.session_state["favorites"]):
            if fav_cols[idx].button(fav, key=f"fav_{fav}"):
                st.session_state["last_sorgu"] = fav
                st.rerun()

    res = get_analysis(st.session_state["last_sorgu"])
    if res:
        color = "#00ff88" if res['ch'] > 0 else "#ff4b4b"
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} // CORE</p>
                    <span class='price-main'>{res['p']:.2f}</span>
                    <span style='color:{color}; font-size:20px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='label-mini'>GÜÇ: {res['vol']:.1f}x</span><br>
                    <span style='color:{"#00ff88" if res['vol']>1.2 else "#8b949e"}; font-weight:bold;'>{"BALİNA GİRİŞİ" if res['vol']>1.2 else "NORMAL"}</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:20px;'>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center;'>
                    <p class='label-mini'>PİVOT (MA20)</p><p style='font-size:20px; font-weight:bold;'>{res['ma']:.2f}</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center; border-bottom:3px solid #00ff88;'>
                    <p class='label-mini'>HEDEF</p><p style='font-size:20px; font-weight:bold; color:#00ff88;'>{res['target']:.2f}</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center; border-bottom:3px solid #ff4b4b;'>
                    <p class='label-mini'>STOP</p><p style='font-size:20px; font-weight:bold; color:#ff4b4b;'>{res['stop']:.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with radar_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 RADAR</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    radar_data = deep_radar_engine(SCAN_LIST)
    for item in radar_data:
        st.markdown(f"""
        <div class='scan-item'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:#ffcc00; font-weight:bold;'>{item['s']}</span>
                <span style='color:#00ff88; font-weight:bold;'>%{item['score']}</span>
            </div>
            <p style
