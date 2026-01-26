import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa ve Stil Ayarları
st.set_page_config(page_title="Gürkan AI Pro Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #1a1c24; border: 1px solid #30363d; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

with c1:
    hisse_input = st.text_input("", value="ULKER", label_visibility="collapsed").upper().strip()

aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

# 3. Gelişmiş Veri Motoru
try:
    # Daha sağlıklı analiz için 6 aylık veri çekiyoruz
    df_raw = yf.download(aktif_hisse, period="6mo", interval="1d", progress=False)
    
    if not df_raw.empty:
        # MultiIndex Temizliği
        df = df_raw.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        son_fiyat = float(df['Close'].iloc[-1])
        dunku_kapanis = float(df['Close'].iloc[-2])
        degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

        with c3: st.metric("SON FİYAT", f"{son_fiyat:.2f} TL")
        with c4: st.metric("GÜNLÜK %", f"%{degisim:.2f}", f"{son_fiyat - dunku_kapanis:+.2f}")

        # --- TEKNİK HESAPLAMALAR ---
        # 1. RSI (14 Günlük)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

        # 2. Hareketli Ortalamalar (MA20 ve MA50)
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]

        # 3. Hacim Kontrolü
        ortalama_hacim = df['Volume'].tail(20).mean()
        son_hacim = df['Volume'].iloc[-1]

        # 4. GRAFİK (Küçültülmüş ve Net)
        st.line_chart(df['Close'].tail(30), color="#00ff88", height=230)

        # 5. 🧠 AI ÇOKLU ANALİZ MOTORU
        st.subheader("🤖 AI Teknik Strateji Raporu")
        
        col1, col2, col3 = st.columns(3)
        
        # Sinyal Karar Mekanizması
        puan = 0
        if rsi < 40: puan += 1 # Aşırı satım fırsatı
        if son_fiyat > ma20: puan += 1 # Kısa vade pozitif
        if son_fiyat > ma50: puan += 1 # Orta vade pozitif
        if son_hacim > ortalama_hacim: puan += 1 # Hacim destekli

        with col1:
            st.markdown("**🔍 İndikatör Analizi**")
            if rsi > 70: st.error(f"RSI: {rsi:.1f} (Aşırı Şişmiş)")
            elif rsi < 30: st.success(f"RSI: {rsi:.1f} (Dip Seviye)")
            else: st.info(f"RSI: {rsi:.1f} (Dengeli)")

        with col2:
            st.markdown("**📈 Trend Gücü**")
            if son_fiyat > ma20: st.success("Fiyat MA20 Üstünde (Pozitif)")
            else: st.error("Fiyat MA20 Altında (Negatif)")
            
        with col3:
            st.markdown("**📢 Nihai Karar**")
            if puan >= 3: st.success("🔥 GÜÇLÜ AL - Trend Destekleniyor")
            elif puan == 2: st.info("⚖️ BEKLE - Belirsiz Bölge")
            else: st.error("⚠️ SAT / DİKKAT - Trend Zayıf")

        st.markdown("---")
        st.write(f"**💡 Özet Yorum:** {hisse_input} hissesi şu an {son_fiyat:.2f} seviyesinde. "
                 f"20 günlük ortalaması olan {ma20:.2f} {'üzerinde' if son_fiyat > ma20 else 'altında'} seyrediyor. "
                 f"Hacim { 'yükselişi destekliyor' if son_hacim > ortalama_hacim else 'zayıf kalıyor'}. ")

except Exception as e:
    st.error("Sembolü doğru girdiğinizden emin olun (Örn: THYAO)")
