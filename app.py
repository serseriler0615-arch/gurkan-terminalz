import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları - Boşlukları azaltmak için padding ayarı
st.set_page_config(page_title="AI Terminal Compact", layout="wide", initial_sidebar_state="collapsed")

# 1 Dakikada Bir Yenileme
st_autorefresh(interval=60 * 1000, key="datarefresh")

# Ekranın en üstündeki boşluğu silmek için CSS
st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1rem; padding-bottom: 1rem; }
    .stMetric { background-color: #f0f2f6; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_stdio=True)

# --- ÜST PANEL (Arama ve Favoriler Yan Yana) ---
col1, col2, col3 = st.columns([1, 1, 1.5])

with col1:
    hisse_ara = st.text_input("🔍 Hisse Ara:", "THYAO", key="search").upper()
    if not hisse_ara.endswith(".IS") and "." not in hisse_ara:
        aktif_hisse = hisse_ara + ".IS"
    else:
        aktif_hisse = hisse_ara

with col2:
    if 'favoriler' not in st.session_state:
        st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)
    if st.button("Seçileni Aç"): aktif_hisse = secilen_fav

with col3:
    # Anlık Analiz Özeti (Kompakt Metrik)
    try:
        data = yf.download(aktif_hisse, period="2d", interval="1m")
        if not data.empty:
            son_fiyat = float(data['Close'].iloc[-1])
            onceki_kapanis = float(data['Close'].iloc[-2])
            fark = son_fiyat - onceki_kapanis
            st.metric(f"{aktif_hisse}", f"{son_fiyat:.2f} TL", f"{fark:.2f} TL")
    except:
        st.write("Veri bekleniyor...")

# --- CANLI GRAFİK (Orta Bölüm) ---
def tradingview_widget(symbol):
    tv_symbol = symbol.replace(".IS", "")
    html_code = f"""
    <div style="height:450px; width:100%;">
      <div id="tradingview_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "BIST:{tv_symbol}", "interval": "1",
        "timezone": "Europe/Istanbul", "theme": "light", "style": "1",
        "locale": "tr", "container_id": "tradingview_chart", "hide_top_toolbar": false
      }});
      </script>
    </div>
    """
    components.html(html_code, height=460)

tradingview_widget(aktif_hisse)

# --- ALT PANEL (Haberler ve AI Tavsiyesi) ---
c1, c2 = st.columns(2)
with c1:
    # Hızlı AI Sinyali
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        if rsi > 70: st.error(f"🚨 Sinyal: DÜŞEBİLİR (RSI: {rsi:.1f})")
        elif rsi < 30: st.success(f"🚀 Sinyal: ÇIKABİLİR (RSI: {rsi:.1f})")
        else: st.info(f"⚖️ Sinyal: NÖTR (RSI: {rsi:.1f})")
    except: pass

with c2:
    link = f"https://www.google.com/search?q={aktif_hisse}+haberleri&tbm=nws"
    st.link_button("📰 Son Haberleri Oku", link, use_container_width=True)
