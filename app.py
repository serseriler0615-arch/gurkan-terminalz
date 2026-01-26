import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Sayfa yenileme (3 dakikada bir - stabilite için)
st_autorefresh(interval=3 * 60 * 1000, key="datarefresh")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stMetricValue"] { font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 Hisse Ara (Örn: THYAO):", "").upper()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hangi hissenin aktif olacağına karar ver
if hisse_input:
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"
else:
    aktif_hisse = secilen_fav

with col_metrik:
    try:
        # Analiz verisini çek (15dk gecikmeli)
        data = yf.download(aktif_hisse, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            onceki = float(data['Close'].iloc[-2])
            degisim = fiyat - onceki
            st.metric(f"{aktif_hisse}", f"{fiyat:.2f} TL", f"{degisim:.2f} TL")
    except:
        st.write("Veri bekleniyor...")

# --- CANLI GRAFİK (TRADINGVIEW FIX) ---
def tradingview_widget(symbol):
    # TradingView için formatı temizle (THYAO.IS -> BIST:THYAO)
    clean_symbol = symbol.split(".")[0]
    tv_target = f"BIST:{clean_symbol}"
    
    html_code = f"""
    <div style="height:450px; width:100%;">
      <div id="tv_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{tv_target}", "interval": "1",
        "timezone": "Europe/Istanbul", "theme": "light", "style": "1",
        "locale": "tr", "container_id": "tv_chart", "hide_side_toolbar": true,
        "allow_symbol_change": true
      }});
      </script>
    </div>
    """
    components.html(html_code, height=460)

tradingview_widget(aktif_hisse)

# --- ALT PANEL ---
c1, c2 = st.columns([1, 1])
with c1:
    try:
        # Teknik Analiz (RSI)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        if rsi > 70: st.error(f"🚨 RSI: {rsi:.1f} - AŞIRI ALIM (Düşebilir)")
        elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - AŞIRI SATIM (Çıkabilir)")
        else: st.info(f"⚖️ RSI: {rsi:.1f} - NÖTR")
    except:
        st.write("Analiz hazırlanıyor...")

with c2:
    link = f"https://www.google.com/search?q={aktif_hisse}+haberleri&tbm=nws"
    st.link_button("📰 Son Haberleri Gör", link, use_container_width=True)
