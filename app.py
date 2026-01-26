import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. SIKIŞTIRILMIŞ SAYFA AYARLARI
st.set_page_config(page_title="Gürkan AI", layout="wide", initial_sidebar_state="collapsed")

# TÜM BOŞLUKLARI VE KAYMALARI SIFIRLAYAN ÖZEL CSS
st.markdown("""
    <style>
    /* Üst boşluğu tamamen yok et */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; max-width: 98%; }
    header {visibility: hidden;} /* Streamlit üst barını gizle */
    #MainMenu {visibility: hidden;}
    
    /* Kutuları ve Metrikleri Hizala */
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; padding: 5px 15px !important; border-radius: 10px; }
    .stTextInput > div > div > input { height: 45px !important; }
    .stSelectbox > div > div > div { height: 45px !important; }
    
    /* Grafik ve Yazı Arasındaki Mesafeyi Daralt */
    .element-container { margin-bottom: -0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. ÜST PANEL: TEK SATIRDA 4 SÜTUN
# Arama ve seçim kutularını fiyatlarla aynı hizaya çektik
with st.container():
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
    
    if 'favoriler' not in st.session_state:
        st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

    with c1:
        hisse_input = st.text_input("", placeholder="🔍 Hisse Yaz...", label_visibility="collapsed").upper().strip()
    with c2:
        secilen_fav = st.selectbox("", st.session_state.favoriler, label_visibility="collapsed")

    aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
    aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. VERİ MOTORU
try:
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty and len(gunluk) >= 2:
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        with c3: st.metric("SON", f"{son_fiyat:.2f} TL")
        with c4: st.metric("DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f}")

        # 4. ULTRA KOMPAKT GRAFİK
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.25, 0.75])
        
        # Neon Renkli Mumlar
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat", increasing_line_color='#00ff88', decreasing_line_color='#ff3333',
            increasing_fillcolor='#00ff88', decreasing_fillcolor='#ff3333'
        ), row=1, col=1)

        # Hacim Barları
        h_colors = ['#00ff88' if (c >= o) else '#ff3333' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=h_colors, opacity=0.4), row=2, col=1)

        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False, 
            height=380, # Grafik boyutu optimize edildi
            margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 5. ALT PANEL: TEK SATIRDA SİNYALLER
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        s1, s2, s3 = st.columns([1, 1, 1])
        
        with s1:
            if rsi > 70: st.error(f"🔴 SINYAL: SAT ({rsi:.1f})")
            elif rsi < 30: st.success(f"🟢 SINYAL: AL ({rsi:.1f})")
            else: st.info(f"🔵 SINYAL: BEKLE ({rsi:.1f})")
        
        with s2:
            st.warning(f"📊 Durum: {'Yükseliş' if degisim > 0 else 'Düşüş'}")
            
        with s3:
            st.link_button("🚀 HABERLER", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.warning("Hisse aranıyor...")

except Exception as e:
    st.error("Bağlantı hatası, lütfen kodu kontrol edin.")
