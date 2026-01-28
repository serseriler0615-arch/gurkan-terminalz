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

# --- 3. TASARIM VE RENK SABİTLEME ---
st.set_page_config(page_title="Gürkan AI PRO v145", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp { background: #0b0d11 !important; color: #e1e1e1 !important; }
    div.stButton > button { background-color: #161b22 !important; color: #ffcc00 !important; border: 1px solid #30363d !important; border-radius: 8px !important; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 12px; margin-bottom: 10px; }
    .stat-val { font-size: 18px; font-weight: bold; color: #ffffff; }
    .stat-label { font-size: 10px; color: #8b949e; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 4. DEEP-HUNTER ANALİZ MOTORU ---
def get_deep_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        prev_p = float(df['Close'].iloc[-2])
        change = ((last_p - prev_p) / prev_p) * 100
        
        ma20 = df['Close'].rolling(20).mean(); std20 = df['Close'].rolling(20).std()
        up_pot = round((( (ma20 + (std20*2)).iloc[-1] - last_p) / last_p) * 100, 1)
        down_risk = round(((last_p - (ma20 - (std20*2)).iloc[-1]) / last_p) * 100, 1)
        
        delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # Hacim Analizi
        avg_vol = df['Volume'].tail(10).mean()
        last_vol = df['Volume'].iloc[-1]
        vol_power = "GÜÇLÜ" if last_vol > avg_vol else "ZAYIF"
        
        # Gürkan AI Analizci Notu
        score = 0
        if change > 0: score += 1
        if rsi < 40: score += 2
        if last_p > ma20.iloc[-1]: score += 1
        if vol_power == "GÜÇLÜ": score += 1

        if score >= 4: note, clr = f"Hissede para girişi çok belirgin. RSI {rsi:.1f} seviyesinde alıcıları iştahlandırıyor. Teknik görünüm 'Ateş Ediyor'.", "#00ff88"
        elif score >= 2: note, clr = f"Trend dengeli. {vol_power} hacimle yatay-pozitif bir seyir var. RSI {rsi:.1f} ile güvenli bölgede.", "#ffcc00"
        else: note, clr = f"Dikkat patron! Teknikte yorulma var. RSI {rsi:.1f} seviyesinde. Destekleri takip edip nakitte beklemek mantıklı olabilir.", "#ff4b4b"

        return {"p": last_p, "ch": change, "up": max(up_pot, 1.0), "down": down_risk, "rsi": rsi, "vol": vol_power, "note": note, "color": clr, "df": df}
    except: return None

# --- 5. ARAYÜZ ---
st.markdown("<h4 style='color:#ffcc00; text-align:center;'>★ GÜRKAN AI PRO v145</h4>", unsafe_allow_html=True)

# Arama
_, sc_mid, _ = st.columns([1.5, 2, 1.5])
with sc_mid:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: s_input = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ANALİZ ET", use_container_width=True): st.session_state["last_sorgu"] = s_input; st.rerun()
    with c3:
        if st.button("➕"): 
            if s_input not in st.session_state["favorites"]: st.session_state["favorites"].append(s_input); st.rerun()

# Paneller
c_fav, c_main, c_radar = st.columns([0.8, 4, 1.2])

with c_fav:
    st.markdown("<p class='stat-label'>LİSTEM</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        cf1, cf2 = st.columns([4, 1.5])
        with cf1:
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with cf2:
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with c_main:
    res = get_deep_analysis(st.session_state["last_sorgu"])
    if res:
        # Üst Bilgi Kartı (Şu anki Oranlar)
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                <b style='color:#ffcc00;'>🤵 GÜRKAN AI DERİN ANALİZ: {st.session_state["last_sorgu"]}</b>
                <span style='background:{res['color']}; color:black; padding:2px 10px; border-radius:5px; font-weight:bold; font-size:10px;'>SKOR: {res['vol']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; text-align:center;'>
                <div><p class='stat-label'>ANLIK FİYAT</p><p class='stat-val'>{res['p']:.2f}</p></div>
                <div><p class='stat-label'>GÜNLÜK FARK</p><p class='stat-val' style='color:{"#00ff88" if res['ch']>0 else "#ff4b4b"};'>{res['ch']:+.2f}%</p></div>
                <div><p class='stat-label'>RSI GÜCÜ</p><p class='stat-val'>{res['rsi']:.1f}</p></div>
                <div><p class='stat-label'>HACİM</p><p class='stat-val'>{res['vol']}</p></div>
            </div>
            <div style='margin-top:15px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.1);'>
                <p style='font-size:13px; color:#cfcfcf; line-height:1.4;'><b>AI NOTU:</b> {res['note']}</p>
            </div>
            <div style='display:flex; justify-content:space-around; margin-top:10px; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;'>
                <div><p class='stat-label' style='color:#00ff88;'>GÜVENLİ HEDEF</p><p class='stat-val' style='color:#00ff88;'>+ %{res['up']}</p></div>
                <div><p class='stat-label' style='color:#ff4b4b;'>RİSK SINIRI</p><p class='stat-val' style='color:#ff4b4b;'>- %{res['down']}</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with c_radar:
    st.markdown("<p class='stat-label'>RADAR (TAKİP)</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
