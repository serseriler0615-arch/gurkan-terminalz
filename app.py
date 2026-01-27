import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 2. GİRİŞ KONTROLÜ (KESİN ÇÖZÜM) ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    with tab1:
        vip_k = st.text_input("Giriş Anahtarı", type="password", key="v_key")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vip_k.strip().upper().startswith("GAI-"):
                st.session_state["access_granted"] = True
                st.rerun()
    with tab2:
        adm_u = st.text_input("Admin ID", key="a_user")
        adm_p = st.text_input("Şifre", type="password", key="a_pass")
        if st.button("ADMİN YETKİSİ AL", use_container_width=True):
            if adm_u.strip().upper() == "GURKAN" and adm_p.strip().upper() == "HEDEF2026":
                st.session_state["access_granted"] = True
                st.rerun()
    st.stop()

# --- 3. ANALİZ MOTORU ---
def get_advanced_analysis(symbol):
    try:
        sembol = symbol if "." in symbol else symbol + ".IS"
        df = yf.download(sembol, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 20: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        last_p = float(df['Close'].iloc[-1])
        change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
        
        vol = (df['High'] - df['Low']).tail(10).mean() / last_p
        trend_mult = 1.2 if last_p > ma20 else 0.8
        up_pot = round(vol * 180 * trend_mult, 1)
        down_risk = round(vol * 130, 1)

        if rsi > 70: strat, color, comment = "DOYUM NOKTASI", "#ff4b4b", "RSI aşırı alımda, dikkat!"
        elif rsi < 35: strat, color, comment = "DİP ALIM", "#00ff88", "Hisse dipte, tepki gelebilir."
        elif last_p > ma20: strat, color, comment = "TREND POZİTİF", "#00ff88", f"Görünüm güçlü, destek {ma20:.2f}"
        else: strat, color, comment = "ZAYIF SEYİR", "#ffcc00", "Trend zayıf, temkinli olun."

        return {"last_p": last_p, "rsi": rsi, "up": up_pot, "down": down_risk, "strat": strat, "color": color, "comment": comment, "df": df, "change": change}
    except: return None

# --- 4. ANA ARAYÜZ ---
st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
    .stApp { background-color: #0b0d11 !important; }
    .gurkan-pro-box { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-left: 6px solid #ffcc00; }
    .neon-green { color: #00ff88; text-shadow: 0 0 8px #00ff88; font-weight: bold; font-size: 20px !important; }
    .neon-red { color: #ff4b4b; text-shadow: 0 0 8px #ff4b4b; font-weight: bold; font-size: 20px !important; }
    .strat-badge { padding: 4px 12px; border-radius: 6px; font-weight: bold; color: black; font-size: 11px; text-transform: uppercase; }
</style>""", unsafe_allow_html=True)

st.markdown("<h4 style='color:#ffcc00; text-align:center;'>★ GÜRKAN AI PRO</h4>", unsafe_allow_html=True)

# Üst Arama Barı
_, sc2, sc3, _ = st.columns([2.5, 2, 0.6, 2.5])
with sc2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed", key="search_bar").upper().strip()
with sc3: 
    if st.button("➕"): 
        if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

c_fav, c_main, c_radar = st.columns([0.8, 4, 1.2])

with c_fav:
    st.markdown("<p style='color:#8b949e; font-weight:bold;'>LİSTE</p>", unsafe_allow_html=True)
    for f in st.session_state["favorites"]:
        if st.button(f, key=f"f_{f}", use_container_width=True):
            st.session_state["last_sorgu"] = f; st.rerun()

with c_main:
    res = get_advanced_analysis(st.session_state["last_sorgu"])
    if res:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("FİYAT", f"{res['last_p']:.2f}")
        m2.metric("GÜNLÜK", f"%{res['change']:+.2f}")
        m3.metric("RSI", f"{res['rsi']:.1f}")
        m4.metric("VOLATİLİTE", "YÜKSEK" if res['up'] > 5 else "STABİL")

        st.markdown(f"""
        <div class='gurkan-pro-box'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <b style='color:#ffcc00;'>🤵 GÜRKAN PRO ANALİZ</b>
                <span class='strat-badge' style='background:{res['color']};'>{res['strat']}</span>
            </div>
            <div style='display:flex; justify-content:space-around; margin-top:10px; background:rgba(255,255,255,0.03); padding:10px; border-radius:10px;'>
                <div style='text-align:center;'>
                    <span style='color:#8b949e; font-size:10px;'>🚀 MAX HEDEF</span><br><span class='neon-green'>+ %{res['up']}</span>
                </div>
                <div style='text-align:center; border-left: 1px solid #30363d; padding-left:20px;'>
                    <span style='color:#8b949e; font-size:10px;'>⚠️ RİSK SINIRI</span><br><span class='neon-red'>- %{res['down']}</span>
                </div>
            </div>
            <p style='margin-top:10px;'><b>Not:</b> {res['comment']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
        fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else: st.warning("Sembol aranıyor...")

with c_radar:
    st.markdown("<p style='color:#8b949e; font-weight:bold;'>RADAR</p>", unsafe_allow_html=True)
    for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
        if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
            st.session_state["last_sorgu"] = r; st.rerun()
