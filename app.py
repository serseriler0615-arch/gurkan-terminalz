import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# --- 1. LİSANS DOĞRULAMA FONKSİYONU ---
def validate_key(key):
    try:
        # Key formatı: GAI-BaslangicTimestamp-BitisTimestamp-İsim
        parts = key.split("-")
        if len(parts) != 4: return False
        
        bitis_timestamp = int(parts[2])
        simdi = int(time.time())
        
        # Eğer şu anki zaman bitiş zamanından küçükse Key geçerlidir
        if simdi < bitis_timestamp:
            return True
        else:
            return "expired"
    except:
        return False

# --- 2. GİRİŞ SİSTEMİ ---
def check_access():
    if "access_granted" not in st.session_state:
        st.session_state["access_granted"] = False

    if not st.session_state["access_granted"]:
        st.markdown("<h1 style='text-align:center; color:#00ff88;'>Gürkan AI VIP Terminal</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 ADMIN GİRİŞİ"])
        
        with tab1:
            vip_key = st.text_input("VIP Lisans Anahtarınız", placeholder="GAI-XXXX-XXXX-XXXX")
            if st.button("Erişimi Doğrula"):
                status = validate_key(vip_key)
                if status == True:
                    st.session_state["access_granted"] = True
                    st.session_state["role"] = "user"
                    st.rerun()
                elif status == "expired":
                    st.error("❌ Bu anahtarın süresi dolmuş! Lütfen yenileyin.")
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
    st.set_page_config(page_title="Gürkan AI VIP", layout="wide")

    # ADMIN PANELİ: SÜRELİ KEY ÜRETME
    if st.session_state["role"] == "admin":
        with st.expander("🛠️ ADMIN KEY ÜRETİM MERKEZİ"):
            c1, c2 = st.columns(2)
            with c1:
                uye_ad = st.text_input("Üye Adı:")
            with c2:
                gun_sayisi = st.number_input("Lisans Süresi (Gün):", min_value=1, value=30)
            
            if st.button("Süreli VIP Key Oluştur"):
                baslangic = int(time.time())
                # Saniyeyi güne çevir: gün * 24 saat * 60 dak * 60 san
                bitis = baslangic + (gun_sayisi * 86400)
                new_key = f"GAI-{baslangic}-{bitis}-{uye_ad[:3].upper()}"
                
                st.subheader("Üretilen Süreli Key:")
                st.code(new_key)
                bitis_tarihi = datetime.fromtimestamp(bitis).strftime('%d/%m/%Y')
                st.success(f"Bu anahtar {bitis_tarihi} tarihine kadar (%{gun_sayisi} gün) geçerlidir.")

    # --- TERMİNAL İÇERİĞİ (GRAFİKLER VE RADAR) ---
    st.title("📈 VIP Strateji Paneli")
    # (Buraya önceki bölümlerdeki grafik ve radar kodlarını ekleyebilirsin)
    st.info("VIP Lisansınız Aktif. İyi kazançlar!")
