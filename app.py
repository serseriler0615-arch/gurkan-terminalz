import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="BIST AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Yenileme (Hataları önlemek için 10 dakikaya çıkardık)
st_autorefresh(interval=10 * 60 * 1000, key="refresh_clock")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Kod (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme
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
            st.metric(f"{aktif_temiz} (BIST)", f"{fiyat:.2f} TL")
    except:
        st.write("Veri bekleniyor...")

# --- CANLI GRAFİK (SIFIR HATA VERSİYONU) ---
def tradingview_widget(ticker):
    # 'key' parametresini tamamen kaldırdık, TypeError'ı bu çözer.
    # TradingView sembolünü BIST: ön ekiyle garanti altına alıyoruz.
    tv_ticker = f"BIST:{ticker}"
    
    html_code = f"""
    <div id="tv_container" style="height:500px; width:100%;">
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_ticker}",
        "interval": "D",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tv_container"
      }});
      </script>
    </div>
    """
    components.html(html_code, height=510)

st.divider()
tradingview_widget(aktif_temiz)

# --- ALT PANEL ---
try:
    if not data.empty:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        c1, c2 = st.columns(2)
        with c1:
            if rsi > 70: st.error(f"🚨 RSI: {rsi:.1f} - AŞIRI ALIM")
            elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - AŞIRI SATIM")
            else: st.info(f"⚖️ RSI: {rsi:.1f} - NÖTR")
        with c2:
            st.link_button("📰 Haberler", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
except:
    pass
