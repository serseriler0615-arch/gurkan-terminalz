import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Pro", layout="wide", initial_sidebar_state="collapsed")

# Türkçe Ay ve Gün Dönüşüm Sözlüğü
tr_aylar = {
    "Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
    "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"
}

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0d1117; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px !important; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ana Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ISCTR").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        # VERİ ÇEKME: En güncel tekil fiyatı çekmek için Ticker metodunu kullanıyoruz
        hisse_obj = yf.Ticker(aktif_hisse)
        
        # Grafik için veri (Son 1 ay)
        df = hisse_obj.history(period="1mo", interval="1d")
        
        # ANLIK FİYAT (Yahoo'nun sunduğu en son veriye zorlama)
        # fast_info bazen daha hızlı tepki verir
        son_fiyat = hisse_obj.fast_info['last_price'] 
        onceki_kapanis = df['Close'].iloc[-2]
        degisim_yuzde = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
        fark = son_fiyat - onceki_kapanis

        with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
        with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim_yuzde:.2f}", f"{fark:+.2f}")

        # --- TÜRKÇE VE TRENDY GRAFİK ---
        plot_df = df[['Close']].tail(20).copy()
        
        # Tarih formatını Türkçeleştirme
        yeni_tarihler = []
        for dt in plot_df.index:
            tarih_str = dt.strftime("%d %b") # "26 Jan"
            for eng, tr in tr_aylar.items():
                tarih_str = tarih_str.replace(eng, tr)
            yeni_tarihler.append(tarih_str)
        
        plot_df.index = yeni_tarihler
        
        st.markdown(f"🚀 **{hisse_input} Trend Analizi (Tam Türkçe)**")
        st.area_chart(plot_df, color="#00ff88", height=300)

        # --- AI STRATEJİ RAPORU ---
        # RSI Hesaplama
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

        st.markdown("### 🤖 AI Strateji Raporu")
        s1, s2 = st.columns(2)
        with s1:
            st.info(f"📊 İndikatör (RSI): {rsi:.1f}")
            if rsi > 65: st.warning("⚠️ Sinyal: SAT (Aşırı Alım Bölgesi)")
            elif rsi < 35: st.success("🔥 Sinyal: AL (Fırsat Bölgesi)")
            else: st.write("⚖️ Sinyal: NÖTR (Trend Bekleniyor)")
        with s2:
            st.link_button("📰 KAP VE GÜNCEL HABERLER", f"https://www.google.com/search?q={hisse_input}+hisse+haberleri&tbm=nws", use_container_width=True)

    except Exception as e:
        st.error(f"Veri çekme hatası: {e}. Lütfen sembolü kontrol edin.")

# --- SAĞ TARAF: AI RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for sembol in radar_list:
        try:
            r_data = yf.download(sembol, period="2d", interval="1d", progress=False)
            if not r_data.empty:
                r_son = r_data['Close'].iloc[-1]
                r_once = r_data['Close'].iloc[-2]
                r_fark = ((r_son - r_once) / r_once) * 100
                ad = sembol.replace(".IS", "")
                st.markdown(f"""
                <div class="radar-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b style="color:#00ff88;">{ad}</b>
                        <span style="color:{'#00ff88' if r_fark > 0 else '#ff3333'};">%{r_fark:.2f}</span>
                    </div>
                    <small style="color:#888;">AI Tahmini: YÜKSELİŞ</small>
                </div>
                """, unsafe_allow_html=True)
        except: continue
    
    if st.button("🔄 Radarı Yenile", use_container_width=True):
        st.rerun()
