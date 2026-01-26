import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Sayfa Ayarları
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide")

# 2. Üst Panel
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "ULKER.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Kodu:", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme
try:
    df = yf.download(aktif_hisse, period="5d", interval="1m", progress=False, auto_adjust=True)
    gunluk = yf.download(aktif_hisse, period="5d", interval="1d", progress=False, auto_adjust=True)
    
    if not df.empty and len(gunluk) >= 2:
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(gunluk['Close'].iloc[-2])
        fark = son_fiyat - dunku_kapanis
        degisim_yuzde = (fark / dunku_kapanis) * 100

        with col_metrik:
            st.metric(label=f"{aktif_temiz}", value=f"{son_fiyat:.2f} TL", delta=f"{degisim_yuzde:+.2f}%")

        # Grafik
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim"), row=2, col=1)
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # --- 🧠 AI YORUM MOTORU ---
        st.subheader("🤖 AI Teknik Analiz Yorumu")
        
        # RSI Hesapla
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain/loss))).iloc[-1])

        c1, c2 = st.columns(2)
        
        with c1:
            st.write(f"**Gösterge Durumu:**")
            if rsi > 70:
                st.error(f"🔴 RSI: {rsi:.1f} (Aşırı Alım)")
                yorum = "Hisse çok ısınmış. Buralardan kar satışı gelme ihtimali yüksek. Yeni giriş için riskli olabilir."
            elif rsi < 30:
                st.success(f"🟢 RSI: {rsi:.1f} (Aşırı Satım)")
                yorum = "Hisse çok ezilmiş. Teknik olarak tepki alımı beklenir. Buralar toplama bölgesi olabilir."
            else:
                st.info(f"🔵 RSI: {rsi:.1f} (Nötr)")
                yorum = "Hisse dengeli bölgede. Trendin yönünü belirlemek için hacim artışı beklemek mantıklı olacaktır."
            
            st.markdown(f"> {yorum}")

        with c2:
            st.write("**Trend Analizi:**")
            if degisim_yuzde > 0:
                st.write(f"✅ Bugün piyasadan pozitif ayrışıyor. {dunku_kapanis} TL seviyesinin üzerinde kalması olumlu.")
            else:
                st.write(f"❌ Bugün satış baskısı altında. {dunku_kapanis} TL seviyesi direnç haline gelmiş durumda.")
            
            st.link_button(f"📰 {aktif_temiz} Haberlerini Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.error("Veri alınamadı, lütfen kodu kontrol edin.")

except Exception as e:
    st.error(f"Hata: {e}")
