import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# --- 1. OTURUM HAFIZASI (Sıfırlama Korumalı) ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "ISCTR"
if "favorites" not in st.session_state:
    st.session_state["favorites"] = ["THYAO", "ASELS", "ISCTR", "EREGL"]

# --- 🔐 GİRİŞ PANELİ (KESİN ÇÖZÜM) ---
def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP Login", layout="centered")
        st.markdown("<h2 style='text-align: center; color: #ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
        
        tab_vip, tab_admin = st.tabs(["💎 VIP KEY GİRİŞİ", "🔐 YÖNETİCİ PANELİ"])
        
        with tab_vip:
            vip_k = st.text_input("Giriş Anahtarı", type="password", key="main_vip_input")
            if st.button("Sistemi Başlat", use_container_width=True):
                if vip_k.strip().upper().startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"
                    st.rerun()
                else: st.error("Geçersiz Anahtar!")

        with tab_admin:
            # Buradaki şifreleri kontrol et: GURKAN / HEDEF2026!
            adm_id = st.text_input("Yönetici ID", key="main_adm_id")
            adm_ps = st.text_input("Yönetici Şifre", type="password", key="main_adm_ps")
            if st.button("Yönetici Girişi Yap", use_container_width=True):
                # Boşlukları siler (.strip) ve ID'yi büyütür (.upper)
                if adm_id.strip().upper() == "GURKAN" and adm_ps.strip() == "HEDEF2026!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"
                    st.rerun()
                else:
                    st.error(f"Hatalı Giriş! Şifrenin 'HEDEF2026!' olduğundan emin ol.")
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 PRO DARK CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .main-header { font-size: 22px; font-weight: bold; color: #ffcc00; }
        .gurkan-ai-box { background: #0d1117; border: 1px solid #1c2128; padding: 15px; border-radius: 8px; border-left: 5px solid #ffcc00; margin-bottom: 10px; }
        .guven-box { background: rgba(0, 255, 136, 0.05); border: 1px solid #00ff88; padding: 12px; border-radius: 8px; text-align: center; }
        div.stButton > button { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; text-align: left !important; }
        .active-btn button { background-color: #00c853 !important; border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 👑 ADMIN ÜST PANEL (SADECE ADMİNE GÖRÜNÜR) ---
    if st.session_state["role"] == "admin":
        with st.container():
            st.markdown("<div style='border:1px solid #ffcc00; padding:10px; border-radius:5px; margin-bottom:15px;'>", unsafe_allow_html=True)
            ac1, ac2, ac3, ac4 = st.columns([1, 1, 2, 0.5])
            with ac1: s_gun = st.selectbox("Süre", [30, 90, 365], label_visibility="collapsed")
            with ac2: 
                if st.button("💎 LİSANS ÜRET"): 
                    st.session_state["gen_key"] = f"GAI-{s_gun}-{int(time.time())%1000}-VIP"
            with ac3: 
                if "gen_key" in st.session_state: st.code(st.session_state["gen_key"])
            with ac4:
                if st.button("🚪"): 
                    st.session_state["access_granted"] = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- ANA ARAYÜZ ---
    h_col1, h_col2 = st.columns([1.2, 4])
    with h_col1: st.markdown("<div class='main-header'>★ GÜRKAN AI PRO</div>", unsafe_allow_html=True)
    with h_col2: h_input = st.text_input("", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()

    col_side, col_main, col_radar = st.columns([0.7, 3, 1.3])

    # SOL MENÜ
    with col_side:
        for f in st.session_state["favorites"]:
            is_active = "active-btn" if f == h_input else ""
            st.markdown(f"<div class='{is_active}'>", unsafe_allow_html=True)
            if st.button(f"🔍 {f}", key=f"fav_btn_{f}", use_container_width=True):
                st.session_state["last_sorgu"] = f; st.rerun()
            st.markdown("
