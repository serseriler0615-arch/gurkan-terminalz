import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="AI Terminal v4", layout="wide", initial_sidebar_state="collapsed")

# CSS ile Boşlukları Sıfırlama
st.markdown("""<style>.block-container { padding-top: 1rem; }</style>""", unsafe_allow_html=True)

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    # Boş bırakılırsa "THYAO" varsayılan olur
    hisse_input = st.text_input("🔍 Hisse Ara (Örn: SASA):", "").upper()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hangi hissenin aktif olacağına karar verme mantığı
if hisse_input != "":
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"
else:
    aktif_hisse = secilen_fav

with col_metrik:
    try:
        data = yf.download(aktif_hisse, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            degisim = fiyat - data['Close'].iloc[-2]
            yuzde = (degisim / data['Close'].iloc[-2]) * 100
            st.metric(f"{aktif_hisse}", f"{fiyat:.2f} TL", f"%{yuzde:.2f}")
    except:
        st.write("Veri bekleniyor...")

# --- CANLI GRAFİK (TRADINGVIEW DİNAMİK) ---
def tradingview_widget(symbol):
    # Sembolü TradingView formatına tam uyumlu yap (BIST:THYAO)
    clean_symbol = symbol.split(".")[0]
    tv_target = f"BIST:{clean_symbol}"
    
    # Her hisse değiştiğinde benzersiz bir ID oluşturarak grafiği yenilemeye zorluyoruz
    html_code = f"""
    <div id="wrapper_{clean_symbol}" style="height:480px; width:100%;">
      <div id="tv_chart_{clean_symbol}" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_target}",
        "interval": "1",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "container_id": "tv_chart_{clean_symbol}",
        "hide_side_toolbar": true,
        "allow_symbol_change": true,
        "save_image": false
      }});
      </script>
    </div>
    """
    components.html(html_code, height=500)

# Grafiği çiz
st.divider()
tradingview_widget(aktif_hisse)

# --- ALT PANEL (AI & HABER) ---
c1, c2 = st.columns(2)
with c1:
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        if rsi > 70: st.error(f"🚨 RSI: {rsi:.1f} - AŞIRI ALIM (Düşüş Beklenebilir)")
        elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - AŞIRI SATIM (Yükseliş Beklenebilir)")
        else: st.info(f"⚖️ RSI: {rsi:.1f} - NÖTR")
    except: pass

with c2:
    st.link_button("📰 Google Haberlerde Araştır", f"https://www.google.com/search?q={aktif_hisse}+haberleri&tbm=nws", use_container_width=True)
