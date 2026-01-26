import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Borsa Asistanı", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel: Kontrol Merkezi
col_ara, col_fav, col_bilgi = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "ULKER.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 Hisse Kodu Girin:", placeholder="Örn: SASA").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Hızlı Erişim:", st.session_state.favoriler)

# Sembol Kararı
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Motoru
try:
    # Teknik analiz için 60 günlük, grafik için dakikalık veri
    df = yf.download(aktif_hisse, period="60d", interval="1h", progress=False, auto_adjust=True)
    dakikalik = yf.download(aktif_hisse, period="1d", interval="1m", progress=False, auto_adjust=True)

    if not df.empty:
        # Fiyat ve Değişim Hesaplama
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(df['Close'].iloc[-2])
        degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

        with col_bilgi:
            st.metric(label=f"{aktif_temiz} Güncel Durum", 
                      value=f"{son_fiyat:.2f} TL", 
                      delta=f"{degisim:+.2f}%")

        # 4. Profesyonel Analiz Grafiği
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_width=[0.2, 0.8])

        # Mumlar ve Hareketli Ortalamalar (MA20 ve MA50)
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()

        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='yellow', width=1), name="MA20 (Kısa Vade)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='orange', width=1), name="MA50 (Orta Vade)"), row=1, col=1)
        
        # Hacim
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='#30363d'), row=2, col=1)

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 5. 🧠 AI ASİSTAN YORUMU
        st.subheader(f"🤖 AI Asistan Analiz Notları: {aktif_temiz}")
        
        # RSI Hesaplama
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("### 📊 Güç Göstergesi (RSI)")
            if rsi > 70:
                st.error(f"Seviye: {rsi:.1f} - AŞIRI ALIM")
                st.write("Hisse teknik olarak doyuma ulaşmış görünüyor. Kar satışlarına karşı tetikte olun.")
            elif rsi < 30:
                st.success(f"Seviye: {rsi:.1f} - AŞIRI SATIM")
                st.write("Hisse çok ucuzlamış (ezilmiş). Buradan bir tepki yükselişi gelebilir.")
            else:
                st.info(f"Seviye: {rsi:.1f} - NÖTR")
                st.write("Hisse dengeli bölgede. Trendin yönü için hacim artışı takip edilmeli.")

        with c2:
            st.markdown("### 📈 Trend Durumu")
            if son_fiyat > df['MA20'].iloc[-1]:
                st.write("✅ **Pozitif:** Fiyat 20 günlük ortalamanın üzerinde. Kısa vadeli yükseliş trendi korunuyor.")
            else:
                st.write("❌ **Negatif:** Fiyat ortalamanın altında. Satış baskısı devam ediyor olabilir.")

        with c3:
            st.markdown("### 💡 Strateji Önerisi")
            if rsi < 40 and son_fiyat > dunku_kapanis:
                st.write("🌟 **Potansiyel:** Toplama aşamasında olabilir. Kademeli alım düşünülebilir.")
            elif rsi > 65:
                st.write("⚠️ **Dikkat:** Mevcut pozisyonlar için 'Stop-Loss' (Zarar Kes) seviyesi yukarı çekilmeli.")
            else:
                st.write("🔎 **Bekle-Gör:** Net bir kırılım olana kadar pozisyon korunmalı.")

        st.divider()
        st.link_button(f"🔗 {aktif_temiz} Haberlerini ve KAP Bildirimlerini Kontrol Et", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws")

    else:
        st.error("Veri çekilemedi. Lütfen internet bağlantınızı veya hisse kodunu kontrol edin.")

except Exception as e:
    st.error(f"Asistan şu an veriye ulaşamıyor: {e}")
