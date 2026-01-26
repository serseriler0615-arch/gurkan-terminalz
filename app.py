import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI", layout="wide")

# Tasarımı Sadeleştiren CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel
c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])

with c1:
    hisse_input = st.text_input("🔍 Hisse Yaz ve Enterla:", "ULKER").upper().strip()
with c2:
    st.write("") # Boşluk
    st.write("Favoriler: THYAO, EREGL, ISCTR")

# Sembol Hazırlığı
aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

# 3. Veri Çekme ve Temizleme (Hatasız Yöntem)
try:
    # Veriyi çekiyoruz
    raw_data = yf.download(aktif_hisse, period="1mo", interval="1d", progress=False)
    
    if not raw_data.empty:
        # MultiIndex hatasını engellemek için sadece 'Close' sütununu saf hale getiriyoruz
        df = raw_data[['Close']].copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_kapanis = float(df['Close'].iloc[-2])
        degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
        fark = son_fiyat - onceki_kapanis

        # Metrikler
        with c3: st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with c4: st.metric("GÜNLÜK %", f"%{degisim:.2f}", f"{fark:+.2f}")

        # 4. GARANTİ GRAFİK (Siyah Ekran Vermeyen Yerel Motor)
        st.subheader(f"📈 {hisse_input} Fiyat Takibi (Son 1 Ay)")
        st.area_chart(df['Close'], color="#00ff88")

        # 5. GERÇEK ANALİZ MOTORU (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

        st.markdown("---")
        a1, a2 = st.columns(2)
        
        with a1:
            st.write(f"**🤖 AI Analiz Notu (RSI: {rsi:.1f})**")
            if rsi > 70:
                st.error("🚨 SİNYAL: SAT - Hisse teknik olarak aşırı primli (Doygunluk).")
            elif rsi < 30:
                st.success("🚀 SİNYAL: AL - Hisse teknik olarak dipte (Fırsat Bölgesi).")
            else:
                st.info("⚖️ SİNYAL: BEKLE - Hisse yatay/dengeli seyrediyor.")

        with a2:
            st.link_button("🚀 GÜNCEL HABERLERİ AÇ", f"https://www.google.com/search?q={hisse_input}+hisse+haberleri&tbm=nws", use_container_width=True)

except Exception as e:
    st.error(f"Veri çekilemedi. Hata: {e}")
