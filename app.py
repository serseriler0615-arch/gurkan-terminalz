import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 2. GİRİŞ (HIZLI GEÇİŞ) ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    u, p = st.sidebar.text_input("Admin ID"), st.sidebar.text_input("Şifre", type="password")
    if st.sidebar.button("GİRİŞ"):
        if u.strip().upper() == "GURKAN" and p.strip().upper() == "HEDEF2026":
            st.session_state["access_granted"] = True; st.rerun()
    st.info("Lütfen Admin Girişi Yapın.")
    st.stop()

# --- 3. ANALİZ MOTORU (BIST ÖZEL AYARLI) ---
def get_bist_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        
        # RSI Momentum
        delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # Hacim Kontrolü (Son 5 güne göre)
        avg_vol = df['Volume'].tail(10).mean()
        curr_vol = df['Volume'].iloc[-1]
        vol_status = "AKARLI" if curr_vol > avg_vol * 0.8 else "DURGUN"
        
        # --- ZEKA MANTIĞI (BIST MODU) ---
        score = 0
        if last_p > ma20: score += 2  # Trend üstü
        if rsi > 45 and rsi < 70: score += 2  # Sağlıklı alım bölgesi
        if change > 0: score += 1  # Günlük momentum
        if curr_vol > avg_vol: score += 1 # Hacim desteği

        if score >= 4: 
            note, clr, status = "Trend güçlü, para girişi iştahlı. Pozisyon korunabilir.", "#00ff88", "GÜÇLÜ"
        elif score >= 2: 
            note, clr, status = "Hisse dinleniyor, trend bozulmadı. Güç toplama evresi.", "#ffcc00", "POTANSİYEL"
        else: 
            note, clr, status = "Baskı var. 20 günlük ortalamanın altında, dikkatli izlenmeli.", "#ff4b4b", "ZAYIF"

        # Hedef Hesaplama (BIST Volatilitesine Uygun)
        std = df['Close'].tail(20).std()
        up = round((std * 2.5 / last_p) * 100, 1)
        down = round((std * 1.8 / last_p) * 100, 1)

        return {"p": last_p, "ch": change, "up": max(up, 2.0), "down": down, "rsi": rsi, "vol": vol_status, "note": note, "color": clr, "stat": status, "df": df}
    except: return None

# --- 4. ARAYÜZ ---
st.set_page_config(page_title="Gürkan AI PRO v146", layout="wide")
st.markdown("""<style>
    .stApp { background: #0b0d11 !important; color: white; }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 12px; margin-bottom: 15px; }
</style>""", unsafe_allow_html=True)

# Arama Paneli
st.markdown("<h3 style='color:#ffcc00; text-align:center;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 2, 1])
with mid:
    s_inp = st.text_input("Hisse Kodu (Örn: THYAO)", value=st.session_state["last_sorgu"]).upper().strip()
    if st.button("ANALİZ ET", use_container_width=True):
        st.session_state["last_sorgu"] = s_inp; st.rerun()

# Ana Panel
c1, c2, c3 = st.columns([1, 4, 1.2])

with c1:
    st.write("📋 LİSTEM")
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with c2:
    res = get_bist_analysis(st.session_state["last_sorgu"])
    if res:
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex; justify-content:space-between;'>
                <b style='color:#ffcc00;'>GÜRKAN AI ANALİZ: {st.session_state["last_sorgu"]}</b>
                <span style='background:{res['color']}; color:black; padding:0 10px; border-radius:4px; font-weight:bold;'>{res['stat']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; margin-top:15px; text-align:center;'>
                <div><small>FİYAT</small><br><b>{res['p']:.2f}</b></div>
                <div><small>GÜNLÜK</small><br><b style='color:{res['color']};'>{res['ch']:+.2f}%</b></div>
                <div><small>RSI</small><br><b>{res['rsi']:.1f}</b></div>
                <div><small>HACİM</small><br><b>{res['vol']}</b></div>
            </div>
            <p style='margin-top:15px; font-size:14px; border-top:1px solid #333; padding-top:10px;'><b>YORUM:</b> {res['note']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right'))
        st.plotly_chart(fig, use_container_width=True)

with c3:
    st.write("⚡ RADAR")
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(r, key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
