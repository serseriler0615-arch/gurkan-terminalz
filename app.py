import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Konfigürasyonu (Geniş ve Dar Boşluklu)
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# ARAMA MOTORUNU AŞAĞI ÇEKEN VE TASARIMI DÜZELTEN ÖZEL CSS
st.markdown("""
    <style>
    .block-container { padding-top: 3rem; max-width: 95%; }
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; padding: 15px; border-radius: 12px; }
    .stTextInput { margin-top: 15px; } /* Arama motorunu aşağı çeker */
    .stSelectbox { margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. ANA PANEL (Arama ve Fiyatlar Tek Satırda)
with st.container():
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
    
    if 'favoriler' not in st.session_state:
        st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

    with c1:
        hisse_input = st.text_input("🔍 Hisse Ara", placeholder="Örn: SASA").upper().strip()
    with c2:
        secilen_fav = st.selectbox("⭐ Favoriler", st.session_state.favoriler)

    # Aktif Sembol Kararı
    aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
    aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. VERİ MOTORU VE HESAPLAMA
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

        st.markdown("<br>", unsafe_allow_html=True) # Küçük bir boşluk

        # 4. RENKLENDİRİLMİŞ GRAFİK (TRADINGVIEW RENKLERİ)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_width=[0.2, 0.8])

        # Mumlar
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat",
            increasing_line_color='#089981', decreasing_line_color='#f23645',
            increasing_fillcolor='#089981', decreasing_fillcolor='#f23645'
        ), row=1, col=1)

        # Hacim Barları (Hatasız Renklendirme)
        h_colors = ['#089981' if (c >= o) else '#f23645' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=h_colors, opacity=0.4), row=2, col=1)

        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False, height=500,
            margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. ALT PANEL: AI YORUMU
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        st.info(f"🤖 **AI ANALİZ NOTU:** {aktif_temiz} hissesi şu an %{degisim:.2f} değişimle işlem görüyor. RSI değeri {rsi:.1f} seviyesinde. Trend durumu teknik olarak takip edilmeli.")

    else:
        st.warning("Hisse verisi aranıyor...")

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
