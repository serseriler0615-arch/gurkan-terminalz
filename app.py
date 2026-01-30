import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Neon v231", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: 
    st.session_state["favorites"] = ["THYAO", "SASA", "SISE", "ISCTR"]
if "last_sorgu" not in st.session_state: 
    st.session_state["last_sorgu"] = "SASA"

SCAN_LIST = ["THYAO", "SASA", "SISE", "ISCTR", "TUPRS", "AKBNK", "EREGL", "KCHOL", "ASELS", "BIMAS"]

# --- 2. CSS (GOLD & NEON RADAR) ---
st.markdown("""
<style>
    .stApp { background-color: #010203 !important; color: #e1e1e1 !important; }
    .master-card { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 25px; border-left: 8px solid #ffcc00; margin-bottom: 20px; }
    .radar-container { background: #0d1117; border: 1px solid #30363d; border-radius: 15px; padding: 15px; height: 800px; overflow-y: auto; }
    .scan-item { background: #161b22; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; border-left: 4px solid #00ff88; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    
    /* Favori Butonları - ALTIN SARISI */
    div.stButton > button { background: #21262d !important; color: #ffcc00 !important; border: 1px solid #ffcc00 !important; border-radius: 8px; font-weight: bold; }
    div.stButton > button:hover { background: #ffcc00 !important; color: #000 !important; }
    
    /* Radar Git Butonları */
    .radar-container div.stButton > button { height: 30px; font-size: 11px; margin-top: 5px; border: 1px solid #00ff88 !important; color: #00ff88 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def deep_inspector(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = 0
        if lp > ma20: score += 50
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        if vol_r > 1.1: score += 30
        if ch > 0: score += 20
        return {"p": lp, "ch": ch, "score": score, "df": df, "vol": vol_r}
    except: return None

# --- 4. UI ---
m_col, r_col = st.columns([3, 1])

with m_col:
    # Arama ve Favori Ekle/Çıkar
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1: s_inp = st.text_input("HİSSE ARA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        is_fav = s_inp in st.session_state["favorites"]
        if st.button("🌟 ÇIKAR" if is_fav else "⭐ EKLE"):
            if is_fav: st.session_state["favorites"].remove(s_inp)
            else: st.session_state["favorites"].append(s_inp)
            st.rerun()

    # Favori Listesi (Gold Görünüm)
    if st.session_state["favorites"]:
        st.markdown("<p class='label-mini'>FAVORİLERİM (GOLD LİST)</p>", unsafe_allow_html=True)
        f_cols = st.columns(len(st.session_state["favorites"]))
        for i, fv in enumerate(st.session_state["favorites"]):
            if f_cols[i].button(fv, key=f"f_{fv}"):
                st.session_state["last_sorgu"] = fv
                st.rerun()

    # Ana Analiz
    res = deep_inspector(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div><p class='label-mini'>{st.session_state["last_sorgu"]} // CANLI</p><span style='font-size:45px; font-weight:bold;'>{res['p']:.2f}</span><span style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:22px;'> {res['ch']:+.2f}%</span></div>
                <div style='text-align:right;'><p class='label-mini'>GÜVEN SKORU</p><h1 style='color:{"#00ff88" if res['score']>=70 else "#ffcc00"};'>%{res['score']}</h1></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

with r_col:
    st.markdown("<p class='label-mini' style='text-align:center;'>📡 NEON RADAR</p>", unsafe_allow_html=True)
    st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
    for s in SCAN_LIST:
        r_res = deep_inspector(s)
        if r_res and r_res['score'] >= 50:
            st.markdown(f"""
            <div class='scan-item'>
                <div style='display:flex; justify-content:space-between;'><b>{s}</b><span style='color:#00ff88;'>%{r_res['score']}</span></div>
                <p style='font-size:10px; color:#8b949e; margin:0;'>Fiyat: {r_res['p']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"İncele {s}", key=f"r_{s}"):
                st.session_state["last_sorgu"] = s
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
