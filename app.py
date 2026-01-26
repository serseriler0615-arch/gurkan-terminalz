import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa ve Stil Yapılandırması
st.set_page_config(page_title="Gürkan Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

# Arama motorunu ve boşlukları hizalayan özel CSS
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; }
    .stTextInput { margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
col_ara, col_fav, col_fiyat, col_degisim = st.columns([1, 1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("Hisse Ara", placeholder="Örn: SASA").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("Favoriler", st.session_state.favoriler)

# Aktif Sembol Kararı
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme ve Hata Kontrolü
try:
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty and len(gunluk) >= 2:
        # Değerleri saf sayıya (float) çevirerek hatayı engelliyoruz
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        with col_fiyat:
            st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with col_degisim:
            st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f} TL")

        # 4. Profesyonel Grafik (Renklendirilmiş)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_width=[0.2, 0.8])

        # Mum Grafik
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat",
            increasing_line_color='#089981', decreasing_line_color='#f23645',
            increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
        ), row=1, col=1)

        # Hacim Barları - Hata veren kısım düzeltildi
        colors = ['#089981' if (c >= o) else '#f23645' for o, c in zip(df['Open'], df['Close'])]
        
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'], 
            marker_color=colors, opacity=0.4, name="Hacim"
        ), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=550,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. Analiz ve Yorum Paneli
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_val = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**⚡ RSI:** `{rsi_val:.1f}`")
            if rsi_val > 70: st.error("Aşırı Alım: Dikkat!")
            elif rsi_val < 30: st.success("Aşırı Satım: Fırsat?")
            else: st.info("Bölge: Nötr")
        
        with c2:
            st.write(f"**📉 Dünkü Kapanış:** `{dunku_kapanis:.2f}`")
            st.write(f"**📈 Gün içi Yüksek:** `{float(df['High'].max()):.2f}`")

        with c3:
            st.link_button("🚀 HABERLER", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.warning("Veri yükleniyor veya sembol hatalı...")

except Exception as e:
    st.error(f"Sistem Hatası Gideriliyor: {str(e)[:50]}")
