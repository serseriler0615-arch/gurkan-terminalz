import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR"]

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="VIP Login", layout="centered")
        st.markdown("<style>.stApp{background-color:#0d1117;} h1,p,label{color:white !important;}</style>", unsafe_allow_html=True)
        st.title("Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            key = st.text_input("Lisans Anahtarı", key="login_key")
            if st.button("Sistemi Aktive Et"):
                if key.startswith("GAI-"): 
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=30)
                    st.rerun()
        with t2:
            u, p = st.text_input("ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # ULTRA OKUNABİLİR CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-weight: bold !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 15px; border-radius: 12px; }
        .trend-up { color: #00ff88 !important; border: 1px solid #00ff88; padding: 2px 8px; border-radius: 4px; }
        .trend-down { color: #ff4b4b !important; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; }
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 8px; color: #00ff88 !important; }
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 24px !important; }
        .main .block-container { padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST PANEL ---
    c_st1, c_st2, c_st3 = st.columns([2, 2, 1])
    with c_st1: st.markdown(f"⭐ **Gürkan AI VIP Dashboard**")
    with c_st2: 
        if st.session_state.get("role") == "user":
            st.markdown(f"⏳ **Lisans:** {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Çıkış", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

    # --- ANA DASHBOARD ---
    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        y_fav = st.text_input("Ekle:", placeholder="SASA", label_visibility="collapsed", key="fav_in").upper()
        if st.button("Ekle", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)
        if st.button("Temizle"): st.session_state["favorites"] = []; st.rerun()

    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="6mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                # Trendy Hesaplamalar
                hedef_1 = fiyat * 1.05  # %5 Kar hedefi
                hedef_2 = fiyat * 1.12  # %12 Ana hedef
                stop_loss = fiyat * 0.96 # %4 Zarar kes
                trendy_durum = "YUKARI" if fiyat > ma20 else "AŞAĞI"
                trendy_class = "trend-up" if trendy_durum == "YUKARI" else "trend-down"

                # Metrikler
                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("GÜNCEL FİYAT", f"{fiyat:.2f} TL")
                m_c2.metric("TRENDY DURUM", trendy_durum)
                m_c3.metric("STOP-LOSS", f"{stop_loss:.2f}")
                
                st.area_chart(df['Close'].tail(30), color="#00ff88", height=200)

                # --- GELİŞMİŞ TRENDY ASİSTAN ---
                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88; font-size:18px;'>🤵 VIP STRATEJİ MERKEZİ: {h_input}</b><br>
                        <p style='margin-top:10px;'>
                        🔥 <b>Trendy Yönü:</b> <span class='{trendy_class}'>{trendy_durum}</span><br>
                        🎯 <b>Kısa Vade Hedef:</b> <span style='color:#00ff88;'>{hedef_1:.2f} TL</span><br>
                        🏆 <b>VIP Ana Hedef:</b> <span style='color:#00ff88;'>{hedef_2:.2f} TL</span><br>
                        🛡️ <b>Zarar Kes (Stop):</b> <span style='color:#ff4b4b;'>{stop_loss:.2f} TL</span>
                        </p>
                        <hr style='border-color:#333;'>
                        <b>Asistan Notu:</b> {h_input} şu an {trendy_durum.lower()} ivmesinde. 
                        { 'Güçlü duruş sergiliyor, hedefler güncel.' if trendy_durum == "YUKARI" else 'Baskı devam ediyor, stop seviyesine dikkat.'}
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri hatası!")

    with col_radar:
        st.markdown("### 🚀 VIP RADAR")
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "SASA"]:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r}</b><br>Potansiyel: %2+</div>", unsafe_allow_html=True)
        if st.session_state.get("role") == "admin":
            st.markdown("---")
            if st.button("🔑 Key Üret"): st.code(f"GAI-{int(time.time())}-30-VIP")
