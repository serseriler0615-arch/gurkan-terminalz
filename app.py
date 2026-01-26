import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="BIST Terminal", layout="wide", initial_sidebar_state="collapsed")

# 5 dakikada bir yenileme
st_autorefresh(interval=5 * 60 * 1000, key="refresh")

# --- ÜST PANEL ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 Hisse Ara (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Aktif Hisse Belirleme
aktif_temiz = hisse_input.split(".")[0] if hisse_input else secilen_fav.split(".")[0]
aktif_yfinance = aktif_temiz + ".IS"

with col_metrik:
    try:
        data = yf.download(aktif_yfinance, period="2d", interval="1m", progress=False)
        if not data.empty:
            fiyat = float(data['Close'].iloc[-1])
            st.metric(f"{aktif_temiz}", f"{fiyat:.2f} TL")
    except:
        st.write("Fiyat yükleniyor...")

# --- CANLI GRAFİK (SIFIR HATA VE BIST GARANTİLİ) ---
def final_tradingview(ticker):
    # Bu URL yapısı TradingView'in en stabil gömme formatıdır
    # ticker: BIST:THYAO formatında gönderilir
    tv_ticker = f"BIST:{ticker}"
    
    html_code = f"""
    <div style="height:550px; width:100%;">
        <iframe 
            src="https://s.tradingview.com/widgetembed/?symbol={tv_ticker}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=light&style=1&timezone=Europe%2FIstanbul&locale=tr"
            width="100%" 
            height="550" 
            frameborder="0" 
            allowtransparency="true" 
            scrolling="no" 
            allowfullscreen>
        </iframe>
    </div>
    """
    components.html(html_code, height=560)

st.divider()
st.subheader(f"📊 {aktif_temiz} Canlı Grafik")
final_tradingview(aktif_temiz)

# --- ALT PANEL ---
if not data.empty:
    st.link_button(f"📰 {aktif_temiz} Haberlerini Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)
