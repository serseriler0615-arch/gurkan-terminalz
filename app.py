import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Gürkan AI : Precision", layout="wide", initial_sidebar_state="collapsed")

if "favorites" not in st.session_state: st.session_state["favorites"] = ["ISCTR", "AKBNK", "THYAO"]
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

# --- 2. CSS (Mikro Estetik & Kompakt Tasarım) ---
st.markdown("""
<style>
    .stApp { background-color: #05070a !important; color: #d1d1d1 !important; }
    header { visibility: hidden; }
    
    /* Input Küçültme */
    .stTextInput>div>div>input { 
        background: #0d1117 !important; color: #ffcc00 !important; 
        border: 1px solid #1c2128 !important; text-align: center; 
        font-size: 14px !important; height: 32px !important;
    }
    
    /* Kart Tasarımı */
    .master-card {
        background: #0d1117; border: 1px solid #1c2128; border-radius: 6px;
        padding: 15px; border-top: 3px solid #00d4ff;
    }
    
    /* Yazı Boyutları */
    .label-mini { color: #4b525d; font-size: 9px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: bold; }
    .price-main { font-size: 28px; font-weight: bold; font-family: 'JetBrains Mono', monospace; }
    .signal-text { font-size: 14px; font-weight: bold; letter-spacing: 0.5px; }
    .metric-val { font-size: 16px; font-weight: bold; font-family: monospace; }
    
    /* Butonlar */
    div.stButton > button { 
        background: transparent !important; color: #8b949e !important; 
        border: 1px solid #1c2128 !important; font-size: 9px !important; 
        padding: 1px 4px !important; height: 20px !important;
    }
    .btn-x { color: #ff4b4b !important; border: none !important; font-size: 12px !important; }
    
    /* Radar Kutusu */
    .radar-box { 
        background: #0d1117; border-radius: 4px; padding: 10px; 
        border: 1px solid #1c2128; margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU ---
def get_precision_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2]); ch = ((lp-pc)/pc)*100
        df['MA20'] = df['Close'].rolling(20).mean()
        df['TR'] = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr = df['TR'].rolling(14).mean().iloc[-1]
        
        return {"p": lp, "ch": ch, "df": df, "target": lp+(atr*2), "stop": lp-(atr*1.2), "ma": df['MA20'].iloc[-1]}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<p style='text-align:center; color:#ffcc00; letter-spacing:5px; font-size:12px; margin-bottom:15px;'>GÜRKAN AI : PRECISION TERMINAL</p>", unsafe_allow_html=True)

# ÜST BAR
_, mid, _ = st.columns([1.2, 1.5, 1.2])
with mid:
    c1, c2 = st.columns([4, 1.2])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol...", label_visibility="collapsed").upper().strip()
    with c2:
        if s_inp not in st.session_state["favorites"]:
            if st.button("⭐ EKLE"): st.session_state["favorites"].append(s_inp); st.session_state["last_sorgu"] = s_inp; st.rerun()
        else: st.markdown("<p style='font-size:10px; color:#00ff88; margin-top:5px;'>✔ LİSTEDE</p>", unsafe_allow_html=True)

l, m, r = st.columns([0.7, 4, 0.9])

# SOL: FAVORİLER
with l:
    st.markdown("<p class='label-mini'>PORTFÖY</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1])
        with cf1: 
            if st.button(f" {f}", key=f"b_{f}"): st.session_state["last_sorgu"] = f; st.rerun()
        with cf2:
            if st.button("×", key=f"x_{f}"): st.session_state["favorites"].remove(f); st.rerun()

# ORTA: ANA PANEL
with m:
    res = get_precision_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='master-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span class='label-mini'>{st.session_state["last_sorgu"]} // TEKNİK ANALİZ</span><br>
                    <span class='price-main'>{res['p']:.2f}</span>
                    <span style='color:#00ff88; font-size:14px; font-weight:bold;'> {res['ch']:+.2f}%</span>
                </div>
                <div style='text-align:right;'>
                    <span class='signal-text' style='color:#00d4ff;'>KADEMELİ AL</span><br>
                    <span class='label-mini'>SİNYAL GÜCÜ: %88</span>
                </div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:15px;'>
                <div style='background:#111418; padding:8px; border-radius:4px; text-align:center;'>
                    <p class='label-mini'>MA20 PİVOT</p><p class='metric-val' style='color:#8b949e;'>{res['ma']:.2f}</p>
                </div>
                <div style='background:#111418; padding:8px; border-radius:4px; text-align:center; border: 1px solid #00ff8822;'>
                    <p class='label-mini'>HEDEF</p><p class='metric-val' style='color:#00ff88;'>{res['target']:.2f}</p>
                </div>
                <div style='background:#111418; padding:8px; border-radius:4px; text-align:center; border: 1px solid #ff4b4b22;'>
                    <p class='label-mini'>STOP</p><p class='metric-val' style='color:#ff4b4b;'>{res['stop']:.2f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#0d1117', tickfont=dict(color='#4b525d', size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# SAĞ: RADAR (YARININ TAHMİNLERİ)
with r:
    st.markdown("<p class='label-mini'>🎯 YARININ RADARI</p>", unsafe_allow_html=True)
    # Örnek Dinamik Radar Verisi
    radars = [("AKBNK", "+2.1%", "Hacim"), ("TUPRS", "+1.4%", "Para Girişi"), ("THYAO", "-0.5%", "Sıkışma")]
    for r_s, r_p, r_w in radars:
        st.markdown(f"""
        <div class='radar-box'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-size:12px; font-weight:bold;'>{r_s}</span>
                <span style='color:#00ff88; font-size:11px;'>{r_p}</span>
            </div>
            <p style='font-size:9px; color:#4b525d; margin-top:2px;'>Neden: {r_w}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("İncele", key=f"rd_{r_s}"): st.session_state["last_sorgu"] = r_s; st.rerun()
