import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import random

# Sayfa Ayarları
st.set_page_config(page_title="BIST Terminal Kesin Çözüm", layout="wide", initial_sidebar_state="collapsed")

# Sayfayı çok sık yenileme, widget'ı bozabiliyor (5 dakikaya çektik)
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Ara:", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme Mantığı
if hisse_input:
    aktif_temiz = hisse_input.split(".")[0]
    aktif_yfinance = aktif_temiz + ".IS"
else:
    aktif_temiz = secilen_fav.split(".")[0]
    aktif_yfinance = secilen_fav

with col_metrik:
    try:
        data = yf.download(aktif_yfinance, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            st.metric(f"{aktif_temiz} (CANLI)", f"{fiyat:.2f} TL")
    except:
        st.write("Fiyat bekleniyor...")

# --- CANLI GRAFİK (SIFIRLAMA GARANTİLİ) ---
def tradingview_widget(ticker):
    # ID'yi her seferinde değiştirerek tarayıcıyı kandırıyoruz
    unique_id = f"tv_{ticker}_{random.randint(100, 999)}"
    tv_ticker = f"BIST:{ticker}"
    
    html_code = f"""
    <html>
    <body style="margin:0; padding:0; overflow:hidden;">
        <div id="container_{unique_id}"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "width": "100%",
          "height": 500,
          "symbol": "{tv_ticker}",
          "interval": "5",
          "timezone": "Europe/Istanbul",
          "theme": "light",
          "style": "1",
          "locale": "tr",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "allow_symbol_change": false,
          "save_image": false,
          "container_id": "container_{unique_id}"
        }});
        </script>
    </body>
    </html>
    """
    # Her hisse değişiminde benzersiz bir 'key' vererek widget'ı yeniden yaratıyoruz
    components.html(html_code, height=520, key=f"comp_{ticker}")

st.divider()
tradingview_widget(aktif_temiz)

# --- ALT PANEL (YAPAY ZEKA) ---
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
            st.link_button("📰 Google Haberler", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
except:
    pass
