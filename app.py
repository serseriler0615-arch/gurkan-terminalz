import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="AI Borsa Pro V3", layout="wide")

# 1 Dakikada Bir Otomatik Yenileme
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 AI Borsa Pro: Canlı Terminal")

# --- YAN PANEL (SIDEBAR) ---
st.sidebar.header("🔍 Hisse Araştırma")

# 1. ARAMA EN ÜSTTE
hisse_ara = st.sidebar.text_input("Hisse Kodu Gir (Örn: THYAO):", "THYAO").upper()
if not hisse_ara.endswith(".IS") and "." not in hisse_ara:
    hisse_ara_kod = hisse_ara + ".IS"
else:
    hisse_ara_kod = hisse_ara

# 2. FAVORİLER BİR TIK AŞAĞIDA
st.sidebar.divider()
st.sidebar.subheader("⭐ Favori Listem")
if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]

yeni_fav = st.sidebar.text_input("Yeni Favori Ekle:").upper()
if st.sidebar.button("Listeye Ekle"):
    if yeni_fav and yeni_fav not in st.session_state.favoriler:
        st.session_state.favoriler.append(yeni_fav)

secilen_fav = st.sidebar.selectbox("Favorilerinden Hızlı Seç:", st.session_state.favoriler)

# --- ANA EKRAN ---

# TradingView Canlı Widget (0 Saniye Gecikme)
def tradingview_widget(symbol):
    # .IS kısmını TradingView formatına çevir (BIST:THYAO)
    tv_symbol = symbol.replace(".IS", "")
    target = f"BIST:{tv_symbol}"
    
    html_code = f"""
    <div class="tradingview-widget-container" style="height:500px;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{target}",
        "interval": "1",
        "timezone": "Europe/Istanbul",
        "theme": "light",
        "style": "1",
        "locale": "tr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(html_code, height=520)

# Veri Çekme (Analiz İçin)
@st.cache_data(ttl=10)
def veri_indir(kod):
    data = yf.download(kod, period="5d", interval="1m")
    return data

try:
    # Arama kutusu boş değilse onu kullan, yoksa favoriyi
    aktif_hisse = hisse_ara_kod if hisse_ara else secilen_fav
    df = veri_indir(aktif_hisse)
    
    if not df.empty:
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_fiyat = float(df['Close'].iloc[-2])
        degisim_yuzde = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100

        # Üst Metrikler
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{aktif_hisse} Son Fiyat", f"{son_fiyat:.2f} TL")
        m2.metric("Anlık Değişim (%)", f"%{degisim_yuzde:.2f}")
        m3.write("ℹ️ *Analizler 15dk gecikmeli veriye dayanır, grafik CANLI'dır.*")

        st.divider()

        # CANLI GRAFİK PANELİ
        st.subheader(f"📊 {aktif_hisse} CANLI VERİ (0sn Gecikme)")
        tradingview_widget(aktif_hisse)

        st.divider()

        # AI ANALİZ PANELİ
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🤖 AI Teknik Analiz Yorumu")
            # RSI ve MA Hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

            if rsi > 70:
                st.error("📉 TAVSİYE: DÜŞEBİLİR (Aşırı Alım)")
                st.write(f"RSI {rsi:.2f} ile aşırı alım bölgesinde. Kar satışı gelebilir.")
            elif rsi < 30:
                st.success("📈 TAVSİYE: ÇIKABİLİR (Aşırı Satım)")
                st.write(f"RSI {rsi:.2f} ile dipte. Tepki alımı gelebilir.")
            else:
                if son_fiyat > ma20:
                    st.info("⬆️ TAVSİYE: TREND POZİTİF")
                else:
                    st.warning("⬇️ TAVSİYE: TREND NEGATİF")

        with col2:
            st.subheader("📰 Haber ve Araştırma")
            link = f"https://www.google.com/search?q={aktif_hisse}+hisse+haberleri&tbm=nws"
            st.link_button("Haberleri Yeni Sekmede Aç", link)
            st.write("---")
            st.caption("AI Terminal V3.0 - Bol Kazançlar!")

    else:
        st.warning("Hisse verisi yükleniyor veya kod hatalı...")
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")
