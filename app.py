import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Ayarları (Tam ekran ve modern)
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Tasarımı daraltan ve estetik katan CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; }
    .stTextInput > div > div > input { background-color: #0d1117; color: white; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli (Tek Satır)
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with c1:
    hisse_input = st.text_input("🔍 Hisse Ara", placeholder="SASA yaz ve Enter'la").upper().strip()
with c2:
    secilen_fav = st.selectbox("⭐ Favoriler", st.session_state.favoriler)

# Sembol Kararı
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Motoru (Hata Korumalı)
try:
    # Veriyi MultiIndex karmaşasından kurtararak çekiyoruz
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty and len(gunluk) >= 2:
        # Değerleri saf sayıya çevirerek o meşhur hatayı engelliyoruz
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        with c3:
            st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with c4:
            st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f} TL")

        # 4. Profesyonel Renkli Grafik (Tek Parça)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])

        # Mumlar (Canlı Yeşil ve Kırmızı)
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat",
            increasing_line_color='#089981', decreasing_line_color='#f23645',
            increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
        ), row=1, col=1)

        # Hacim Barları (Hatasız Döngü ile Renklendirme)
        hacim_renkleri = ['#089981' if (c >= o) else '#f23645' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=hacim_renkleri, opacity=0.4, name="Hacim"), row=2, col=1)

        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False, height=500,
            margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. Akıllı Asistan Yorumu (Tek Satır)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        y1, y2 = st.columns([2, 1])
        with y1:
            if rsi > 70: rsi_mesaj = "⚠️ Hisse çok yükselmiş (Aşırı Alım), kar satışı gelebilir."
            elif rsi < 30: rsi_mesaj = "🚀 Hisse çok düşmüş (Aşırı Satım), tepki yükselişi yakın olabilir."
            else: rsi_mesaj = "⚖️ Hisse dengeli bölgede, trend takibi devam etmeli."
            st.info(f"**🤖 AI Analizi:** {rsi_mesaj} (RSI: {rsi:.1f})")
        with y2:
            st.link_button("🚀 HABERLERİ GÖR", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.warning("Hisse verisi aranıyor... Lütfen bekleyin.")

except Exception as e:
    st.error("Veri çekme sırasında bir sorun oluştu. Lütfen sayfayı yenileyin.")
