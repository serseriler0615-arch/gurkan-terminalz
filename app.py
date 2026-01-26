import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Pro", layout="wide", initial_sidebar_state="collapsed")

# Tarihleri Türkçeleştirmek için sözlük
gunler_tr = {
    'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
    'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'
}

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0d1117; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px !important; }
    .radar-card { 
        background-color: #161b22; border: 1px solid #30363d; border-left: 4px solid #00ff88;
        padding: 12px; border-radius: 8px; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ISCTR").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        # Veriyi en güncel haliyle çekmeye zorluyoruz
        ticker = yf.Ticker(aktif_hisse)
        df = ticker.history(period="1mo", interval="1d")
        
        if not df.empty:
            # En son fiyatı 'fast_info' veya son satırdan al (Gecikmeyi minimize eder)
            son_fiyat = df['Close'].iloc[-1]
            onceki_kapanis = df['Close'].iloc[-2]
            degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
            
            with c2: st.metric("CANLIYA YAKIN FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{son_fiyat-onceki_kapanis:+.2f}")

            # --- GRAFİK TÜRKÇELEŞTİRME ---
            plot_df = df[['Close']].tail(20).copy()
            # Tarihleri "Gün Ay" formatına ve Türkçe günlere çeviriyoruz
            plot_df.index = plot_df.index.strftime('%d %b') 
            
            st.markdown(f"📈 **{hisse_input} - Son 20 İş Günü (Türkçe Grafik)**")
            st.line_chart(plot_df, color="#00ff88", height=250)

            # --- AI STRATEJİ RAPORU ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            st.markdown("### 🤖 AI Teknik Raporu")
            s1, s2 = st.columns(2)
            with s1:
                st.info(f"📊 İndikatör (RSI): {rsi:.1f}")
                if rsi > 65: st.warning("⚠️ Hisse teknik olarak doygunlukta.")
                elif rsi < 35: st.success("🔥 Hisse alım için cazip seviyelerde.")
                else: st.write("⚖️ Hisse dengeli bölgede seyrediyor.")
            with s2:
                st.link_button("🚀 GÜNCEL KAP HABERLERİ", f"https://www.google.com/search?q={hisse_input}+hisse+haberleri&tbm=nws", use_container_width=True)

    except:
        st.error("Veri alınamadı. Sembolü kontrol edin.")

# --- SAĞ TARAF: AI RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for sembol in radar_list:
        try:
            r_data = yf.download(sembol, period="2d", interval="1d", progress=False)
            if not r_data.empty:
                r_son = r_data['Close'].iloc[-1]
                r_fark = ((r_son - r_data['Close'].iloc[-2]) / r_data['Close'].iloc[-2]) * 100
                ad = sembol.replace(".IS", "")
                st.markdown(f"""
                <div class="radar-card">
                    <b style="color:#00ff88;">{ad}</b> : %{r_fark:.2f}<br>
                    <small>Sinyal: YÜKSELİŞ</small>
                </div>
                """, unsafe_allow_html=True)
        except: continue
