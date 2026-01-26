import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Konfigürasyonu (Daha dar ve odaklanmış)
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Görsel karmaşayı bitiren Özel CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; max-width: 95%; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 10px; }
    [data-testid="column"] { border-radius: 10px; }
    h1, h2, h3 { color: #e6edf3; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli (Sıkıştırılmış)
with st.container():
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
    
    if 'favoriler' not in st.session_state:
        st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

    with c1:
        hisse_input = st.text_input("", placeholder="🔍 Hisse Ara (Örn: SASA)", label_visibility="collapsed").upper().strip()
    with c2:
        secilen_fav = st.selectbox("", st.session_state.favoriler, label_visibility="collapsed")

    aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
    aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri İşleme (Gelişmiş Hata Filtresi)
try:
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty and len(gunluk) >= 2:
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        with c3:
            st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with c4:
            st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f} TL")

        st.markdown("---") # Ayırıcı Çizgi

        # 4. Profesyonel BIST Grafiği
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_width=[0.2, 0.8])

        # Mumlar (Gerçek borsa renkleri)
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat",
            increasing_line_color='#089981', decreasing_line_color='#f23645',
            increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
        ), row=1, col=1)

        # Hacim Barları (Fiyata göre renk alan dinamik yapı)
        h_colors = ['#089981' if (c >= o) else '#f23645' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=h_colors, opacity=0.3, name="Hacim"), row=2, col=1)

        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False, height=500,
            margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0d1117", plot_bgcolor="#0d1117"
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. Alt Panel: Akıllı AI Özet
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        y1, y2 = st.columns([3, 1])
        with y1:
            durum = "🟢 Alıcılı" if degisim > 0 else "🔴 Satıcılı"
            st.markdown(f"**🤖 AI Notu:** {aktif_temiz} şu an {durum} bir seyir izliyor. RSI değeri **{rsi:.1f}**. Trend yönü kuvvetli.")
        with y2:
            st.link_button("📰 Haberleri Gör", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.info("Hisse verisi çekiliyor, lütfen bekleyin...")

except Exception as e:
    st.error("Bir hata oluştu. Lütfen sembolü (Örn: SASA) kontrol edip tekrar girin.")
