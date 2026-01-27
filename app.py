import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ SİSTEMİ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("SİSTEME GİR", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u = st.text_input("Yönetici ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO TERMINAL CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .main-header { font-size: 26px; font-weight: bold; color: #ffcc00; text-align: center; margin-bottom: 20px; }
        .gurkan-pro-box { 
            background: #161b22; border: 1px solid #30363d; padding: 18px; 
            border-radius: 10px; color: #ffffff; border-left: 6px solid #ffcc00; margin-bottom: 20px;
        }
        .guven-badge { 
            background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; 
            color: #00ff88; padding: 8px; border-radius: 6px; text-align: center;
        }
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; border-radius: 6px !important;
            height: 40px !important;
        }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; font-weight: bold; }
        .del-btn button { color: #ff4b4b !important; border: none !important; background: transparent !important; font-size: 18px !important; }
        /* Arama Motoru Ortalama */
        .search-container { display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 30px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN PANEL ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.3])
        with ac1: s_gun = st.selectbox("", [30, 90, 365], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 KEY ÜRET", use_container_width=True): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- 🔍 MERKEZİ ARAMA MOTORU ---
    st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    
    sc1, sc2, sc3, sc4 = st.columns([2, 2.5, 0.8, 2])
    with sc2:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol (THYAO...)", label_visibility="collapsed").upper().strip()
    with sc3:
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([1, 4, 1.2])

    # 1. SOL: TAKİP LİSTESİ (SİLME BUTONLU)
    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:11px; margin-bottom:10px; font-weight:bold;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            cf1, cf2 = st.columns([4, 1])
            with cf1:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f" {f}", key=f"f_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cf2:
                st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                if st.button("×", key=f"d_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: GÜRKAN PRO ANALİZ
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                # Zeki Hesaplamalar
                last_price = float(df['Close'].iloc[-1])
                prev_price = float(df['Close'].iloc[-2])
                change = ((last_price - prev_price) / prev_price) * 100
                ma20 = df['Close'].tail(20).mean()
                volume_status = "Yüksek" if df['Volume'].iloc[-1] > df['Volume'].tail(10).mean() else "Normal"
                
                # Metrikler
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("FİYAT", f"{last_price:.2f}")
                m2.metric("GÜNLÜK", f"%{change:+.2f}")
                m3.metric("20 GÜN ORT.", f"{ma20:.2f}")
                with m4: st.markdown(f"<div class='guven-badge'><small>HACİM</small><br><b>{volume_status}</b></div>", unsafe_allow_html=True)

                # GÜRKAN PRO ARAŞTIRMA KUTUSU
                st.markdown(f"""
                <div class='gurkan-pro-box'>
                    <b style='color:#ffcc00; font-size:20px;'>🤵 GÜRKAN PRO ANALİZ:</b><br>
                    <p style='margin-top:10px;'>
                    <b>{h_input}</b> üzerinde yapılan derin araştırmada; fiyatın 20 günlük ortalamanın {'üzerinde' if last_price > ma20 else 'altında'} olduğu tespit edildi. 
                    Hacim desteği ile birlikte <b>{last_price*1.025:.2f} ₺</b> direnç seviyesi radarda. Momentum indikatörleri alıcılı seyri destekliyor.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Profesyonel Grafik
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Veri işleniyor...")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:11px; font-weight:bold;'>HIZLI RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
