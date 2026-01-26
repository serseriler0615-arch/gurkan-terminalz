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
    [data-testid="stMetricDelta"] svg { display: none; } /* Ok işaretini temizle */
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

# Aktif Hisse Mantığı
aktif_hisse = (hisse_input if "." in hisse_input else hisse_input + ".IS") if hisse_input else secilen_fav
aktif_temiz = aktif_hisse.replace(".IS", "")

# 3. Veri Çekme ve Doğru Hesaplama
try:
    # 'period="5d"' alıyoruz ki dünkü kapanışa (Close.iloc[-2]) erişebilelim
    df = yf.download(aktif_hisse, period="5d", interval="1m", progress=False)
    
    if not df.empty:
        # GERÇEK HESAPLAMA: Son Fiyat vs Önceki Gün Kapanış
        # 1 dakikalık veride bir önceki günün kapanışını bulmak için gün bazlı veri çekiyoruz
        gunluk = yf.download(aktif_hisse, period="2d", interval="1d", progress=False)
        
        son_fiyat = float(df['Close'].iloc[-1])
        # Eğer bugün borsa açıksa dünkü kapanışı, kapalıysa bir önceki günü alırız
        onceki_kapanis = float(gunluk['Close'].iloc[-2]) 
        
        fark = son_fiyat - onceki_kapanis
        degisim_yuzde = (fark / onceki_kapanis) * 100

        with col_metrik:
            label_text = f"{aktif_temiz} (BIST)"
            val_text = f"{son_fiyat:.2f} TL"
            delta_text = f"{degisim_yuzde:+.2f}% ({fark:+.2f} TL)"
            
            # Değişim artıysa yeşil, eksiyse kırmızı görünür
            st.metric(label=label_text, value=val_text, delta=delta_text)

        # 4. Grafik Bölümü (Plotly)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_width=[0.2, 0.8])

        # Mum Grafik
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # Hacim
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Hacim", marker_color='rgba(100, 100, 100, 0.5)'), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117"
        )
        st.plotly_chart(fig, use_container_width=True)

        # 5. RSI ve Haberler
        c1, c2 = st.columns(2)
        with c1:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            if rsi > 70: st.warning(f"⚠️ RSI: {rsi:.1f} - Aşırı Alım (Dikkat!)")
            elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - Aşırı Satım (Fırsat olabilir)")
            else: st.info(f"⚖️ RSI: {rsi:.1f} - Kararlı Bölge")
        with c2:
            st.link_button(f"📰 {aktif_temiz} Haberlerini Oku", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.error("Veri çekilemedi. Lütfen hisse kodunu kontrol edin.")

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
