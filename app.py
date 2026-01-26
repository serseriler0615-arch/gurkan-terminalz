import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları - Boşlukları minimize etme
st.set_page_config(page_title="AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# 1 Dakikada Bir Yenileme
st_autorefresh(interval=60 * 1000, key="datarefresh")

# Üst Boşluğu Kapatan CSS ve Stil Düzenlemesi
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    </style>
    """, unsafe_allow_html=True) # Hatalı yer burasıydı, düzeltildi.

# --- ÜST PANEL (Kompakt Arama ve Favoriler) ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1])

with col_ara:
    hisse_ara = st.text_input("🔍 Hisse Ara:", "THYAO").upper()
    if not hisse_ara.endswith(".IS") and "." not in hisse_ara:
        aktif_hisse = hisse_ara + ".IS"
    else:
        aktif_hisse = hisse_ara

with col_fav:
    if 'favoriler' not in st.session_state:
        st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)
    # Eğer kutuda bir şey arandıysa onu, aranmadıysa favoriyi seç
    hisse_final = aktif_hisse if hisse_ara != "THYAO" else secilen_fav

with col_metrik:
    try:
        data = yf.download(hisse_final, period="2d", interval="1m")
        if not data.empty:
            fiyat = data['Close'].iloc[-1]
            degisim = fiyat - data['Close'].iloc[-2]
            st.metric(f"{hisse_final}", f"{fiyat:.2f} TL", f"{degisim:.2f} TL")
    except:
        st.write("Veri alınıyor...")

# --- CANLI GRAFİK (Ekranın Büyük Kısmı) ---
def tradingview_widget(symbol):
    tv_symbol = symbol.replace(".IS", "")
    html_code = f"""
    <div style="height:420px; width:100%;">
      <div id="tv_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "BIST:{tv_symbol}", "interval": "1",
        "timezone": "Europe/Istanbul", "theme": "light", "style": "1",
        "locale": "tr", "container_id": "tv_chart", "hide_side_toolbar": true
      }});
      </script>
    </div>
    """
    components.html(html_code, height=430)

tradingview_widget(hisse_final)

# --- ALT PANEL (Hızlı Analiz ve Haberler) ---
c1, c2 = st.columns([1, 1])

with c1:
    try:
        # RSI Sinyali
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        if rsi > 70: st.error(f"🚨 Sinyal: DÜŞEBİLİR (RSI: {rsi:.1f})")
        elif rsi < 30: st.success(f"🚀 Sinyal: ÇIKABİLİR (RSI: {rsi:.1f})")
        else: st.info(f"⚖️ Sinyal: NÖTR (RSI: {rsi:.1f})")
    except:
        st.write("Analiz hazırlanıyor...")

with c2:
    link = f"https://www.google.com/search?q={hisse_final}+haberleri&tbm=nws"
    st.link_button("📰 Son Haberleri Gör", link, use_container_width=True)
