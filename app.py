import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. GÜVENLİK VE GİRİŞ KONTROLÜ ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False

def login_panel():
    st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🤵 GÜRKAN AI PRO</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💎 VIP GİRİŞ", "🔐 ADMİN"])
    
    with tab1:
        with st.form("vip_form"):
            key = st.text_input("Giriş Anahtarı", type="password", placeholder="GAI-XXXX")
            submit = st.form_submit_button("SİSTEME BAĞLAN", use_container_width=True)
            if submit:
                if key.strip().upper().startswith("GAI-"):
                    st.session_state["access_granted"] = True
                    st.rerun()
                else:
                    st.error("Geçersiz Anahtar!")

    with tab2:
        with st.form("admin_form"):
            admin_user = st.text_input("Admin ID")
            admin_pass = st.text_input("Şifre", type="password")
            admin_submit = st.form_submit_button("ADMİN YETKİSİ AL")
            if admin_submit:
                if admin_user == "GURKAN" and admin_pass == "HEDEF2026":
                    st.session_state["access_granted"] = True
                    st.success("Hoş geldin patron!")
                    st.rerun()
                else:
                    st.error("Yetkisiz Erişim!")

# --- 2. ANA UYGULAMA DÖNGÜSÜ ---
if not st.session_state["access_granted"]:
    login_panel()
else:
    # --- EĞER GİRİŞ YAPILDIYSA ANA SAYFAYI ÇALIŞTIR ---
    st.set_page_config(page_title="Gürkan AI PRO", layout="wide", initial_sidebar_state="collapsed")
    
    # CSS ve Stil Ayarları
    st.markdown("""<style>
        .stApp { background-color: #0b0d11 !important; }
        .gurkan-pro-box { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-left: 6px solid #ffcc00; }
        .neon-green { color: #00ff88;
