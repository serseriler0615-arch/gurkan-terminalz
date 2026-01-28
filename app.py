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
    t1, t2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    with t1:
        vip_k = st.text_input("Giriş Anahtarı", type="password", key="v_key")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vip_k.strip().upper().startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
    with t2:
        u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
        if st.button("ADMİN YETKİSİ AL", use_container_width=True):
            if u.strip().upper() == "GURKAN" and p.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 3. DERİN ARAŞTIRMACI ZEKA MOTORU ---
def get_gurkan_ai_logic(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        
        # RSI & Momentum
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # Hacim Analizi
        vol_avg = df['Volume'].tail(10).mean()
        last_vol = df['Volume'].iloc[-1]
        vol_spike = last_vol > vol_avg * 1.5
        
        # Gürkan AI Stratejik Karar
        score = 0
        if last_p > ma20: score += 1
        if last_p > ma50: score += 1
        if rsi < 40: score += 2  # Aşırı satış fırsatı
        if rsi > 70: score -= 2  # Aşırı alım riski
        if vol_spike and last_p > df['Open'].iloc[-1]: score += 1 # Hacimli yükseliş
        
        if score >= 3: strat, color, note = "GÜÇLÜ AL", "#00ff88", "Hacim ve trend destekli, para girişi belirgin."
        elif score >= 1: strat, color, note = "POZİTİF", "#aaffaa", "Trend yönü yukarı, riskler yönetilebilir."
        elif score >= -1: strat, color, note = "BEKLE-GÖR", "#ffcc00", "Piyasa kararsız, hacim zayıf. Destek takibi."
        else: strat, color, note = "RİSKLİ/SAT", "#ff4b4b", "Teknik bozulma var, nakit korumak mantıklı."

        # Akıllı Hedefler
        atr = (df['High'] - df['Low']).tail(14).mean()
        up = round((atr * 2.8 / last_p) * 100, 1)
        down = round((atr * 2.1 / last_p) * 100, 1)

        return {"p": last_p, "rsi": rsi, "up": up, "down": down, "strat": strat, "color": color, "note": note, "df": df, "ch": ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100}
    except: return None

# --- 4. ARAYÜZ ---
st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    .stApp { background-color: #0b0d11 !important; }
    .gurkan-card { background: #161b22; border: 1px solid #30363d; padding: 10px 15px; border-radius: 10px; border-left: 4px solid #ffcc00; margin-bottom: 10px; }
    .neon-g { color: #00ff88; font-weight: bold; font-size: 18px !important; }
    .neon-r { color: #ff4b4b; font-weight: bold; font-size: 18px !important; }
    .strat-badge { padding: 2px 8px; border-radius: 4px; font-weight: bold; color: black; font-size: 10px; }
    p { font-size: 12px !important; margin-bottom: 2px !important; }
</style>""", unsafe_allow_html=True)

# Arama (Ortalanmış)
_, sc_center, _ = st.columns([1.5, 2, 1.5])
with sc_center:
    c1, c2, c3 = st.columns([3, 1, 0.5])
    with c1: 
        s_input = st.text_input("", value=st.session_state["last_sorgu"], key="new_s", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍 ARA", use_container_width=True): st.session_state["last_sorgu"] = s_input; st.rerun()
    with c3: 
        if st.button("➕"): 
            if s_input not in st.session_state["favorites"]: st.session_state["favorites"].append(s_input); st.rerun()

c_fav, c_main, c_radar = st.columns([0.7, 4.3, 1])

with c_fav:
    st.markdown("<p style='font-weight:bold; color:#8b949e;'>LİSTE</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        f1, f2 = st.columns([4, 1])
        with f1: 
            if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
        with f2: 
            if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

with c_main:
    res = get_gurkan_ai_logic(st.session_state["last_sorgu"])
    if res:
        # Metrikler
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("FİYAT", f"{res['p']:.2f}")
        m2.metric("GÜNLÜK", f"%{res['ch']:+.2f}")
        m3.metric("RSI (14)", f"{res['rsi']:.1f}")
        m4.metric("VOL.", "HACİMLİ" if res['up'] > 4 else "NORMAL")

        # Kompakt Strateji Kutusu
        st.markdown(f"""
        <div class='gurkan-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#ffcc00; font-weight:bold;'>🤵 GÜRKAN AI PRO-ZEKA</span>
                <span class='strat-badge' style='background:{res['color']};'>{res['strat']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; margin: 8px 0;'>
                <div style='text-align:center;'> <span style='color:#8b949e; font-size:9px;'>🚀 HEDEF</span><br><span class='neon-g'>+ %{res['up']}</span> </div>
                <div style='text-align:center; border-left: 1px solid #333; padding-left:15px;'> <span style='color:#8b949e; font-size:9px;'>⚠️ RİSK</span><br><span class='neon-r'>- %{res['down']}</span> </div>
                <div style='text-align:center; border-left: 1px solid #333; padding-left:15px;'> <span style='color:#8b949e; font-size:9px;'>🧠 AI NOTU</span><br><span style='font-size:11px;'>{res['note']}</span> </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with c_radar:
    st.markdown("<p style='font-weight:bold; color:#8b949e;'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
