import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa ve Stil Ayarları
st.set_page_config(page_title="Gürkan AI", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { 
        background-color: #1a1c24; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 5px 15px !important; 
    }
    /* Grafik alanını biraz daraltıyoruz */
    [data-testid="stVerticalBlock"] > div:nth-child(3) {
        max-height: 300px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol ve Fiyat Paneli
with st.container():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    with c1:
        hisse_input = st.text_input("", value="ULKER", label_visibility="collapsed").upper().strip()
    
    # Otomatik sembol tamamlama
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    # Veri Çekme
    try:
        raw_data = yf.download(aktif_hisse, period="1mo", interval="1d", progress=False)
        
        if not raw_data.empty:
            df = raw_data[['Close']].copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            onceki_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
            fark = son_fiyat - onceki_kapanis

            with c2: st.write(f"**{hisse_input} Portföy**")
            with c3: st.metric("FİYAT", f"{son_fiyat:.2f} TL")
            with c4: st.metric("DEĞİŞİM", f"%{degisim:.2f}", f"{fark:+.2f}")

            # 3. Küçültülmüş Grafik
            # st.line_chart kullanarak daha ince ve zarif bir görünüm elde ediyoruz
            st.markdown(f"📊 **Trend Analizi (Son 30 Gün)**")
            st.line_chart(df['Close'], color="#00ff88", height=250) # Boyut 250px'e çekildi

            # 4. AI Sinyalleri (Kompakt Alt Panel)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            st.markdown("---")
            s1, s2 = st.columns([2, 1])
            
            with s1:
                if rsi > 70:
                    st.error(f"🔴 AI SİNYAL: SAT (RSI: {rsi:.1f}) - Kar realizasyonu zamanı gelmiş olabilir.")
                elif rsi < 30:
                    st.success(f"🟢 AI SİNYAL: AL (RSI: {rsi:.1f}) - Hisse toplama bölgesinde görünüyor.")
                else:
                    st.info(f"🔵 AI SİNYAL: BEKLE (RSI: {rsi:.1f}) - Trendin netleşmesi beklenmeli.")
            
            with s2:
                st.link_button("📰 HABERLER", f"https://www.google.com/search?q={hisse_input}+hisse+haberleri&tbm=nws", use_container_width=True)

    except Exception as e:
        st.warning("Veri güncellenirken bir sorun oluştu, sembolü kontrol edin.")
