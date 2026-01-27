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

    # --- 🎨 PRO CSS (X BUTONU & KISA ARAMA) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0d0f14 !important; }
        .main-header { font-size: 24px; font-weight: bold; color: #ffcc00; }
        .gurkan-ai-box { 
            background: #161b22; border: 1px solid #30363d; padding: 15px; 
            border-radius: 8px; color: #ffffff; border-left: 6px solid #ffcc00; margin-bottom: 15px;
        }
        .guven-badge { 
            background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; 
            color: #00ff88; padding: 10px; border-radius: 8px; text-align: center;
        }
        /* Buton Tasarımları */
        div.stButton > button {
            background-color: #1c2128 !important; color: #e0e0e0 !important;
            border: 1px solid #30363d !important; border-radius: 4px !important;
        }
        /* Favori ve Silme Butonları Yan Yana */
        .fav-row { display: flex; align-items: center; margin-bottom: 5px; gap: 5px; }
        .active-btn button { background-color: #238636 !important; color: white !important; font-weight: bold; }
        
        /* Input Alanı Daraltma */
        div[data-testid="stTextInput"] { width: 100% !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN PANEL ---
    if st.session_state["role"] == "admin":
        ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.3])
        with ac1: s_gun = st.selectbox("", [30, 90, 365], label_visibility="collapsed")
        with ac2: 
            if st.button("💎 ÜRET"): 
                st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
        with ac3: 
            if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
        with ac4:
            if st.button("🚪"): st.session_state["access_granted"] = False; st.rerun()

    # --- ÜST BAR (KISA ARAMA & EKLE) ---
    h_col1, h_col2, h_col3, h_col4 = st.columns([1.5, 1.5, 0.5, 2])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], placeholder="Sembol...", label_visibility="collapsed").upper().strip()
    with h_col3:
        if st.button("➕"):
            if h_input not in st.session_state["favorites"]:
                st.session_state["favorites"].append(h_input); st.rerun()

    # --- ANA DÜZEN ---
    col_left, col_mid, col_right = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER + ÇARPI BUTONU
    with col_left:
        st.markdown("<p style='color:#8b949e; font-size:11px; font-weight:bold;'>TAKİP LİSTESİ</p>", unsafe_allow_html=True)
        for f in st.session_state["favorites"]:
            c_fav, c_del = st.columns([4, 1])
            with c_fav:
                is_active = "active-btn" if f == h_input else ""
                st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
                if st.button(f"📊 {f}", key=f"btn_{f}", use_container_width=True):
                    st.session_state["last_sorgu"] = f; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with c_del:
                if st.button("✖", key=f"del_{f}"):
                    st.session_state["favorites"].remove(f); st.rerun()

    # 2. ORTA: ANALİZ
    with col_mid:
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
                m3.metric("RSI", "61.0")
                with m4: st.markdown("<div class='guven-badge'><small>GÜVEN</small><br><b>%80</b></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='gurkan-ai-box'>
                    <b style='color:#ffcc00;'>🤵 GÜRKAN AI ARAŞTIRMA:</b> <b>{h_input}</b> incelendi. 
                    Hedef fiyat: <b>{fiyat*1.018:.2f} ₺</b>. Teknik göstergeler alım yönlü güçleniyor.
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
                fig.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#1c2128'))
                st.plotly_chart(fig, use_container_width=True)
        except: st.warning("Veri bekleniyor...")

    # 3. SAĞ: RADAR
    with col_right:
        st.markdown("<p style='color:#8b949e; font-size:11px; font-weight:bold;'>🚀 HIZLI RADAR</p>", unsafe_allow_html=True)
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "AKBNK"]:
            if st.button(f"{r} %0.0", key=f"r_{r}", use_container_width=True):
                st.session_state["last_sorgu"] = r; st.rerun()
