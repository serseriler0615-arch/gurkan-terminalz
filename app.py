import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. VIP LİSANS VE GİRİŞ SİSTEMİ ---
def check_access():
    if "access_granted" not in st.session_state:
        st.session_state["access_granted"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = None

    if not st.session_state["access_granted"]:
        st.markdown("<h1 style='text-align:center; color:#00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        
        # İki Sekmeli Giriş: Üye ve Admin
        tab1, tab2 = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 ADMIN GİRİŞİ"])
        
        with tab1:
            st.markdown("<p style='color:white;'>Size özel tanımlanan VIP Lisans Anahtarını giriniz:</p>", unsafe_allow_html=True)
            vip_key = st.text_input("Lisans Anahtarı (Key)", placeholder="GAI-XXXX-XXXX")
            if st.button("VIP Erişimi Başlat"):
                # Basit bir kontrol: Key 'GAI' ile başlıyorsa ve 10 karakterden uzunsa (Geliştirilebilir)
                if vip_key.startswith("GAI-") and len(vip_key) > 10:
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.rerun()
                else:
                    st.error("Geçersiz Lisans Anahtarı! Lütfen @GurkanAI ile iletişime geçin.")

        with tab2:
            admin_id = st.text_input("Yönetici ID")
            admin_pass = st.text_input("Yönetici Şifre", type="password")
            if st.button("Yönetici Olarak Giriş Yap"):
                if admin_id.upper() == "GURKAN" and admin_pass == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
                else:
                    st.error("Admin bilgileri hatalı!")
        return False
    return True

# --- 2. ANA TERMİNAL ---
if check_access():
    st.set_page_config(page_title="Gürkan AI VIP", layout="wide")
    
    # Görünürlük CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        h1, h2, h3, p, span, label { color: #ffffff !important; }
        .stTextInput label { color: #00ff88 !important; }
        .radar-card { background-color: #161b22; border-left: 5px solid #00ff88; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363d; }
        .admin-box { background: #1e2327; border: 1px dashed #00ff88; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # ADMİN PANELİ (SADECE ADMİN GÖRÜR)
    if st.session_state["role"] == "admin":
        with st.expander("🛠️ ADMIN KEY ÜRETİM MERKEZİ"):
            st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
            uye_ad = st.text_input("Yeni Üye Adı:")
            if st.button("Yeni Lisans Key Oluştur"):
                # Ürettiğin bu keyi kopyalayıp üyeye vereceksin
                generated_key = f"GAI-{int(time.time())}-{uye_ad[:3].upper()}"
                st.subheader("Üretilen Key (Kopyalayın):")
                st.code(generated_key)
                st.success(f"{uye_ad} için lisans hazır!")
            st.markdown("</div>", unsafe_allow_html=True)

    # TERMİNAL İÇERİĞİ
    sol, sag = st.columns([3, 1])
    with sol:
        st.title("📈 VIP Analiz Paneli")
        hisse = st.text_input("Hisse Sembolü Girin:", value="ISCTR").upper()
        # ... (Grafik ve Asistan Analiz Kodları Buraya Gelecek) ...
        st.area_chart(yf.download(hisse+".IS", period="1mo", progress=False)['Close'], color="#00ff88")

    with sag:
        st.markdown("### 🚀 VIP RADAR")
        # Radar Listesi
        for r in ["THYAO", "ASELS", "EREGL"]:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{r}</b><br>Potansiyel: %2+</div>", unsafe_allow_html=True)

    if st.button("Çıkış Yap"):
        st.session_state["access_granted"] = False
        st.rerun()
