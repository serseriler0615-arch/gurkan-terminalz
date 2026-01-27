import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

# --- 2. GİRİŞ KONTROLÜ (MOBİL DOSTU) ---
if not st.session_state["access_granted"]:
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h3 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h3>", unsafe_allow_html=True)
    
    # Form yerine sekmeli direkt giriş
    tab1, tab2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    
    with tab1:
        vip_k = st.text_input("Giriş Anahtarı", type="password", key="v_key")
        if st.button("SİSTEME BAĞLAN", use_container_width=True):
            if vip_k.strip().upper().startswith("GAI-"):
                st.session_state["access_granted"] = True
                st.rerun()
            else:
                st.error("Anahtar Hatalı!")

    with tab2:
        adm_u = st.text_input("Admin ID", key="a_user")
        adm_p = st.text_input("Şifre", type="password", key="a_pass")
        if st.button("ADMİN YETKİSİ AL", use_container_width=True):
            # Mobilde yazım hatasını önlemek için temizleme yapıyoruz
            if adm_u.strip().upper() == "GURKAN" and adm_p.strip().upper() == "HEDEF2026":
                st.session_state["access_granted"] = True
                st.rerun()
            else:
                st.error("Kimlik Doğrulanamadı!")
    st.stop() # Giriş yapılana kadar alt kodları çalıştırma

# --- 3. ANA UYGULAMA (GİRİŞTEN SONRA) ---
st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

# (Buradan aşağısı önceki v134/v135 kodunun aynısı...)
# Zeka motoru fonksiyonunu ve arayüzü buraya ekle...
st.success("Sisteme Başarıyla Girildi! Veriler yükleniyor...")

# Örnek içerik (Hata almamak için v134'teki get_advanced_analysis fonksiyonunu buraya eklemeyi unutma)
# ...
