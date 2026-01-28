import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    vk = st.text_input("Giriş Anahtarı", type="password")
    if st.button("SİSTEME GİR"):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. EXECUTIVE UI CSS ---
st.set_page_config(page_title="Gürkan AI v165", layout="wide")
st.markdown("""
<style>
    .stApp { background: #0a0c10 !important; color: #e1e1e1 !important; }
    /* Ana Kart Tasarımı */
    .exec-card {
        background: #0d1117; border: 1px solid #30363d; border-radius: 15px;
        padding: 25px; margin-bottom: 15px; border-top: 4px solid #ffcc00;
    }
    .price-big { font-size: 48px; font-weight: bold; margin: 0; color: #fff; }
    .label-mini { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; }
    .status-badge { padding: 5px 15px; border-radius: 50px; font-weight: bold; font-size: 14px; }
    
    /* Butonlar */
    div.stButton > button {
        background: #161b22 !important; color: #ffcc00 !important;
        border: 1px solid #30363d !important; border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ZEKA MOTORU ---
def get_exec_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1]); pc = float(df['Close'].iloc[-2])
        ch = ((lp - pc) / pc) * 100
        
        # Kesinlik & Tahmin Araştırması
        rets = df['Close'].pct_change().dropna()
        vol = rets.tail(30).std()
        plus = (rets.tail(20).mean() + (vol * 2)) * 100
        minus = (rets.tail(20).mean() - (vol * 2)) * 100
        
        # Karar
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        decision = "POZİTİF" if lp > ma20 else "NEGATİF"
        clr = "#00ff88" if decision == "POZİTİF" else "#ff4b4b"
        
        return {"p": lp, "ch": ch, "plus": plus, "minus": minus, "dec": decision, "clr": clr, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI</h2>", unsafe_allow_html=True)

# Üst Kontrol
_, mid, _ = st.columns([1, 2, 1])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("SORGULA"): st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"):
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

col_left, col_main, col_right = st.columns([0.8, 4, 0.8])

with col_left:
    st.markdown("<p class='label-mini'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with col_main:
    res = get_exec_data(st.session_state["last_sorgu"])
    if res:
        # TEK VE NET KARAR KARTI
        st.markdown(f"""
        <div class='exec-card'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <p class='label-mini'>{st.session_state["last_sorgu"]} ANLIK DURUM</p>
                    <p class='price-big'>{res['p']:.2f}</p>
                    <p style='color:{res['clr']}; font-weight:bold; font-size:20px;'>{res['ch']:+.2f}%</p>
                </div>
                <div style='text-align:right;'>
                    <span class='status-badge' style='border: 1px solid {res['clr']}; color:{res['clr']};'>BEKLENTİ: {res['dec']}</span>
                    <div style='margin-top:20px;'>
                        <p class='label-mini'>GÜNLÜK HEDEF ALANI</p>
                        <p style='color:#00ff88; font-weight:bold; font-size:18px;'>+%{res['plus']:.2f}</p>
                        <p style='color:#ff4b4b; font-weight:bold; font-size:18px;'>-%{abs(res['minus']):.2f}</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # GRAFİK
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.markdown("<p class='label-mini'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
