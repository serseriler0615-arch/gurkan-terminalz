import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Yapay Zeka Borsa Asistanı", layout="wide")

st.title("🚀 AI Destekli Borsa Analiz & Haber Terminali")

# Yan Panel - Arama ve Hızlı Seçim
st.sidebar.header("🔍 Hisse Araştır")
hisse_kod = st.sidebar.text_input("Hisse Kodu Gir (Örn: THYAO.IS):", "THYAO.IS").upper()

if not hisse_kod.endswith(".IS"):
    hisse_kod += ".IS"

period = st.sidebar.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y"])

# Veri Çekme
@st.cache_data
def veri_indir(kod, per):
    data = yf.download(kod, period=per, interval="1d")
    return data

try:
    df = veri_indir(hisse_kod, period)
    
    if not df.empty:
        # Teknik Hesaplamalar (RSI & MA)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # Üst Panel: Fiyat ve Tavsiye
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📈 {hisse_kod} Grafik")
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'], name="Mum Grafiği")])
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20 Trend", line=dict(color='orange')))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🤖 AI Analiz & Tavsiye")
            son_fiyat = float(df['Close'].iloc[-1])
            son_rsi = float(df['RSI'].iloc[-1])
            ma20 = float(df['MA20'].iloc[-1])
            
            st.metric("Son Fiyat", f"{son_fiyat:.2f} TL")
            
            # Tavsiye Mekanizması
            if son_rsi > 70:
                st.error("⚠️ TAVSİYE: DÜŞEBİLİR (Aşırı Alım)")
                st.write("RSI değeri 70'in üzerinde. Hisse çok yükselmiş, kar satışı gelebilir.")
            elif son_rsi < 30:
                st.success("✅ TAVSİYE: ÇIKABİLİR (Aşırı Satım)")
                st.write("RSI değeri 30'un altında. Hisse çok düşmüş, tepki alımları başlayabilir.")
            else:
                if son_fiyat > ma20:
                    st.info("⚖️ TAVSİYE: TREND YUKARI")
                    st.write("Fiyat 20 günlük ortalamanın üzerinde. Olumlu hava korunuyor.")
                else:
                    st.warning("⚖️ TAVSİYE: TREND AŞAĞI")
                    st.write("Fiyat ortalamanın altında. Baskı devam edebilir.")

        # Haberler Bölümü
        st.divider()
        st.subheader(f"📰 {hisse_kod} Hakkında Son Haberler")
        haber_linki = f"https://www.google.com/search?q={hisse_kod}+hisse+haberleri&tbm=nws"
        st.write(f"🌐 [Buraya tıklayarak en güncel internet haberlerini gör]({haber_linki})")
        
    else:
        st.error("Hisse verisi bulunamadı. Lütfen kodu doğru girdiğinizden emin olun.")
except Exception as e:
    st.error(f"Bir hata oluştu: {e}")

st.sidebar.info("Not: Bu analizler teknik verilere dayanır, yatırım tavsiyesi değildir.")
