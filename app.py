import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Deep Validation", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "ISCTR", "EREGL", "TUPRS", "ASTOR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "THYAO"

SCAN_LIST = ["THYAO", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SAHOL", "SISE", "KCHOL", "ASELS", "BIMAS", "ASTOR", "SASA", "PGSUS", "YKBNK", "DOHOL", "KOZAL", "PETKM", "ARCLK"]

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    header { visibility: hidden; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 25px; border-top: 5px solid #ffcc00; margin-bottom: 20px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 15px; height: 850px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    .scan-item.gold { border-left: 5px solid #ffcc00; background: rgba(255, 204, 0, 0.08); }
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 12px; font-weight: bold; font-size: 11px; height: 35px; width: 100%; }
    .stTextInput>div>div>input { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; text-align: center; border-radius: 10px !important; }
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
    .price-main { font-size: 45px; font-weight: bold; font-family: 'JetBrains Mono'; color: #fff; }
    @media (max-width: 1000px) { .radar-container { height: auto; max-height: 400px; margin-top: 20px; } }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORLARI ---
@st.cache_data(ttl=300)
def deep_radar_engine(symbols):
    results = []
    for s in symbols:
        try:
            df = yf.download(s + ".IS", period="60d", interval="1d", progress=False)
            if len(df) < 30: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            cp = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean()
            std_dev = df['Close'].rolling(20).std().iloc[-1]
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = (100 - (100 / (1 + gain/loss))).iloc[-1]
            
            vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            
            score = 0
            warn = ""
            if cp > ma20.iloc[-1]: score += 30
            if vol_r > 1.2: score += 30
            if 45 < rsi < 65: score += 30
            elif rsi > 70: score += 10; warn = "AŞIRI ALIM"
            
            if score >= 50:
                results.append({"s": s, "p": cp, "score": score, "rsi": rsi, "vol": vol_r, "warn": warn})
        except: continue
    return sorted(results, key=lambda x: x['score'], reverse=True)

def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]; atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi_val = (100 - (100 / (1 + g/l))).iloc[-1]
        
        return {"p": lp, "ch": ch, "df": df, "ma": ma20, "target": lp+(atr*2.7), "stop": min(lp-(atr*2.3), ma20*0.95), "vol": df['Volume'].iloc[-1]/df['Volume'].rolling(10).mean().iloc[-1], "rsi": rsi_val}
    except: return None

# --- 4. LAYOUT ---
main_col, radar_col = st.columns([3.2, 1])

with main_col:
    # Arama
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("⭐"):
            if s_inp in st.session_state["favorites"]: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favoriler
    if st.session_state["favorites"]:
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, fav in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(fav): st.session_state["last_sorgu"] = fav; st.rerun()

    res = get_analysis(st.session_state["last_sorgu"])
    if res:
        change_color = "#00ff88" if res['ch'] > 0 else "#ff4b4b"
        card = """
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div>
                    <p class='label-mini'>SYM // CORE</p>
                    <span class='price-main'>PRICE</span>
                    <span style='color:C_COLOR; font-size:20px; font-weight:bold;'> CHG%</span>
                </div>
                <div style='text-align:right;'>
                    <p class='label-mini'>RSI MOMENTUM</p>
                    <span style='color:#ffcc00; font-size:22px; font-weight:bold;'>RSI_V</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:20px;'>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center;'>
                    <p class='label-mini'>PİVOT</p><p style='font-size:18px; font-weight:bold;'>PIV_V</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center; border-bottom:3px solid #00ff88;'>
                    <p class='label-mini'>HEDEF</p><p style='font-size:18px; font-weight:bold; color:#00ff88;'>TGT_V</p>
                </div>
                <div style='background:#161b22; padding:15px; border-radius:12px; text-align:center; border-bottom:3px solid #ff4b4b;'>
                    <p class='label-mini'>STOP</p><p style='font-size:18px; font-weight:bold; color:#ff4b4b;'>STP_V</p>
                </div>
            </div>
        </div>
        """.replace("SYM", st.session_state["last_sorgu"]).replace("PRICE", f"{res['p']:.2f}").replace("CHG", f"{res['ch']:+.2f}")\
           .replace("C_COLOR", change_color).replace("RSI_V", f"{res['rsi']:.1f}").replace("PIV_V", f"{res['ma']:.2f}")\
           .replace("TGT_V", f"{res['target']:.2f}").replace("STP_V", f"{res['stop']:.2f}")
        
        st.markdown(card, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with radar_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 GÜVENLİ RADAR</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    radar_data = deep_radar_engine(SCAN_LIST)
    for item in radar_data:
        cls = "gold" if item['score'] >= 90 else ""
        item_html = """
        <div class='scan-item CLS'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:#ffcc00; font-weight:bold;'>S_NAME</span>
                <span style='color:#00ff88; font-weight:bold;'>%S_SCORE</span>
            </div>
            <p style='font-size:11px; margin:5px 0; color:#8b949e;'>RSI: S_RSI | Vol: S_VOLx</p>
            <p style='font-size:10px; color:#ff4b4b; font-weight:bold;'>S_WARN</p>
        </div>
        """.replace("CLS", cls).replace("S_NAME", item['s']).replace("S_SCORE", str(item['score']))\
           .replace("S_RSI", f"{item['rsi']:.1f}").replace("S_VOL", f"{item['vol']:.1f}").replace("S_WARN", item['warn'])
        
        st.markdown(item_html, unsafe_allow_html=True)
        if st.button(f"GİT: {item['s']}", key=f"rdr_{item['s']}"):
            st.session_state["last_sorgu"] = item['s']; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
