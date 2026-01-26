import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Gürkan AI Pro", layout="wide", initial_sidebar_state="collapsed")

# Türkçe Ay Sözlüğü
aylar_tr = {
    "Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisan", "May": "Mayıs", "Jun": "Haziran",
    "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"
}

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; background-color: #0d1117; }
    header {visibility: hidden;}
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #30363d; }
    /* Siyahlıkları yok etmek için zorunlu CSS */
    .stPlotlyChart { background: transparent !important; }
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
        # VERİ ÇEKME (Zeki Asistan için 3 aylık çekiyoruz ama 20 gün gösteriyoruz)
        h_obj = yf.Ticker(aktif_hisse)
        df = h_obj.history(period="3mo", interval="1d")
        
        if not df.empty:
            son_fiyat = h_obj.fast_info['last_price']
            onceki_kapanis = df['Close'].iloc[-2]
            degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100

            with c2: st.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK DEĞİŞİM", f"%{degisim:.2f}", f"{son_fiyat-onceki_kapanis:+.2f}")

            # --- TÜRKÇE VE 20 GÜNLÜK TRENDY GRAFİK ---
            # Sadece son 20 gün
            plot_df = df[['Close']].tail(20).copy()
            
            yeni_eks = []
            for dt in plot_df.index:
                t = dt.strftime("%d %b")
                for e, tr in aylar_tr.items(): t = t.replace(e, tr)
                yeni_eks.append(t)
            plot_df.index = yeni_eks
            
            st.markdown(f"🚀 **{hisse_input} - Son 20 İş Günü Analizi**")
            # Siyahlık yapmayan en güvenli grafik tipi
            st.area_chart(plot_df, color="#00ff88", height=280)

            # --- 🧠 ZEKİ ASİSTAN ANALİZ MOTORU ---
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            # RSI 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]

            st.markdown("### 🤖 Zeki Asistan Strateji Raporu")
            s1, s2, s3 = st.columns(3)
            
            with s1:
                st.write("**GÜÇ DENGESİ (RSI)**")
                if rsi > 70: st.error(f"🔴 Aşırı Alım ({rsi:.1f})")
                elif rsi < 30: st.success(f"🟢 Aşırı Satım ({rsi:.1f})")
                else: st.info(f"🔵 Dengeli ({rsi:.1f})")

            with s2:
                st.write("**TREND (MA20)**")
                if son_fiyat > ma20: st.success("📈 Fiyat Ort. Üstünde")
                else: st.error("📉 Satış Baskısı Var")

            with s3:
                st.write("**HEDEF / DURUM**")
                # Zeki Yorumlama
                if son_fiyat > ma20 and rsi < 60: st.success("🚀 YÜKSELİŞ POTANSİYELİ")
                elif son_fiyat < ma20 and rsi > 40: st.warning("⚠️ BEKLE VE GÖR")
                else: st.error("🛑 RİSKLİ BÖLGE")

            st.markdown(f"> **Zeki Not:** {hisse_input} için 20 günlük ortalama **{ma20:.2f} TL**. Fiyat bu seviyenin {'üzerinde' if son_fiyat > ma20 else 'altında'} kalarak {'güç topluyor' if son_fiyat > ma20 else 'zayıflıyor'}.")

    except:
        st.error("Veri hatası! Sembolü kontrol edin.")

# --- SAĞ TARAF: AI RADAR ---
with ana_sag:
    st.markdown("### 🛰️ AI POTANSİYEL")
    radar_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    for sembol in radar_list:
        try:
            r_data = yf.download(sembol, period="5d", interval="1d", progress=False)
            if not r_data.empty:
                fark = ((r_data['Close'].iloc[-1] - r_data['Close'].iloc[-2]) / r_data['Close'].iloc[-2]) * 100
                st.markdown(f'<div class="radar-card"><b style="color:#00ff88;">{sembol.split(".")[0]}</b> : %{fark:.2f}</div>', unsafe_allow_html=True)
        except: continue
    if st.button("🔄 Radarı Yenile", use_container_width=True): st.rerun()
