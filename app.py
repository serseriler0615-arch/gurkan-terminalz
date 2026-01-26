import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Konfigürasyonu (Geniş ve Sıkıştırılmış)
st.set_page_config(page_title="Gürkan Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

# CSS ile Boşlukları ve Kaydırmayı Minimuma İndirme
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; }
    iframe { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli (Tek Satır)
col_ara, col_fav, col_fiyat, col_degisim = st.columns([1, 1, 1, 1])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("", placeholder="Hisse Kodu (Örn: SASA)", label_visibility="collapsed").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("", st.session_state.favoriler, label_visibility="collapsed")

# Aktif Sembol
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme
try:
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty:
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        with col_fiyat:
            st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with col_degisim:
            st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f} TL")

        # 4. Renklendirilmiş Profesyonel Grafik
        # Subplot: Üstte mumlar, altta hacim
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_width=[0.2, 0.8])

        # Mum Grafik Renkleri (TradingView Standartları)
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat",
            increasing_line_color='#089981', decreasing_line_color='#f23645', # Canlı Yeşil / Kırmızı
            increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
        ), row=1, col=1)

        # Hareketli Ortalamalar
        df['MA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#2962ff', width=1.5), name="MA20"), row=1, col=1)

        # Hacim Renkleri (Fiyata göre renk alan hacim barları)
        colors = ['#089981' if row['Open'] < row['Close'] else '#f23645' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color=colors, opacity=0.5), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=550, # Tek ekrana sığması için optimize edildi
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. Alt Panel: AI Yorum ve RSI (Tek Satırda 3 Sütun)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**💪 RSI Gücü:** `{rsi:.1f}`")
            if rsi > 70: st.error("Aşırı Alım: Dikkat Satış Gelebilir")
            elif rsi < 30: st.success("Aşırı Satım: Tepki Gelebilir")
            else: st.info("Nötr Bölge: Trend Bekleniyor")
        
        with c2:
            trend = "YÜKSELİŞ" if son_fiyat > df['MA20'].iloc[-1] else "DÜŞÜŞ"
            st.markdown(f"**📈 Ana Trend:** `{trend}`")
            st.write(f"MA20 Desteği: {df['MA20'].iloc[-1]:.2f}")

        with c3:
            st.link_button("🚀 KAP / HABERLER", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

except Exception as e:
    st.error(f"Veri Hatası: {e}")
