import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Ayarları
st.set_page_config(page_title="Gürkan BIST Terminal", layout="wide")

# Üst boşluğu silmek için CSS
st.markdown("<style>.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True)

# 2. Üst Panel (Hisse Seçimi)
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "SASA.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Kod (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Aktif Hisse Mantığı
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme (Yahoo Finance üzerinden doğrudan BIST)
try:
    df = yf.download(aktif_hisse, period="5d", interval="1m", progress=False)
    
    if not df.empty:
        # Fiyat Bilgileri
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_kapanis = float(df['Close'].iloc[0])
        degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100

        with col_metrik:
            st.metric(f"{aktif_temiz} (BIST)", f"{son_fiyat:.2f} TL", f"%{degisim:.2f}")

        # 4. Profesyonel Plotly Grafiği (Mum + Hacim)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, subplot_titles=(f'{aktif_temiz} Mum Grafik', 'Hacim'), 
                           row_width=[0.2, 0.7])

        # Mum Grafik
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat"
        ), row=1, col=1)

        # Hareketli Ortalama (MA20)
        df['MA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1), name="MA20"), row=1, col=1)

        # Hacim (Volume)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='dodgerblue'), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # 5. RSI Analizi ve Haberler
        c1, c2 = st.columns(2)
        with c1:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            if rsi > 70: st.error(f"🚨 RSI: {rsi:.1f} - Aşırı Alım (Düşüş Riski)")
            elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - Aşırı Satım (Tepki Alımı)")
            else: st.info(f"⚖️ RSI: {rsi:.1f} - Nötr")

        with c2:
            st.link_button("📰 Haberleri Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.warning(f"⚠️ {aktif_hisse} verisi alınamadı. Kodun doğruluğunu kontrol et.")

except Exception as e:
    st.error(f"Hata: {e}")
