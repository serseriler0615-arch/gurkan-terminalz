import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state: st.session_state["access_granted"] = False
if "role" not in st.session_state: st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state: st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state: st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("GİRİŞ", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN"):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 NEON & OKUNAKLI CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1250px !important; padding-top: 0.5rem !important; margin: auto; }
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 20px; 
            border-radius: 12px; color: #ffffff; border-left: 6px solid #ffcc00; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .neon-green { color: #00ff88; text-shadow: 0 0 10px #00ff88; font-weight: bold; font-size: 26px !important; }
        .neon-red { color: #ff4b4b; text-shadow: 0 0 10px #ff4b4b; font-weight: bold; font-size: 26px !important; }
        .text-blue { color: #00d4ff; font-weight: bold; }
        .strat-badge { padding: 5px 15px; border-radius: 8px; font-weight: bold; color: black; font-size: 16px; text-transform: uppercase; }
        div.stButton > button { background-color: #1c2128 !important; border: 1px solid #30363d !important; border-radius: 8px !important; height: 42px !important; font-weight: bold; }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ARAMA MOTORU (MERKEZİ) ---
    st.markdown("<h2 style='color:#ffcc00; text-align:center; margin-bottom:15px;'>★ GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
    _, sc2, sc3, _ = st.columns([2, 2.5, 0.7, 2])
    with sc2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol (EREGL, THYAO...)", label_visibility="collapsed").upper().strip()
    with sc3: 
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

    col_fav, col_main, col_radar = st.columns([1, 4, 1.2])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"📊 {f}", key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
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
                
                # RSI & Para Akışı
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                vol_status = "GÜÇLÜ" if df['Volume'].iloc[-1] > df['Volume'].tail(5).mean() else "ZAYIF"

                # Akıllı Oranlar
                volatility = (df['High'] - df['Low']).tail(10).mean() / last_p * 100
                up_pot, down_risk = round(volatility * 1.6, 1), round(volatility * 1.3, 1)

                if rsi > 72: strat, color, up_pot, down_risk = "DİKKAT: SATIŞ YAKIN", "#ff4b4b", up_pot*0.4, down_risk*2.2
                elif rsi < 35: strat, color, up_pot, down_risk = "FIRSAT: ALIM BÖLGESİ", "#00ff88", up_pot*2.3, down_risk*0.6
                elif last_p > ma20: strat, color = "POZİTİF TREND", "#00ff88"
                else: strat, color = "ZAYIF SEYİR", "#ffcc00"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_p:.2f} ₺")
                m2.metric("GÜNLÜK", f"%{change:+.2f}")
                m3.metric("RSI (14)", f"{rsi:.1f}")
                m4.metric("PARA AKIŞI", vol_status)

                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <b style='color:#ffcc00; font-size:22px;'>🤵 GÜRKAN PRO ANALİZ</b>
                        <span class='strat-badge' style='background:{color};'>{strat}</span>
                    </div>
                    <div style='display:flex; justify-content:space-around; margin-top:20px; background:rgba(255,255,255,0.03); padding:15px; border-radius:10px;'>
                        <div style='text-align:center;'>
                            <span style='color:#8b949e; font-size:14px;'>🚀 POTANSİYEL ÇIKIŞ</span><br>
                            <span class='neon-green'>+ %{up_pot}</span>
                        </div>
                        <div style='width:1px; background:#30363d;'></div>
                        <div style='text-align:center;'>
                            <span style='color:#8b949e; font-size:14px;'>⚠️ OLASI DÜŞÜŞ</span><br>
                            <span class='neon-red'>- %{down_risk}</span>
                        </div>
                    </div>
                    <p style='margin-top:15px; font-size:15px; line-height:1.6;'>
                        <b>{h_input}</b> için teknik araştırma: Fiyat <span class='text-blue'>{ma20:.2f}</span> desteğinin 
                        <b>{'üzerinde' if last_p > ma20 else 'altında'}</b>. Hacim girişi <b>{vol_status}</b>. 
                        Trend korunduğu takdirde hedef <span class='neon-green' style='font-size:16px;'>{last_p*(1+up_pot/100):.2f} ₺</span>.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.info("Hisse analiz ediliyor...")

    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:12px; font-weight:bold;'>RADAR (HIZLI)</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True): st.session_state["last_sorgu"] = r; st.rerun()
