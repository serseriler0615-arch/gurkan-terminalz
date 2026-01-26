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
        else:
            return "expired", None
    except:
        return False, None

# --- 2. GİRİŞ KONTROLÜ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

if not st.session_state["access_granted"]:
    st.set_page_config(page_title="VIP Giriş", layout="centered")
    
    # GİRİŞ EKRANI İÇİN ÖZEL BEYAZ YAZI CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; font-weight: bold !important; }
        .stTextInput input { color: #000000 !important; background-color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["💎 VIP KEY AKTİVASYON", "🔐 ADMIN GİRİŞİ"])
    
    with tab1:
        v_key = st.text_input("VIP Lisans Anahtarınız", placeholder="GAI-XXXX-XXXX")
        st.checkbox("Beni Hatırla", key="remember_me", value=True)
        if st.button("Sistemi Aktive Et"):
            status, bitis = validate_key(v_key)
            if status == True:
                st.session_state["access_granted"] = True
                st.session_state["role"] = "user"
                st.rerun()
            else:
                st.error("Key Geçersiz veya Süresi Dolmuş!")
    
    with tab2:
        u = st.text_input("Yönetici ID")
        p = st.text_input("Yönetici Şifre", type="password")
        if st.button("Yönetici Girişi"):
            if u.upper() == "GURKAN" and p == "HEDEF2024!":
                st.session_state["access_granted"] = True
                st.session_state["role"] = "admin"
                st.rerun()
    st.stop()

# --- 3. ANA TERMİNAL (BÜTÜN YAZILAR BEYAZA ZORLANDI) ---
st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide")

st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #0d1117 !important; }
    
    /* TÜM YAZILARI BEYAZ YAP (Önemli: Burası her şeyi okutur) */
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Input kutularının başlıklarını Neon Yeşil Yap */
    .stTextInput label { color: #00ff88 !important; }
    
    /* Metrik Değerleri (Fiyatlar) */
    div[data-testid="stMetricValue"] { color: #00ff88 !important; }
    
    /* Kartlar ve Kutular */
    .radar-card { background-color: #161b22; border-left: 5px solid #00ff88; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363d; }
    .asistan-box { background: #1c2128; border: 1px solid #00ff88; padding: 20px; border-radius: 15px; }
    
    /* Tablo ve Grafik başlıklarını beyazlat */
    .stPlotlyChart text { fill: white !important; }
    </style>
""", unsafe_allow_html=True)

# ÜST PANEL
if st.session_state["role"] == "admin":
    with st.expander("🛠️ ADMIN KEY MERKEZİ"):
        u_ad = st.text_input("Üye Adı:")
        l_sure = st.selectbox("Süre:", [1, 7, 30, 365], format_func=lambda x: f"{x} Gün")
        if st.button("Bekleyen Key Üret"):
            generated = f"GAI-{int(time.time())}-{l_sure}-{u_ad[:3].upper()}"
            st.code(generated)

sol, sag = st.columns([3, 1])

with sol:
    if st.session_state["role"] == "user":
        st.success(f"🔔 VIP Üyeliğiniz Aktif. Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    
    st.markdown("<h1 style='color:#00ff88 !important;'>📈 VIP Analiz Paneli</h1>", unsafe_allow_html=True)
    h_input = st.text_input("🔍 Hisse Sembolü Sorgula:", value="ISCTR").upper()
    
    try:
        sembol = h_input if "." in h_input else h_input + ".IS"
        df = yf.download(sembol, period="1mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            fiyat = float(df['Close'].iloc[-1])
            
            c1, c2 = st.columns(2)
            c1.metric("GÜNCEL FİYAT", f"{fiyat:.2f} TL")
            c2.metric("GÜNLÜK DEĞİŞİM", f"%{((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100:.2f}")
            
            st.area_chart(df['Close'].tail(20), color="#00ff88")
            
            st.markdown(f"""
                <div class='asistan-box'>
                    <h3 style='color:#00ff88 !important; margin-top:0;'>🤵 VIP Asistan Analizi</h3>
                    <p style='color:white !important;'>{h_input} hissesi için teknik veriler okundu. 
                    Şu anki {fiyat:.2f} seviyesi VIP radarımızla %100 uyumlu ilerliyor.</p>
                </div>
            """, unsafe_allow_html=True)
    except: st.error("Veri Alınamadı.")

with sag:
    st.markdown("<h2 style='color:#00ff88 !important; text-align:center;'>🚀 VIP RADAR</h2>", unsafe_allow_html=True)
    for r in ["THYAO.IS", "ASELS.IS", "EREGL.IS", "SASA.IS", "TUPRS.IS"]:
        st.markdown(f"""
            <div class="radar-card">
                <b style="color:#00ff88 !important;">{r.split('.')[0]}</b><br>
                <span style="color:white !important;">Sinyal: %2+ Potansiyel</span>
            </div>
        """, unsafe_allow_html=True)

if st.button("Çıkış Yap"):
    st.session_state.clear()
    st.rerun()
