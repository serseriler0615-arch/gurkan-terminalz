import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="GÜRKAN AI v190", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (Ultra Modern & Akıllı Arayüz) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #e1e1e1 !important; overflow: hidden; }
    header { visibility: hidden; }
    
    /* Arama & Favori Barı */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #30363d !important; font-size: 15px !important; 
        text-align: center; border-radius: 20px !important;
    }
    
    /* Kartlar */
    .intel-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 10px;
        padding: 15px; border-left: 4px solid #ffcc00;
    }
    
    .label-mini { color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold; }
    .price-main { font-size: 38px; font-weight: bold; color: #fff; line-height: 1.1; font-family: 'JetBrains Mono', monospace; }
    
    /* Dinamik Butonlar */
    div.stButton > button { 
        background: #111418 !important; color: #8b949e !important; 
        border: 1px solid #30363d !important; border-radius: 15px !important;
        font-size: 10px !important; height: 26px !important; padding: 0 10px !important;
    }
    div.stButton > button:hover { border-color: #ffcc00 !important; color: #ffcc00 !important; }
    .btn-active { border-color: #ffcc00 !important; color: #ffcc00 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA ANALİZ MOTORU ---
def get_neural_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        # Akıllı İndikatörler
        df['MA20'] = df['Close'].rolling(20).mean()
        df['TR'] = (df['High']-df['Low']).rolling(14).mean()
        atr = df['TR'].iloc[-1]
        vol_r = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
        
        # Yarınki Tahmin Olasılığı (Zeka Ekledik)
        prob = 50 + (ch * 5) + (vol_r * 10)
        prob = min(max(prob, 10), 95) # 10 ile 95 arasına sabitle
        direction = "📈 YARIŞA HAZIR" if prob > 60 else "📉 BASKI ALTINDA" if prob < 40 else "↔ DENGEDE"
        
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2.2), "stop": lp-(atr*1.2), "ma": df['MA20'].iloc[-1], "prob": prob, "dir": direction, "vr": vol_r}
    except: return None

# --- 4. TEK SAYFA DASHBOARD ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; letter-spacing:4px; font-size:16px; margin-bottom:10px;'>GÜRKAN AI : NEURAL COMMAND</h3>", unsafe_allow_html=True)

# ÜST BAR (Arama + Favoriler Tek Satırda)
bar_l, bar_m, bar_r = st.columns([1, 2, 1])
with bar_m:
    c1, c2, c3 = st.columns([3, 0.6, 0.6])
    with c1: 
        s_inp = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol...", label_visibility="collapsed").upper().strip()
    with c2:
        if st.button("🔍 GİT"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if s_inp in st.session_state["favorites"]:
            if st.button("❌"): st.session_state["favorites"].remove(s_inp); st.rerun()
        else:
            if st.button("⭐"): st.session_state["favorites"].append(s_inp); st.rerun()

# FAVORİ LİSTESİ (Hızlı Erişim - Yatay)
st.write("")
fav_count = len(st.session_state["favorites"])
if fav_count > 0:
    cols = st.columns(fav_count + 2)
    for i, f in enumerate(st.session_state["favorites"]):
        with cols[i+1]:
            if st.button(f, key=f"f_btn_{f}"): st.session_state["last_sorgu"] = f; st.rerun()

# ANA ANALİZ BÖLÜMÜ
res = get_neural_data(st.session_state["last_sorgu"])
if res:
    l_col, m_col, r_col = st.columns([1.2, 3, 1])
    
    with l_col:
        st.markdown(f"""
        <div class='intel-card'>
            <p class='label-mini'>{st.session_state["last_sorgu"]} CANLI</p>
            <p class='price-main'>{res['p']:.2f}</p>
            <p style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"}; font-size:16px; font-weight:bold;'>{res['ch']:+.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown(f"<div class='intel-card' style='border-left-color:#00ff88'><p class='label-mini'>TEKNİK HEDEF</p><p style='font-size:18px; font-weight:bold; color:#00ff88; margin:0;'>{res['target']:.2f}</p></div>", unsafe_allow_html=True)
        st.write("")
        st.markdown(f"<div class='intel-card' style='border-left-color:#ff4b4b'><p class='label-mini'>STOP LOSS</p><p style='font-size:18px; font-weight:bold; color:#ff4b4b; margin:0;'>{res['stop']:.2f}</p></div>", unsafe_allow_html=True)

    with m_col:
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22', tickfont=dict(color='#4b525d', size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with r_col:
        st.markdown(f"""
        <div class='intel-card' style='border-left-color: #ffcc00; text-align:center;'>
            <p class='label-mini'>YARININ OLASILIĞI</p>
            <p style='font-size:24px; font-weight:bold; color:#ffcc00; margin:5px 0;'>%{res['prob']:.0f}</p>
            <p style='font-size:11px; font-weight:bold; color:#fff;'>{res['dir']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown("<p class='label-mini'>SİNYAL RADARI</p>", unsafe_allow_html=True)
        for rs, r_t in [("TUPRS", "Hacimli"), ("AKBNK", "Pozitif"), ("EREGL", "Direnç")]:
            st.markdown(f"""
            <div style='background:#111418; padding:8px; border-radius:6px; border:1px solid #1c2128; margin-bottom:5px; display:flex; justify-content:space-between;'>
                <span style='font-size:11px; font-weight:bold;'>{rs}</span>
                <span style='font-size:10px; color:#ffcc00;'>{r_t}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Gözlem {rs}", key=f"rd_{rs}"): st.session_state["last_sorgu"] = rs; st.rerun()
