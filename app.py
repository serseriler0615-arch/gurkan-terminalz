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

    # DASHBOARD STİLİ (Tek Ekran Odaklı)
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        
        /* Yazılar ve Başlıklar */
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        h1 { font-size: 18px !important; color: #00ff88 !important; }
        
        /* Metrikler */
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 20px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        
        /* VIP ASİSTAN KUTUSU (Gelişmiş) */
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        .trendy-title { color: #00ff88 !important; font-size: 15px !important; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 8px; }
        .target-text { color: #00ff88 !important; font-weight: bold; }
        .stop-text { color: #ff4b4b !important; font-weight: bold; }
        
        /* Kartlar */
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 6px; color: #00ff88 !important; border-radius: 4px; margin-bottom: 2px; }
        .radar-card { background: #161b22; border-left: 4px solid #00ff88; padding: 8px; margin-bottom: 4px; border-radius: 6px; border: 1px solid #30363d; }
        </style>
    """, unsafe_allow_html=True)

    # --- ÜST BAR ---
    c_st1, c_st2, c_st3 = st.columns([3, 1, 1])
    with c_st1: st.markdown(f"🚀 **GÜRKAN AI VIP DASHBOARD**")
    with c_st2: 
        if st.session_state["role"] == "user": st.markdown(f"⌛ Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    with c_st3: 
        if st.button("Çıkış", use_container_width=True): st.session_state.clear(); st.rerun()

    # --- 3 SÜTUNLU PANEL ---
    col_fav, col_main, col_radar = st.columns([0.7, 3.2, 1.1])

    # 1. SOL: FAVORİ TAKİP
    with col_fav:
        st.markdown("### ⭐ FAVORİLER")
        y_fav = st.text_input("Ekle:", placeholder="THYAO", key="fav_input", label_visibility="collapsed").upper()
        if st.button("➕ EKLE", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-8:]:
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ MERKEZİ
    with col_main:
        h_input = st.text_input("Sembol Sorgu:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                
                # Trendy Hedefler
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96
                trendy_yon = "YUKARI" if fiyat > ma20 else "AŞAĞI"

                # Metrikler
                m1, m2, m3 = st.columns(3)
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("TRENDY", trendy_yon)
                m3.metric("ZARAR KES", f"{stop:.2f}")

                # RENKLİ VE KÜÇÜLTÜLMÜŞ GRAFİK
                st.area_chart(df['Close'].tail(20), color="#00ff88", height=160) # Yükseklik 160'a çekildi

                # DETAYLI ASİSTAN (Önceki Stil)
                st.markdown(f"""
                    <div class='asistan-box'>
                        <div class='trendy-title'>🤵 VIP STRATEJİ RAPORU: {h_input}</div>
                        <p style='margin-bottom:5px;'>📊 <b>Trend Yönü:</b> <span style='color:{"#00ff88" if trendy_yon=="YUKARI" else "#ff4b4b"};'>{trendy_yon}</span></p>
                        <p style='margin-bottom:5px;'>🎯 <b>Kısa Hedef:</b> <span class='target-text'>{h1:.2f} TL</span> | 🏆 <b>Ana Hedef:</b> <span class='target-text'>{h2:.2f} TL</span></p>
                        <p style='margin-bottom:5px;'>🛡️ <b>Zarar Kes:</b> <span class='stop-text'>{stop:.2f} TL</span></p>
                        <p style='border-top:1px solid #333; padding-top:5px; margin-top:5px;'>
                        <b>Sinyal:</b> { 'Kademeli alım uygun görünüyor, trend pozitif.' if trendy_yon == "YUKARI" else 'Baskı devam ediyor, stop seviyesi takip edilmeli.'}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Sembol bulunamadı veya veri hatası.")

    # 3. SAĞ: VIP RADAR
    with col_radar:
        st.markdown("### 🚀 VIP RADAR")
        for r in ["THYAO", "ASELS", "EREGL", "TUPRS", "SASA"]:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r}</b><br>%2+ Potansiyel</div>", unsafe_allow_html=True)
        
        if st.session_state.get("role") == "admin":
            if st.button("🔑 KEY"): st.code(f"GAI-{int(time.time())}-30-VIP")
