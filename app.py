import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa ve Stil Ayarları
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    [data-testid="stMetricDelta"] svg { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Kodu (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Aktif Hisse Belirleme
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme ve Kusursuz Hesaplama
try:
    # Veriyi MultiIndex hatasını önlemek için auto_adjust=True ile çekiyoruz
    df = yf.download(aktif_hisse, period="5d", interval="1m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)
    
    if not df.empty and not gunluk.empty:
        # Verileri garantiye almak için Series'ten saf sayıya (float) çeviriyoruz
        son_fiyat = float(df['Close'].iloc[-1])
        
        # Gerçek Değişim: Bugünkü son fiyat ile DÜNKÜ kapanış arasındaki fark
        # Günlük veride son satır bugündür, bir önceki satır (-2) dündür.
        if len(gunluk) >= 2:
            dunku_kapanis = float(gunluk['Close'].iloc[-2])
        else:
            dunku_kapanis = float(gunluk['Close'].iloc[0])

        fark = son_fiyat - dunku_kapanis
        degisim_yuzde = (fark / dunku_kapanis) * 100

        with col_metrik:
            # Metrikleri hatasız formatla yazdırıyoruz
            st.metric(
                label=f"{aktif_temiz} (BIST)", 
                value=f"{son_fiyat:.2f} TL", 
                delta=f"{degisim_yuzde:+.2f}% ({fark:+.2f} TL)"
            )

        # 4. Grafik (Plotly)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_width=[0.2, 0.8])

        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ), row=1, col=1)

        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='gray'), row=2, col=1)

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 5. RSI Analizi
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        st.info(f"📊 Teknik Analiz Notu: {aktif_temiz} hissesinde RSI değeri {float(rsi):.1f} seviyesinde.")

    else:
        st.error("Veri bulunamadı. Lütfen kodu doğru girdiğinizden emin olun.")

except Exception as e:
    # Hata mesajını daha detaylı ama temiz gösteriyoruz
    st.warning(f"Bağlantı bekleniyor... (Hata Detayı: {str(e)[:50]})")
