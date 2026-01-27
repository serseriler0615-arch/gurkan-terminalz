import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. FONKSİYONLAR (Hata Almamak İçin Üstte) ---

@st.cache_data(ttl=300)
def check_status(symbol):
    try:
        d = yf.download(symbol + ".IS", period="1mo", interval="1d", progress=False)
        if d.empty or len(d) < 14: return "🔍"
        delta = d['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        if rsi > 70: return "🔴"
        if rsi < 35: return "🟢"
        return "🟡"
    except: return "⏳"

# --- 2. OTURUM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "THYAO"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
        with st.form("v"):
            k = st.text_input("Giriş Anahtarı", type="password")
            if st.form_submit_button("SİSTEME GİR", use_container_width=True):
                if k.strip().upper().startswith("GAI-"): 
                    st.session_state["access_granted"] = True; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 KOMPAKT CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1200px !important; padding-top: 0.5rem !important; }
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 12px; 
            border-radius: 10px; color: #ffffff; border-left: 5px solid #ffcc00;
        }
        .neon-green { color: #00ff88; text-shadow: 0 0 8px #00ff88; font-weight: bold; font-size: 18px !important; }
        .neon-red { color: #ff4b4b; text-shadow: 0 0 8px #ff4b4b; font-weight: bold; font-size: 18px !important; }
        .strat-badge { padding: 3px 10px; border-radius: 5px; font-weight: bold; color: black; font-size: 11px; text-transform: uppercase; }
        p, span { font-size: 13px !important; }
        div.stButton > button { height: 32px !important; font-size: 11px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ÜST PANEL ---
    st.markdown("<h4 style='color:#ffcc00; text-align:center;'>★ GÜRKAN AI PRO</h4>", unsafe_allow_html=True)
    _, sc2, sc3, _ = st.columns([2.5, 2, 0.6, 2.5])
    with sc2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
    with sc3: 
        if st.button("➕"):
            if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

    col_fav, col_main, col_radar = st.columns([0.8, 4, 1.2])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-weight:bold;'>LİSTE</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                if st.button(f"{f}", key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
            with cf2:
                if st.button("×", key=f"d_{f}"): st.session_state["favorites"].remove(f); st.rerun()

    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                last_p = float(df['Close'].iloc[-1])
                change = ((last_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
                
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                volatility = (df['High'] - df['Low']).tail(10).mean() / last_p * 100
                up_pot, down_risk = round(volatility * 1.6, 1), round(volatility * 1.3, 1)

                if rsi > 70: strat, color, c_txt = "DİKKAT: DOYUM", "#ff4b4b", "RSI riskli bölgede, kar alımları gelebilir."
                elif rsi < 35: strat, color, c_txt = "FIRSAT: ALIM", "#00ff88", "Aşırı satış bölgesinde, tepki beklenebilir."
                elif last_p > ma20: strat, color, c_txt = "TREND POZİTİF", "#00ff88", f"Fiyat {ma20:.2f} ortalamasının üstünde."
                else: strat, color, c_txt = "ZAYIF SEYİR", "#ffcc00", "Trend desteği kırılmış, dikkat!"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_p:.2f}")
                m2.metric("DEĞİŞİM", f"%{change:+.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                m4.metric("VOL.", f"%{volatility:.1f}")

                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <b style='color:#ffcc00;'>🤵 GÜRKAN PRO ANALİZ</b>
                        <span class='strat-badge' style='background:{color};'>{strat}</span>
                    </div>
                    <div style='display:flex; justify-content:space-around; margin-top:10px; background:rgba(255,255,255,0.03); padding:8px; border-radius:8px;'>
                        <div style='text-align:center;'>
                            <span style='color:#8b949e; font-size:10px;'>🚀 BEKLENTİ</span><br><span class='neon-green'>+ %{up_pot}</span>
                        </div>
                        <div style='text-align:center; border-left: 1px solid #30363d; padding-left:15px;'>
                            <span style='color:#8b949e; font-size:10px;'>⚠️ RİSK</span><br><span class='neon-red'>- %{down_risk}</span>
                        </div>
                    </div>
                    <p style='margin-top:10px;'><b>Yorum:</b> {c_txt}</p>
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
                fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128', tickfont=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except: st.empty()

    with col_radar:
        st.markdown("<p style='color:#8b949e; font-weight:bold;'>RADAR (CANLI)</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "BIMAS"]:
            icon = check_status(r)
            if st.button(f"{icon} {r}", key=f"rad_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
