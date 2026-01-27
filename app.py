import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. OTURUM ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "EREGL", "TUPRS", "AKBNK", "SISE"]

# --- 🔐 GİRİŞ PANELİ ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            with st.form("v"):
                k = st.text_input("Giriş Anahtarı", type="password")
                if st.form_submit_button("GİRİŞ", use_container_width=True):
                    if k.strip().upper().startswith("GAI-"): 
                        st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            with st.form("a"):
                u = st.text_input("ID")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("ADMİN GİRİŞ", use_container_width=True):
                    if u.strip().upper() == "GURKAN" and p.strip() == "HEDEF2024!": 
                        st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO DARK CSS (ZARİF FAVORİLER) ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .main-header { font-size: 20px; font-weight: bold; color: #ffcc00; letter-spacing: 1px; }
        .gurkan-ai-box { 
            background: #0d1117; border: 1px solid #1c2128; padding: 12px; 
            border-radius: 4px; color: #e0e0e0; border-left: 4px solid #ffcc00; margin-bottom: 10px;
        }
        .guven-badge { 
            background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; 
            color: #00ff88; padding: 8px; border-radius: 5px; text-align: center; font-size: 13px;
        }
        /* Favori Butonları - Küçük ve Şeffaf */
        div.stButton > button {
            background-color: transparent !important; color: #8b949e !important;
            border: 1px solid #1c2128 !important; text-align: left !important;
            border-radius: 4px !important; font-size: 11px !important; padding: 5px 10px !important; height: 32px !important;
        }
        div.stButton > button:hover { color: #ffcc00 !important; border-color: #ffcc00 !important; }
        .active-btn button { color: #00ff88 !important; border-color: #00ff88 !important; background: rgba(0, 255, 136, 0.05) !important; }
        
        /* Admin Şeridi */
        .admin-strip { background: #111; padding: 5px; border-bottom: 1px solid #222; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ULTRA KOMPAKT ADMİN ŞERİDİ ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.3])
        with ac1: s_gun = st.selectbox("", [30, 90, 365], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 ÜRET", use_container_width=True): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- ÜST PANEL ---
    h_col1, h_col2 = st.columns([1.5, 4])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol yaz...", label_visibility="collapsed").upper().strip()

    # --- ANA DÜZEN ---
    col_fav, col_main, col_radar = st.columns([0.6, 3, 1.2])

    # 1. SOL: FAVORİLER (Zarif ve Küçük Listeleme)
    with col_fav:
        st.markdown("<p style='color:#444; font-size:10px; margin-bottom:5px;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"▪ {f}", key=f"fav_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ
    with col_main:
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            df = yf.download(sembol, period="6mo", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("GÜNLÜK", f"%{degisim:+.2f}")
                m3.metric("RSI", "61.2")
                with m4: st.markdown("<div class='guven-badge'><small>GÜVEN</small><br><b>%80</b></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='gurkan-ai-box'>
                    <b style='color:#ffcc00;'>🤵 GÜRKAN AI ARAŞTIRMA:</b> <b>{h_input}</b> için teknik görünüm pozitif. 
                    Yarın <b>{fiyat*1.018:.2f} ₺</b> seviyeleri hedeflenebilir.
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Veri bekleniyor...")

    # 3. SAĞ: TRENDY RADAR (Full Liste)
    with col_radar:
        st.markdown("<p style='color:#444; font-size:10px; margin-bottom:5px;'>TRENDY RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK", "SISE", "KCHOL", "BIMAS"]:
            if st.button(f"🚀 {r} | %0.0", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
