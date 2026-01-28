import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM & GÜVENLİK ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI ULTRA", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#ffcc00; font-family:monospace;'>🧠 NEURAL PREDATOR v152</h2>", unsafe_allow_html=True)
    vk = st.text_input("Giriş Anahtarı", type="password", placeholder="Neural Key...")
    if st.button("SİSTEMİ UYANDIR", use_container_width=True):
        if vk.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 2. ULTRA-DARK CSS ---
st.set_page_config(page_title="Gürkan AI ULTRA", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #030406 !important; color: #e1e1e1 !important; }
    div.stButton > button { background: #0d1117 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 4px !important; font-family: monospace; }
    .intelligence-card { background: linear-gradient(180deg, #0d1117 0%, #030406 100%); border-left: 3px solid #ffcc00; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px; }
    .predator-label { font-size: 10px; color: #8b949e; letter-spacing: 2px; }
    .predator-val { font-size: 22px; font-weight: bold; color: #ffffff; text-shadow: 0 0 10px rgba(255,204,0,0.3); }
</style>
""", unsafe_allow_html=True)

# --- 3. NEURAL ANALİZ MOTORU ---
def get_neural_logic(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        lp = float(df['Close'].iloc[-1])
        # Volatilite Bazlı Tahmin (3 Günlük Hareket Alanı)
        std_dev = df['Close'].tail(20).std()
        pred_high = round(lp + (std_dev * 1.618), 2)
        pred_low = round(lp - (std_dev * 1.618), 2)
        
        # Zeka Skoru Hesaplama
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        delta = df['Close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g.iloc[-1] / l.iloc[-1])))
        
        intelligence_score = 0
        if lp > ma20: intelligence_score += 40
        if 45 < rsi < 65: intelligence_score += 40
        if df['Volume'].iloc[-1] > df['Volume'].tail(10).mean(): intelligence_score += 20
        
        # Predator Yorumu
        if intelligence_score > 80: n = "AV BAŞLADI: Tüm metrikler yukarıyı gösteriyor. Sistemsel hata payı %5."
        elif intelligence_score > 50: n = "İZ SÜRME: Trend stabil, ancak hacim onayı beklemek akıllıca olur."
        else: n = "PUSU: Piyasa zayıf. Avcı yerinden kıpırdamaz, beklemede kal."

        return {"p": lp, "high": pred_high, "low": pred_low, "score": intelligence_score, "rsi": rsi, "n": n, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='text-align:center; color:#ffcc00; font-family:monospace;'>🤵 GÜRKAN AI : NEURAL PREDATOR</h3>", unsafe_allow_html=True)

_, mid, _ = st.columns([1.5, 2, 1.5])
with mid:
    c1, c2 = st.columns([4, 1.2])
    with c1: s_inp = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed", placeholder="Sistem Taraması...").upper().strip()
    with c2: 
        if st.button("TARAMA"): st.session_state["last_sorgu"] = s_inp; st.rerun()

res = get_neural_logic(st.session_state["last_sorgu"])
if res:
    # Aşırı Zeki Analiz Paneli
    st.markdown(f"""
    <div class='intelligence-card'>
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;'>
            <span style='font-family:monospace; color:#8b949e;'>NEURAL SCAN: {st.session_state["last_sorgu"]}</span>
            <span style='color:#ffcc00; font-weight:bold; letter-spacing:2px;'>ZEKÂ SKORU: %{res['score']}</span>
        </div>
        <div style='display:flex; justify-content:space-around; text-align:center;'>
            <div><p class='predator-label'>FİYAT</p><p class='predator-val'>{res['p']:.2f}</p></div>
            <div><p class='predator-label'>3G TAHMİN (ÜST)</p><p class='predator-val' style='color:#00ff88;'>{res['high']}</p></div>
            <div><p class='predator-label'>3G TAHMİN (ALT)</p><p class='predator-val' style='color:#ff4b4b;'>{res['low']}</p></div>
            <div><p class='predator-label'>RSI GÜCÜ</p><p class='predator-val'>{res['rsi']:.1f}</p></div>
        </div>
        <div style='margin-top:20px; padding:10px; background:rgba(255,204,0,0.05); border-radius:5px;'>
            <p style='margin:0; font-family:monospace; font-size:14px; color:#ffcc00;'><b>PREDATOR NOTU:</b> {res['n']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Strateji Blokları (Al/Sat/Bekle Tek Seferde)
    st.columns(1) # Boşluk
    c_al, c_sat = st.columns(2)
    with c_al:
        st.markdown(f"<div style='border:1px solid #30363d; padding:10px; border-radius:5px;'><b>🟢 GİRİŞ STRATEJİSİ:</b><br><small>Limit: {res['low']} | Kademeli: {res['p']}</small></div>", unsafe_allow_html=True)
    with c_sat:
        st.markdown(f"<div style='border:1px solid #30363d; padding:10px; border-radius:5px;'><b>🔴 ÇIKIŞ STRATEJİSİ:</b><br><small>Hedef 1: {res['high']} | Stop: {res['low']}</small></div>", unsafe_allow_html=True)

    # Grafik
    fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("<p style='text-align:center; font-size:10px; color:#333;'>Gürkan AI - Neural Predator Mode Active</p>", unsafe_allow_html=True)
