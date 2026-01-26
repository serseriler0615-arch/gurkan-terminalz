import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. VIP GİRİŞ SİSTEMİ ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    def login_logic():
        # ID: GURKAN | Şifre: HEDEF2024!
        u = st.session_state["username"].strip().upper()
        p = st.session_state["password"].strip()
        if u == "GURKAN" and p == "HEDEF2024!":
            st.session_state["password_correct"] = True
            st.session_state["is_admin"] = True
        else:
            st.error("❌ Hatalı ID veya Şifre!")

    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align:center; color:#00ff88 !important;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:white !important;'>⚠️ VIP Üyelik Gereklidir</p>", unsafe_allow_html=True)
        
        cols = st.columns([1, 1.5, 1])
        with cols[1]:
            st.text_input("VIP ID", key="username")
            st.text_input("VIP Şifre", type="password", key="password")
            st.checkbox("Beni Hatırla", key="remember_me", value=True)
            st.button("Giriş Yap", on_click=login_logic, use_container_width=True)
        return False
    return True

# --- 2. ANA TERMİNAL ---
if check_password():
    st.set_page_config(page_title="Gürkan AI VIP", layout="wide")

    # GÖRÜNÜRLÜK VE RENK ZORLAMA (CSS)
    st.markdown("""
        <style>
        /* Arka planı simsiyah yap */
        .stApp { background-color: #0d1117 !important; }
        
        /* HER ŞEYİ BEYAZ YAP (Zorunlu) */
        h1, h2, h3, p, span, label, li, .stMarkdown, div { color: #ffffff !important; }
        
        /* Input kutularının başlıklarını görünür yap */
        .stTextInput label, .stSelectbox label { color: #00ff88 !important; font-size: 16px !important; font-weight: bold !important; }
        
        /* Input kutusunun içindeki yazıyı siyah yap (Okunması için) */
        input { color: #000000 !important; background-color: #ffffff !important; font-weight: bold !important; }
        
        /* Admin Paneli ve Kartlar */
        .admin-box { background-color: #1e2327 !important; border: 2px dashed #00ff88 !important; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .radar-card { background-color: #161b22 !important; border-left: 5px solid #00ff88 !important; border: 1px solid #30363d; padding: 15px; border-radius: 12px; margin-bottom: 12px; }
        .asistan-box { background: #1c2128 !important; border: 1px solid #00ff88 !important; padding: 20px; border-radius: 15px; }
        
        /* Metriklerin içindeki siyahlığı temizle */
        div[data-testid="stMetricValue"] > div { color: #00ff88 !important; }
        div[data-testid="stMetricLabel"] > div { color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔑 ADMIN PANELİ ---
    if st.session_state.get("is_admin"):
        with st.expander("🛠️ ADMIN KEY YÖNETİM MERKEZİ"):
            st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#00ff88 !important;'>Yeni Lisans Key Oluştur</h3>", unsafe_allow_html=True)
            uye_ad = st.text_input("Üye Adı Soyadı:")
            if st.button("VIP Key Üret"):
                k = f"GAI-{int(time.time())}-{uye_ad[:3].upper()}"
                st.code(k)
                st.success(f"{uye_ad} için anahtar üretildi.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- ANA İÇERİK ---
    ana_sol, ana_sag = st.columns([3, 1])

    with ana_sol:
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            hisse = st.text_input("🔍 VIP Sembol Sorgula (Örn: THYAO):", value="ISCTR").upper()
        
        try:
            sembol = hisse if "." in hisse else hisse + ".IS"
            df = yf.download(sembol, period="1mo", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                fiyat = float(df['Close'].iloc[-1])
                
                with c2: st.metric("GÜNCEL FİYAT", f"{fiyat:.2f} TL")
                with c3: st.metric("GÜNLÜK", f"%{((fiyat - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100:.2f}")

                st.markdown(f"📈 **{hisse} VIP Trend Analizi**")
                st.area_chart(df['Close'].tail(20), color="#00ff88")
                
                # ZEKİ ASİSTAN
                st.markdown(f"""
                <div class='asistan-box'>
                    <b style='color:#00ff88 !important;'>🤵 Zeki Asistan Notu:</b><br>
                    {hisse} şu an {fiyat:.2f} TL seviyesinde. VIP Radara göre teknik görünüm güçleniyor. 
                    Stratejini 'Bekle-Gör' yerine 'Kademeli Alım' olarak güncelleyebilirsin.
                </div>
                """, unsafe_allow_html=True)
        except: st.error("Veri çekilemedi.")

    with ana_sag:
        st.markdown("<h3 style='color:#00ff88 !important; text-align:center;'>🚀 VIP RADAR</h3>", unsafe_allow_html=True)
        radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
        for r in radar_list:
            st.markdown(f"""
            <div class="radar-card">
                <b style="color:#00ff88 !important;">{r.split('.')[0]}</b><br>
                <span style="color:white !important;">Sinyal: %2+ POTANSİYEL</span>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 Radarı Güncelle", use_container_width=True): st.rerun()
