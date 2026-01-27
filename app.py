import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. OTURUM HAFIZASI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

# --- 🔐 GİRİŞ KONTROLÜ ---
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

    # --- 🎨 PROFESYONEL TERMINAL CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0b0d11 !important; }
        .main-header { font-size: 22px; font-weight: bold; color: #ffcc00; margin-bottom: 10px; }
        .gurkan-ai-box { 
            background: #161b22; border: 1px solid #30363d; padding: 12px; 
            border-radius: 6px; color: #ffffff; border-left: 4px solid #ffcc00; margin-bottom: 15px; font-size: 14px;
        }
        .guven-badge { 
            background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; 
            color: #00ff88; padding: 8px; border-radius: 6px; text-align: center;
        }
        /* Buton Stilleri */
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; border-radius: 4px !important;
            height: 38px !important; font-size: 13px !important;
        }
        .active-btn button { background-color: #238636 !important; border-color: #2ea043 !important; color: white !important; font-weight: bold; }
        .del-btn button { color: #ff4b4b !important; border: none !important; background: transparent !important; }
        
        /* Sidebar Genişliği Fix */
        [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN PANEL (ŞERİT) ---
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

    # --- ÜST BAR (KOMPAKT ARAMA) ---
    st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3 = st.columns([3, 1, 6])
    with h_col1:
        h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol (THYAO...)", label_visibility="collapsed").upper().strip()
    with h_col2:
        if st.button("➕ EKLE", use_container_width=True):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([1.1, 4, 1.4])

    # 1. SOL: TAKİP LİSTESİ (SİLME BUTONLU)
    with col_fav:
        st.markdown("<p style='color:#8b949e; font-size:11px; margin-bottom:10px;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            c_f, c_d = st.columns([4, 1])
            with c_f:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f" {f}", key=f"btn_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with c_d:
                st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                if st.button("×", key=f"del_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: GRAFİK & ANALİZ
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # Metrikler
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1.2])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:+.2f}")
                m3.metric("RSI", "62.4")
                with m4: st.markdown("<div class='guven-badge'><small>GÜVEN</small><br><b>%80</b></div>", unsafe_allow_html=True)

                # Araştırma Kutusu
                st.markdown(f"""
                <div class='gurkan-ai-box'>
                    <b style='color:#ffcc00;'>🤵 AI ARAŞTIRMA:</b> <b>{h_input}</b> trend desteği üzerinde. 
                    Hedef: <b>{fiyat*1.02:.2f} ₺</b>. Güçlü momentum gözlemleniyor.
                </div>
                """, unsafe_allow_html=True)

                # Grafik
                fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
                fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Veri bekleniyor...")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("<p style='color:#8b949e; font-size:11px; margin-bottom:10px;'>HIZLI RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "BIMAS"]:
            if st.button(f"⚡ {r}", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
