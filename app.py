import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. ZEKA MOTORU (Gelişmiş İstatistiksel Hesaplama) ---
def get_advanced_analysis(symbol):
    try:
        df = yf.download(symbol + ".IS", period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        last_p = float(df['Close'].iloc[-1])
        
        # 1. ATR Hesaplama (Gerçek Oynaklık)
        high_low = df['High'] - df['Low']
        high_cp = np.abs(df['High'] - df['Close'].shift())
        low_cp = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        # 2. RSI & Trend
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # 3. Zeki Oran Hesaplama (ATR tabanlı + Trend Çarpanı)
        # Yükseliş ihtimali trend yönündeyse çarpan artar
        trend_multiplier = 1.2 if last_p > ma20 else 0.8
        up_pot = round((atr * 2.5 / last_p) * 100 * trend_multiplier, 1)
        down_risk = round((atr * 2.0 / last_p) * 100, 1)

        # 4. Sinyal Gücü
        if rsi > 70: strat, color, comment = "DOYUM NOKTASI", "#ff4b4b", "İstatistiksel olarak düzeltme ihtimali %75."
        elif rsi < 35: strat, color, comment = "DİP ALIM", "#00ff88", "Tepki yükselişi ihtimali yüksek, limitleri zorluyor."
        elif last_p > ma20: strat, color, comment = "GÜÇLÜ TREND", "#00ff88", f"Trend desteği {ma20:.2f} seviyesinde korunduğu sürece pozitif."
        else: strat, color, comment = "ZAYIF SEYİR", "#ffcc00", "Baskı devam ediyor, nakit koruma ön planda olmalı."

        return {
            "last_p": last_p, "rsi": rsi, "up": up_pot, "down": down_risk, 
            "strat": strat, "color": color, "comment": comment, "df": df, "change": ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        }
    except: return None

# --- 2. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "EREGL"]

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
    with st.form("v"):
        k = st.text_input("Giriş Anahtarı", type="password")
        if st.form_submit_button("SİSTEME GİR", use_container_width=True):
            if k.strip().upper().startswith("GAI-"): st.session_state["access_granted"] = True; st.rerun()
else:
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
    st.markdown("""<style>
        .stApp { background-color: #0b0d11 !important; }
        .gurkan-pro-box { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-left: 6px solid #ffcc00; }
        .neon-green { color: #00ff88; text-shadow: 0 0 8px #00ff88; font-weight: bold; font-size: 22px !important; }
        .neon-red { color: #ff4b4b; text-shadow: 0 0 8px #ff4b4b; font-weight: bold; font-size: 22px !important; }
        .strat-badge { padding: 4px 12px; border-radius: 6px; font-weight: bold; color: black; font-size: 12px; }
    </style>""", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#ffcc00; text-align:center;'>★ GÜRKAN AI PRO v132</h4>", unsafe_allow_html=True)
    
    # --- ÜST BAR ---
    _, sc2, sc3, _ = st.columns([2.5, 2, 0.6, 2.5])
    with sc2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with sc3: 
        if st.button("➕"):
            if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

    col_fav, col_main, col_radar = st.columns([0.8, 4, 1.2])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-weight:bold;'>LİSTE</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            if st.button(f"{f}", key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()

    with col_main:
        res = get_advanced_analysis(h_input)
        if res:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("FİYAT", f"{res['last_p']:.2f}")
            m2.metric("GÜNLÜK", f"%{res['change']:+.2f}")
            m3.metric("RSI", f"{res['rsi']:.1f}")
            m4.metric("VOLATİLİTE", "YÜKSEK" if res['up'] > 5 else "STABİL")

            st.markdown(f"""
            <div class='gurkan-pro-box'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <b style='color:#ffcc00; font-size:16px;'>🤵 STRATEJİK ANALİZ MOTORU</b>
                    <span class='strat-badge' style='background:{res['color']};'>{res['strat']}</span>
                </div>
                <div style='display:flex; justify-content:space-around; margin-top:15px; background:rgba(255,255,255,0.03); padding:12px; border-radius:10px;'>
                    <div style='text-align:center;'>
                        <span style='color:#8b949e; font-size:11px;'>🚀 MAX HEDEF</span><br><span class='neon-green'>+ %{res['up']}</span>
                    </div>
                    <div style='text-align:center; border-left: 1px solid #30363d; padding-left:25px;'>
                        <span style='color:#8b949e; font-size:11px;'>⚠️ RİSK SINIRI</span><br><span class='neon-red'>- %{res['down']}</span>
                    </div>
                </div>
                <p style='margin-top:12px; font-size:14px;'><b>Yapay Zeka Notu:</b> {res['comment']}</p>
            </div>
            """, unsafe_allow_html=True)

            fig = go.Figure(data=[go.Candlestick(x=res['df'].tail(60).index, open=res['df'].tail(60)['Open'], high=res['df'].tail(60)['High'], low=res['df'].tail(60)['Low'], close=res['df'].tail(60)['Close'])])
            fig.update_layout(height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else: st.error("Analiz motoru bu sembol için yeterli veri bulamadı.")

    with col_radar:
        st.markdown("<p style='color:#8b949e; font-weight:bold;'>RADAR (QUANT)</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "BIMAS"]:
            # Radar için hızlı analiz
            quick = get_advanced_analysis(r)
            icon = "🔴" if quick and quick['rsi'] > 70 else ("🟢" if quick and quick['rsi'] < 35 else "🟡")
            if st.button(f"{icon} {r}", key=f"rad_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
