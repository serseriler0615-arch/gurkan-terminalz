import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="BIST AI Terminal", layout="wide")

# Otomatik yenilemeyi hata vermemesi için kapattık veya süresini uzattık
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 Hisse Kodu (Örn: SASA):", "").upper().strip()

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
            st.metric(f"{aktif_temiz} Fiyat", f"{fiyat:.2f} TL")
    except:
        st.write("Veri bekleniyor...")

# --- CANLI GRAFİK (BIST ÖZEL WIDGET) ---
def tradingview_bist_widget(ticker):
    # Bu widget formatı BIST verileri için en kararlı olanıdır
    tv_ticker = f"BIST:{ticker}"
    
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_bist"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": 550,
        "symbol": "{tv_ticker}",
        "interval": "D",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "watchlist": ["BIST:THYAO", "BIST:ISCTR", "BIST:EREGL", "BIST:SASA"],
        "container_id": "tradingview_bist"
      }});
      </script>
    </div>
    """
    components.html(html_code, height=560)

st.divider()
tradingview_bist_widget(aktif_temiz)

# --- ALT PANEL ---
c1, c2 = st.columns(2)
with c1:
    st.info(f"💡 {aktif_temiz} için teknik analiz aşağıda hazırlanıyor...")
with c2:
    st.link_button("📰 Google Haberler", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
