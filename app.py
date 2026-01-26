import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="BIST AI Terminal", layout="wide")

# Görsel Yerleşimi Düzelten Özel CSS
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stMetric { background-color: #1a1c24; border: 1px solid #30363d; padding: 20px; border-radius: 15px; }
    .stTextInput > div > div > input { font-size: 20px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Arama Bölümü (Üstte Tek Başına)
if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

st.title("🚀 BIST AI Analiz Terminali")
c1, c2 = st.columns([2, 1])
with c1:
    hisse_input = st.text_input("🔍 Hisse Kodu Girin (Örn: SASA):", "").upper().strip()
with c2:
    secilen_fav = st.selectbox("⭐ Favori Listesi:", st.session_state.favoriler)

# Aktif Sembol
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri ve Hesaplama
try:
    df = yf.download(aktif_hisse, period="5d", interval="15m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)

    if not df.empty and len(gunluk) >= 2:
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim = (fark / dunku_kapanis) * 100

        # Fiyat Metrikleri
        m1, m2, m3 = st.columns(3)
        m1.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
        m2.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}")
        m3.metric("FARK", f"{fark:+.2f} TL")

        # 4. Profesyonel Renkli Grafik
        st.markdown("---")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
        
        # Mumlar
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat", increasing_line_color='#00ff41', decreasing_line_color='#ff0000'
        ), row=1, col=1)

        # Hacim
        h_colors = ['#00ff41' if (c >= o) else '#ff0000' for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=h_colors, name="Hacim"), row=2, col=1)

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # 5. 🧠 AI SİNYAL VE YORUM (İstediğin Bölüm)
        st.markdown("---")
        st.subheader("🤖 AI Teknik Analiz ve Strateji")
        
        # RSI Hesapla
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        col_si1, col_si2 = st.columns(2)
        
        with col_si1:
            st.write(f"📊 **Gösterge Durumu (RSI):** `{rsi:.1f}`")
            if rsi > 70:
                st.error("🚨 SİNYAL: AŞIRI ALIM (SAT)")
                st.markdown("> **Yorum:** Hisse teknik olarak çok ısınmış. Kar satışları gelebilir, yeni alım için riskli bölge.")
            elif rsi < 30:
                st.success("🚀 SİNYAL: AŞIRI SATIM (AL)")
                st.markdown("> **Yorum:** Hisse çok ucuzlamış. Buradan bir tepki yükselişi beklenir, kademeli alım düşünülebilir.")
            else:
                st.info("⚖️ SİNYAL: NÖTR (BEKLE)")
                st.markdown("> **Yorum:** Hisse denge fiyatında. Net bir trend oluşumu için hacim artışı takip edilmeli.")

        with col_si2:
            st.write("📈 **Trend Analizi:**")
            if degisim > 0:
                st.write(f"✅ Hisse bugün **ALICILI** bir seyir izliyor. {dunku_kapanis} TL desteği üzerinde güç topluyor.")
            else:
                st.write(f"❌ Hisse bugün **SATICILI** bir seyir izliyor. {dunku_kapanis} TL seviyesi şu an direnç konumunda.")
            
            st.link_button("🚀 HABERLERİ AÇ", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.info("Lütfen bir BIST kodu girin veya favorilerden seçin.")

except Exception as e:
    st.error(f"Hata: {e}")
