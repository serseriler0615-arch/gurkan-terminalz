import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa ve Tema Ayarları
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

# Türkçe Ay Sözlüğü
tr_aylar = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
            "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    header {visibility: hidden;}
    /* Siyah kutuları engellemek için grafik alanını şeffaflaştır */
    .stAreaChart { background-color: transparent !important; border-radius: 10px; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 10px; border-radius: 8px; margin-bottom: 5px; border: 1px solid #30363d; }
    .asistan-box { background-color: #1c2128; border: 1px solid #00ff88; padding: 15px; border-radius: 10px; color: #e6edf3; }
    </style>
    """, unsafe_allow_html=True)

# 2. Üst Kontrol Paneli
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        hisse_kod = st.text_input("🔍 Hisse:", value="ISCTR").upper().strip()
    
    sembol = hisse_kod if "." in hisse_kod else hisse_kod + ".IS"

    try:
        ticker = yf.Ticker(sembol)
        # Zeka için 6 aylık, grafik için 20 günlük veri
        df = ticker.history(period="6mo", interval="1d")
        
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            # Anlık Fiyat (Gecikmeyi azaltmak için)
            son_fiyat = ticker.fast_info['last_price']
            dunku_kapanis = df['Close'].iloc[-2]
            yuzde_degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK %", f"%{yuzde_degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # --- TÜRKÇE VE SİYAHSIZ 20 GÜNLÜK GRAFİK ---
            plot_df = df[['Close']].tail(20).copy()
            tr_eks = []
            for d in plot_df.index:
                t = d.strftime("%d %b")
                for e, tr in tr_aylar.items(): t = t.replace(e, tr)
                tr_eks.append(t)
            plot_df.index = tr_eks
            
            st.write(f"📈 **{hisse_kod} - Son 20 Günlük Güç Göstergesi**")
            st.area_chart(plot_df, color="#00ff88", height=250)

            # --- 🧠 STRATEJİ MOTORU (DeltaGenerator Hatasız) ---
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            # RSI 14
            diff = df['Close'].diff()
            g = (diff.where(diff > 0, 0)).rolling(14).mean()
            l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🤖 Gürkan AI Stratejik Değerlendirme")
            s1, s2, s3 = st.columns(3)
            
            with s1:
                st.write("**GÜÇ (RSI)**")
                if rsi > 70: st.error(f"🔴 Aşırı Alım ({rsi:.1f})")
                elif rsi < 35: st.success(f"🟢 Fırsat Bölgesi ({rsi:.1f})")
                else: st.info(f"🔵 Dengeli ({rsi:.1f})")

            with s2:
                st.write("**TREND (MA20)**")
                if son_fiyat > ma20: st.success("📈 Pozitif (Ort. Üstü)")
                else: st.error("📉 Negatif (Ort. Altı)")

            with s3:
                st.write("**ANA YÖN (MA50)**")
                if ma20 > ma50: st.success("🚀 YÜKSELİŞ TRENDİ")
                else: st.warning("⚠️ ZAYIF GÖRÜNÜM")

            # Zeki Yorum Alanı
            st.markdown(f"""
            <div class="asistan-box">
                <b>Zeki Asistan Notu:</b> {hisse_kod} şu an {son_fiyat:.2f} TL seviyesinde. 
                RSI değeri {rsi:.1f} ile {'düzeltme bekliyor' if rsi > 70 else 'güçlü duruyor'}. 
                Kısa vadeli direnç noktası 20 günlük ortalama olan {ma20:.2f} TL olarak takip edilmelidir.
            </div>
            """, unsafe_allow_html=True)

    except: st.error("Hisse bulunamadı veya veri çekilemiyor.")

# --- SAĞ RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI RADAR")
    radar = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    for r in radar:
        try:
            rd = yf.download(r, period="2d", interval="1d", progress=False)
            if not rd.empty:
                f = ((rd['Close'].iloc[-1] - rd['Close'].iloc[-2]) / rd['Close'].iloc[-2]) * 100
                st.markdown(f'<div class="radar-card"><b>{r.split(".")[0]}</b> : %{f:.2f}</div>', unsafe_allow_html=True)
        except: continue
    if st.button("🔄 Radarı Yenile", use_container_width=True): st.rerun()
