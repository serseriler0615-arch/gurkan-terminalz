import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Sayfa Ayarları
st.set_page_config(page_title="AI Terminal v9", layout="wide")

# 1 Dakikada Bir Yenileme
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- ÜST PANEL (Arama ve Favoriler) ---
col_ara, col_fav, col_metrik = st.columns([1, 1, 1.2])

if 'favoriler' not in st.session_state:
    st.session_state.favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "ISCTR.IS", "SASA.IS"]

with col_ara:
    hisse_input = st.text_input("🔍 BIST Hisse Ara (Örn: SASA):", "").upper().strip()

with col_fav:
    secilen_fav = st.selectbox("⭐ Favoriler:", st.session_state.favoriler)

# Hisse Belirleme
if hisse_input:
    aktif_yfinance = hisse_input if "." in hisse_input else hisse_input + ".IS"
else:
    aktif_yfinance = secilen_fav

aktif_temiz = aktif_yfinance.replace(".IS", "")

# --- VERİ ÇEKME ---
try:
    df = yf.download(aktif_yfinance, period="5d", interval="1m", progress=False)
    
    if not df.empty:
        # Hata Veren Kısımları .item() ile Sayıya Dönüştürüyoruz
        son_fiyat = float(df['Close'].iloc[-1])
        acilis_fiyat = float(df['Open'].iloc[0])
        degisim_yuzde = ((son_fiyat - acilis_fiyat) / acilis_fiyat) * 100

        with col_metrik:
            # Metrik kısmında format hatası almamak için float değerleri gönderiyoruz
            st.metric(label=f"{aktif_temiz} (BIST)", 
                      value=f"{son_fiyat:.2f} TL", 
                      delta=f"{degisim_yuzde:.2f}%")

        st.divider()

        # --- PLOTLY GRAFİK ---
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Fiyat"
        )])

        fig.update_layout(
            title=f"📊 {aktif_temiz} Teknik Analiz Grafiği",
            template="plotly_dark",
            height=500,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ALT PANEL (YAPAY ZEKA ANALİZİ) ---
        c1, c2 = st.columns(2)
        with c1:
            # RSI Hesaplama (Hatasız Formül)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_serisi = 100 - (100 / (1 + rs))
            rsi_deger = float(rsi_serisi.iloc[-1])
            
            if rsi_deger > 70:
                st.error(f"🚨 RSI: {rsi_deger:.1f} - AŞIRI ALIM (Satış Gelebilir)")
            elif rsi_deger < 30:
                st.success(f"🚀 RSI: {rsi_deger:.1f} - AŞIRI SATIM (Tepki Gelebilir)")
            else:
                st.info(f"⚖️ RSI: {rsi_deger:.1f} - NÖTR")

        with c2:
            st.link_button("📰 Google Haberleri Gör", 
                           f"https://www.google.com/search?q={aktif_temiz}+hisse+haberleri&tbm=nws", 
                           use_container_width=True)

    else:
        st.warning(f"⚠️ {aktif_yfinance} için veri bulunamadı. Lütfen Borsa İstanbul kodunu doğru girdiğinizden emin olun.")

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
