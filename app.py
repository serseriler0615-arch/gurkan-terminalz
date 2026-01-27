import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# --- 1. SİSTEM AYARLARI ---
if "access_granted" not in st.session_state:
    st.session_state["access_granted"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "last_sorgu" not in st.session_state:
    st.session_state["last_sorgu"] = "THYAO"
if "currency" not in st.session_state:
    st.session_state["currency"] = "TRY"

def check_access():
    if not st.session_state["access_granted"]:
        st.set_page_config(page_title="Gürkan AI VIP", layout="centered")
        st.title("🤵 Gürkan AI VIP Terminal")
        t1, t2 = st.tabs(["💎 VIP KEY", "🔐 ADMIN"])
        with t1:
            k = st.text_input("Giriş Anahtarı")
            if st.button("Sistemi Başlat"):
                if k.startswith("GAI-"): 
                    st.session_state["access_granted"], st.session_state["role"] = True, "user"; st.rerun()
        with t2:
            u, p = st.text_input("Admin ID"), st.text_input("Şifre", type="password")
            if st.button("Yönetici Girişi"):
                if u.upper() == "GURKAN" and p == "HEDEF2024!": 
                    st.session_state["access_granted"], st.session_state["role"] = True, "admin"; st.rerun()
        return False
    return True

if check_access():
    st.set_page_config(page_title="Gürkan AI VIP v92", layout="wide", initial_sidebar_state="collapsed")

    # --- 🎨 VIP STYLE ---
    st.markdown("""
        <style>
        .stApp { background-color: #05070a !important; }
        .asistan-box { background: #0d1117; border-left: 4px solid #00ff88; padding: 12px; border-radius: 8px; border: 1px solid #1c2128; }
        .tahmin-box { background: linear-gradient(90deg, #0d1117, #161b22); border: 1px solid #00ff88; padding: 10px; border-radius: 10px; text-align: center; }
        .news-card { background: #0d1117; border: 1px solid #1c2128; padding: 8px; border-radius: 5px; margin-bottom: 5px; font-size: 11px; }
        div.stButton > button { background-color: rgba(0, 255, 136, 0.02) !important; color: #00ff88 !important; border: 1px solid #1c2128 !important; }
        </style>
    """, unsafe_allow_html=True)

    # KUR VERİSİ
    @st.cache_data(ttl=3600)
    def get_usd_rate():
        try: return float(yf.download("USDTRY=X", period="1d", progress=False)['Close'].iloc[-1])
        except: return 35.20

    usd_rate = get_usd_rate()
    curr_sym = "$" if st.session_state["currency"] == "USD" else "₺"

    col_fav, col_main, col_radar = st.columns([0.7, 3, 1.4])

    with col_main:
        h1, h2 = st.columns([3, 1])
        with h1: h_input = st.text_input("SORGULA", value=st.session_state["last_sorgu"], label_visibility="collapsed").upper().strip()
        with h2:
            if st.button(f"Birim: {st.session_state['currency']}", use_container_width=True):
                st.session_state["currency"] = "USD" if st.session_state["currency"] == "TRY" else "TRY"; st.rerun()

        sembol = h_input if "." in h_input else h_input + ".IS"
        
        try:
            df = yf.download(sembol, period="1y", interval="1d", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                if st.session_state["currency"] == "USD": df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] / usd_rate
                
                fiyat = float(df['Close'].iloc[-1])
                
                # --- 🔮 AI TAHMİN MODELİ (v92) ---
                # Basit bir momentum ve regresyon tahmini (Gelecek 3 gün)
                son_5_degisim = df['Close'].pct_change().tail(5).mean()
                tahmin_3_gun = fiyat * (1 + son_5_degisim * 3)
                tahmin_renk = "#00ff88" if tahmin_3_gun > fiyat else "#ff4b4b"

                m1, m2, m3 = st.columns([1, 1, 2])
                m1.metric("GÜNCEL FİYAT", f"{curr_sym}{fiyat:.2f}")
                m2.metric("3 GÜN SONRA (AI)", f"{curr_sym}{tahmin_3_gun:.2f}")
                with m3:
                    st.markdown(f"<div class='tahmin-box'><span style='font-size:10px;'>GÜRKAN AI PROJEKSİYON</span><br><b style='color:{tahmin_renk}; font-size:18px;'>3 Günlük Trend: {'YUKARI' if tahmin_3_gun > fiyat else 'AŞAĞI'}</b></div>", unsafe_allow_html=True)

                # GRAFİK
                fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
                fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side='right', gridcolor='#161b22'))
                st.plotly_chart(fig, use_container_width=True)

                # --- 🗞️ HATA KORUMALI HABERLER ---
                st.markdown("### 🗞️ SON HABERLER")
                try:
                    ticker = yf.Ticker(sembol)
                    news = ticker.news[:3]
                    if news:
                        for n in news:
                            p = n.get('publisher', 'Borsa Gündem')
                            t = n.get('title', 'Haber başlığına ulaşılamadı.')
                            st.markdown(f"<div class='news-card'><b>{p}:</b> {t}</div>", unsafe_allow_html=True)
                    else: st.write("Haber yok.")
                except: st.write("Haber servisi geçici olarak kapalı.")

        except Exception as e:
            st.error(f"Grafik verisi alınamadı. Lütfen sembolü kontrol edin.")

    # 3. SAĞ: RADAR
    with col_radar:
        st.markdown("### 🚀 RADAR")
        t_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "BIMAS.IS"]
        try:
            r_all = yf.download(t_list, period="2d", interval="1d", progress=False)['Close']
            if isinstance(r_all.columns, pd.MultiIndex): r_all.columns = r_all.columns.get_level_values(0)
            for s in t_list:
                n = s.split('.')[0]
                c = r_all[s].iloc[-1]
                if st.button(f"🔍 {n} | {c:.2f}", key=f"v92_r_{n}", use_container_width=True):
                    st.session_state["last_sorgu"] = n; st.rerun()
        except: pass
        
        if st.session_state["role"] == "admin":
            st.markdown("---")
            if st.button("🚪 ÇIKIŞ"): st.session_state["access_granted"] = False; st.rerun()
