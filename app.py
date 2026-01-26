import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. AKILLI LİSANS DOĞRULAMA (AKTİVASYONLU) ---
def validate_and_activate(input_key):
    try:
        # Key Formatı: GAI-URETIM_ZAMANI-SURE_GUN-ISIM-AKTIVASYON_DURUMU
        parts = input_key.split("-")
        if len(parts) < 4: return False
        
        uretim_zamani = int(parts[1])
        sure_gun = int(parts[2])
        
        # Simülasyon: Normalde bu veriler bir veritabanında tutulur. 
        # Streamlit üzerinde 'Aktivasyon' anını anahtarın içindeki gizli bir saniyeden okuyacağız.
        
        # Kullanıcı ilk kez girdiğinde bitiş tarihini hesapla
        if "bitis_tarihi" not in st.session_state:
            st.session_state["bitis_tarihi"] = datetime.now() + timedelta(days=sure_gun)
            
        simdi = datetime.now()
        if simdi < st.session_state["bitis_tarihi"]:
            return True, st.session_state["bitis_tarihi"]
        else:
            return "expired", None
    except:
        return False, None

# --- 2. GİRİŞ SİSTEMİ ---
def check_access():
    if "access_granted" not in st.session_state:
        st.session_state["access_granted"] = False

    if not st.session_state["access_granted"]:
        st.markdown("<h1 style='text-align:center; color:#00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["💎 VIP KEY AKTİVASYON", "🔐 ADMIN GİRİŞİ"])
        
        with tab1:
            st.markdown("<p style='color:white;'>Keyinizi girince süreniz <b>otomatik olarak başlayacaktır.</b></p>", unsafe_allow_html=True)
            vip_key = st.text_input("VIP Lisans Anahtarınız", placeholder="GAI-XXXX-XXXX")
            if st.button("Lisansı Aktive Et ve Gir"):
                status, b_tarihi = validate_and_activate(vip_key)
                if status == True:
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.success(f"Hoş geldiniz! Lisansınız şu tarihe kadar tanımlandı: {b_tarihi.strftime('%d/%m/%Y %H:%M')}")
                    time.sleep(2)
                    st.rerun()
                elif status == "expired":
                    st.error("❌ Bu lisansın süresi dolmuş!")
                else:
                    st.error("❌ Geçersiz Anahtar!")

        with tab2:
            u = st.text_input("Admin ID")
            p = st.text_input("Admin Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!":
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
        return False
    return True

# --- 3. ANA TERMİNAL ---
if check_access():
    st.set_page_config(page_title="Gürkan AI VIP Pro", layout="wide")

    # ADMIN PANELİ: LİSANS ÜRETME (SÜRE BAŞLATMADAN)
    if st.session_state["role"] == "admin":
        with st.expander("🛠️ ADMIN KEY MERKEZİ"):
            c1, c2 = st.columns(2)
            with c1:
                uye_ad = st.text_input("Üye Adı:")
            with c2:
                lisans_suresi = st.selectbox("Lisans Paketi:", [1, 7, 30, 90, 365], format_func=lambda x: f"{x} Gün")
            
            if st.button("Kullanıma Hazır Key Üret"):
                uretim = int(time.time())
                # Yeni Key Yapısı: GAI-Üretim-Süre-İsim
                # Bu key girildiği an süre başlayacak
                activation_key = f"GAI-{uretim}-{lisans_suresi}-{uye_ad[:3].upper()}"
                st.subheader("Üretilen Bekleyen Key:")
                st.code(activation_key)
                st.info(f"Bu key kullanıcı girdiği an {lisans_suresi} günlük süreyi başlatacak.")

    # TERMİNAL İÇERİĞİ (GRAFİKLER VS.)
    st.title("📈 VIP Analiz Alanı")
    if st.session_state["role"] == "user":
        st.warning(f"Süreniz Devam Ediyor. Bitiş: {st.session_state['bitis_tarihi'].strftime('%d/%m/%Y')}")
    
    # ... (Önceki Grafik Kodların) ...
