import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- GİRİŞ EKRANI (FULL MODERN) ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#ffcc00; font-family:sans-serif;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
    with t1:
        vk = st.text_input("Giriş Anahtarı", type="password", key="vk")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vk.strip().upper().startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
    with t2:
        u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
        if st.button("YETKİ AL", use_container_width=True):
            if u.strip().upper() == "GURKAN" and p.strip().upper() == "HEDEF2026": st.session_state["access_granted"] = True; st.rerun()
    st.stop()

# --- 🧠 ULTRA INTEL ANALİZ MOTORU ---
def get_ultra_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 40: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        last_p = float(df['Close'].iloc[-1])
        ma20 = df['Close'].rolling(20).mean(); std20 = df['Close'].rolling(20).std()
        upper_b = ma20 + (std20 * 2); lower_b = ma20 - (std20 * 2)
        
        # Smart Money Flow (Hacim & Fiyat İlişkisi)
        df['Price_Dir'] = np.where(df['Close'] > df['Open'], 1, -1)
        df['Money_Flow'] = df['Volume'] * df['Price_Dir']
        mf_score = df['Money_Flow'].tail(5).sum() / df['Volume'].tail(5).sum()
        
        # Olasılık Motoru
        up_pot = round(((upper_b.iloc[-1] - last_p) / last_p) * 100, 1)
        down_risk = round(((last_p - lower_b.iloc[-1]) / last_p) * 100, 1)
        
        confidence = 50 + (mf_score * 50) # -100 to +100 arası skaladan güven skoru
        if last_p > ma20.iloc[-1]: confidence += 10
        
        conf_label = "YÜKSEK (%90+)" if confidence > 75 else ("ORTA (%60+)" if confidence > 45 else "ZAYIF")
        color = "#00ff88" if confidence > 45 else "#ff4b4b"
        
        return {"p": last_p, "up": max(up_pot, 1.2), "down": down_risk, "conf": conf_label, "color": color, "df": df, "ch": ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100}
    except: return None

# --- TASARIM VE ARAYÜZ ---
st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
st.markdown(f"""<style>
    .stApp {{ background: radial-gradient(circle at top right, #1a1f25, #0b0d11) !important; color: white; }}
    .glass-card {{ 
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8); margin-bottom: 15px;
    }}
    .metric-box {{ text-align: center; border-right: 1px solid rgba(255,255,255,0.1); }}
    .neon-text {{ color: #ffcc00; text-shadow: 0 0 10px rgba(255,204,0,0.5); font-weight: bold; }}
</style>""", unsafe_allow_html=True)

# Üst Arama (Kompakt ve Şık)
_, sc_mid, _ = st.columns([1.5, 2, 1.5])
with sc_mid:
    inp_col, btn_col = st.columns([4, 1])
    with inp_col: 
        s_input = st.text_input("", value=st.session_state["last_sorgu"], key="s_key", placeholder="Hisse Ara...", label_visibility="collapsed").upper().strip()
    with btn_col:
        if st.button("🔍"): st.session_state["last_sorgu"] = s_input; st.rerun()

# Ana Gövde
c_list, c_main = st.columns([1, 5])

with c_list:
    st.markdown("<p style='font-size:12px; color:#8b949e; margin-left:5px;'>FAVORİLER</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f"★ {f}", key=f"fav_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

with c_main:
    res = get_ultra_analysis(st.session_state["last_sorgu"])
    if res:
        # Cam Kart Analiz Paneli
        st.markdown(f"""
        <div class='glass-card'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                <span style='font-size:18px; font-weight:bold;'>{st.session_state["last_sorgu"]} ANALİZ <small style='color:#8b949e; font-weight:normal;'>v142</small></span>
                <span style='color:{res['color']}; border: 1px solid {res['color']}; padding: 2px 12px; border-radius: 20px; font-size:12px;'>{res['conf']}</span>
            </div>
            <div style='display:flex; justify-content:space-around;'>
                <div class='metric-box' style='flex:1;'> <p style='color:#8b949e; font-size:11px;'>GÜNCEL FİYAT</p> <span style='font-size:22px; font-weight:bold;'>{res['p']:.2f}</span> </div>
                <div class='metric-box' style='flex:1;'> <p style='color:#8b949e; font-size:11px;'>GÜVENLİ HEDEF</p> <span style='font-size:22px; color:#00ff88; font-weight:bold;'>+% {res['up']}</span> </div>
                <div class='metric-box' style='flex:1;'> <p style='color:#8b949e; font-size:11px;'>MAKS RİSK</p> <span style='font-size:22px; color:#ff4b4b; font-weight:bold;'>-% {res['down']}</span> </div>
                <div style='flex:1; text-align:center;'> <p style='color:#8b949e; font-size:11px;'>AI SKORU</p> <span class='neon-text' style='font-size:22px;'>{res['conf'].split(' ')[0]}</span> </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grafik (Netleştirilmiş)
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=10, color='#8b949e')))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Veri işleniyor, lütfen bekleyin...")
