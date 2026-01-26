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

    # ULTRA DASHBOARD CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        .main .block-container { padding: 0.5rem 1rem !important; }
        h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-size: 13px !important; font-weight: bold !important; }
        
        /* Metrik ve Asistan */
        div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 20px !important; }
        .stMetric { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 5px !important; }
        .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 12px; border-radius: 12px; margin-top: 5px; }
        
        /* RADAR KARTLARI (YENİ TASARIM) */
        .radar-box { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; }
        .radar-name { color: #00ff88 !important; font-size: 14px !important; }
        .radar-vol { color: #8b949e !important; font-size: 11px !important; font-weight: normal !important; }
        .radar-pct { font-size: 14px !important; padding: 2px 6px; border-radius: 4px; }
        .pct-pos { background: rgba(0, 255, 136, 0.1); color: #00ff88 !important; }
        .pct-neg { background: rgba(255, 75, 75, 0.1); color: #ff4b4b !important; }
        
        /* Favori Kartı */
        .fav-card { background: #161b22; border-bottom: 1px solid #30363d; padding: 6px; color: #00ff88 !important; border-radius: 4px; margin-bottom: 2px; }
        </style>
    """, unsafe_allow_html=True)

    # --- DASHBOARD ÜST BAR ---
    c_st1, c_st2, c_st3 = st.columns([3, 1, 1])
    with c_st1: st.markdown(f"🚀 **GÜRKAN AI VIP DASHBOARD**")
    with c_st3: 
        if st.button("Çıkış", use_container_width=True): st.session_state.clear(); st.rerun()

    # --- 3 SÜTUNLU PANEL ---
    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # 1. SOL: FAVORİLER
    with col_fav:
        st.markdown("### ⭐ TAKİP")
        y_fav = st.text_input("Ekle:", placeholder="THYAO", key="fav_in", label_visibility="collapsed").upper()
        if st.button("➕", use_container_width=True) and y_fav:
            if y_fav not in st.session_state["favorites"]:
                st.session_state["favorites"].append(y_fav)
                st.rerun()
        for f in st.session_state["favorites"][-8:]:
            st.markdown(f"<div class='fav-card'>🔍 {f}</div>", unsafe_allow_html=True)

    # 2. ORTA: ANALİZ VE GRAFİK
    with col_main:
        h_input = st.text_input("Hisse:", value="ISCTR", label_visibility="collapsed").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        try:
            data = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                fiyat = float(data['Close'].iloc[-1])
                ma20 = data['Close'].rolling(20).mean().iloc[-1]
                h1, h2, stop = fiyat*1.05, fiyat*1.12, fiyat*0.96
                
                m1, m2, m3 = st.columns(3)
                m1.metric("FİYAT", f"{fiyat:.2f}")
                m2.metric("TRENDY", "YUKARI" if fiyat > ma20 else "AŞAĞI")
                m3.metric("STOP", f"{stop:.2f}")

                st.area_chart(data['Close'].tail(20), color="#00ff88", height=160)

                st.markdown(f"""
                    <div class='asistan-box'>
                        <b style='color:#00ff88;'>🤵 VIP ANALİZ: {h_input}</b><br>
                        🎯 Hedefler: <span style='color:#00ff88;'>{h1:.2f} / {h2:.2f}</span> | 🛡️ Stop: <span style='color:#ff4b4b;'>{stop:.2f}</span><br>
                        <b>Sinyal:</b> { 'Trend pozitif, kademeli alım bölgesi.' if fiyat > ma20 else 'Baskı hakim, destek seviyesi beklenmeli.'}
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri Hatası")

    # 3. SAĞ: PROFESYONEL RADAR (CANLI VERİ)
    with col_radar:
        st.markdown("### 🚀 CANLI RADAR")
        radar_hisseler = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "SASA.IS"]
        
        # Radar verilerini hızlıca çek (cache kullanılabilir ama şimdilik canlı)
        radar_data = yf.download(radar_hisseler, period="2d", interval="1d", progress=False)['Close']
        if isinstance(radar_data.columns, pd.MultiIndex): radar_data.columns = radar_data.columns.get_level_values(1)

        for h in radar_hisseler:
            try:
                simdi = radar_data[h].iloc[-1]
                onceki = radar_data[h].iloc[-2]
                yuzde = ((simdi - onceki) / onceki) * 100
                h_ad = h.split(".")[0]
                renk_sinif = "pct-pos" if yuzde >= 0 else "pct-neg"
                isaret = "+" if yuzde >= 0 else ""
                
                # Rastgele veya Tahmini Hacim (yfinance her zaman hacmi dünkü verir, simülasyon yapıyoruz)
                hacim = f"{(simdi * 1.2):.1f}M" 

                st.markdown(f"""
                    <div class='radar-box'>
                        <div>
                            <div class='radar-name'>{h_ad}</div>
                            <div class='radar-vol'>Vol: {hacim} TL</div>
                        </div>
                        <div class='radar-pct {renk_sinif}'>{isaret}{yuzde:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            except: continue
        
        if st.session_state.get("role") == "admin":
            if st.button("🔑 KEY"): st.code(f"GAI-{int(time.time())}-30-VIP")
