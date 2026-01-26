import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SÜRE VE GİRİŞ SİSTEMİ ---
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
                else:
                    st.error("Geçersiz Key!")
        with t2:
            u = st.text_input("Yönetici ID", key="admin_id")
            p = st.text_input("Yönetici Şifre", type="password", key="admin_pass")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
                else:
                    st.error("Admin Bilgileri Hatalı!")
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide", initial_sidebar_state="collapsed")

    # TEK EKRAN TASARIMI (CSS - OKUNABİLİR YAZILAR)
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-size: 14px !important; font-weight: bold !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 15px; border-radius: 12px; }
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 8px; margin-bottom: 2px; color: #00ff88 !important; }
        .radar-card { background: #161b22; border-left: 4px solid #00ff88; padding: 10px; margin-bottom: 5px; border: 1px solid #30363d; }
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 22px !important; }
        .main .block-container { padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST PANEL ---
    c_st1, c_st2, c_st3 = st.columns([2, 2, 1])
    with c_st1: st.markdown(f"⭐ **Gürkan AI VIP Dashboard** | {datetime.now().strftime('%H:%M')}")
    with c_st2: 
        if st.session_state.get("role") == "user":
            st.markdown(f"⏳ **Kalan Süre:** {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Güvenli Çıkış", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

    # --- ANA DASHBOARD (3 SÜTUN) ---
    col_fav, col_main, col_radar = st.columns([0.8, 3, 1.2])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        yeni_fav = st.text_input("Ekle:", placeholder="SASA", label_visibility="collapsed").upper()
        if st.button("Listeye Ekle", use_container_width=True) and yeni_fav:
            if yeni_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(yeni_fav)
                st.rerun()
        
        for f in st.session_state["favorites"][-6:]:
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)
        
        if st.button("Temizle"): 
            st.session_state["favorites"] = []
            st.rerun()

    # 2. ORTA: ANA ANALİZ VE GRAFİK
    with col_main:
        h_input = st.text_input("Hisse Sorgula:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="3mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                degisim = ((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # Metrikler
                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("FİYAT", f"{fiyat:.2f} TL")
                m_c2.metric("GÜNLÜK", f"%{degisim:.2f}")
                m_c3.metric("MA20", f"{ma20:.2f}")
                
                # Kompakt Grafik
                st.area_chart(df['Close'].tail(30), color="#00ff88", height=220)

                # DETAYLI ASİSTAN RAPORU
                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88; font-size:16px;'>🤵 VIP ANALİZ: {h_input}</b><br>
                        <p style='margin-top:5px;'><b>Trend:</b> {'🚀 Pozitif Trend' if fiyat > ma20 else '⚠️ Satış Baskısı'}<br>
                        <b>Strateji:</b> Teknik analizde {h_input} için {fiyat:.2f} seviyesi {'güçlü duruyor. VIP Radar alım yönünde.' if fiyat > ma20 else 'biraz zayıf. Destek noktaları takip edilmeli.'}</p>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.error("Veri alınırken hata oluştu.")

    # 3. SAĞ: VIP RADAR & ADMIN
    with col_radar:
        st.markdown("### 🚀 VIP RADAR")
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "SASA"]:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r}</b><br>Potansiyel: %2+</div>", unsafe_allow_html=True)
        
        if st.session_state.get("role") == "admin":
            st.markdown("---")
            if st.button("🔑 Yeni Key Üret"):
                st.code(f"GAI-{int(time.time())}-30-VIP")
