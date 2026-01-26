import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. SÜRE VE KEY SİSTEMİ ---
def validate_key(key_input):
    try:
        parts = key_input.split("-")
        if len(parts) < 4: return False, None
        gun_sayisi = int(parts[2])
        if "bitis_tarihi" not in st.session_state:
            st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=gun_sayisi)
        simdi = datetime.now()
        if simdi < st.session_state["bitis_tarihi"]:
            return True, st.session_state["bitis_tarihi"]
        else: return "expired", None
    except: return False, None

# --- 2. GİRİŞ KONTROLÜ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="VIP Giriş", layout="centered")
    st.markdown("<style>.stApp { background-color: #0d1117 !important; } h1, h2, h3, p, span, label { color: #ffffff !important; font-weight: bold !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💎 VIP KEY AKTİVASYON", "🔐 ADMIN GİRİŞİ"])
    with tab1:
        v_key = st.text_input("VIP Lisans Anahtarınız", placeholder="GAI-XXXX-XXXX")
        if st.button("Sistemi Aktive Et"):
            status, bitis = validate_key(v_key)
            if status == True:
                st.session_state["access_granted"] = True
                st.session_state["role"] = "user"
                st.rerun()
            else: st.error("Key Geçersiz!")
    with tab2:
        u = st.text_input("Yönetici ID")
        p = st.text_input("Yönetici Şifre", type="password")
        if st.button("Yönetici Girişi"):
            if u.upper() == "GURKAN" and p == "HEDEF2024!":
                st.session_state["access_granted"] = True
                st.session_state["role"] = "admin"
                st.rerun()
    st.stop()

# --- 3. ANA TERMİNAL ---
st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide")

# OKUNABİLİRLİK CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; font-weight: 600 !important; }
    .stTextInput label { color: #00ff88 !important; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; }
    .asistan-box { background: #1c2128; border: 2px solid #00ff88; padding: 25px; border-radius: 15px; margin-top: 15px; }
    .asistan-header { color: #00ff88 !important; font-size: 22px; margin-bottom: 10px; border-bottom: 1px solid #00ff88; padding-bottom: 5px; }
    .trend-badge { background: #00ff88; color: black; padding: 2px 10px; border-radius: 5px; font-weight: bold; }
    .radar-card { background-color: #161b22; border-left: 5px solid #00ff88; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# ADMIN PANELİ
if st.session_state["role"] == "admin":
    with st.expander("🛠️ ADMIN KEY MERKEZİ"):
        u_ad = st.text_input("Üye Adı:")
        l_sure = st.selectbox("Süre:", [1, 7, 30, 365], format_func=lambda x: f"{x} Gün")
        if st.button("Bekleyen Key Üret"):
            st.code(f"GAI-{int(time.time())}-{l_sure}-{u_ad[:3].upper()}")

sol, sag = st.columns([3, 1])

with sol:
    if st.session_state["role"] == "user":
        st.success(f"🔔 VIP Lisans Aktif | Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    
    st.markdown("<h1 style='color:#00ff88 !important;'>📈 VIP Teknik Analiz</h1>", unsafe_allow_html=True)
    h_input = st.text_input("🔍 Hisse Sembolü:", value="ISCTR").upper()
    
    try:
        sembol = h_input if "." in h_input else h_input + ".IS"
        df = yf.download(sembol, period="6mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # TEKNİK HESAPLAMALAR
            son_fiyat = float(df['Close'].iloc[-1])
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            
            # RSI Hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Trend Belirleme
            trend = "YUKARI (BULLISH)" if son_fiyat > ma20 else "AŞAĞI (BEARISH)"
            
            # METRİKLER
            c1, c2, c3 = st.columns(3)
            c1.metric("FİYAT", f"{son_fiyat:.2f} TL")
            c2.metric("RSI (14)", f"{rsi:.1f}")
            c3.metric("MA20 DESTEĞİ", f"{ma20:.2f}")

            st.area_chart(df['Close'].tail(30), color="#00ff88")

            # --- DETAYLI VIP ASİSTAN ---
            st.markdown(f"""
                <div class='asistan-box'>
                    <div class='asistan-header'>🤵 Gürkan AI Strateji Raporu</div>
                    <p><b>Hisse:</b> {h_input} | <b>Analiz Tarihi:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                    <p>📊 <b>Genel Trend:</b> <span class='trend-badge'>{trend}</span></p>
                    <p>🚀 <b>RSI Durumu:</b> {"Aşırı Alım Bölgesi (Dikkat!)" if rsi > 70 else "Aşırı Satım (Fırsat Olabilir)" if rsi < 30 else "Nötr Bölge (Güvenli)"}</p>
                    <p>📉 <b>Destek/Direnç:</b> Mevcut fiyat MA20 seviyesinin {"<b>üzerinde</b>, bu olumlu bir işaret." if son_fiyat > ma20 else "<b>altında</b>, baskı sürebilir."}</p>
                    <hr style='border-color:#333;'>
                    <p style='color:#00ff88;'><b>VIP TAVSİYE:</b> {h_input} için mevcut momentum { "korunuyor. Kademeli alım düşünülebilir." if trend == "YUKARI (BULLISH)" else "zayıf. Güçlenmesi beklenmeli."}</p>
                </div>
            """, unsafe_allow_html=True)
    except: st.error("Veri Alınamadı.")

with sag:
    st.markdown("<h2 style='color:#00ff88 !important; text-align:center;'>🚀 VIP RADAR</h2>", unsafe_allow_html=True)
    for r in ["THYAO.IS", "ASELS.IS", "EREGL.IS", "SASA.IS", "TUPRS.IS"]:
        st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r.split('.')[0]}</b><br><span style='color:white;'>Sinyal: %2+ Potansiyel</span></div>", unsafe_allow_html=True)
