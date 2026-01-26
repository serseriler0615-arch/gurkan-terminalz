import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Sayfa Ayarları
st.set_page_config(page_title="BIST AI Terminal v8", layout="wide")

# 1 Dakikada Bir Yenileme (Gecikmeyi azaltmak için)
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- ÜST PANEL (Arama ve Favoriler) ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "SASA.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Ara (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme Mantığı
if hisse_input:
    aktif_yfinance = hisse_input if "." in hisse_input else hisse_input + ".IS"
    aktif_temiz = aktif_yfinance.replace(".IS", "")
else:
    aktif_yfinance = secilen_fav
    aktif_temiz = aktif_yfinance.replace(".IS", "")

# --- VERİ ÇEKME VE GRAFİK ÇİZME ---
try:
    # Veriyi çekiyoruz
    df = yf.download(aktif_yfinance, period="5d", interval="1m", progress=False)
    
    if not df.empty:
        with col_metrik:
            son_fiyat = float(df['Close'].iloc[-1])
            degisim = ((son_fiyat - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
            st.metric(f"{aktif_temiz} Fiyat", f"{son_fiyat:.2f} TL", f"%{degisim:.2f}")

        st.divider()

        # PLOTLY İLE KENDİ GRAFİĞİMİZİ ÇİZİYORUZ (Asla Apple Gelmez)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Fiyat"
        )])

        fig.update_layout(
            title=f"📊 {aktif_temiz} Canlı Teknik Analiz Grafiği (TL)",
            yaxis_title="Fiyat (TL)",
            xaxis_rangeslider_visible=False,
            template="plotly_dark", # Daha profesyonel görünüm için karanlık tema
            height=600,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ALT PANEL (AI SİNYAL) ---
        c1, c2 = st.columns(2)
        with c1:
            # RSI Hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            if rsi > 70: st.error(f"🚨 RSI: {rsi:.1f} - AŞIRI ALIM (Satış Gelebilir)")
            elif rsi < 30: st.success(f"🚀 RSI: {rsi:.1f} - AŞIRI SATIM (Tepki Gelebilir)")
            else: st.info(f"⚖️ RSI: {rsi:.1f} - NÖTR BÖLGE")

        with c2:
            st.link_button("📰 Google Haberleri Gör", f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", use_container_width=True)

    else:
        st.warning(f"⚠️ {aktif_yfinance} için veri bulunamadı. Lütfen kodu kontrol edin.")

except Exception as e:
    st.error(f"Hata oluştu: {e}")
