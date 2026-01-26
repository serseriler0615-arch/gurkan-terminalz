import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. GİRİŞ VE OTURUM ---
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

    # ULTRA KOMPAKT CSS
    st.markdown("""
        <style>
        /* Ekranı daralt ve kaydırmayı engelle */
        html, body, [data-testid="stAppViewContainer"] { overflow: hidden; }
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; max-width: 100%; }
        
        /* Yazı Boyutlarını Küçült */
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: 600 !important; }
        h1 { font-size: 18px !important; color: #00ff88 !important; }
        
        /* Metrik ve Kartlar */
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 2px 10px !important; }
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 18px !important; }
        .asistan-box { background: #1c2128; border: 1px solid #00ff88; padding: 8px; border-radius: 8px; margin-top: 5px; line-height: 1.2; }
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 4px; font-size: 11px !important; color: #00ff88 !important; }
        .radar-card { background: #161b22; border-left: 3px solid #00ff88; padding: 6px; margin-bottom: 3px; border-radius: 4px; border: 1px solid #30363d; }
        
        /* Butonları küçült */
        .stButton button { padding: 0.2rem 0.5rem; font-size: 11px !important; height: auto; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST BAR (STATUS) ---
    c_st1, c_st2, c_st3 = st.columns([3, 1, 1])
    with c_st1: st.markdown(f"⭐ **Gürkan AI VIP Dashboard** | {datetime.now().strftime('%H:%M')}")
    with c_st2: 
        if st.session_state["role"] == "user": st.markdown(f"⌛ Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Çıkış", use_container_width=True): st.session_state.clear(); st.rerun()

    # --- DASHBOARD (3 SÜTUNLU YAPI) ---
    col_fav, col_main, col_radar = st.columns([0.7, 3.2, 1.1])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", placeholder="SASA", label_visibility="collapsed").upper()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-10:]: # Daha fazla favori sığar
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ
    with col_main:
        h_input = st.text_input("Hisse Sorgu:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

                # Trendy Hesaplar
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96
                
                # Metrikler (Tek Satır)
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("FİYAT", f"{fiyat:.2f}")
                m_c2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m_c3.metric("TRENDY", "YUKARI" if fiyat > ma20 else "AŞAĞI")
                m_c4.metric("STOP", f"{stop:.2f}")

                # RENKLENDİRİLMİŞ GRAFİK (Gradyan Efekti)
                st.area_chart(df['Close'].tail(25), color="#00ff88", height=180)

                # KOMPAKT ASİSTAN
                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88;'>🤵 VIP ANALİZ:</b> {h_input} Trendi {'🚀 GÜÇLÜ' if fiyat > ma20 else '⚠️ ZAYIF'}. 
                        <b>Hedefler:</b> <span style='color:#00ff88;'>{h1:.2f}</span> / <span style='color:#00ff88;'>{h2:.2f}</span> | 
                        <b>Sinyal:</b> {'Kademeli Alım Uygun' if fiyat > ma20 else 'Destek Beklenmeli'}.
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri Hatası")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 RADAR")
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "SASA"]:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r}</b><br>%2+ Hedef</div>", unsafe_allow_html=True)
        
        if st.session_state.get("role") == "admin":
            if st.button("🔑 Üret"): st.code(f"GAI-{int(time.time())}-30-VIP")
