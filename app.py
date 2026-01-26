import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="AI Borsa Terminali", layout="wide", initial_sidebar_state="collapsed")

# 2 Dakikada Bir Otomatik Yenileme
st_autorefresh(interval=2 * 60 * 1000, key="datarefresh")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Ara (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme Mantığı
if hisse_input:
    # Kullanıcı ne girerse girsin sadece kodu alıp .IS ekliyoruz
    aktif_temiz = hisse_input.split(".")[0]
    aktif_yfinance = aktif_temiz + ".IS"
else:
    aktif_temiz = secilen_fav.split(".")[0]
    aktif_yfinance = secilen_fav

with col_metrik:
    try:
        # Veri çekme - yfinance (15dk gecikmeli analiz için)
        data = yf.download(aktif_yfinance, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            degisim = ((fiyat - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            st.metric(f"{aktif_temiz} (BIST)", f"{fiyat:.2f} TL", f"%{degisim:.2f}")
    except:
        st.info("Fiyat verisi bekleniyor...")

# --- CANLI GRAFİK (TRADINGVIEW - BIST ZORUNLU MOD) ---
def tradingview_widget(ticker):
    # Amerika borsasına gitmemesi için BIST: ön ekini kesinleştiriyoruz
    tv_ticker = f"BIST:{ticker}"
    
    html_code = f"""
    <div id="tradingview_outer" style="height:500px; width:100%;">
      <div id="tv_chart_logic" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_ticker}",
        "interval": "1",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tv_chart_logic"
      }});
      </script>
    </div>
    """
    # Hata veren 'key' parametresini buradan kaldırdım veya statik yaptım
    components.html(html_code, height=510)

st.divider()
tradingview_widget(aktif_temiz)

# --- ALT PANEL (AI SİNYAL) ---
try:
    if not data.empty:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        c1, c2 = st.columns(2)
        with c1:
            if rsi > 70: st.error(f"🚨 Sinyal: DÜŞEBİLİR (RSI: {rsi:.1f})")
            elif rsi < 30: st.success(f"🚀 Sinyal: ÇIKABİLİR (RSI: {rsi:.1f})")
            else: st.info(f"⚖️ Sinyal: NÖTR (RSI: {rsi:.1f})")
        with c2:
            st.link_button("📰 Haberleri Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
except:
    st.write("Analiz verisi bekleniyor...")
