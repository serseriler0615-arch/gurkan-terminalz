import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Stil ve Arka Plan Sabitleme (Siyahlığı Boğma)
st.set_page_config(page_title="Gürkan AI Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Tüm ekranı tek renge zorla */
    .stApp, .block-container, [data-testid="stVerticalBlock"] { background-color: #0d1117 !important; }
    header {visibility: hidden;}
    
    /* Metrik ve Kartlar */
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    .radar-card { background-color: #161b22; border-left: 4px solid #00ff88; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #30363d; }
    .asistan-notu { background: #1c2128; border: 1px solid #00ff88; padding: 15px; border-radius: 12px; color: #e6edf3; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ana Panel Düzeni
ana_sol, ana_sag = st.columns([3, 1])

with ana_sol:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        h_input = st.text_input("🔍 Hisse:", value="ISCTR").upper().strip()
    
    sembol = h_input if "." in h_input else h_input + ".IS"

    try:
        # ANA VERİ ÇEKME
        df = yf.download(sembol, period="3mo", interval="1d", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            son_fiyat = float(df['Close'].iloc[-1])
            dunku_kapanis = float(df['Close'].iloc[-2])
            degisim = ((son_fiyat - dunku_kapanis) / dunku_kapanis) * 100

            with c2: st.metric("FİYAT", f"{son_fiyat:.2f} TL")
            with c3: st.metric("GÜNLÜK", f"%{degisim:.2f}", f"{son_fiyat-dunku_kapanis:+.2f}")

            # GRAFİK: Sadece 20 gün ve siyahlık yapmayan yerel bileşen
            st.write(f"📈 **{h_input} - Son 20 Günlük Trend**")
            st.area_chart(df['Close'].tail(20), color="#00ff88", height=250)

            # ASİSTAN ANALİZİ
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            diff = df['Close'].diff(); g = (diff.where(diff > 0, 0)).rolling(14).mean(); l = (-diff.where(diff < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (g/l))).iloc[-1]

            st.markdown("### 🤵 Kişisel Asistan Yorumu")
            not_metni = f"Dostum, **{h_input}** şu an {son_fiyat:.2f} TL. "
            if rsi < 45: not_metni += "Hisse dinlenmiş, RSI düşük seviyelerde. Bu bir fırsat olabilir."
            elif rsi > 70: not_metni += "Hisse çok ısınmış, buralardan girmek riskli gözüküyor."
            else: not_metni += "Şu an dengeli bir seyir var, MA20 desteğini takip etmelisin."
            
            st.markdown(f'<div class="asistan-notu">{not_metni}</div>', unsafe_allow_html=True)
    except:
        st.error("Veri alınamadı.")

with ana_sag:
    st.markdown("### 🛰️ AI RADAR")
    # Radarı garantiye alan liste ve döngü
    radarlar = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "ISCTR.IS", "SASA.IS"]
    
    for r in radarlar:
        try:
            r_df = yf.download(r, period="5d", interval="1d", progress=False)
            if not r_df.empty:
                if isinstance(r_df.columns, pd.MultiIndex): r_df.columns = r_df.columns.get_level_values(0)
                r_son = r_df['Close'].iloc[-1]
                r_once = r_df['Close'].iloc[-2]
                r_fark = ((r_son - r_once) / r_once) * 100
                st.markdown(f"""
                <div class="radar-card">
                    <b style="color:#00ff88;">{r.split('.')[0]}</b><br>
                    <span style="font-size: 14px; color: #e6edf3;">Fiyat: {r_son:.2f} TL</span>
                    <span style="color: {'#00ff88' if r_fark > 0 else '#ff4b4b'}; float: right;">%{r_fark:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.caption(f"{r} güncellenemedi")

    if st.button("🔄 Radarı Yenile", use_container_width=True):
        st.rerun()
