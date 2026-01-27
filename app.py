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
        st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("GİRİŞ", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 KOMPAKT CSS (Yazılar Küçültüldü) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .block-container { max-width: 1200px !important; padding-top: 0.5rem !important; margin: auto; }
        
        /* Ana Başlık Küçültüldü */
        .main-header { color:#ffcc00; text-align:center; font-size: 20px !important; font-weight: bold; margin-bottom: 10px; }
        
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 15px; 
            border-radius: 10px; color: #ffffff; border-left: 5px solid #ffcc00;
        }
        
        /* Neon Yazılar Küçültüldü */
        .neon-green { color: #00ff88; text-shadow: 0 0 8px #00ff88; font-weight: bold; font-size: 20px !important; }
        .neon-red { color: #ff4b4b; text-shadow: 0 0 8px #ff4b4b; font-weight: bold; font-size: 20px !important; }
        
        .text-blue { color: #00d4ff; font-weight: bold; font-size: 13px; }
        .strat-badge { padding: 3px 10px; border-radius: 5px; font-weight: bold; color: black; font-size: 13px; text-transform: uppercase; }
        
        /* Buton ve Metrik Yazıları */
        div.stButton > button { height: 34px !important; font-size: 12px !important; }
        [data-testid="stMetricValue"] { font-size: 20px !important; }
        [data-testid="stMetricLabel"] { font-size: 11px !important; }
        
        p, span { font-size: 13px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔍 ÜST BAR ---
    st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    _, sc2, sc3, _ = st.columns([2.5, 2, 0.6, 2.5])
    with sc2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol...", label_visibility="collapsed").upper().strip()
    with sc3: 
        if st.button("➕", use_container_width=True):
            if h_input not in st.session_state["favorites"]: st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([0.8, 4, 1])

    with col_fav:
        st.markdown("<p style='color:#8b949e; font-weight:bold; margin-bottom:5px;'>TAKİP</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"{f}", key=f"f_{f}", use_container_width=True): st.session_state["last_sorgu"] = f; st.rerun()
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
                
                # Zeka Hesapları
                delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                volatility = (df['High'] - df['Low']).tail(10).mean() / last_p * 100
                up_pot, down_risk = round(volatility * 1.6, 1), round(volatility * 1.3, 1)

                # Renk ve Strateji
                if rsi > 72: strat, color, up_pot, down_risk = "DİKKAT: DOYUM", "#ff4b4b", up_pot*0.4, down_risk*2.2
                elif rsi < 35: strat, color, up_pot, down_risk = "FIRSAT: ALIM", "#00ff88", up_pot*2.3, down_risk*0.6
                else: strat, color = ("TREND POZİTİF" if last_p > ma20 else "ZAYIF SEYİR"), ("#00ff88" if last_p > ma20 else "#ffcc00")

                # Metrikler
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_p:.2f}")
                m2.metric("DEĞİŞİM", f"%{change:+.2f}")
                m3.metric("RSI", f"{rsi:.1f}")
                m4.metric("VOLATİLİTE", f"%{volatility:.1f}")

                # --- 🤵 KÜÇÜLTÜLMÜŞ ANALİZ KUTUSU ---
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <b style='color:#ffcc00; font-size:16px;'>🤵 GÜRKAN PRO</b>
                        <span class='strat-badge' style='background:{color};'>{strat}</span>
                    </div>
                    <div style='display:flex; justify-content:space-around; margin-top:12px; background:rgba(255,255,255,0.03); padding:10px; border-radius:8px;'>
                        <div style='text-align:center;'>
                            <span style='color:#8b949e; font-size:11px;'>🚀 BEKLENTİ</span><br>
                            <span class='neon-green'>+ %{up_pot}</span>
                        </div>
                        <div style='text-align:center; border-left: 1px solid #30363d; padding-left:20px;'>
                            <span style='color:#8b949e; font-size:11px;'>⚠️ RİSK</span><br>
                            <span class='neon-red'>- %{down_risk}</span>
                        </div>
                    </div>
                    <p style='margin-top:10px; margin-bottom:0px;'>
                        <span class='text-blue'>{h_input}</span> trendi <span style='color:{color}'><b>{'Güçlü' if last_p > ma20 else 'Zayıf'}</b></span>. 
                        Hedef: <b>{last_p*(1+up_pot/100):.2f}</b> | Destek: <b>{last_p*(1-down_risk/100):.2f}</b>
                    </p>
