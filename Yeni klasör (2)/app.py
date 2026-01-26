import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gürkan VIP Terminal", layout="wide")

# --- SİMÜLE EDİLMİŞ VERİTABANI (İnternet sürümü için başlangıç) ---
# Gerçek veritabanı bağlantısı buraya gelecek, şimdilik test için:
if 'users' not in st.session_state:
    st.session_state['users'] = {
        "admin": {"sifre": "Gurkan123!", "bitis": "2099-12-31"},
        "test": {"sifre": "1234", "bitis": "2026-02-22"}
    }

# --- GİRİŞ KONTROLÜ ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🛡️ GÜRKAN VIP TERMİNAL GİRİŞ")
    uid = st.text_input("Kullanıcı ID")
    psw = st.text_input("Şifre", type="password")
    
    if st.button("Sisteme Bağlan"):
        if uid in st.session_state['users'] and st.session_state['users'][uid]['sifre'] == psw:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = uid
            st.rerun()
        else:
            st.error("Hatalı Giriş!")
else:
    # --- ANA TERMİNAL ---
    user = st.session_state['user_id']
    
    # YAN PANEL (Sidebar)
    with st.sidebar:
        st.write(f"👤 Hoş geldin: **{user.upper()}**")
        if st.button("Çıkış Yap"):
            st.session_state['logged_in'] = False
            st.rerun()
        
        st.divider()
        if user == "admin":
            st.subheader("⚙️ YÖNETİCİ PANELİ")
            for u_id, u_info in st.session_state['users'].items():
                b_tarih = datetime.strptime(u_info['bitis'], '%Y-%m-%d')
                kalan_gun = (b_tarih - datetime.now()).days
                st.write(f"**{u_id}**: {kalan_gun} Gün Kaldı")
        
        st.divider()
        st.subheader("💎 ÖNERİ LİSTESİ")
        oneriler = ["THYAO", "EREGL", "ASELS", "SASA", "BIMAS"]
        secilen_oneri = st.radio("Hızlı Analiz:", oneriler)

    # ANA EKRAN
    st.title("📈 Borsa Analiz & Sinyal")
    hisse = st.text_input("Hisse Kodu (Örn: THYAO)", secilen_oneri).upper()
    
    if hisse:
        with st.spinner('Veriler analiz ediliyor...'):
            q = f"{hisse}.IS"
            df = yf.download(q, period="6mo", progress=False)
            
            if not df.empty:
                # Teknik Analiz
                last_p = df['Close'].iloc[-1]
                ma9 = df['Close'].rolling(9).mean().iloc[-1]
                
                # ANALİZ KUTUSU (ÜSTTE)
                if last_p > ma9:
                    st.success(f"🚀 {hisse} ANALİZİ: GÜÇLÜ AL - Yükseliş trendi devam ediyor.")
                else:
                    st.error(f"⚠️ {hisse} ANALİZİ: SATIŞ BASKISI - Dikkatli olunmalı.")

                # GRAFİK
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
                st.plotly_chart(fig, use_container_width=True)