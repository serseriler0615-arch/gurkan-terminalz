import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Terminal", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "AKBNK", "ISCTR"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"

# --- 2. CSS (Maksimum Düzen & Estetik) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; overflow: hidden; }
    header { visibility: hidden; }
    
    /* Arama Çubuğu Tasarımı */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; border-radius: 4px !important;
        font-size: 14px !important; text-align: center;
    }

    /* Kartlar */
    .glass-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 8px;
        padding: 15px; border-top: 3px solid #ffcc00; margin-bottom: 10px;
    }
    
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; }
    .price-main { font-size: 32px; font-weight: bold; color: #fff; line-height: 1; }
    
    /* Favori Butonları */
    div.stButton > button {
        background: #111418 !important; color: #8b949e !important;
        border: 1px solid #1c2128 !important; border-radius: 4px !important;
        font-size: 10px !important; height: 24px !important; width: 100% !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .btn-x { color: #ff4b4b !important; font-weight: bold !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_clean_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        df['MA20'] = df['Close'].rolling(20).mean()
        atr = (df['High']-df['Low']).rolling(14).mean().iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Zeka Katmanı
        prob = min(max(50 + (ch * 4) + (vol_r * 8), 15), 92)
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2.3), "stop": lp-(atr*1.4), "ma": df['MA20'].iloc[-1], "prob": prob}
    except: return None

# --- 4. ARAYÜZ (TEK SAYFA KOKPİT) ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:5px; font-size:16px;'>GÜRKAN AI : STRATEGIC TERMINAL</h3>", unsafe_allow_html=True)

# ÜST KONTROL BAR
c_search, c_fav_list = st.columns([1.5, 3.5])

with c_search:
    sc1, sc2, sc3 = st.columns([2.5, 0.8, 0.8])
    with sc1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with sc2: 
        if st.button("🔍"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with sc3:
        if s_inp in st.session_state["favorites"]:
            if st.button("❌"): st.session_state["favorites"].remove(s_inp); st.rerun()
        else:
            if st.button("⭐"): st.session_state["favorites"].append(s_inp); st.rerun()

with c_fav_list:
    f_cols = st.columns(6)
    for i, f in enumerate(st.session_state["favorites"][:6]):
        with f_cols[i]:
            if st.button(f, key=f"fav_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

# ANA PANEL
res = get_clean_data(st.session_state["last_sorgu"])
if res:
    l_col, m_col, r_col = st.columns([1.2, 3.2, 1.1])
    
    with l_col:
        st.markdown(f"""
        <div class='glass-card'>
            <p class='label-mini'>{st.session_state["last_sorgu"]}</p>
            <p class='price-main'>{res['p']:.2f}</p>
            <p style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:16px; font-weight:bold;'>{res['ch']:+.2f}%</p>
        </div>
        <div class='glass-card' style='border-top-color:#00ff88'>
            <p class='label-mini'>HEDEF</p><p style='font-size:20px; font-weight:bold; color:#00ff88; margin:0;'>{res['target']:.2f}</p>
        </div>
        <div class='glass-card' style='border-top-color:#ff4b4b'>
            <p class='label-mini'>STOP LOSS</p><p style='font-size:20px; font-weight:bold; color:#ff4b4b; margin:0;'>{res['stop']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with m_col:
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d', size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with r_col:
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;'>
            <p class='label-mini'>YARIN OLASILIĞI</p>
            <p style='font-size:32px; font-weight:bold; color:#ffcc00; margin:5px 0;'>%{res['prob']:.0f}</p>
            <p style='font-size:10px; color:#8b949e;'>TREND GÜCÜ ANALİZİ</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p class='label-mini' style='margin-left:5px;'>RADAR</p>", unsafe_allow_html=True)
        for rs, r_t in [("AKBNK", "Pozitif"), ("TUPRS", "Hacimli"), ("EREGL", "Sıkışma")]:
            if st.button(f"{rs} | {r_t}", key=f"rd_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
