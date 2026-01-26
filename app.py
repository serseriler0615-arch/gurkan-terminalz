import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. VIP GÜVENLİK & LİSANS SİSTEMİ ---
def check_password():
    # Tarayıcıda bilgileri tutmak için session_state başlatma
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    def login_logic():
        # ID: GURKAN | Şifre: HEDEF2024!
        u_input = st.session_state["username"].strip().upper()
        p_input = st.session_state["password"].strip()
        
        if u_input == "GURKAN" and p_input == "HEDEF2024!":
            st.session_state["password_correct"] = True
            st.session_state["is_admin"] = True # Yönetici yetkisi
            if st.session_state["remember_me"]:
                # Beni hatırla seçilirse (Basit simülasyon)
                st.toast("Giriş bilgileri bu oturum için kaydedildi.")
        else:
            st.error("❌ Hatalı ID veya Şifre!")

    if not st.session_state["password_correct"]:
        st.markdown("""
            <div style='text-align: center;'>
                <h1 style='color: #00ff88;'>Gürkan AI VIP Terminal</h1>
                <p style='color: #888;'>⚠️ Bu Terminal Gürkan AI VIP Üyelik Gerektirir</p>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1.5, 1])
        with cols[1]:
            st.text_input("VIP ID", key="username")
            st.text_input("VIP Şifre", type="password", key="password")
            st.checkbox("Beni Hatırla", key="remember_me")
            st.button("Terminale Güvenli Giriş", on_click=login_logic, use_container_width=True)
            st.markdown("<p style='text-align: center; font-size: 11px; color: #444;'>Gürkan AI Licensing System v1.0</p>", unsafe_allow_html=True)
        return False
    return True

# Giriş Başarılıysa
if check_password():
    st.set_page_config(page_title="Gürkan AI - Pro Terminal", layout="wide")

    # Stil Ayarları
    st.markdown("""
        <style>
        .stApp { background-color: #0d1117 !important; }
        header {visibility: hidden;}
        .admin-panel { background-color: #1e2327; border: 1px dashed #00ff88; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- 🔑 SADECE ADMİN İÇİN KEY OLUŞTURUCU ---
    if st.session_state["is_admin"]:
        with st.expander("🛠️ YÖNETİCİ PANELİ (Sadece Sen Görebilirsin)"):
            st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
            st.write("🔑 **Yeni Üye İçin VIP Key Oluştur**")
            uye_adi = st.text_input("Üye Adı Soyadı:")
            if st.button("Lisans Key Üret"):
                new_key = f"GAI-{int(time.time())}-{uye_adi[:3].upper()}"
                st.code(new_key, language="text")
                st.success(f"{uye_adi} için lisans anahtarı oluşturuldu. Bu anahtarı üyeye iletebilirsin.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- ANA TERMİNAL ---
    sol, sag = st.columns([3, 1])
    
    with sol:
        h_input = st.text_input("🔍 VIP Sembol Sorgula:", value="ISCTR").upper()
        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            ticker = yf.Ticker(sembol)
            df = ticker.history(period="1mo")
            if not df.empty:
                st.metric(f"{h_input} - CANLI", f"{ticker.fast_info['last_price']:.2f} TL")
                st.area_chart(df['Close'].tail(20), color="#00ff88")
                st.info(f"🤵 **VIP Asistan:** {h_input} hissesinde momentum pozitif, 10:00 açılışı için radarda tutulmalı.")
        except:
            st.warning("Veri çekilemedi.")

    with sag:
        st.markdown("<h3 style='color:#00ff88;'>🚀 VIP RADAR</h3>", unsafe_allow_html=True)
        vip_liste = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "TUPRS.IS"]
        for v in vip_liste:
            st.markdown(f"<div class='radar-card'><b style='color:#00ff88;'>{v.split('.')[0]}</b><br>Sinyal: %2+ Potansiyel</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Radarı Tara"): st.rerun()
