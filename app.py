import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 2. GİRİŞ KONTROLÜ ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
    vk = st.text_input("Giriş Anahtarı", type="password")
    if st.button("SİSTEME BAĞLAN", use_container_width=True):
        if vk.strip().upper().startswith("GAI-") or vk == "HEDEF2026":
            st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 3. DARK MATRIX CSS (Siyah Buton Zırhı) ---
st.set_page_config(page_title="Gürkan AI PRO v147", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Ana Tema */
    .stApp { background: #0b0d11 !important; color: #e1e1e1 !important; }
    
    /* BUTONLARI SİYAHA SABİTLE (BEYAZLAMAYI ENGELLER) */
    div.stButton > button {
        background-color: #161b22 !important;
        color: #ffcc00 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        padding: 2px 10px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #ffcc00 !important;
        background-color: #1c2128 !important;
    }
    
    /* Favori Silme (Özel Kırmızı) */
    button[key*="d_"] { color: #ff4b4b !important; border-color: #442222 !important; }

    /* Cam Kart */
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stat-label { font-size: 9px; color: #8b949e; text-transform: uppercase; }
    .stat-val { font-size: 16px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. BIST AGGRESSIVE ANALİZ MOTORU ---
def get_bist_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 25: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        ch = ((lp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        # Momentum & RSI
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        # Karar Mekanizması
        score = 0
        if lp > ma20: score += 2
        if 40 < rsi < 70: score += 2
        if ch > 0: score += 1
        
        if score >= 4: n, c, s = "Trend ve hacim onayı var. Pozitif seyir beklentisi.", "#00ff88", "GÜÇLÜ"
        elif score >= 2: n, c, s = "Hisse dengeleniyor. Trend desteği üzerinde.", "#ffcc00", "POTANSİYEL"
        else: n, c, s = "Baskı devam ediyor. Destek seviyelerini izle.", "#ff4b4b", "TEMKİNLİ"

        up = round((df['Close'].tail(20).std() * 2.2 / lp) * 100, 1)
        return {"p": lp, "ch": ch, "up": max(up, 1.8), "rsi": rsi, "n": n, "c": c, "s": s, "df": df}
    except: return None

# --- 5. ARAYÜZ TASARIMI ---
st.markdown("<h5 style='color:#ffcc00; text-align:center; margin-bottom:15px;'>★ GÜRKAN AI PRO</h5>", unsafe_allow_html=True)

# Kompakt Arama
_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2, c3 = st.columns([3, 1, 0.4])
    with c1: 
        s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed", placeholder="Hisse...").upper().strip()
    with c2: 
        if st.button("ARA", use_container_width=True): # Analiz Et yazısı "ARA" olarak küçültüldü
            st.session_state["last_sorgu"] = s_inp; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_inp not in st.session_state["favorites"]: st.session_state["favorites"].append(s_inp); st.rerun()

# Paneller
c_f, c_m, c_r = st.columns([0.8, 4, 1.2])

with c_f:
    st.markdown("<p class='stat-label'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([3, 1])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with c_m:
    res = get_bist_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <b style='color:#ffcc00; font-size:13px;'>{st.session_state["last_sorgu"]} ANALİZ</b>
                <span style='background:{res['c']}; color:black; padding:1px 8px; border-radius:4px; font-weight:bold; font-size:10px;'>{res['s']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; margin-top:10px; text-align:center;'>
                <div><p class='stat-label'>FİYAT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>GÜNLÜK</p><p class='stat-val' style='color:{res['c']};'>{res['ch']:+.2f}%</p></div>
                <div><p class='stat-label'>RSI</p><p class='stat-val'>{res['rsi']:.1f}</p></div>
                <div><p class='stat-label'>HEDEF</p><p class='stat-val' style='color:#00ff88;'>+%{res['up']}</p></div>
            </div>
            <p style='font-size:12px; margin-top:10px; border-top:1px solid rgba(255,255,255,0.05); padding-top:8px;'><b>AI:</b> {res['n']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(50).index, open=res['df'].tail(50)['Open'], high=res['df'].tail(50)['High'], low=res['df'].tail(50)['Low'], close=res['df'].tail(50)['Close'])])
        fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with c_r:
    st.markdown("<p class='stat-label'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
