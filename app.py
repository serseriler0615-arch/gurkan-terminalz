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
    tab1, tab2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    with tab1:
        vk = st.text_input("Giriş Anahtarı", type="password", key="vk")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vk.strip().upper().startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
    with tab2:
        u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
        if st.button("ADMİN YETKİSİ AL", use_container_width=True):
            if u.strip().upper() == "GURKAN" and p.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 3. TASARIM VE RENK SABİTLEME (CSS) ---
st.set_page_config(page_title="Gürkan AI PRO v144", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background: #0b0d11 !important; color: #e1e1e1 !important; }
    
    /* Butonları Karartma ve Neonlaştırma */
    div.stButton > button {
        background-color: #161b22 !important;
        color: #ffcc00 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #ffcc00 !important;
        box-shadow: 0 0 10px rgba(255, 204, 0, 0.2);
    }
    
    /* Favori Silme Butonu Özel (Kırmızı) */
    button[key*="d_"] { color: #ff4b4b !important; }

    /* Cam Kart Tasarımı */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. ANALİZ MOTORU ---
def get_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std20 = df['Close'].rolling(20).std()
        up_pot = round((( (ma20 + (std20*2)).iloc[-1] - last_p) / last_p) * 100, 1)
        down_risk = round(((last_p - (ma20 - (std20*2)).iloc[-1]) / last_p) * 100, 1)
        
        delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        if rsi > 70: note, clr = "Hissede şişme var, kar realizasyonu beklenebilir.", "#ff4b4b"
        elif rsi < 35: note, clr = "Dip seviyeler. AI alım fırsatı olarak görüyor.", "#00ff88"
        else: note, clr = "Trend dengeli. Akıllı para hareketlerini izliyoruz.", "#ffcc00"

        return {"p": last_p, "up": max(up_pot, 1.0), "down": down_risk, "rsi": rsi, "note": note, "color": clr, "df": df}
    except: return None

# --- 5. ARAYÜZ ---
st.markdown("<h4 style='color:#ffcc00; text-align:center;'>★ GÜRKAN AI PRO v144</h4>", unsafe_allow_html=True)

# Merkezi Arama
_, sc_mid, _ = st.columns([1.5, 2, 1.5])
with sc_mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_input = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ARA", use_container_width=True): st.session_state["last_sorgu"] = s_input; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_input not in st.session_state["favorites"]: st.session_state["favorites"].append(s_input); st.rerun()

# Paneller
c_fav, c_main, c_radar = st.columns([0.8, 4, 1.2])

with c_fav:
    st.markdown("<p style='font-size:11px; color:#8b949e; font-weight:bold;'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1.5])
        with cf1:
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with cf2:
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with c_main:
    res = get_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                <b style='color:#ffcc00; font-size:14px;'>🤵 GÜRKAN AI PRO YORUMU</b>
                <span style='color:{res['color']}; font-size:12px; font-weight:bold;'>{st.session_state["last_sorgu"]}</span>
            </div>
            <p style='font-size:13px; color:#cfcfcf;'>{res['note']}</p>
            <div style='display:flex; justify-content:space-around; margin-top:10px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;'>
                <div style='text-align:center;'><small style='color:#8b949e;'>FİYAT</small><br><b>{res['p']:.2f}</b></div>
                <div style='text-align:center;'><small style='color:#8b949e;'>HEDEF</small><br><b style='color:#00ff88;'>+ %{res['up']}</b></div>
                <div style='text-align:center;'><small style='color:#8b949e;'>RİSK</small><br><b style='color:#ff4b4b;'>- %{res['down']}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with c_radar:
    st.markdown("<p style='font-size:11px; color:#8b949e; font-weight:bold;'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
