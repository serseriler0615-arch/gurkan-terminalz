import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Elite", layout="wide", initial_sidebar_state="collapsed")

# Türkçe Ay İsimleri
aylar_tr = {
    "Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
    "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"
}

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0d1117; }
    header {visibility: hidden;}
    /* Metrik Kartları - Trendy Dark */
    div[data-testid="stMetric"] { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Radar Kartları */
    .radar-card { 
        background-color: #161b22; border: 1px solid #30363d; border-left: 4px solid #00ff88;
        padding: 12px; border-radius: 10px; margin-bottom: 10px;
    }
    /* Alt Bilgi Kutuları */
    .status-box { background-color: #1c2128; border: 1px solid #30363d; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_input = st.text_input("🔍 Hisse Sorgula:", value="ISCTR").upper().strip()
    
    aktif_hisse = hisse_input if "." in hisse_input else hisse_input + ".IS"

    try:
        # Veriyi çek (En güncel hali için interval='15m' denenebilir ama stabilite için 1d)
        df = yf.download(aktif_hisse, period="1mo", interval="1d", progress=False, auto_adjust=True)
        
        if not df.empty:
            # MultiIndex Temizliği
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            onceki_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
            
            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{son_fiyat-onceki_kapanis:+.2f}")

            # --- TRENDY GRAFİK (DOLGULU VE TÜRKÇE) ---
            plot_df = df[['Close']].tail(20).copy()
            
            # Tarihleri Türkçeleştirme İşlemi
            yeni_index = []
            for d in plot_df.index:
                gun_ay = d.strftime("%d %b") # "26 Jan" gibi
                for eng, tr in aylar_tr.items():
                    gun_ay = gun_ay.replace(eng, tr)
                yeni_index.append(gun_ay)
            plot_df.index = yeni_index
            
            st.markdown(f"🚀 **{hisse_input} Trend Analizi (Türkçe)**")
            st.area_chart(plot_df, color="#00ff88", height=280)

            # --- AI ANALİZ ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            st.markdown("### 🤖 AI Strateji Raporu")
            s1, s2 = st.columns(2)
            with s1:
                st.markdown(f'<div class="status-box"><b>📊 İndikatör (RSI):</b> {rsi:.1f}</div>', unsafe_allow_html=True)
                if rsi > 65: st.error("🚨 Sinyal: SAT (Aşırı Alım)")
                elif rsi < 35: st.success("🚀 Sinyal: AL (Fırsat Bölgesi)")
                else: st.info("⚖️ Sinyal: NÖTR (Bekle)")
            with s2:
                st.write("") # Hizalama için
                st.link_button("📰 KAP HABERLERİNİ GÖR", f"https://www.google.com/search?q={hisse_input}+hisse+haberleri&tbm=nws", use_container_width=True)

    except:
        st.error("Veri alınamadı. İnternet bağlantınızı veya sembolü kontrol edin.")

# --- SAĞ TARAF: TRENDY RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for sembol in radar_list:
        try:
            r_data = yf.download(sembol, period="2d", interval="1d", progress=False)
            if not r_data.empty:
                if isinstance(r_data.columns, pd.MultiIndex): r_data.columns = r_data.columns.get_level_values(0)
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
                </div>
                """, unsafe_allow_html=True)
        except: continue
