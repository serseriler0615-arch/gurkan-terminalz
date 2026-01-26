import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Sayfa Ayarları
st.set_page_config(page_title="AI Borsa Pro", layout="wide")

# 5 Dakikada Bir Otomatik Yenileme (Hızlandırdık)
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

st.title("🚀 AI Borsa Pro: Analiz & Favoriler")

# Yan Panel
st.sidebar.header("⭐ Favori Listem")
if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]

yeni_fav = st.sidebar.text_input("Favori Ekle (Örn: SASA.IS):").upper()
if st.sidebar.button("Listeye Ekle"):
    if yeni_fav and yeni_fav not in st.session_state.favoriler:
        st.session_state.favoriler.append(yeni_fav)

secilen_fav = st.sidebar.selectbox("Favorilerinden Seç:", st.session_state.favoriler)

st.sidebar.divider()
hisse_kod = st.sidebar.text_input("Manuel Hisse Ara:", secilen_fav).upper()

if not hisse_kod.endswith(".IS"):
    hisse_kod += ".IS"

# Veri Çekme - Hızlandırılmış ve Güncellenmiş
@st.cache_data(ttl=60) 
def veri_indir(kod):
    # En güncel dakikalık veriyi çekmek için interval=1m
    data = yf.download(kod, period="5d", interval="1m")
    return data

try:
    df = veri_indir(hisse_kod)
    
    if not df.empty:
        # Günlük Değişim Hesaplama - HATALI SATIR BURADA DÜZELTİLDİ
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_fiyat = float(df['Close'].iloc[-2])
        degisim_tl = son_fiyat - onceki_fiyat
        degisim_yuzde = (degisim_tl / onceki_fiyat) * 100

        # Teknik Hesaplamalar
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # Üst Panel Metrikleri
        m1, m2, m3 = st.columns(3)
        m1.metric("Anlık Fiyat (15dk Gecikmeli)", f"{son_fiyat:.2f} TL")
        m2.metric("Değişim (TL)", f"{degisim_tl:.2f} TL")
        m3.metric("Değişim (%)", f"%{degisim_yuzde:.2f}")

        st.divider()

        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📈 {hisse_kod} Teknik Grafik")
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'], name="Mum")])
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="Trend (MA20)", line=dict(color='orange')))
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🤖 AI Teknik Yorum")
            son_rsi = float(df['RSI'].iloc[-1])
            ma20 = float(df['MA20'].iloc[-1])
            
            if son_rsi > 70:
                st.error("📉 TAVSİYE: DÜŞEBİLİR")
                st.write("Aşırı alım (RSI > 70). Dikkatli olun.")
            elif son_rsi < 30:
                st.success("📈 TAVSİYE: ÇIKABİLİR")
                st.write("Aşırı satım (RSI < 30). Tepki gelebilir.")
            else:
                if son_fiyat > ma20:
                    st.info("⬆️ TAVSİYE: TREND YUKARI")
                else:
                    st.warning("⬇️ TAVSİYE: TREND AŞAĞI")
            
            st.caption(f"Sistem Saati: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            st.write("---")
            st.subheader("📰 Haber Araştır")
            link = f"https://www.google.com/search?q={hisse_kod}+hisse+haberleri&tbm=nws"
            st.link_button("İnternetteki Son Haberleri Gör", link)

    else:
        st.error("Veri bulunamadı. Lütfen kodu doğru girdiğinizden emin olun.")
except Exception as e:
    st.error(f"Sistem hatası: {e}")
