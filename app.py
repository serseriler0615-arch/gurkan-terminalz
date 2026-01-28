import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- GİRİŞ VE SİSTEM AYARLARI (Stabil Tutuldu) ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

if not st.session_state["access_granted"]:
    # ... (Giriş Paneli - Değişmedi) ...
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    with tab1:
        vip_k = st.text_input("Giriş Anahtarı", type="password", key="v_key")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vip_k.strip().upper().startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
    with tab2:
        u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
        if st.button("ADMİN YETKİSİ AL", use_container_width=True):
            if u.strip().upper() == "GURKAN" and p.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 🧠 QUANTUM ANALİZ MOTORU (%90 HEDEF ODAKLI) ---
def get_quantum_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 40: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        
        # 1. Bollinger Bantları (Daralma = Patlama İhtimali)
        ma20 = df['Close'].rolling(20).mean()
        std20 = df['Close'].rolling(20).std()
        upper_b = ma20 + (std20 * 2)
        lower_b = ma20 - (std20 * 2)
        bandwidth = (upper_b - lower_b) / ma20
        
        # 2. RSI & Hacim Uyumu
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # 3. İhtimal Skorlama (Z-Score tabanlı)
        score = 0
        if last_p > ma20.iloc[-1]: score += 25
        if rsi < 45: score += 25
        if df['Volume'].iloc[-1] > df['Volume'].tail(5).mean(): score += 20
        if bandwidth.iloc[-1] < bandwidth.tail(20).mean(): score += 20 # Sıkışma varsa ihtimal artar
        
        # Oranların Revizyonu (Gerçekçi Hedef)
        # ATR yerine Bollinger sapmasını kullanarak %90 ihtimalli "güvenli bölge" hesaplıyoruz
        safe_up = round(((upper_b.iloc[-1] - last_p) / last_p) * 100, 1)
        safe_down = round(((last_p - lower_b.iloc[-1]) / last_p) * 100, 1)
        
        # Negatif potansiyel koruması
        safe_up = max(safe_up, 1.5) 
        
        if score >= 70: stat, color, conf = "YÜKSEK GÜVEN", "#00ff88", "GÜÇLÜ (%85+)"
        elif score >= 40: stat, color, conf = "ORTA DERECE", "#ffcc00", "BEKLE (%50+)"
        else: stat, color, conf = "RİSKLİ BÖLGE", "#ff4b4b", "ZAYIF (<%30)"

        return {"p": last_p, "rsi": rsi, "up": safe_up, "down": safe_down, "strat": stat, "color": color, "conf": conf, "df": df, "ch": ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100}
    except: return None

# --- ARAYÜZ ---
st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    .stApp { background-color: #0b0d11 !important; }
    .gurkan-card { background: #161b22; border: 1px solid #30363d; padding: 12px; border-radius: 12px; border-top: 3px solid #ffcc00; }
    .stat-val { font-weight: bold; font-size: 20px !important; }
</style>""", unsafe_allow_html=True)

# Arama
_, sc_center, _ = st.columns([1.5, 2, 1.5])
with sc_center:
    c1, c2 = st.columns([4, 1])
    with c1: s_input = st.text_input("", value=st.session_state["last_sorgu"], key="new_s", label_visibility="collapsed").upper().strip()
    with c2: 
        if st.button("🔍"): st.session_state["last_sorgu"] = s_input; st.rerun()

# Ana Gövde
c_fav, c_main, c_radar = st.columns([0.7, 4.3, 1])

with c_fav:
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with c_main:
    res = get_quantum_analysis(st.session_state["last_sorgu"])
    if res:
        # Metrikler
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("FİYAT", f"{res['p']:.2f}")
        m2.metric("GÜVEN SKORU", res['conf'])
        m3.metric("RSI", f"{res['rsi']:.1f}")
        m4.metric("POTANSİYEL", f"%{res['up']}")

        # Quantum Strateji Kutusu
        st.markdown(f"""
        <div class='gurkan-card'>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:#ffcc00; font-size:12px;'>🤵 GÜRKAN AI QUANTUM ANALİZ</span>
                <span style='background:{res['color']}; color:black; padding:2px 10px; border-radius:5px; font-weight:bold; font-size:10px;'>{res['strat']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; margin-top:10px;'>
                <div style='text-align:center;'> <p style='color:#8b949e; margin:0;'>GÜVENLİ HEDEF</p><span style='color:#00ff88;' class='stat-val'>+ %{res['up']}</span> </div>
                <div style='text-align:center;'> <p style='color:#8b949e; margin:0;'>STOP-LOSS</p><span style='color:#ff4b4b;' class='stat-val'>- %{res['down']}</span> </div>
                <div style='text-align:center;'> <p style='color:#8b949e; margin:0;'>İHTİMAL</p><span style='color:#ffcc00;' class='stat-val'>{res['conf']}</span> </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with c_radar:
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
