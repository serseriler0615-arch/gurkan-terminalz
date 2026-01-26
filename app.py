import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="BIST Terminal Kesin Çözüm", layout="wide", initial_sidebar_state="collapsed")

# Sayfa yenileme (Hataları önlemek için kapalı kalsın veya 10 dk yapalım)
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Ara (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme
aktif_temiz = hisse_input.split(".")[0] if hisse_input else secilen_fav.split(".")[0]
aktif_yfinance = aktif_temiz + ".IS"

with col_metrik:
    try:
        data = yf.download(aktif_yfinance, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            st.metric(f"{aktif_temiz} (BIST)", f"{fiyat:.2f} TL")
    except:
        st.info("Veri bekleniyor...")

# --- CANLI GRAFİK (IFRAME YÖNTEMİ - AMERİKA'YA KAÇIŞI ENGELLER) ---
def tradingview_iframe(ticker):
    # TradingView'in ham chart URL'sini kullanarak widget'ın kararsızlığından kurtuluyoruz
    chart_url = f"https://s.tradingview.com/widgetembed/?symbol=BIST%3A{ticker}&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=light&style=1&timezone=Europe%2FIstanbul&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=tr&utm_source=www.tradingview.com&utm_medium=widget&utm_campaign=chart&utm_term=BIST%3A{ticker}"
    
    components.iframe(chart_url, height=500)

st.divider()
st.subheader(f"📊 {aktif_temiz} CANLI GRAFİK")
tradingview_iframe(aktif_temiz)

# --- ALT PANEL (AI SİNYAL) ---
try:
    if not data.empty:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        c1, c2 = st.columns(2)
        with c1:
            if rsi > 70: st.error(f"🚨 Sinyal: AŞIRI ALIM (RSI: {rsi:.1f})")
            elif rsi < 30: st.success(f"🚀 Sinyal: AŞIRI SATIM (RSI: {rsi:.1f})")
            else: st.info(f"⚖️ Sinyal: NÖTR (RSI: {rsi:.1f})")
        with c2:
            st.link_button("📰 Haberleri Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
except:
    pass
